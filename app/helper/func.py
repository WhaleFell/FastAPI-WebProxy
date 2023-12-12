from fastapi import Request
from typing import Optional
from loguru import logger
import re


def get_client_ip(request: Request) -> Optional[str]:
    """get client ip"""
    x = "x-forwarded-for".encode("utf-8")
    for header in request.headers.raw:
        if header[0] == x:
            origin_ip, forward_ip = re.split(", ", header[1].decode("utf-8"))
            # print(f"origin_ip:\t{origin_ip}")
            # print(f"forward_ip:\t{forward_ip}")
            return origin_ip
    if request.client:
        return request.client.host


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
