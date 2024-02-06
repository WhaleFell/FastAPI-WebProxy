from fastapi import FastAPI
import pprint
from loguru import logger
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings, APPPATH
from app.helper.ip_lookup import setup_qqwry


# fastapi lifespan https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app start
    setup_qqwry(update=not settings.DEV)
    logger.info(
        f"""
FastAPI CONIG:
{pprint.pformat(settings.model_dump())}
"""
    )
    yield
    # after app stop
    logger.success("After app stop")


app = FastAPI(
    description=settings.PROJECT_DESC,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)


# mount static file
# from fastapi.staticfiles import StaticFiles

# app.mount(
#     "/static", StaticFiles(directory=Path(APPPATH, "static").as_posix()), name="static"
# )

# template directory
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=Path(APPPATH, "templates").as_posix())

# register exception handler
from app.register.exception import register_exception

register_exception(app)

# register router
from app.router import ip_lookup_route
from app.router import webproxy
from app.router import index
from app.router import sub_airport
from app.router import onedrive
from app.router import gps

app.include_router(ip_lookup_route.router, tags=["ip_lookup"])
app.include_router(webproxy.router, tags=["webproxy"])
app.include_router(index.router, tags=["access_log"])
app.include_router(sub_airport.router, tags=["sub_airport"])
app.include_router(onedrive.router, tags=["onedrive"])
app.include_router(gps.router, tags=["gps_upload"])

# register middleware
from app.register.middleware import register_middleware

register_middleware(app)

if __name__ == "__main__":
    import uvicorn

    # uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
