# fastapi
from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse

# typing
from typing import Optional, List
from typing_extensions import Annotated


from pathlib import Path

# internal import
from .db import accessLog
from .schema import AccessLog

# external import
from app.config import settings, ROOTPATH, APPPATH
from app.core.schema import BaseResp
from app.core.mongodb import mongoCrud, AsyncIOMotorClient
from app.core.func import get_client_ip
from app.core.ip_lookup import lookupIP

router = APIRouter()


@router.get("/")
async def root():
    """root route return project description or Readme.md"""
    # if Path(ROOTPATH, "README.md").exists():
    #     with open(Path(ROOTPATH, "README.md"), "r", encoding="utf-8") as f:
    #         html_content = markdown(f.read())
    #         return HTMLResponse(content=html_content)
    if Path(APPPATH, "index.html").exists():
        with open(Path(APPPATH, "index.html"), "r", encoding="utf-8") as f:
            html_content = f.read()
            return HTMLResponse(content=html_content)

    # return PlainTextResponse(content=settings.PROJECT_DESC)


@router.get("/ping/")
async def ping():
    """ping health check"""
    return PlainTextResponse(content="pong")


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = Path(ROOTPATH, "favicon.ico").as_posix()
    return FileResponse(favicon_path)


@router.get(path="/log/")
async def checkLog(
    skip: Annotated[
        int, Query(title="log start index", description="log start index")
    ] = 0,
    limit: Annotated[int, Query(title="limit", description="return log limit")] = 200,
    kw: Annotated[
        Optional[str], Query(title="keyword", description="search keyword")
    ] = None,
) -> BaseResp[List[AccessLog]]:
    """check log"""
    result = await accessLog.searchAccessLog(skip=skip, limit=limit, include_keyword=kw)

    if result:
        return BaseResp[List[AccessLog]](code=1, msg="success", data=result)
    else:
        return BaseResp[List[AccessLog]](code=0, msg="no log", data=result)


@router.get(path="/log/rm/")
async def rmLog(
    key: Annotated[str, Query(title="password", description="remove log password")]
) -> BaseResp[bool]:
    """remove all log"""
    if key == settings.PASSWORD:
        await accessLog.rmAllAccessLog()
        return BaseResp[bool](code=1, msg="success rm all log", data=True)
    return BaseResp[bool](code=0, msg="password error", data=False)


@router.get(path="/rm_database/")
async def rm_database(
    key: Annotated[str, Query(title="password", description="remove log password")]
) -> BaseResp[bool]:
    """remove app database
    !!! VERY DANGEROUS !!!
    """
    if key == settings.PASSWORD:
        await mongoCrud.rm_database(settings.MONGODB_DATABASE)
        return BaseResp[bool](code=1, msg="success remove app database", data=True)

    return BaseResp[bool](code=0, msg="password error", data=False)


@router.get(path="/ip/")
async def ipLookup(
    request: Request,
    ip: Annotated[Optional[str], Query(title="IP", description="IP address")] = None,
) -> BaseResp[dict]:
    """ip lookup"""
    if not ip:
        ip = get_client_ip(request)

    if ip == "Unknown":
        raise HTTPException(status_code=400, detail="Unknown IP address")

    result = lookupIP(ip)
    return BaseResp[dict](code=1, msg="success", data={"ip": ip, "where": f"{result}"})
