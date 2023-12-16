from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, FastAPI
from starlette.background import BackgroundTask
import time

from app.helper.mongodb_connect import mongoCrud
from app.helper.func import get_client_ip
from fastapi.middleware.gzip import GZipMiddleware


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # don't record 404 error
        if response.status_code == 404:
            return response

        NOT_RECORD_PATH = ["/docs", "/onedrive/file/"]

        if any([path in request.url._url for path in NOT_RECORD_PATH]):
            return response

        # fastapi middleware run background task
        # https://stackoverflow.com/questions/72372029/fastapi-background-task-in-middleware
        response.background = BackgroundTask(
            mongoCrud.newAccessLog,
            get_client_ip(request),
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
    # app.add_middleware(GZipMiddleware, minimum_size=200)
