#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   dy_parse.py
@Time    :   2024/01/11 22:01:08
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   Douyin download video

reference: https://github.com/Johnserf-Seed/f2
"""
import httpx
import asyncio
import random
from pathlib import Path
from typing import Optional, List, Union
from pydantic import BaseModel, model_validator
from filter import PostDetailFilter

from xbogus import XBogusManager
from utils import AwemeIdFetcher, extract_valid_urls


class VedioDetail(BaseModel):
    """vedio detail model"""

    aweme_id: Optional[str] = None
    desc: Optional[str] = None
    nickname: Optional[str] = None
    cover_url: Optional[str] = None
    mp3_url: Optional[str] = None
    is_vedio: bool = False
    is_picture: bool = False
    vedio_url: Optional[str] = None
    picture_urls: List = []

    @model_validator(mode="after")
    def decide_type(self):
        if self.vedio_url and not self.vedio_url.endswith(".mp3"):
            self.is_vedio = True
        if self.picture_urls != []:
            self.is_picture = True

        return self


class DYAPI(object):
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        }
        self.msToken = self.gen_false_msToken()
        cookie = self.read_cookie()
        if cookie:
            self.headers["Cookie"] = cookie
        self.client = httpx.AsyncClient(headers=self.headers)

    def gen_false_msToken(self) -> str:
        """生成随机msToken (Generate random msToken)"""
        base_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
        msToken = "".join(random.choice(base_str) for _ in range(126))

        return msToken + "=="

    def read_cookie(self) -> Optional[str]:
        """read cookie string in current directory `Cookie` file

        If the file does not exist, return None
        """
        cookie_file = Path(__file__).parent / "Cookie"
        if cookie_file.exists():
            with open(cookie_file, "r", encoding="utf8") as f:
                return f.read()
        else:
            return None

    def gen_vedio_api_url(self, aweme_id: str):
        """Calculate xbogus values via complete link"""

        params_str = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={aweme_id}&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=550&screen_height=1203&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0&browser_online=true&engine_name=Blink&engine_version=120.0.0.0&os_name=Android&os_version=6.0&cpu_core_num=12&device_memory=8&platform=Android&downlink=10&effective_type=4g&round_trip_time=50&webid=7323045148056389130&msToken={self.msToken}"

        self.headers["Referer"] = f"https://www.douyin.com/video/{aweme_id}"

        return XBogusManager.str_2_endpoint(params_str)

    def parse_jsonData(self, jsonData: dict) -> VedioDetail:
        """Parse json data and return VedioDetail model"""
        filter = PostDetailFilter(jsonData)
        res_dict = {
            "aweme_id": str(filter.aweme_id),
            "desc": filter.desc,
            "nickname": filter.nickname,
            "mp3_url": str(filter.music_play_url),
            "cover_url": str(filter.cover),
            "vedio_url": filter.video_play_addr,
            "picture_urls": filter.images,
        }

        return VedioDetail(**res_dict)

    async def request_api(self, aweme_id: str):
        """Request api and return response"""
        url = self.gen_vedio_api_url(aweme_id)
        response = await self.client.get(url, headers=self.headers)
        vedio_detail = self.parse_jsonData(response.json())
        print(vedio_detail.model_dump_json(by_alias=True))


async def main():
    text = "3.30 TLj:/ 07/27 g@O.kc 0108浙江湖州猫车部分🐱孩子照片，爱心接力，帮助让汤姆和它的小伙伴们回家!# 0108湖州猫车 # 我和流浪猫的故事 # 爱心接力  https://v.douyin.com/iLjGPkNu/ 复制此链接，打开Dou音搜索，直接观看视频！"
    dyapi = DYAPI()
    url = extract_valid_urls(text)
    if isinstance(url, str):
        aweme_id = await AwemeIdFetcher.get_aweme_id(url)
        if aweme_id:
            await dyapi.request_api(aweme_id)


if __name__ == "__main__":
    asyncio.run(main())
