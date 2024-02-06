#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   app/router/gps_upload.py
@Time    :   2024/01/28 16:35:01
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   GPS data upload
"""
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi import Query
from fastapi.responses import (
    StreamingResponse,
    Response,
    HTMLResponse,
)
from typing import Optional, List
from typing_extensions import Annotated
from pathlib import Path

from app.schema.base import GPSUploadData, BaseResp
from app.helper.mongodb_connect import gps_mongodb
from app.helper.gps_kml_generator import make_kml
from app.config import settings
from app.main import templates


router = APIRouter()


@router.post("/gps/upload/")
async def gps_upload_route(data: GPSUploadData) -> BaseResp[bool]:
    """GPS data upload route

    Args:
        data (GPSUploadData): GPS data model
    """
    status = await gps_mongodb.insert_GPS_data(data)
    return BaseResp[bool](msg="upload", data=status)


@router.post("/gps/upload/multi/")
async def gps_upload_multi_route(datas: List[GPSUploadData]) -> BaseResp[bool]:
    """mutiple GPS data upload"""
    status = await gps_mongodb.insert_mutiple_GPS_data(datas)
    return BaseResp[bool](code=1 if status else 0, msg="upload", data=status)


@router.get("/gps/data/")
async def get_gps_data(
    skip: Annotated[
        Optional[int],
        Query(title="GPS data start index", description="log start index"),
    ] = 0,
    limit: Annotated[
        Optional[int], Query(title="limit", description="return GPS data limit")
    ] = None,
    start_timestamp: Annotated[
        Optional[int],
        Query(
            title="start timestamp",
        ),
    ] = None,
    end_timestamp: Annotated[
        Optional[int],
        Query(
            title="end timestamp",
        ),
    ] = None,
    direction: Annotated[
        Optional[int],
        Query(
            title="sort direction -1 descend 1 asc",
        ),
    ] = -1,
) -> BaseResp[List[GPSUploadData]]:
    """get gps data"""

    result = await gps_mongodb.query_GPS_by_time(
        limit=limit,
        skip=skip,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        direction=direction,
    )

    if result:
        return BaseResp[List[GPSUploadData]](code=1, msg="success", data=result)
    else:
        return BaseResp[List[GPSUploadData]](code=0, msg="no data", data=result)


@router.get("/gps/data/kml/")
async def get_gps_data_kml(
    start_timestamp: Annotated[
        Optional[int],
        Query(
            title="start timestamp",
        ),
    ] = None,
    end_timestamp: Annotated[
        Optional[int],
        Query(
            title="end timestamp",
        ),
    ] = None,
) -> Response:
    """get gps data kml file"""
    result = await gps_mongodb.query_GPS_by_time(
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        direction=1,
    )

    if result != []:
        kml_str = make_kml(result)
        bytes = kml_str.encode("utf-8")
        return Response(
            content=bytes,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": "attachment; filename=GPS.kml"},
        )

    else:
        raise HTTPException(status_code=404, detail="no data")


@router.get("/gps/rm/")
async def gps_collection_rm(
    key: str = Query(..., title="remove password")
) -> BaseResp[bool]:
    """remove gps collection"""
    if key == settings.PASSWORD:
        status = await gps_mongodb.gps_collection_rm()
        return BaseResp[bool](msg="remove gps collection", data=status)
    return BaseResp[bool](code=0, msg="key incorrect", data=False)


@router.get("/gps/live/")
async def get_gps_live() -> BaseResp[Optional[GPSUploadData]]:
    """get latest gps data"""
    result = await gps_mongodb.query_latest_GPS()
    if result:
        return BaseResp[Optional[GPSUploadData]](code=1, msg="success", data=result)
    else:
        return BaseResp[Optional[GPSUploadData]](code=0, msg="no data", data=result)


@router.get("/gps/")
async def gps_index_html(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="gps.html",
        context={
            "MAP": {"MAP_KEY": settings.MAP_KEY, "MAP_SECURITY": settings.MAP_SECURITY}
        },
    )
