import random
import re
import httpx
import asyncio
from typing import Union, Optional, List
from pathlib import Path


def gen_random_str(randomlength: int) -> str:
    """
    根据传入长度产生随机字符串 (Generate a random string based on the given length)

    Args:
        randomlength (int): 需要生成的随机字符串的长度 (The length of the random string to be generated)

    Returns:
        str: 生成的随机字符串 (The generated random string)
    """

    base_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    return "".join(random.choice(base_str) for _ in range(randomlength))


def extract_valid_urls(inputs: Union[str, List[str]]) -> Union[str, List[str], None]:
    """从输入中提取有效的URL (Extract valid URLs from input)

    Args:
        inputs (Union[str, list[str]]): 输入的字符串或字符串列表 (Input string or list of strings)

    Returns:
        Union[str, list[str]]: 提取出的有效URL或URL列表 (Extracted valid URL or list of URLs)
    """
    url_pattern = re.compile(r"https?://\S+")

    # 如果输入是单个字符串
    if isinstance(inputs, str):
        match = url_pattern.search(inputs)
        return match.group(0) if match else None

    # 如果输入是字符串列表
    elif isinstance(inputs, list):
        valid_urls = []

        for input_str in inputs:
            matches = url_pattern.findall(input_str)
            if matches:
                valid_urls.extend(matches)

        return valid_urls


class AwemeIdFetcher:
    """Extract aweme_id from url"""

    # 预编译正则表达式
    _DOUYIN_VIDEO_URL_PATTERN = re.compile(r"video/([^/?]*)")
    _DOUYIN_NOTE_URL_PATTERN = re.compile(r"note/([^/?]*)")

    @classmethod
    async def get_aweme_id(cls, url: str) -> Optional[str]:
        """
        从单个url中获取aweme_id (Get aweme_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的aweme_id (Matched aweme_id)。
        """

        if not isinstance(url, str):
            raise TypeError("url must be str")

        # 提取有效URL
        url = str(extract_valid_urls(url))

        # 重定向到完整链接
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, follow_redirects=True)
            url = str(response.url)

        video_pattern = cls._DOUYIN_VIDEO_URL_PATTERN
        note_pattern = cls._DOUYIN_NOTE_URL_PATTERN

        if video_pattern.search(url):
            match = video_pattern.search(url)
        elif note_pattern.search(url):
            match = note_pattern.search(url)
        else:
            raise Exception(
                "aweme_id not found in the response address, check if the link is the work page"
            )

        if match:
            return match.group(1)
