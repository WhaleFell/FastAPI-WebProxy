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
from fastapi import Query, Body
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from typing import Optional, List
from typing_extensions import Annotated
from datetime import datetime, date
from pathlib import Path
from pydantic import BaseModel

from app.schema.base import GPSUploadData, BaseResp
from app.helper.mongodb_connect import gps_mongodb


router = APIRouter()


@router.post("/gps/upload/")
async def gps_upload_route(data: GPSUploadData) -> BaseResp[bool]:
    """GPS data upload route

    Args:
        data (GPSUploadData): GPS data model
    """
    status = await gps_mongodb.insert_GPS_data(data)
    return BaseResp[bool](msg="upload success!", data=status)


@router.get("/gps/data/")
async def get_gps_data(
    skip: Annotated[
        int, Query(title="GPS data start index", description="log start index")
    ] = 0,
    limit: Annotated[
        int, Query(title="limit", description="return GPS data limit")
    ] = 200,
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
) -> BaseResp[List[GPSUploadData]]:
    """get gps data"""

    result = await gps_mongodb.query_GPS_by_time(
        limit=limit,
        skip=skip,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )

    if result:
        return BaseResp[List[GPSUploadData]](code=1, msg="success", data=result)
    else:
        return BaseResp[List[GPSUploadData]](code=0, msg="no data", data=result)
