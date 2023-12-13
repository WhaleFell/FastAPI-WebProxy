from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from loguru import logger
from typing import List

from app.config import settings
from app.helper.ip_lookup import lookupIP
from app.schema.base import AccessLog
import asyncio

# client = AsyncIOMotorClient(settings.MONGODB_URL)
# db = client["webproxy"]
# collection = db["access_log"]


class MongoDBCRUD:
    def __init__(self, mongodb_url: str, database_name: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.database = self.client[database_name]
        self.client.get_io_loop = asyncio.get_event_loop

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

    async def searchAccessLog(self, skip: int = 0, limit: int = 200) -> List[AccessLog]:
        """search access log"""
        cursor = (
            self.database["access_log"]
            .find({})
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


mongoCrud = MongoDBCRUD(settings.MONGODB_URL, "webproxy")

# async def main():
#     # await collection.insert_one({"name": "test"})
#     cursor = collection.find()
#     async for document in cursor:
#         print(document)


if __name__ == "__main__":
    import asyncio

    # asyncio.run(main())
