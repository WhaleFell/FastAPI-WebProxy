from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import RedirectResponse, Response, FileResponse
from loguru import logger

from typing import Optional, Union
from typing_extensions import Annotated

from app.helper.mongodb_connect import od_mongodb_auth
from app.helper.onedrive_sdk import OnedriveSDK
from app.schema import BaseResp
from app.config import settings
from app.helper.webproxy_func import proxy_stream_file
from app.helper.image2webp import pic_2_webp, get_pic_bytes

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
    request: Request,
    path: Annotated[
        str, Query(title="onedrive file path", description="onedrive file path")
    ],
    proxy: Annotated[
        bool, Query(title="proxy download file url for onedrive", description="proxy")
    ] = False,
    webp: Annotated[
        bool, Query(title="convert image to webp and compress", description="webp")
    ] = False,
):
    filename = path.split("/")[-1]
    url = await onedrive_sdk.get_file_download_url(path)
    if not url:
        raise HTTPException(status_code=404, detail="File not found")

    if webp:
        pic = await get_pic_bytes(url)
        webp_bytes = pic_2_webp(pic)
        return Response(
            content=webp_bytes.read(),
            media_type="image/webp",
            headers={"Content-Disposition": "inline", "filename": f"{filename}"},
        )

    if proxy:
        stream_response = await proxy_stream_file(request=request, target_url=url)
        # modify header Content-Disposition in order to open file in browser
        header_content_disposition = stream_response.headers["Content-Disposition"]
        stream_response.headers[
            "Content-Disposition"
        ] = header_content_disposition.replace("attachment", "inline")
        return stream_response

    return RedirectResponse(url=url)
