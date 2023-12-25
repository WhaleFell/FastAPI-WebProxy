from fastapi import Request
from typing import Optional
from loguru import logger
import httpx
import traceback


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
