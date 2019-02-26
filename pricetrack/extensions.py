import aiohttp_cors
import asyncio
from config.secret_settings import SecretConfig
from motor.motor_asyncio import AsyncIOMotorClient


def setup_database(app, loop):
    if loop:
        asyncio.set_event_loop(loop)
        db = AsyncIOMotorClient(SecretConfig.MongoURL, io_loop=loop)["pricetrack"]
    else:
        db = AsyncIOMotorClient(SecretConfig.MongoURL)["pricetrack"]
    app["db"] = db


# handle cors
async def change_headers(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"


def apply_cors(app):
    aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })

    # subscribing to on_response_prepare aiohttp signal
    app.on_response_prepare.append(change_headers)
