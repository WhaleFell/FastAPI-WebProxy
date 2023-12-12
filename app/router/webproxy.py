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
)


router = APIRouter()


@router.get(path="/file/{url:path}")
@router.post(path="/file/{url:path}")
@logger.catch()
async def largeFileProxy(request: Request, url: str):
    if not isValidDomain(url):
        logger.error(f"Invalid URL {url}")
        return Response(
            content=f"Error: Invalid URL {url}",
            status_code=400,
        )

    url = modifyUrl(request, url)
    # url = getMovedUrl(url)

    # large file proxy use stream download
    # must use **request** headers.
    async with httpx.AsyncClient(verify=False) as client:
        stream_req = client.build_request(
            request.method,
            url,
            headers=request.headers.raw,
            content=await request.body(),
        )
        stream_resp = await client.send(stream_req, stream=True)
        logger.info(f"Proxy large stream File: {url} {stream_resp.status_code}")

    # must use **response** headers.
    return StreamingResponse(
        stream_resp.aiter_raw(),
        status_code=stream_resp.status_code,
        # headers=stream_resp.headers,
        headers=modifyResponseHeader(stream_resp.headers),
        background=BackgroundTask(stream_resp.aclose),
    )


@router.post(path="/proxy/{url:path}")
@router.get(path="/proxy/{url:path}")
@logger.catch()
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
    content = resp.content

    # NOT ADD ANY HEADERS.(because of some headers may influence the browser)
    return Response(
        content=content,
        status_code=resp.status_code,
        # headers=modifyResponseHeader(resp.headers),
        # headers=resp.headers,
    )
