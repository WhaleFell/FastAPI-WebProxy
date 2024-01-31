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
from pathlib import Path
from pydantic import BaseModel
from app.schema.base import GPSUploadData, BaseResp


router = APIRouter()


@router.post("/gps/upload/")
async def gps_upload_route(data: GPSUploadData) -> BaseResp[GPSUploadData]:
    return BaseResp[GPSUploadData](msg="upload success!", data=data)
