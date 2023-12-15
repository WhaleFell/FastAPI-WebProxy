from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse, Response

from typing import Optional, Union
from typing_extensions import Annotated

from app.helper.mongodb_connect import od_mongodb_auth
from app.helper.onedrive_sdk import OnedriveSDK
from app.schema import BaseResp
from app.config import settings
from loguru import logger

onedrive_sdk = OnedriveSDK(
    client_id=settings.OD_CLIENT_ID,
    client_secret=settings.OD_CLIENT_SECRET,
    od_auth=od_mongodb_auth,
    redirect_uri=settings.OD_REDIRECT_URI,
)

router = APIRouter()


@router.get("/onedrive/login/")
async def od_login(
    code: Annotated[
        Optional[str],
        Query(
            title="onedrive callback code",
        ),
    ] = None
):
    if not code:
        url = onedrive_sdk.generateLoginURL()
        return RedirectResponse(url=url)

    await onedrive_sdk.getRefreshTokenByCode(code)
    return BaseResp[bool](msg="login success!", data=True)


@router.get("/onedrive/logout/")
async def od_logout() -> BaseResp[bool]:
    await onedrive_sdk.logout()
    return BaseResp[bool](msg="logout success!", data=True)


@router.get("/onedrive/check/")
async def od_check() -> BaseResp[bool]:
    result = await onedrive_sdk.checkOnedriveStatus()
    msg = "success connect to onedrive" if result else "fail connect to onedrive"
    return BaseResp[bool](code=0 if result else 1, msg=msg, data=result)


@router.get("/onedrive/file/")
async def get_od_file(
    path: Annotated[
        str, Query(title="onedrive file path", description="onedrive file path")
    ]
):
    try:
        url = await onedrive_sdk.get_file_download_url(path)
        if not url:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error("get onedrive file download url error: %s" % e)
        raise HTTPException(
            status_code=502, detail="get onedrive file download url error"
        )
    return RedirectResponse(url=url)
