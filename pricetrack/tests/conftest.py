import asyncio
import pytest
from app import create_app


@pytest.yield_fixture
async def registration(client):
    user_data = {"email": "testuser@mail.com",
                 "password": "test_password"}
    resp = await client.post('/users', json=user_data)
    assert resp.status == 200
    yield user_data
    db = client.app["db"]
    db.users.delete_one({"email": user_data["email"]})


@pytest.yield_fixture
async def access_token(client, registration):
    resp = await client.post("/users/login", json=registration)
    data = await resp.json()
    assert resp.status == 200
    pytest.access_token = data["access_token"]
    yield data["access_token"]


@pytest.fixture
async def client(aiohttp_client):
    loop = asyncio.get_event_loop()
    app = create_app(loop)
    client = await aiohttp_client(app)
    return client
