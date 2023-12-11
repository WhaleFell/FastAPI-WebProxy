import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response, PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from loguru import logger

from urllib.parse import unquote

app = FastAPI(description="A WebProxy Base on FastAPI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


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


@app.post(path="/")
@app.get(path="/")
async def index(request: Request):
    return PlainTextResponse(content="FastAPI WebProxy!")


client = httpx.AsyncClient(verify=False)


@app.get(path="/file/{url:path}")
@app.post(path="/file/{url:path}")
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


@app.post(path="/{url:path}")
@app.get(path="/{url:path}")
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
                # content=await request.body(),
            )
            resp = await client.send(req, follow_redirects=True)
            logger.info(f"Proxy web {url} {resp.status_code}")
        except Exception as exc:
            logger.error(f"Proxy {url} Error: {exc}")
            return PlainTextResponse(
                content=f"Proxy {url} Error: {exc}", status_code=500
            )

    # NOT ADD ANY HEADERS.(because of some headers may influence the browser)
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        # headers=modifyResponseHeader(resp.headers),
        # headers=resp.headers,
    )


if __name__ == "__main__":
    import uvicorn

    # uvicorn main:app --port 8000 --host 0.0.0.0 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
