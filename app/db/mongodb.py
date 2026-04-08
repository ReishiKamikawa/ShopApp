from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    print("Connected to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_database() -> AsyncIOMotorDatabase:
    return database
