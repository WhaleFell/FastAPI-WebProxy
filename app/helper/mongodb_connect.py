from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from loguru import logger
from typing import List
from typing import Optional
import asyncio

from app.config import settings
from app.helper.ip_lookup import lookupIP
from app.schema.base import AccessLog
from app.helper.onedrive_sdk import ODAuth, OnedriveSDK

client = AsyncIOMotorClient(settings.MONGODB_URL)
# https://stackoverflow.com/questions/65542103/future-task-attached-to-a-different-loop
# deploy in vercel.May cause attached to a different loop.
client.get_io_loop = asyncio.get_event_loop


class MongoDBCRUD:
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.client = client
        self.database = self.client[database_name]

    async def insert_one(self, collection_name: str, document: dict) -> bool:
        """insert one document with error handling"""
        try:
            result = await self.database[collection_name].insert_one(document=document)
            return result.inserted_id
        except Exception as e:
            logger.error("insert one document error: %s" % e)
            return False

    async def newAccessLog(self, ip: str, url: str, status_code: int):
        """new access log"""
        document = {
            "time": datetime.utcnow(),
            "ip": ip,
            "where": lookupIP(ip),
            "url": url,
            "status_code": status_code,
        }
        await self.insert_one(collection_name="access_log", document=document)

    async def searchAccessLog(
        self, skip: int = 0, limit: int = 200, include_keyword: Optional[str] = None
    ) -> List[AccessLog]:
        """search access log"""
        cursor = (
            self.database["access_log"]
            .find({} if not include_keyword else {"url": {"$regex": include_keyword}})
            .skip(skip)
            .limit(limit)
            .sort("time", direction=-1)
        )
        logs = []
        async for document in cursor:
            logs.append(AccessLog(**document))
        return logs

    async def rmAllAccessLog(self):
        """remove all access log"""
        await self.database["access_log"].delete_many({})


class ODAuthUseMongoDB(ODAuth):
    """override ODAuth class to use mongodb as storage

    NOTE: MUST achieve THE `get_or_set_access_token` and `get_or_set_refresh_token` method.

    only one document in mongodb collection named "od_auth".
    {"access_token": "xxx", "refresh_token": "xxx"}
    """

    def __init__(
        self,
        mongodb_client: AsyncIOMotorClient,
    ) -> None:
        super().__init__()
        self.mongodb_client = mongodb_client

    def __repr__(self) -> str:
        return f"ODAuthUseMongoDB(access_token={self.access_token}, refresh_token={self.refresh_token})"

    async def __get_or_set_token(
        self, token_type: str, value: Optional[str] = None
    ) -> Optional[str]:
        """get or set token to mongodb
        token_type: access_token or refresh_token
        """
        if value:
            # set access_token to mongodb
            # upsert means insert if not exist, update if exist.
            await self.mongodb_client["webproxy"]["od_auth"].update_one(
                {}, {"$set": {token_type: value}}, upsert=True
            )
            return value
        document = await self.mongodb_client["webproxy"]["od_auth"].find_one()
        return document.get(token_type, None) if document else None

    async def get_or_set_access_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        return await self.__get_or_set_token("access_token", value)

    async def get_or_set_refresh_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        return await self.__get_or_set_token("refresh_token", value)


mongoCrud = MongoDBCRUD(client=client, database_name="webproxy")
od_mongodb_auth = ODAuthUseMongoDB(mongodb_client=client)

# async def main():
#     # await collection.insert_one({"name": "test"})
#     cursor = collection.find()
#     async for document in cursor:
#         print(document)


if __name__ == "__main__":
    import asyncio

    # asyncio.run(main())
