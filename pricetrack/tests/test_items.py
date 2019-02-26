import pytest


@pytest.yield_fixture
async def item(access_token, client):
    access_token = pytest.access_token
    headers = {"Authorization": access_token}
    # create item
    resp = await client.post("/items", headers=headers)
    item_id = (await resp.json())["item_id"]
    assert resp.status == 200
    yield item_id  # return item
    # delete item
    resp = await client.delete("/items/{}".format(item_id), headers=headers)
    assert resp.status == 200


async def test_get_all_items(access_token, client):
    headers = {"Authorization": access_token}
    resp = await client.get("/items", headers=headers)
    data = await resp.json()
    assert isinstance(data, list)
    assert resp.status == 200


async def test_get_one_item(access_token, client, item):
    headers = {"Authorization": access_token}
    resp = await client.get("/items/{}".format(item), headers=headers)
    assert resp.status == 200


async def test_change_one_item(access_token, client, item):
    headers = {"Authorization": access_token}
    data = {"title": "Some Test Item", "image": "image_url_here",
            "page_url": "page_url_here", "css_selector": "div.class-name",
            "tracking": {"status": "stoped", "message": ""}}
    resp = await client.put("/items/{}".format(item), json=data, headers=headers)
    assert resp.status == 200
