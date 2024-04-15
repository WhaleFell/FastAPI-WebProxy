from fastapi import Body

# typing
from typing_extensions import Annotated
from typing import Optional
from pydantic import BaseModel

# custom function
from app.core.func import getTimestamp


class GPSUploadData(BaseModel):
    """GPS upload data model"""

    latitude: Annotated[float, Body(title="GPS Latitude", default=23.4)]  # 纬度
    longitude: Annotated[float, Body(title="GPS Longitude", default=113.3)]  # 经度
    altitude: Annotated[Optional[float], Body(title="GPS Altitude")] = 0  # 海拔
    speed: Annotated[Optional[float], Body(title="GPS Speed")] = 0  # 速度

    # https://docs.pydantic.dev/2.0/usage/types/datetime/
    # use timestamp allow float and int
    GPSTimestamp: Annotated[
        Optional[int],
        Body(title="GPS Time", default_factory=getTimestamp),
    ]  # GPS 时间戳

    uploadTimestamp: Annotated[
        Optional[int], Body(title="Upload Time", default_factory=getTimestamp)
    ]  # 上传 时间戳
