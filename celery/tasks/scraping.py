from celery import Celery
from secret_settings import MongoURL
from pymongo import MongoClient
import requests
from requests.exceptions import HTTPError
import bs4
from bson import ObjectId
import datetime

celery_app = Celery("scraping", broker="pyamqp://rabbitmq:5672")
items = MongoClient(MongoURL)["pricetrack"]["items"]


@celery_app.task
def get_items():
    projection = {"page_url": 1, "css_selector": 1, "attribute_name": 1}
    # item_cursor = items.find({"tracking.status":"tracking"}, projection)
    items_cursor = items.find({"tracking.status": "tracking"}, projection)
    for item in items_cursor:
        prepared_item = item
        prepared_item["_id"] = str(prepared_item["_id"])
        parse_item.delay(**prepared_item)
    return "scraping has been finished"


@celery_app.task
def parse_item(_id, page_url, css_selector, attribute_name):
    result = None
    resp = requests.get(page_url)
    try:
        resp.raise_for_status()
    except HTTPError:
        # add message to tracking: message and change status to stoped
        message = "Wrong page url"
        items.update_one({"_id": ObjectId(_id)}, {"$set": {"tracking": {"status": "stoped", "message": message}}})
        # print("HTTP error")
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    el = soup.select_one(css_selector)
    print("testttttttttttttttttttttttttt: ", attribute_name, el)
    # check if bs4 find any elements
    if not el:
        message = "Wrong css selector"
        items.update_one({"_id": ObjectId(_id)}, {"$set": {"tracking": {"status": "stoped", "message": message}}})
        # print("wrong css selector, element not found")
    elif attribute_name:
        try:
            result = float(el[attribute_name])
            data = {"timestamp": datetime.datetime.now().timestamp(), "value": result}
            items.update_one({"_id": ObjectId(_id)}, {"$push": {"data": data}})
            # print("Write data to the database")
        except KeyError:
            message = "Attribute not found"
            items.update_one({"_id": ObjectId(_id)}, {"$set": {"tracking": {"status": "stoped", "message": message}}})
            # print("Wrong attribute name")
    else:
        result = float(el.text.replace(" ", ""))
        data = {"timestamp": datetime.datetime.now().timestamp(), "value": result}
        items.update_one({"_id": ObjectId(_id)}, {"$push": {"data": data}})
        # print("Write data to the database")
    return result
    # return el.attrs[attribute_name]
    # return item[::-1]
