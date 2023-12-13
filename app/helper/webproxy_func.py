# modify for: https://github.com/WSH032/fastapi-proxy-lib/blob/main/src/fastapi_proxy_lib/core/http.py
import httpx
import re
from fastapi import Request, Response
from urllib.parse import unquote, urljoin
from loguru import logger
from typing import List
from starlette.datastructures import (
    Headers as StarletteHeaders,
)
from starlette.datastructures import (
    MutableHeaders as StarletteMutableHeaders,
)
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse, PlainTextResponse
import gzip

from typing import (
    List,
    NamedTuple,
)

# # NOTE: client must be a global variable.outside of the function.
GlobalHttpxClient = httpx.AsyncClient(
    verify=False, timeout=10, limits=httpx.Limits(max_keepalive_connections=1000)
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


def is_valid_domain(url):
    if url.startswith("http://") or url.startswith("https://"):
        return True


def modify_url(request: Request, url: str) -> str:
    if request.url.query:
        url += "?" + request.url.query
    return unquote(url)


def get_redirect_url(url: str) -> str:
    """get the moved url"""
    with httpx.Client(verify=False) as client:
        resp = client.head(url, follow_redirects=True)
        return str(resp.url)


def replace_html(html: bytes, proxy_url: str) -> str:
    """replace the src and href in html"""
    pattern = r'(src|href|content)="(.*?)"'
    content = re.sub(
        pattern,
        lambda match: match.group(1) + '="' + urljoin(proxy_url, match.group(2)) + '"',
        html.decode("utf-8"),
    )
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

    new_headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/999.0.9999.999 Safari/537.36"

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


async def proxy_stream_file(request: Request, target_url: str) -> StreamingResponse:
    """send request to target url

    return the stream response
    """
    # clean cookie
    GlobalHttpxClient.cookies.clear()

    url = modify_url(request, target_url)
    # not need content body method
    _NON_REQUEST_BODY_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")
    request_content = (
        None if request.method in _NON_REQUEST_BODY_METHODS else request.stream()
    )
    # 将请求头中的host字段改为目标url的host
    # 同时强制移除"keep-alive"字段和添加"keep-alive"值到"connection"字段中保持连接
    require_close, proxy_header = change_client_header(
        headers=request.headers, target_url=httpx.URL(url)
    )

    # generate request
    proxy_request = GlobalHttpxClient.build_request(
        method=request.method,
        url=url,
        params=request.query_params,
        headers=proxy_header,
        content=request_content,  # FIXME: 一个已知问题是，流式响应头包含'transfer-encoding': 'chunked'，但有些服务器会400拒绝这个头
        # cookies=request.cookies,  # NOTE: headers中已有的cookie优先级高，所以这里不需要
    )

    # send request
    # follow redirect can open
    proxy_response = await GlobalHttpxClient.send(
        proxy_request,
        stream=True,
        follow_redirects=True,
    )

    # 依据先前客户端的请求，决定是否要添加"connection": "close"头到响应头中以关闭连接
    # https://www.uvicorn.org/server-behavior/#http-headers
    # 如果响应头包含"connection": "close"，uvicorn会自动关闭连接
    proxy_response_headers = change_server_header(
        headers=proxy_response.headers, require_close=require_close
    )

    return StreamingResponse(
        content=proxy_response.aiter_raw(),
        status_code=proxy_response.status_code,
        headers=proxy_response_headers,
        background=BackgroundTask(proxy_response.aclose),
    )


async def proxy_web_content(request: Request, target_url: str) -> Response:
    """send request to target url

    return the stream response
    """
    # clean cookie
    GlobalHttpxClient.cookies.clear()

    url = modify_url(request, target_url)
    # not need content body method
    _NON_REQUEST_BODY_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")
    request_content = (
        None if request.method in _NON_REQUEST_BODY_METHODS else request.stream()
    )
    # 将请求头中的host字段改为目标url的host
    # 同时强制移除"keep-alive"字段和添加"keep-alive"值到"connection"字段中保持连接
    require_close, proxy_header = change_client_header(
        headers=request.headers, target_url=httpx.URL(url)
    )

    # generate request
    proxy_request = GlobalHttpxClient.build_request(
        method=request.method,
        url=url,
        params=request.query_params,
        headers=proxy_header,
        content=request_content,  # FIXME: 一个已知问题是，流式响应头包含'transfer-encoding': 'chunked'，但有些服务器会400拒绝这个头
        # cookies=request.cookies,  # NOTE: headers中已有的cookie优先级高，所以这里不需要
    )

    # send request
    proxy_response = await GlobalHttpxClient.send(
        proxy_request,
        follow_redirects=True,
    )

    # 依据先前客户端的请求，决定是否要添加"connection": "close"头到响应头中以关闭连接
    # https://www.uvicorn.org/server-behavior/#http-headers
    # 如果响应头包含"connection": "close"，uvicorn会自动关闭连接
    proxy_response_headers = change_server_header(
        headers=proxy_response.headers, require_close=require_close
    )

    content = gzip.compress(proxy_response.content)

    return Response(
        content=content,
        status_code=proxy_response.status_code,
        headers=proxy_response_headers,
    )
