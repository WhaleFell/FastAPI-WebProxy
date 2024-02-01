from fastapi import APIRouter, Request, HTTPException
from fastapi import Query
from typing import Optional
from typing_extensions import Annotated


from app.helper.func import get_client_ip
from app.helper.ip_lookup import lookupIP
from app.schema import BaseResp

router = APIRouter()


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
