from aiohttp import web
from aiohttp_cors import CorsViewMixin
from authorization import login_required
from models.item import Item
from pymongo.errors import WriteError, CollectionInvalid
from models.item import ItemDoesNotExist
from bson import ObjectId

# celery
from tasks.scraping import try_to_parce_page

from asyncio import sleep


class ItemsResource(web.View, CorsViewMixin):

    @login_required
    async def post(self):
        item = Item(self.request.user.data["_id"])  # create an empty Item
        await item.save()
        return web.json_response({"msg": "Item has been created"})

    # get all items that user have
    @login_required
    async def get(self):
        projection = {"title": 1, "image": 1}  # include only title and image in response
        items = await Item.get_many(self.request.user.data["_id"], 20, projection)
        # items contains list of dicts
        items_list = [{**item, "_id": str(item["_id"])} for item in items]
        return web.json_response(items_list)


class OneItemResource(web.View, CorsViewMixin):

    @login_required
    async def get(self):
        item_id = self.request.match_info.get("item_id", None)
        if not item_id:
            return web.json_response({"error": "You must specify item_id"})

        try:
            item = await Item.get(self.request.user.data["_id"], _id=ObjectId(item_id))
        except ItemDoesNotExist:
            return web.json_response({"error": "Item doesn't exist"})

        return web.json_response({"item": item.get_dict(with_data=True)})

    @login_required
    async def put(self):
        item_id = self.request.match_info.get("item_id", None)
        if not item_id:
            return web.json_response({"error": "You must specify item_id"})
        try:
            item = await Item.get(self.request.user.data["_id"], _id=ObjectId(item_id))
        except ItemDoesNotExist:
            return web.json_response({"error": "Item does not exist"}, status=404)

        data = await self.request.json()
        # restrict amount of fields that can be saved to the database
        data_keys = ["owner_id", "title", "image", "page_url",
                     "css_selector", "attribute_name"]
        item_data = {key: value for key, value in data.items() if key in data_keys}
        item.data.update(item_data)  # update those fields

        # form "tracking" key separately because it is embedded dict
        tracking = {key: value for key, value in data["tracking"].items() if key in ["status", "message"]}

        # check if we should start tracking, if do, run asyn task that try to
        # parse data
        task_result = None
        if (item.data["tracking"]["status"] == "stoped") and (tracking["status"] == "tracking"):
            # args needed for async task
            args = {"_id": str(item.data["_id"]), "page_url": item.data["page_url"],
                    "css_selector": item.data["css_selector"],
                    "attribute_name": item.data["attribute_name"]}
            async_res = try_to_parce_page.delay(**args)
            for i in range(10):
                status = async_res.status
                if status == "SUCCESS":
                    # change tracking status here to tracking
                    task_result = async_res.result
                    break
                elif status == "FAILURE":
                    # change tracking status here to stoped and write message
                    break
                else:
                    await sleep(2)
            async_res.forget()

        # data.update({"tracking": tracking})
        if task_result:
            item.data.update({"tracking": task_result})  # result from async task
        else:
            item.data.update({"tracking": tracking})  # from request

        try:
            await item.save()
        except WriteError:
            web.json_response({"error": "Wrong data, write error"}, status=400)
        except CollectionInvalid:
            web.json_response({"error": "Wrong data"})
        return web.json_response({"item": item.get_dict(with_data=True)})

    @login_required
    async def delete(self):
        item_id = self.request.match_info.get("item_id", None)
        if not item_id:
            return web.json_response({"error": "You must specify item_id"})

        try:
            await Item.delete(self.request.user.data["_id"], ObjectId(item_id))
        except ItemDoesNotExist:
            return web.json_response({"error": "Item doesn't exist"}, status=400)
        return web.json_response({"msg": "Item has been deleted"})
