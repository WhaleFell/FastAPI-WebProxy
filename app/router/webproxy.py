from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse, StreamingResponse
from loguru import logger
import httpx
import gzip

from typing import Union

from app.helper.webproxy_func import (
    is_valid_domain,
    proxy_stream_file,
    proxy_web_content,
)

router = APIRouter()


# ref: https://github.com/WSH032/fastapi-proxy-lib/blob/main/src/fastapi_proxy_lib/core/http.py
@router.get(path="/file/{url:path}")
@router.post(path="/file/{url:path}")
async def largeFileProxy(request: Request, url: str):
    if not is_valid_domain(url):
        logger.error(f"Invalid URL {url}")
        return Response(
            content=f"Error: Invalid URL {url}",
            status_code=400,
        )

    return await proxy_stream_file(request, url)


@router.post(path="/proxy/{url:path}")
@router.get(path="/proxy/{url:path}")
async def webProxy(request: Request, url: str):
    if not is_valid_domain(url):
        logger.error(f"Invalid URL {url}")
        return Response(
            content=f"Error: Invalid URL {url}",
            status_code=400,
        )
    return await proxy_web_content(request, url)
