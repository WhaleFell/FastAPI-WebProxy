from fastapi import FastAPI

from .common import router as common_router
from .gps import router as gps_router
from .onedrive import router as onedrive_router
from .sub import router as sub_router
from .webproxy import router as webproxy_router


def register_routes(app: FastAPI):
    app.include_router(common_router, tags=["common"])
    app.include_router(gps_router, tags=["gps"])
    app.include_router(onedrive_router, tags=["onedrive"])
    app.include_router(sub_router, tags=["sub"])
    app.include_router(webproxy_router, tags=["webproxy"])
