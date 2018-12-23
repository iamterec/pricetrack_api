from extensions import db

class ItemDoesNotExist(Exception):
    def __init__(self, message, errors=""):
        super().__init__(message)
        self.errors = errors


class Item:
    def __init__(self, owner_id, title=""):
        self.data = {}
        self.data["owner_id"] = owner_id
        self.data["title"] = title
        self.data["tracking"] = {"status": "stoped", "message": ""}

    @classmethod
    async def get(cls, owner_id, **kwargs):
        item_dict = await db.items.find_one({**kwargs, "owner_id": owner_id})
        if not item_dict:
            raise ItemDoesNotExist("Item not found")
        item = Item(item_dict["owner_id"], item_dict["title"])
        item.data.update(item_dict)
        return item

    @classmethod
    async def get_many(cls, owner_id, quantity, projection=None):
        cursor = db.items.find({"owner_id": owner_id}, projection)
        items = [item for item in await cursor.to_list(length=quantity)]
        return items

    async def save(self):
        item_keys = ["_id", "owner_id", "title", "image", "page_url",
                     "css_selector", "attribute_name", "tracking"]
        if self.data.get("_id", None):
            item_filter = {"_id": self.data["_id"]}
            # print("item filter: ", item_filter)
            update_data = {key: value for key, value in self.data.items()
                           if key in item_keys and key != "_id"}
            # print("Update data: ", update_data)
            result = await db.items.update_one(item_filter, {"$set": update_data})
            print("Save item result: ", result.raw_result)
        else:
            await db.items.insert_one(self.data)

    @classmethod
    async def delete(self, owner_id, id):
        item_filter = {"_id": id, "owner_id": owner_id }
        # try:
        result = await db.items.delete_one(item_filter)
        print("deletion result: ", result.raw_result)
        # except:
        #     return 12



    def get_dict(self):
        if self.data.get("_id", None):
            data = {}
            data["_id"] = str(self.data["_id"])
            data["title"] = self.data["title"]
            data["image"] = self.data.get("image", "")
            data["tracking"] = self.data.get("tracking", {})

            page_url = self.data.get("page_url", None)
            css_selector = self.data.get("css_selector", None)
            attribute_name = self.data.get("attribute_name", None)

            data["page_url"] = page_url if page_url else ""
            data["css_selector"] = css_selector if css_selector else ""
            data["attribute_name"] = attribute_name if attribute_name else ""
            return data
        else:
            return {}
