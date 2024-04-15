# put common routes here

from fastapi import FastAPI
from .router import router


def register_route(app: FastAPI):
    app.include_router(router, tags=["common"])
