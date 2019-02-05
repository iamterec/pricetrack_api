from celery import Celery
from config.secret_settings import SecretConfig
from pymongo import MongoClient
import requests
from requests.exceptions import HTTPError
import bs4
from bson import ObjectId
import datetime


backend = "mongodb://denys2:rN6aJpqVyx6zTYFP@mongodb:27017/celery"
celery_app = Celery("scraping", backend=SecretConfig.MongoAsCeleryBackend, broker="pyamqp://rabbitmq:5672")

items = MongoClient(SecretConfig.MongoURL)["pricetrack"]["items"]


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
def try_to_parce_page(_id: str, page_url: str, css_selector: str, attribute_name: str=None):
    # result = {"tracking": {"status": "tracking", "message": ""}}
    resp = requests.get(page_url)

    # page existings
    try:
        resp.raise_for_status()
    except HTTPError:
        return {"status": "stoped", "message": "Wrong page url"}

    # element existings
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    el = soup.select_one(css_selector)
    if not el:
        return {"status": "stoped", "message": "Element not found"}

    # getting attribute value
    if attribute_name:
        try:
            float(el[attribute_name])
        except KeyError:
            return {"status": "stoped", "message": "Wrong attribute_name"}
        except ValueError:
            return {"status": "stoped", "message": "Attribute value is not a number"}

    return {"status": "tracking", "message": ""}


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
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    el = soup.select_one(css_selector)
    # check if bs4 find any elements
    if not el:
        message = "Wrong css selector"
        items.update_one({"_id": ObjectId(_id)}, {"$set": {"tracking": {"status": "stoped", "message": message}}})
    elif attribute_name:
        try:
            result = float(el[attribute_name])
            data = {"timestamp": datetime.datetime.now().timestamp(), "value": result}
            items.update_one({"_id": ObjectId(_id)}, {"$push": {"data": data}})
        except KeyError:
            message = "Attribute not found"
            items.update_one({"_id": ObjectId(_id)}, {"$set": {"tracking": {"status": "stoped", "message": message}}})
    else:
        result = float(el.text.replace(" ", ""))
        data = {"timestamp": datetime.datetime.now().timestamp(), "value": result}
        items.update_one({"_id": ObjectId(_id)}, {"$push": {"data": data}})
    return result
