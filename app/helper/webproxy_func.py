import httpx
import re
from fastapi import Request
from urllib.parse import unquote, urljoin
from loguru import logger
from typing import List
from starlette.datastructures import (
    Headers as StarletteHeaders,
)
from starlette.datastructures import (
    MutableHeaders as StarletteMutableHeaders,
)

from typing import (
    Any,
    List,
    NamedTuple,
    NoReturn,
    Optional,
    Union,
)


class _ConnectionHeaderParseResult(NamedTuple):
    """Parse result of "connection" header.

    Attributes:
        require_close: If "connection" header contain "close" value, this will be True, else False.
        new_headers: New request headers.
            "connection" header does not contain a 'close' value, but must contain 'keep-alive' value,
            and the "keep-alive" header was removed.
    """

    require_close: bool
    new_headers: StarletteMutableHeaders


def isValidDomain(url):
    if url.startswith("http://") or url.startswith("https://"):
        return True


def modifyResquestHeader(request: Request, url: str) -> dict:
    """Add referer and host header"""
    header = {}
    for k, v in request.headers.items():
        header[k] = v
    header["referer"] = url
    header["host"] = url.replace("http://", "").replace("https://", "").split("/")[0]
    header[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/999.0.9999.999 Safari/537.36"

    logger.info(f"Proxy request header: {header}")
    return header


def modifyResponseHeader(header: httpx.Headers) -> dict:
    """set allow proxy headers to response"""
    final_header = {}
    for k, v in header.items():
        final_header[k] = v
    logger.info(f"Modify Proxy response header: {final_header}")
    return final_header


def modifyUrl(request: Request, url: str) -> str:
    if request.url.query:
        url += "?" + request.url.query
    return unquote(url)


def getMovedUrl(url: str) -> str:
    """get the moved url"""
    with httpx.Client(verify=False) as client:
        resp = client.head(url, follow_redirects=True)
        return str(resp.url)


def disposeHtml(html: bytes, proxy_url: str) -> str:
    """dispose html"""
    pattern = r'(src|href|content)="(.*?)"'
    content = re.sub(
        pattern,
        lambda match: match.group(1) + '="' + urljoin(proxy_url, match.group(2)) + '"',
        html.decode("utf-8"),
    )
    # print(content)
    return content


def change_necessary_client_header_for_httpx(
    *, headers: StarletteHeaders, target_url: httpx.URL
) -> StarletteMutableHeaders:
    """Change client request headers for sending to proxy server.

    - Change "host" header to `target_url.netloc.decode("ascii")`.
    - If "Cookie" header is not in headers,
        will forcibly add a empty "Cookie" header
        to avoid httpx.AsyncClient automatically add another user cookiejar.

    Args:
        headers: original client request headers.
        target_url: httpx.URL of target server url.

    Returns:
        New requests headers, the copy of original input headers.
    """
    # https://www.starlette.io/requests/#headers
    new_headers = headers.mutablecopy()

    # 将host字段更新为目标url的host
    # TODO: 如果查看httpx.URL源码，就会发现netloc是被字符串编码成bytes的，能否想个办法直接获取字符串来提高性能?
    new_headers["host"] = target_url.netloc.decode("ascii")

    # https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Cookie

    # FIX: https://github.com/WSH032/fastapi-proxy-lib/security/advisories/GHSA-7vwr-g6pm-9hc8
    # forcibly set `Cookie` header to avoid httpx.AsyncClient automatically add another user cookiejar
    if "Cookie" not in new_headers:  # case-insensitive
        new_headers["Cookie"] = ""

    return new_headers


def change_client_header(
    *, headers: StarletteHeaders, target_url: httpx.URL
) -> _ConnectionHeaderParseResult:
    """Change client request headers for sending to proxy server.

    - Change "host" header to `target_url.netloc.decode("ascii")`.
    - If "Cookie" header is not in headers,
        will forcibly add a empty "Cookie" header
        to avoid httpx.AsyncClient automatically add another user cookiejar.
    - Will remove "close" value in "connection" header, and add "keep-alive" value to it.
    - And remove "keep-alive" header.

    Args:
        headers: original client request headers.
        target_url: httpx.URL of target server url.

    Returns:
        _ConnectionHeaderParseResult:
            require_close: If "connection" header contain "close" value, this will be True, else False.
            new_headers: New requests headers, the **copy** of original input headers.
    """
    # https://www.starlette.io/requests/#headers

    new_headers = change_necessary_client_header_for_httpx(
        headers=headers, target_url=target_url
    )

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection#syntax
    # NOTE: http标准中规定，connecttion头字段的值用于指示逐段头，而标头是大小写不敏感的，故认为可以转为小写处理
    client_connection_header = [
        v.strip() for v in new_headers.get("connection", "").lower().split(",")
    ]

    # 判断原始请求头中是否有"close"字段，如果有则将其移除，并记录
    if "close" in client_connection_header:
        whether_require_close = True
        client_connection_header.remove("close")
    else:
        whether_require_close = False
    # 强制添加"keep-alive"字段保持连接
    if "keep-alive" not in client_connection_header:
        client_connection_header.insert(0, "keep-alive")
    # 将新的connection头字段更新到新的请求头中
    # 因为 "keep-alive" 一定存在于 "connection"字段 中，所以这里不需要判断是否为空
    new_headers["connection"] = ",".join(client_connection_header)

    # 移除"keep-alive"字段
    if "keep-alive" in new_headers:
        del new_headers["keep-alive"]

    return _ConnectionHeaderParseResult(whether_require_close, new_headers)


def change_server_header(
    *, headers: httpx.Headers, require_close: bool
) -> httpx.Headers:
    """Change server response headers for sending to client.

    - If require_close is True, will make sure "connection: close" in headers, else will remove it.
    - And remove "keep-alive" header.

    Args:
        headers: server response headers
        require_close: whether require close connection

    Returns:
        The **oringinal headers**, but **had been changed**.
    """
    server_connection_header: List[str] = [
        v.strip() for v in headers.get("connection", "").lower().split(",")
    ]

    # 移除或添加"connection": "close"头
    if require_close:
        if "close" not in server_connection_header:
            server_connection_header.insert(0, "close")
    else:
        if "close" in server_connection_header:
            server_connection_header.remove("close")
    # 将新的connection头字段更新到新的请求头中，如果为空则移除
    if server_connection_header:
        headers["connection"] = ",".join(server_connection_header)
    else:
        if "connection" in headers:
            del headers["connection"]

    # 移除"keep-alive"字段
    if "keep-alive" in headers:
        del headers["keep-alive"]

    return headers
