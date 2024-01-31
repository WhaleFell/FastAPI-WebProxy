#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# config.py 配置文件

from pathlib import Path
from typing import List, Union, Mapping
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

import os

# 应用路径
ROOTPATH: Path = Path.cwd().absolute()


# Reference: https://docs.pydantic.dev/usage/settings/
# Use pydantic_settings to set config in envirenment variable
class Settings(BaseSettings):
    PROJECT_DESC: str = "A WebProxy Base on FastAPI"
    PROJECT_VERSION: str = "1.0"
    PASSWORD: str = "lovehyy"

    # DEV mode
    DEV: bool = False

    BASE_URL: str = "http://127.0.0.1:8000"

    # MONGODB_URL: str = "mongodb+srv://root:lovehyy@cluster0.hnv8kgf.mongodb.net/?retryWrites=true&w=majority"
    MONGODB_URL: str = "mongodb://localhost:27017"

    # china ip list download url
    QQWRY_DOWNLOAD_URL: str = (
        "https://raw.githubusercontent.com/FW27623/qqwry/main/qqwry.dat"
    )

    # sub airports url
    SUB_AIRPORTS_DICT: Mapping[str, str] = {
        "good": "QhTycby0GHJECm9h",
    }

    # onedrive config
    OD_CLIENT_ID: str = ""
    OD_CLIENT_SECRET: str = ""
    OD_REDIRECT_URI: str = "http://localhost/"

    # Not record setting
    NOT_RECORD_PATH: List[str] = ["/favicon.ico", "/onedrive/file/", "/"]
    NOT_RECORD_IP: List[str] = ["216.144.248.27"]

    # case_sensitive means that the environment variable name is case sensitive
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
