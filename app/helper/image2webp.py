# #!/usr/bin/env python3
# -*- coding: utf-8 -*-
# image2webp.py
# this script can convert and compress image to webp format
# in order to reduce the size of the image and optimize the loading speed of the website
# ref: https://medium.com/@ajeet214/image-type-conversion-jpg-png-jpg-webp-png-webp-with-python-7d5df09394c9

from PIL import Image
from io import BytesIO
import io
import httpx
from app.helper.webproxy_func import GlobalHttpxClient
from app.config import ROOTPATH
from pathlib import Path

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
)


async def get_pic_bytes(url) -> BytesIO:
    """Get image bytes from url"""
    resp = await GlobalHttpxClient.get(url, headers={"User-Agent": user_agent})
    pic = BytesIO(resp.content)
    return pic


def pic_2_webp(pic: BytesIO) -> BytesIO:
    """
    Convert image to webp format
    :param pic: image file
    :return: webp image file
    """
    img = Image.open(pic)
    img = img.convert("RGB")
    webp = BytesIO()
    img.save(webp, "webp", quality=10, optimize=True)
    webp.seek(0)
    return webp


async def main():
    url = "https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png"
    pic = await get_pic_bytes(url)
    webp = pic_2_webp(pic)
    with open(Path(ROOTPATH, "test.webp"), "b") as f:
        f.write(webp.getbuffer())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
