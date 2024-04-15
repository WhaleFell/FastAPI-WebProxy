# external import
from app.core.mongodb import MongoDBCRUD, client, AsyncIOMotorClient
from app.core.func import getBeijingTime
from app.core.ip_lookup import lookupIP
from app.config import settings

# internal
from .schema import AccessLog

# typing
from typing import List, Optional


class AccessLogUseMongoDB(MongoDBCRUD):
    """Access log use mongodb as storage
    collection name `access_log`
    """

    collection_name = "access_log"

    def __init__(self, client: AsyncIOMotorClient, database_name: str, *args, **kwargs):  # type: ignore
        super().__init__(client, database_name, *args, **kwargs)

    async def newAccessLog(self, ip: str, url: str, status_code: int):
        """new access log"""
        document = {
            "time": getBeijingTime(),
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


accessLog = AccessLogUseMongoDB(client=client, database_name=settings.MONGODB_DATABASE)
