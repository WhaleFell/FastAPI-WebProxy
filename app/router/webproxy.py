from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from starlette.background import BackgroundTask
from loguru import logger
import httpx
from app.helper.webproxy_func import (
    modifyResponseHeader,
    modifyResquestHeader,
    modifyUrl,
    isValidDomain,
    getMovedUrl,
)
import gzip
from app.helper.webproxy_func import change_server_header, change_client_header


router = APIRouter()


@router.get(path="/file/{url:path}")
@router.post(path="/file/{url:path}")
async def largeFileProxy(request: Request, url: str):
    if not isValidDomain(url):
        logger.error(f"Invalid URL {url}")
        return Response(
            content=f"Error: Invalid URL {url}",
            status_code=400,
        )

    _NON_REQUEST_BODY_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")
    request_content = (
        None if request.method in _NON_REQUEST_BODY_METHODS else request.stream()
    )
    url = modifyUrl(request, url)
    url = getMovedUrl(url)
    # 将请求头中的host字段改为目标url的host
    # 同时强制移除"keep-alive"字段和添加"keep-alive"值到"connection"字段中保持连接
    require_close, proxy_header = change_client_header(
        headers=request.headers, target_url=httpx.URL(url)
    )
    # async with httpx.AsyncClient(verify=False) as client:
    proxy_request = client.build_request(
        method=request.method,
        url=url,
        params=request.query_params,
        headers=proxy_header,
        content=request_content,  # FIXME: 一个已知问题是，流式响应头包含'transfer-encoding': 'chunked'，但有些服务器会400拒绝这个头
        # cookies=request.cookies,  # NOTE: headers中已有的cookie优先级高，所以这里不需要
    )

    proxy_response = await client.send(
        proxy_request,
        stream=True,
        # follow_redirects=True,
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


@router.post(path="/proxy/{url:path}")
@router.get(path="/proxy/{url:path}")
async def webProxy(request: Request, url: str):
    if not isValidDomain(url):
        logger.error(f"Invalid URL {url}")
        return Response(
            content=f"Error: Invalid URL {url}",
            status_code=400,
        )
    url = modifyUrl(request, url)
    async with httpx.AsyncClient(verify=False) as client:
        try:
            req = client.build_request(
                method=request.method,
                url=url,
                headers=modifyResquestHeader(request, url),
                content=await request.body(),
            )
            resp = await client.send(req, follow_redirects=True)
            logger.info(f"Proxy web {url} {resp.status_code}")
        except Exception as exc:
            logger.error(f"Proxy {url} Error: {exc}")
            return PlainTextResponse(
                content=f"Proxy {url} Error: {exc}", status_code=500
            )

    # if "text/html" in resp.headers["content-type"]:
    #     content = disposeHtml(resp.content, request.url._url)
    # else:

    # use gzip compress
    content = gzip.compress(resp.content)

    # Now add some allow proxy headers to response.to solve some headers may influence the browser.
    # gzip will cause browser not show content
    return Response(
        content=content,
        status_code=resp.status_code,
        headers=modifyResponseHeader(resp.headers),
        # headers=resp.headers,
    )


# NOTE: client must be a global variable.outside of the function.
client = httpx.AsyncClient()


@router.get("/test/{path:path}")
async def test(request: Request, path: str):
    # url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    url = modifyUrl(request, path)
    url = getMovedUrl(url)
    require_close, proxy_header = change_client_header(
        headers=request.headers, target_url=httpx.URL(url)
    )
    _NON_REQUEST_BODY_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")
    request_content = (
        None if request.method in _NON_REQUEST_BODY_METHODS else request.stream()
    )
    rp_req = client.build_request(
        method=request.method,
        url=url,
        params=request.query_params,
        headers=proxy_header,
        content=request_content,  # FIXME: 一个已知问题是，流式响应头包含'transfer-encoding': 'chunked'，但有些服务器会400拒绝这个头
        # cookies=request.cookies,  # NOTE: headers中已有的cookie优先级高，所以这里不需要
    )
    # rp_req = client.build_request(
    #     request.method, url, headers=request.headers.raw, content=request.stream()
    # )
    rp_resp = await client.send(rp_req, stream=True)

    proxy_response_headers = change_server_header(
        headers=rp_resp.headers, require_close=require_close
    )
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=proxy_response_headers,
        background=BackgroundTask(rp_resp.aclose),
    )
