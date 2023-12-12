#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# config.py 配置文件

from pathlib import Path
from typing import List, Union
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

    BASE_URL: str = "http://127.0.0.1:8000"

    MONGODB_URL: str = "mongodb://localhost:27017"

    # china ip list download url
    QQWRY_DOWNLOAD_URL: str = (
        "https://raw.githubusercontent.com/FW27623/qqwry/main/qqwry.dat"
    )

    model_config = SettingsConfigDict(case_sensitive=True)  # 区分大小写


settings = Settings()
