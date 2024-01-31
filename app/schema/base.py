#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# schemas/base.py
# API 基模型

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Optional, Any, Annotated
from pydantic import ConfigDict
from datetime import datetime, timedelta, timezone
from fastapi import Query

# Pydantic Generic Type 泛型
# reference:
# 1. https://blog.csdn.net/qq_45668004/article/details/113730684
# 2. https://docs.pydantic.dev/2.4/concepts/models/#generic-models
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseResp(BaseModel, Generic[T]):
    code: int = Field(default=1, description="响应状态码 1 true 正常 | 0 false 错误")
    msg: Optional[str] = Field(default=None, description="响应信息")

    data: Optional[T] = None

    # Pydantic V2 changes
    # https://docs.pydantic.dev/latest/migration/#changes-to-config
    # class Config:
    # no only trying to get the id value from a dict
    # also try to get it from an attribute,
    # id = data["id"] 或者 id = data.id
    model_config = ConfigDict(from_attributes=True)


# access log
class AccessLog(BaseModel):
    time: datetime = Field(default=None, description="访问时间")
    ip: str = Field(default=None, description="访问IP")
    where: str = Field(default=None, description="IP归属地")
    url: str = Field(default=None, description="访问URL")
    status_code: int = Field(default=None, description="访问状态码")

    # switch time to utc+8
    @field_validator("time")
    def time_to_utc8(cls, v: datetime) -> datetime:
        return v + timedelta(hours=8)


class GPSUploadData(BaseModel):
    """GPS upload data model"""

    latitude: Annotated[float, Query(title="GPS Latitude")]  # 纬度
    longitude: Annotated[float, Query(title="GPS Longitude")]  # 经度
    altitude: Annotated[float | None, Query(title="GPS Altitude")] = 0  # 海拔
    speed: Annotated[float | None, Query(title="GPS Speed")] = 0  # 速度
    GPSTime: Annotated[
        datetime | None, Query(title="GPS Time", default_factory=datetime.now)
    ]  # GPS时间

    uploadTime: Annotated[
        datetime | None, Query(title="Upload Time", default_factory=datetime.now)
    ]  # 上传时间
