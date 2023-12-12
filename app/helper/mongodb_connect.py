from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from app.helper.ip_lookup import lookupIP

# client = AsyncIOMotorClient(settings.MONGODB_URL)
# db = client["webproxy"]
# collection = db["access_log"]


class MongoDBCRUD:
    def __init__(self, mongodb_url: str, database_name: str):
        self.client = AsyncIOMotorClient(mongodb_url)
        self.database = self.client[database_name]

    async def newAccessLog(self, ip: str, url: str, status_code: int):
        """new access log"""
        document = {
            "time": datetime.utcnow(),
            "ip": ip,
            "where": lookupIP(ip),
            "url": url,
            "status_code": status_code,
        }
        result = await self.database["access_log"].insert_one(document=document)


async def main():
    # await collection.insert_one({"name": "test"})
    cursor = collection.find()
    async for document in cursor:
        print(document)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
