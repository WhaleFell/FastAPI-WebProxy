# typing
from typing import Optional
from typing_extensions import override


# external packages
from app.core.mongodb import MongoDBCRUD, client, AsyncIOMotorClient
from app.core.onedrive_sdk import ODAuth
from app.config import settings


class ODAuthUseMongoDB(ODAuth, MongoDBCRUD):
    """override ODAuth class to use mongodb as storage

    NOTE: MUST achieve the `get_or_set_access_token` and `get_or_set_refresh_token` method.

    only one document in mongodb collection named "od_auth".
    {"access_token": "xxx", "refresh_token": "xxx"}

    collection name `od_auth`
    """

    collection_name = "od_auth"

    def __init__(
        self,
        mongodb_client: AsyncIOMotorClient,  # type: ignore
        database_name: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            client=mongodb_client,
            database_name=database_name,
            *args,
            **kwargs,
        )
        # logger.info(f"ODAuthUseMongoDB init: {self}")
        # self.mongodb_client = mongodb_client
        # self.mongodb_client.get_io_loop = asyncio.get_event_loop
        # self.database = self.mongodb_client[database_name]

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

    @override
    async def get_or_set_access_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        return await self.__get_or_set_token("access_token", value)

    @override
    async def get_or_set_refresh_token(
        self, value: Optional[str] = None
    ) -> Optional[str]:
        return await self.__get_or_set_token("refresh_token", value)


od_mongodb_auth = ODAuthUseMongoDB(
    mongodb_client=client, database_name=settings.MONGODB_DATABASE
)
