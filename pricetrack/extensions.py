from config.secret_settings import SecretConfig
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp_cors

# get database
db = AsyncIOMotorClient(SecretConfig.MongoURL)["pricetrack"]

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
