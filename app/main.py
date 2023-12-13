from fastapi import FastAPI, Request
from starlette.background import BackgroundTask
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager
from pathlib import Path
import time

from app.config import settings, ROOTPATH
from app.helper.ip_lookup import setup_qqwry
from app.helper.mongodb_connect import mongoCrud
from app.helper.func import get_client_ip


# fastapi lifespan https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app start
    setup_qqwry()
    yield
    # after app stop
    logger.success("After app stop")


app = FastAPI(
    description=settings.PROJECT_DESC,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# fastapi middleware run background task
# https://stackoverflow.com/questions/72372029/fastapi-background-task-in-middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # don't record 404 error
    if response.status_code == 404:
        return response

    response.background = BackgroundTask(
        mongoCrud.newAccessLog,
        get_client_ip(request),
        request.url._url,
        response.status_code,
    )
    return response


# register exception handler
from app.register.exception import register_exception

register_exception(app)

# register router
from app.router import ip_lookup
from app.router import webproxy
from app.router import index

app.include_router(ip_lookup.router, tags=["ip_lookup"])
app.include_router(webproxy.router, tags=["webproxy"])
app.include_router(index.router, tags=["access_log"])

if __name__ == "__main__":
    import uvicorn

    # uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
