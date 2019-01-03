from aiohttp import web
from aiohttp_cors import CorsViewMixin
from authorization import login_required
from models.item import Item
from pymongo.errors import WriteError
from models.item import ItemDoesNotExist
# import json
from bson import ObjectId


class ItemsResource(web.View, CorsViewMixin):

    @login_required
    async def post(self):
        item = Item(self.request.user.data["_id"])
        await item.save()
        return web.json_response({"msg": "Item has been created"})

    # get all user's items
    @login_required
    async def get(self):
        projection = {"title": 1, "image": 1}
        items = await Item.get_many(self.request.user.data["_id"], 20, projection)
        print("ITEMS".center(40, "="))
        print(type(items))
        items_list = [{**item, "_id": str(item["_id"])} for item in items]
        print(items_list)
        return web.json_response(items_list)


class OneItemResource(web.View, CorsViewMixin):

    @login_required
    async def get(self):
        item_id = self.request.match_info.get("item_id", None)
        if not item_id:
            return web.json_response({"error": "You must specify item_id"})
        item = await Item.get(self.request.user.data["_id"], _id=ObjectId(item_id))
        return web.json_response({"item": item.get_dict(with_data=True)})

    @login_required
    async def put(self):
        item_id = self.request.match_info.get("item_id", None)
        if not item_id:
            return web.json_response({"error": "You must specify item_id"})
        try:
            item = await Item.get(self.request.user.data["_id"], _id=ObjectId(item_id))
        except ItemDoesNotExist:
            return web.json_response({"msg": "Item does not exist"}, status=404)

        data = await self.request.json()
        # form tracking key separately because it is embedded dict
        tracking = {key: value for key, value in data["tracking"].items() if key in ["status", "message"]}
        data_keys = ["owner_id", "title", "image", "page_url",
                     "css_selector", "attribute_name"]
        data = {key: value for key, value in data.items() if key in data_keys}
        data.update({"tracking": tracking})
        item.data.update(data)
        try:
            await item.save()
        except WriteError:
            web.json_response({"msg": "Wrong data, write error"})
        return web.json_response({"msg": "hello from put"})

    @login_required
    async def delete(self):
        item_id = self.request.match_info.get("item_id", None)
        if not item_id:
            return web.json_response({"error": "You must specify item_id"})
        await Item.delete(self.request.user.data["_id"], ObjectId(item_id))
        return web.json_response({"msg": "Item has been deleted"})
