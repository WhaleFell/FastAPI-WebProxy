# onedrive SDK
""" reference document
# ref: https://learn.microsoft.com/zh-cn/onedrive/developer/?view=odsp-graph-online
# ref: https://learn.microsoft.com/zh-cn/onedrive/developer/rest-api/getting-started/graph-oauth?view=odsp-graph-online
# https://massivescale.com/microsoft-v2-endpoint-primer/
# https://stackoverflow.com/questions/43810200/microsoft-onedrive-api-invalidauthenticationtoken-compacttoken-parsing-failed-wi#:~:text=You%27re%20authenticating%20against%20the%20wrong%20endpoint.%20The%20login.live.com,code%20provided%20should%20give%20you%20everything%20you%20need.
"""

import httpx
from loguru import logger
import urllib.parse
import asyncio
from typing import Dict, Optional, Callable
from typing_extensions import override
from pathlib import Path
import inspect
from app.helper.func import async_retry

UA = "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36"

_ROOT_PATH = Path(__file__).parent.absolute()


class ODAuth(object):
    """onedrive auth class
    inherit it and overide the get and set property.
    Python getter and setter property:
    https://www.geeksforgeeks.org/getter-and-setter-in-python/

    NOTE: MUST achieve THE `get_or_set_access_token` and `get_or_set_refresh_token` method.
    allow to use async function.
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        # python class multil inherit super class
        super().__init__(*args, **kwargs)
        logger.info(f"ODAuth init: {self}")
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_or_set_access_token(self, value: Optional[str] = None) -> Optional[str]:
        """get or set access_token
        if value is not None, set access_token to value.
        """
        raise NotImplementedError

    def get_or_set_refresh_token(self, value: Optional[str] = None) -> Optional[str]:
        """get or set refresh_token
        if value is not None, set refresh_token to value.
        """
        raise NotImplementedError


class ODAuthFile(ODAuth):
    """extand onedrive auth class
    File cache access_token and refresh_token.
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(access_token, refresh_token)

    @override
    def get_or_set_access_token(self, value: Optional[str] = None) -> Optional[str]:
        """get or set access_token
        if value is not None, set access_token to value.
        """
        if not value:
            if Path(_ROOT_PATH, ".onedriveAccess").exists():
                return Path(_ROOT_PATH, ".onedriveAccess").read_text()
        else:
            Path(_ROOT_PATH, ".onedriveAccess").write_text(value)
            return value

    @override
    def get_or_set_refresh_token(self, value: Optional[str] = None) -> Optional[str]:
        """get or set refresh_token
        if value is not None, set refresh_token to value.
        """
        if not value:
            if Path(_ROOT_PATH, ".onedriveRefresh").exists():
                return Path(_ROOT_PATH, ".onedriveRefresh").read_text()
        else:
            Path(_ROOT_PATH, ".onedriveRefresh").write_text(value)
            return value


