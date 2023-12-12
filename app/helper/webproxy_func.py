import httpx
import re
from fastapi import Request
from urllib.parse import unquote, urljoin


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
    return header


def modifyResponseHeader(header: httpx.Headers) -> dict:
    final_header = {}
    for k, v in header.items():
        final_header[k] = v
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
