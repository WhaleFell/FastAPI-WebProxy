from fastapi import APIRouter, Request, Response, HTTPException
from fastapi import Query
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel

from fastapi.responses import ORJSONResponse

from app.helper.func import get_client_ip
from app.helper.ip_lookup import q
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
        if not ip:
            raise HTTPException(status_code=400, detail="Invalid IP address")

    result = q.lookup(ip)
    if not result:
        raise HTTPException(status_code=400, detail="IP address not found")
    (country, province) = result

    return BaseResp[dict](
        code=1, msg="success", data={"ip": ip, "where": f"{country} {province}"}
    )
