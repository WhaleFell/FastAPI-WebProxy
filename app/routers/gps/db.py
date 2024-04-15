# type
from typing import List, Optional

# internal
from .schema import GPSUploadData

# external
from app.core.mongodb import MongoDBCRUD, client, AsyncIOMotorClient
from app.config import settings
from app.core.func import getTimestamp


class GPSUseMongoDB(MongoDBCRUD):
    """GPS upload data use mongodb as storage

    collection name `gps_data`

    document example:
    {"latitude": 0.0, "longitude": 0.0, "altitude": 0.0, "speed": 0.0, "GPSTime": "2021-09-01T00:00:00.000Z", "uploadTime": "2021-09-01T00:00:00.000Z"}
    """

    collection_name = "gps_data"

    def __init__(self, client: AsyncIOMotorClient, database_name: str, *args, **kwargs):  # type: ignore
        super().__init__(client, database_name, *args, **kwargs)
        self.collection = self.database[self.collection_name]

    async def insert_GPS_data(self, GPS_data: GPSUploadData) -> bool:
        """insert GPS data `GPSTimestamp` as a unique index to avoid duplicate data"""

        # check collection exist
        # if not await self.is_collection_exist(self.collection_name):
        # create unique index
        await self.collection.create_index(
            [("GPSTimestamp", 1)], unique=True, name="GPSTimestamp"
        )

        doc = GPS_data.model_dump()
        return await self.insert_one(collection_name=self.collection_name, document=doc)

    async def insert_mutiple_GPS_data(self, GPS_datas: List[GPSUploadData]) -> bool:
        """insert mutiple GPS data
        ordered=False means continue to insert if error occurred
        """
        # check collection exist
        # if not await self.is_collection_exist(self.collection_name):
        # create unique index
        await self.collection.create_index(
            [("GPSTimestamp", 1)], unique=True, name="GPSTimestamp"
        )
        try:
            result_list = await self.collection.insert_many(
                [GPS_data.model_dump() for GPS_data in GPS_datas], ordered=False
            )
            return True if result_list.acknowledged else False
        except:
            return False

    async def query_GPS_by_time(
        self,
        limit: Optional[int] = None,
        skip: Optional[int] = 0,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None,
        direction: Optional[int] = -1,
    ) -> List[GPSUploadData]:
        """query GPS data by time"""
        query = {"GPSTimestamp": {"$gte": 0, "$lte": getTimestamp()}}
        if start_timestamp:
            query["GPSTimestamp"]["$gte"] = start_timestamp
        if end_timestamp:
            query["GPSTimestamp"]["$lte"] = end_timestamp

        if limit and skip:
            cursor = (
                self.collection.find(query)
                .skip(skip)
                .limit(limit)
                .sort("GPSTimestamp", direction=direction)
            )
        else:
            cursor = self.collection.find(query).sort(
                "GPSTimestamp", direction=direction
            )

        result = []
        async for document in cursor:
            result.append(GPSUploadData(**document))
        return result

    async def query_latest_GPS(self) -> Optional[GPSUploadData]:
        """query latest GPS data"""
        cursor = self.collection.find().sort("GPSTimestamp", direction=-1).limit(1)
        async for document in cursor:
            return GPSUploadData(**document)
        return None

    async def gps_collection_rm(self) -> bool:
        """remove collection"""
        return await self.rm_collection(self.collection_name)


gps_mongodb = GPSUseMongoDB(client=client, database_name=settings.MONGODB_DATABASE)
