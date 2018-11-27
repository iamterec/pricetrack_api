from config.secret_settings import SecretConfig
from motor.motor_asyncio import AsyncIOMotorClient

db = AsyncIOMotorClient(SecretConfig.MongoURL)["test"]
