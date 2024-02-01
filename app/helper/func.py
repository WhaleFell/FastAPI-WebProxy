from fastapi import Request
from loguru import logger
from datetime import datetime, timezone, timedelta


def get_client_ip(request: Request) -> str:
    """get client ip"""
    # behind reverse proxy header
    x_header_list = ["x-forwarded-for", "x-real-ip", "x-vercel-forwarded-for"]
    for header in request.headers.raw:
        if header[0].decode("utf-8") in x_header_list:
            return header[1].decode("utf-8").split(",")[0]
    if request.client:
        return request.client.host
    return "Unknown"


# retry decorator
def retry(times: int = 3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"retry {i+1} times.reason: {e}")
                    continue

        return wrapper

    return decorator


# async retry decorator
def async_retry(times: int = 3):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"retry {i+1} times.reason: {e}")
                    # logger.exception("Track")
                    # DEBUG
                    # from app.helper.mongodb_connect import mongoCrud

                    # await mongoCrud.insert_one(
                    #     collection_name="traceback",
                    #     document={"log": traceback.format_exc()},
                    # )
                    if i == times - 1:
                        raise e

        return wrapper

    return decorator


# get Beijing Time UTC+8
def getBeijingTime() -> datetime:
    return datetime.now(tz=timezone(timedelta(hours=8)))


# get timestamp
def getTimestamp() -> int:
    return int(datetime.now().timestamp())


# timestamp convert to datetime USE UTC+8
def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))


# UTC+8 datetime convert to timestamp
def datetime_to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())
