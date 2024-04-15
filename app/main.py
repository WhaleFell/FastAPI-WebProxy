from fastapi import FastAPI
import pprint
from loguru import logger
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

from app.config import settings, APPPATH, ROOTPATH
from app.core.ip_lookup import setup_qqwry


def init_env():
    """init env"""
    state = load_dotenv(dotenv_path=Path(ROOTPATH, ".env").as_posix())
    logger.info(f"load env state: {state}")


# fastapi lifespan https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app start
    init_env()
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


# mount assets folder
from fastapi.staticfiles import StaticFiles

app.mount(
    "/assets", StaticFiles(directory=Path(APPPATH, "assets").as_posix()), name="assets"
)

# template directory
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=Path(APPPATH, "templates").as_posix())

# register exception handler
from app.register.exception import register_exception

register_exception(app)

# register router
from app.routers import register_routes

register_routes(app)


# register middleware
from app.register.middleware import register_middleware

register_middleware(app)

if __name__ == "__main__":
    import uvicorn

    # uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
