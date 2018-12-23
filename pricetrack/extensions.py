from config.settings import CLIENT_URI
from config.secret_settings import SecretConfig
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp_cors
# from tasks.reverse import repeat_print

db = AsyncIOMotorClient(SecretConfig.MongoURL)["pricetrack"]

# repeat_print.apply_async(("hello from pricetrack",), countdown=10)

async def change_headers(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"

def apply_cors(app):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
    })

    app.on_response_prepare.append(change_headers)
    # for resource in app.router.routes():
    #     cors.add(resource)
