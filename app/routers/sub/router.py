# fastapi
from fastapi import APIRouter, Request, Response, Query
from fastapi.responses import PlainTextResponse

# typing
from typing import Optional
from typing_extensions import Annotated

# external import
from app.config import settings
from app.core.func import get_client_ip
from app.core.ip_lookup import lookupIP

import httpx
import datetime

router = APIRouter()
# https://accd.vo0.site/link/eTVpHf7Ju197AK4l?sub=3
haeder = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SUB_TYPES = {
    "clash": "clash=1",
    "v2ray": "sub=3",
}


def replace_content(text: str, request: Request, type_: str = "clash") -> str:
    if type_ == "clash":
        text = text.replace("官网：https://1100.gg", "落落定制高级机场,3000CNY/月")
        lines = text.split("\n")
        new_lines = [line for line in lines if not line.strip().startswith("#")]
        text = "\n".join(new_lines)

        ip = get_client_ip(request)

        banner = f"""
# 落落定制高级机场,300CNY/月
# Generated time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# URL: {request.url._url}
# IP: {ip} {lookupIP(ip)} \n
    """

        return banner + text

    return text


async def get_airport_sub_content(
    key: str, request: Request, type: str = "clash"
) -> str:
    parameter = SUB_TYPES.get(type, "clash=1")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://accd.vo0.site/link/{key}?{parameter}", headers=haeder
        )
        return replace_content(resp.text, request, type)


@router.get("/sub/{name:str}/")
async def sub(
    name: str,
    request: Request,
    type: Annotated[
        str,
        Query(title="sub type", description="support v2ray and clash default clash"),
    ] = "clash",
):
    global SUB_TYPES
    key = settings.SUB_AIRPORTS_DICT.get(name, None)
    if not key:
        return PlainTextResponse(content=f"Not Found {name} config", status_code=400)

    content = await get_airport_sub_content(key, request, type)

    return PlainTextResponse(content=content)
