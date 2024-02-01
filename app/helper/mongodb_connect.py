from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date
from loguru import logger
from typing import List, Optional
from typing_extensions import override
import asyncio

from app.config import settings
from app.helper.ip_lookup import lookupIP
from app.schema.base import AccessLog, GPSUploadData
from app.helper.onedrive_sdk import ODAuth
from app.helper.func import getBeijingTime, getTimestamp

client = AsyncIOMotorClient(settings.MONGODB_URL)
# https://stackoverflow.com/questions/65542103/future-task-attached-to-a-different-loop
# https://github.com/encode/starlette/issues/1315
# deploy in vercel. May cause attached to a different loop.
client.get_io_loop = asyncio.get_event_loop


class MongoDBCRUD:
    def __init__(self, client: AsyncIOMotorClient, database_name: str, *args, **kwargs):
        self.client = client
        self.database = self.client[database_name]
        self.client.get_io_loop = asyncio.get_event_loop

    async def insert_one(self, collection_name: str, document: dict) -> bool:
        """insert one document with error handling"""
        try:
            result = await self.database[collection_name].insert_one(document=document)
            return True if result.acknowledged else False
        except Exception as e:
            logger.error("insert one document error: %s" % e)
            return False

    async def rm_collection(self, collection_name: str) -> bool:
        """remove collection"""
        try:
            await self.database[collection_name].drop()
            return True
        except Exception as e:
            logger.error("remove collection error: %s" % e)
            return False

    async def rm_database(self, database_name: Optional[str] = None) -> bool:
        """remove database"""
        try:
            if not database_name:
                database_name = self.database.name
            await self.client.drop_database(database_name)
            return True
        except Exception as e:
            logger.error("remove database error: %s" % e)
            return False


class AccessLogUseMongoDB(MongoDBCRUD):
    """Access log use mongodb as storage
    collection name `access_log`
    """

    collection_name = "access_log"

    def __init__(self, client: AsyncIOMotorClient, database_name: str, *args, **kwargs):
        super().__init__(client, database_name, *args, **kwargs)

    async def newAccessLog(self, ip: str, url: str, status_code: int):
        """new access log"""
        document = {
            "time": datetime.utcnow(),
            "ip": ip,
            "where": lookupIP(ip),
            "url": url,
            "status_code": status_code,
        }
        await self.insert_one(collection_name=self.collection_name, document=document)

    async def searchAccessLog(
        self, skip: int = 0, limit: int = 200, include_keyword: Optional[str] = None
    ) -> List[AccessLog]:
        """search access log"""
        cursor = (
            self.database[self.collection_name]
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
        await self.rm_collection(self.collection_name)


class ODAuthUseMongoDB(ODAuth, MongoDBCRUD):
    """override ODAuth class to use mongodb as storage

    NOTE: MUST achieve the `get_or_set_access_token` and `get_or_set_refresh_token` method.

    only one document in mongodb collection named "od_auth".
    {"access_token": "xxx", "refresh_token": "xxx"}

    collection name `od_auth`
    """

    collection_name = "od_auth"

    def __init__(
        self, mongodb_client: AsyncIOMotorClient, database_name: str, *args, **kwargs
    ) -> None:
        super().__init__(
            client=mongodb_client, database_name=database_name, *args, **kwargs
        )
        # self.mongodb_client = mongodb_client
        # self.mongodb_client.get_io_loop = asyncio.get_event_loop
        # self.database = self.mongodb_client[database_name]

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
            await self.database[self.collection_name].update_one(
                {}, {"$set": {token_type: value}}, upsert=True
            )
            return value
        document = await self.database[self.collection_name].find_one()
        return document.get(token_type, None) if document else None

    async def get_or_set_access_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        return await self.__get_or_set_token("access_token", value)

    async def get_or_set_refresh_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        return await self.__get_or_set_token("refresh_token", value)


class GPSUseMongoDB(MongoDBCRUD):
    """GPS upload data use mongodb as storage

    collection name `gps_data`

    document example:
    {"latitude": 0.0, "longitude": 0.0, "altitude": 0.0, "speed": 0.0, "GPSTime": "2021-09-01T00:00:00.000Z", "uploadTime": "2021-09-01T00:00:00.000Z"}
    """

    collection_name = "gps_data"

    def __init__(self, client: AsyncIOMotorClient, database_name: str, *args, **kwargs):
        super().__init__(client, database_name, *args, **kwargs)

    async def insert_GPS_data(self, GPS_data: GPSUploadData) -> bool:
        """insert GPS data"""
        doc = GPS_data.model_dump()
        return await self.insert_one(collection_name=self.collection_name, document=doc)

    async def query_GPS_by_time(
        self,
        limit: int = 200,
        skip: int = 0,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
    ) -> List[GPSUploadData]:
        """query GPS data by time"""
        query = {"uploadTimestamp": {"$gte": 0, "$lte": getTimestamp()}}
        if start_timestamp:
            query["uploadTimestamp"]["$gte"] = start_timestamp
        if end_timestamp:
            query["uploadTimestamp"]["$lte"] = end_timestamp

        cursor = (
            self.database[self.collection_name]
            .find(query)
            .skip(skip)
            .limit(limit)
            .sort("uploadTime", direction=-1)
        )
        result = []
        async for document in cursor:
            result.append(GPSUploadData(**document))
        return result


mongoCrud = MongoDBCRUD(client=client, database_name=settings.MONGODB_DATABASE)
accessLog = AccessLogUseMongoDB(client=client, database_name=settings.MONGODB_DATABASE)
od_mongodb_auth = ODAuthUseMongoDB(
    mongodb_client=client, database_name=settings.MONGODB_DATABASE
)
gps_mongodb = GPSUseMongoDB(client=client, database_name=settings.MONGODB_DATABASE)

# async def main():
#     # await collection.insert_one({"name": "test"})
#     cursor = collection.find()
#     async for document in cursor:
#         print(document)


if __name__ == "__main__":
    import asyncio

    # asyncio.run(main())
