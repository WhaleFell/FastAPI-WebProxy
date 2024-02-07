#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# config.py config file

from pathlib import Path
from typing import List, Union, Mapping
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

import os

# app root path
ROOTPATH: Path = Path.cwd().absolute()
APPPATH: Path = Path(__file__).parent.absolute()


# Reference: https://docs.pydantic.dev/usage/settings/
# Use pydantic_settings to set config in envirenment variable
class Settings(BaseSettings):
    PROJECT_DESC: str = "A WebProxy Base on FastAPI"
    PROJECT_VERSION: str = "1.0"
    PASSWORD: str = "lovehyy"

    # DEV mode
    DEV: bool = False

    BASE_URL: str = "http://127.0.0.1:8000"

    # MONGODB_URL: str = (
    # "mongodb+srv://root:lovehyy@cluster0.hnv8kgf.mongodb.net/?retryWrites=true&w=majority"
    # )
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "webproxy"

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
    NOT_RECORD_PATH: List[str] = [
        "/favicon.ico",
        "/onedrive/file/",
        "/gps/upload/",
        "/gps/upload/multi/",
        "/gps/live/",
        "/ping/",
    ]
    NOT_RECORD_IP: List[str] = ["216.144.248.27"]

    # GaoDE JS API
    # https://lbs.amap.com/
    MAP_KEY: str = "1f34538dbd8ac8bb9e143f064ace341f"
    MAP_SECURITY: str = "38e11e519ee47e9a746b9907a5a54620"

    # case_sensitive means that the environment variable name is case sensitive
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
print(settings.json())
