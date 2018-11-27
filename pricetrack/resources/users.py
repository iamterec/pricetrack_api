from aiohttp import web
from extensions import db
import json


class Hello(web.View):

    async def get(self):
        document = await db.test_collection.find_one({}, {"_id": 0})
        print(document)
        return web.Response(text=json.dumps(document))
