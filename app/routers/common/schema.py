# typing
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta


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
