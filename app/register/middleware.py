from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, FastAPI
from starlette.background import BackgroundTask
from fastapi.middleware.gzip import GZipMiddleware
import time

from app.helper.mongodb_connect import accessLog
from app.helper.func import get_client_ip
from app.config import settings


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        ip = get_client_ip(request)

        # don't record 404 error
        if response.status_code == 404:
            return response

        # don't record route path
        if request.url.path in settings.NOT_RECORD_PATH:
            return response

        # don't record special ip
        if ip in settings.NOT_RECORD_IP:
            return response

        # fastapi middleware run background task
        # https://stackoverflow.com/questions/72372029/fastapi-background-task-in-middleware
        response.background = BackgroundTask(
            accessLog.newAccessLog,
            ip,
            request.url._url,
            response.status_code,
        )
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware
    app.add_middleware(GZipMiddleware, minimum_size=200)
