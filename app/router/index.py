from fastapi import APIRouter, Request, Response, HTTPException
from fastapi import Query
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from typing import Optional, List
from typing_extensions import Annotated
from pathlib import Path

# from markdown2 import markdown

from app.schema.base import AccessLog, BaseResp
from app.helper.mongodb_connect import mongoCrud
from app.config import settings, ROOTPATH

router = APIRouter()


@router.get("/")
async def root():
    """root route return project description or Readme.md"""
    # if Path(ROOTPATH, "README.md").exists():
    #     with open(Path(ROOTPATH, "README.md"), "r", encoding="utf-8") as f:
    #         html_content = markdown(f.read())
    #         return HTMLResponse(content=html_content)

    return PlainTextResponse(content=settings.PROJECT_DESC)


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
    result = await mongoCrud.searchAccessLog(skip=skip, limit=limit, include_keyword=kw)

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
        await mongoCrud.rmAllAccessLog()
        return BaseResp[bool](code=1, msg="success rm all log", data=True)
    return BaseResp[bool](code=0, msg="password error", data=False)
