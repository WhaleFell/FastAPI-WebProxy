from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings, ROOTPATH
from app.helper.ip_lookup import q, download_qqwry_dat


# fastapi lifespan https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app start
    logger.success("Before app start")
    logger.info("Download qqwry.dat...")
    download_qqwry_dat(settings.QQWRY_DOWNLOAD_URL, Path(ROOTPATH, "qqwry.dat"))
    logger.info("Download qqwry.dat success start load qqwry.dat...")
    q.load_file(Path(ROOTPATH, "qqwry.dat").as_posix())
    logger.info("Load qqwry.dat success")
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


@app.get("/")
async def root():
    return PlainTextResponse(content=settings.PROJECT_DESC)


# register exception handler
from app.register.exception import register_exception

register_exception(app)

# register router
from app.router import ip_lookup

app.include_router(ip_lookup.router, tags=["ip_lookup"])

from app.router import webproxy

app.include_router(webproxy.router, tags=["webproxy"])


if __name__ == "__main__":
    import uvicorn

    # uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
