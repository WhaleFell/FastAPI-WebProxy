from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from typing import List, Optional
from typing_extensions import override
import asyncio

from app.config import settings
from app.core.ip_lookup import lookupIP
from app.core.func import getTimestamp, getBeijingTime

client = AsyncIOMotorClient(settings.MONGODB_URL)
# https://stackoverflow.com/questions/65542103/future-task-attached-to-a-different-loop
# https://github.com/encode/starlette/issues/1315
# deploy in vercel. May cause attached to a different loop.
client.get_io_loop = asyncio.get_event_loop

# Python multiple inheritance design pattern
# https://stackoverflow.com/questions/3277367/how-does-pythons-super-work-with-multiple-inheritance


class MongoDBCRUD(object):
    def __init__(self, client: AsyncIOMotorClient, database_name: str, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.client = client
        self.database = self.client[database_name]
        self.client.get_io_loop = asyncio.get_event_loop

    async def insert_one(self, collection_name: str, document: dict) -> bool:
        """insert one document with error handling"""
        try:
            result = await self.database[collection_name].insert_one(document=document)
            return True if result.acknowledged else False
        except DuplicateKeyError as e:
            logger.warning("DuplicateKeyError")
            return False
        except Exception as e:
            logger.error("insert one document error: %s" % e)
            return False

    async def is_collection_exist(self, collection_name: str) -> bool:
        """check collection exist"""
        collections = await self.database.list_collection_names()
        return collection_name in collections

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


mongoCrud = MongoDBCRUD(client=client, database_name=settings.MONGODB_DATABASE)


# async def main():
#     # await collection.insert_one({"name": "test"})
#     cursor = collection.find()
#     async for document in cursor:
#         print(document)


if __name__ == "__main__":
    import asyncio

    # asyncio.run(main())