class OnedriveSDK(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        od_auth: ODAuth,
        redirect_uri: str = "http://localhost/",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = "Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All offline_access"
        self.header: dict = {
            "User-Agent": UA,
            # "Authorization": "Bearer "+self.access_token,
        }
        self.onedrive_api = "https://graph.microsoft.com/v1.0"
        self.client = httpx.AsyncClient(
            headers=self.header,
            limits=httpx.Limits(max_keepalive_connections=1000),
            verify=False,
            timeout=8,
        )
        self.od_auth = od_auth

        # use file cache token.
        # but in vercel or other serverless platfrom, it will be reset.
        # self.FILEPATH = Path(__file__).parent.absolute()
        # self.refresh_file_path = Path(self.FILEPATH, ".onedriveRefresh")
        # self.access_file_path = Path(self.FILEPATH, ".onedriveAccess")

    async def __get_or_set_access_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        if not value:
            # getter
            if inspect.iscoroutinefunction(self.od_auth.get_or_set_access_token):
                return await self.od_auth.get_or_set_access_token()
            else:
                return self.od_auth.get_or_set_access_token()
        else:
            # setter
            if inspect.iscoroutinefunction(self.od_auth.get_or_set_access_token):
                return await self.od_auth.get_or_set_access_token(value)
            else:
                return self.od_auth.get_or_set_access_token(value)

    async def __get_or_set_refresh_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        if not value:
            # getter
            if inspect.iscoroutinefunction(self.od_auth.get_or_set_refresh_token):
                return await self.od_auth.get_or_set_refresh_token()
            else:
                return self.od_auth.get_or_set_refresh_token()
        else:
            # setter
            if inspect.iscoroutinefunction(self.od_auth.get_or_set_refresh_token):
                return await self.od_auth.get_or_set_refresh_token(value)
            else:
                return self.od_auth.get_or_set_refresh_token(value)

    def generateLoginURL(self) -> str:
        """return and print login url"""
        url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={self.client_id}&scope={self.scope}&response_type=code&redirect_uri={self.redirect_uri}"

        parsed = urllib.parse.urlsplit(url)
        encoded_query = urllib.parse.quote(parsed.query, safe="=&")
        encoded_url = urllib.parse.urlunsplit(parsed._replace(query=encoded_query))
        logger.info(f"Login onedrive url:{encoded_url}")
        return encoded_url

    async def getRefreshTokenByCode(self, code: str) -> Dict[str, str]:
        data = {
            "client_id": f"{self.client_id}",
            "redirect_uri": f"{self.redirect_uri}",
            "client_secret": f"{self.client_secret}",
            "code": f"{code}",
            "grant_type": "authorization_code",
        }
        resp = await self.client.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data=data,
            headers=self.header,
        )
        logger.debug(f"get token raw resp:{resp.text}")
        resp.raise_for_status()
        respJs = resp.json()
        access_token = respJs["access_token"]
        refresh_token = respJs["refresh_token"]

        # self.od_auth.access_token = access_token
        # self.od_auth.refresh_token = refresh_token
        await self.__get_or_set_access_token(value=access_token)
        await self.__get_or_set_refresh_token(value=refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def getTokenByRefreshToken(self, refresh_token: str) -> Dict[str, str]:
        data = {
            "client_id": f"{self.client_id}",
            "redirect_uri": f"{self.redirect_uri}",
            "client_secret": f"{self.client_secret}",
            "refresh_token": f"{refresh_token}",
            "grant_type": "refresh_token",
        }
        resp = await self.client.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data=data,
            headers=self.header,
        )
        resp.raise_for_status()
        respJs = resp.json()
        access_token = respJs["access_token"]
        refresh_token = respJs["refresh_token"]
        # self.od_auth.access_token = access_token
        # self.od_auth.refresh_token = refresh_token

        await self.__get_or_set_access_token(value=access_token)
        await self.__get_or_set_refresh_token(value=refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def checkOnedriveStatus(self) -> bool:
        access_token = await self.__get_or_set_access_token()
        header = {"Authorization": f"Bearer {access_token}"}
        resp = await self.client.get(
            self.onedrive_api + "/me/drive/root/children", headers=header
        )
        if resp.status_code == 401:
            logger.error(f"AccessToken Invaild!:{resp.text} please relogin.")
            return False
        logger.success("AccessToken Vaild!")
        return True

    async def logout(self):
        """logout onedrive"""
        await self.__get_or_set_access_token(value="Logout")
        await self.__get_or_set_refresh_token(value="Logout")

    async def authorizate(self, relogin: bool = False):
        """authorizate onedrive sdk
        retry: if True, will retry to get access_token by access url code.
        """
        if (not await self.__get_or_set_refresh_token()) or relogin:
            self.generateLoginURL()
            code = input(">> code=")
            await self.getRefreshTokenByCode(code)

        refresh_token = await self.__get_or_set_refresh_token()
        if refresh_token:
            await self.getTokenByRefreshToken(refresh_token)

        state = await self.checkOnedriveStatus()
        logger.info(f"onedrive state:{state}")

        if not state:
            raise Exception("Onedrive authorization is Invaild")

    @async_retry(times=5)
    async def get_file_download_url(self, file_path: str) -> Optional[str]:
        # /drive/root:/path/to/file
        access_token = await self.__get_or_set_access_token()
        api_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{file_path}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await self.client.get(api_url, headers=headers)
        if response.status_code == 401:
            await self.authorizate()
            logger.error(
                f"unauthorized to onedrive! please relogin or refresh file:{file_path}"
            )
            raise Exception("unauthorized to onedrive! please relgin or refresh")
        if response.status_code == 404:
            logger.error(f"file not found on onedrive! file:{file_path}")
            return None
        response.raise_for_status()
        data = response.json()
        download_url = data.get("@microsoft.graph.downloadUrl", None)
        # logger.debug(f"{file_path} download url:{download_url}")
        return download_url


# od_auth = ODAuthFile()
# # from app.helper.mongodb_connect import od_mongodb_auth
# # from app.config import settings

# CLIENT_ID: str = ""
# CLIENT_SECRET: str = ""

# onedrive_sdk = OnedriveSDK(
#     client_id=CLIENT_ID,
#     client_secret=CLIENT_SECRET,
#     od_auth=od_auth,
# )


# @logger.catch()
# async def main():
#     # await onedrive_sdk.authorizate()
#     await onedrive_sdk.get_file_download_url("/PicStorage/blog/hyy.jpg")


# if __name__ == "__main__":
#     asyncio.run(main())
