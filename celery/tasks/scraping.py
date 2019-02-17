from celery import Celery
from config.secret_settings import SecretConfig
from pymongo import MongoClient
import requests
from requests.exceptions import HTTPError, ConnectionError
import bs4
from bson import ObjectId
import datetime


celery_app = Celery("scraping", backend=SecretConfig.MongoAsCeleryBackend,
                    broker="pyamqp://rabbitmq:5672")

items = MongoClient(SecretConfig.MongoURL)["pricetrack"]["items"]  # get items collection


@celery_app.task
def get_items():
    '''
    Get all items from the database where tracking.status == "tracking"
    and run async task parce_item for each one
    '''
    projection = {"page_url": 1, "css_selector": 1, "attribute_name": 1}
    items_cursor = items.find({"tracking.status": "tracking"}, projection)
    for item in items_cursor:
        prepared_item = item
        prepared_item["_id"] = str(prepared_item["_id"])
        parse_item.delay(**prepared_item)
    return "scraping has been finished"


@celery_app.task
def try_to_parce_page(_id: str, page_url: str, css_selector: str, attribute_name: str=None):
    '''
    Try to parce data but without saving the result to the database.
    Using when user turn on "tracking" on item and we need to know if it's even
    possible to parse this data with provided url, css_selector and attribute.
    '''
    # result = {"tracking": {"status": "tracking", "message": ""}}

    # get the page
    try:
        resp = requests.get(page_url)
        resp.raise_for_status()
    except HTTPError:
        return {"status": "stoped", "message": "Wrong page url"}
    except ConnectionError:
        return {"status": "stoped", "message": "Connections error"}

    # get the element
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    el = soup.select_one(css_selector)
    if not el:
        return {"status": "stoped", "message": "Element not found"}

    # get attribute value
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
    '''
    Try to parce data and save it to the item.

    '''
    result = None
    # get the page
    try:
        resp = requests.get(page_url)
        resp.raise_for_status()
    except HTTPError:
        # change tracking to stoped and write message
        message = "Wrong page url"
        items.update_one({"_id": ObjectId(_id)},
                         {"$set": {"tracking": {"status": "stoped", "message": message}}})
        return result
    except ConnectionError:
        return result

    # get the element
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    el = soup.select_one(css_selector)
    if not el:
        message = "Wrong css selector"
        items.update_one({"_id": ObjectId(_id)},
                         {"$set": {"tracking": {"status": "stoped", "message": message}}})

    # get the attribute value if it's provided and save it
    elif attribute_name:
        try:
            result = float(el[attribute_name])
            data = {"timestamp": datetime.datetime.now().timestamp(), "value": result}
            items.update_one({"_id": ObjectId(_id)}, {"$push": {"data": data}})
            return result
        except KeyError:
            message = "Attribute not found"
            items.update_one({"_id": ObjectId(_id)},
                             {"$set": {"tracking": {"status": "stoped", "message": message}}})
            return result

    # if not: get data from the element
    else:
        result = float(el.text.replace(" ", ""))
        data = {"timestamp": datetime.datetime.now().timestamp(), "value": result}
        items.update_one({"_id": ObjectId(_id)}, {"$push": {"data": data}})
    return result
