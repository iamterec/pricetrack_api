async def test_get_user(access_token, client):
    headers = {"Authorization": access_token}
    resp = await client.get("/users/me", headers=headers)
    data = await resp.json()
    assert resp.status == 200
    assert data.get("user", False)


async def test_update_user(access_token, client):
    headers = {"Authorization": access_token}
    data = {"avatar": "url_of_picture"}
    resp = await client.put("/users/me", json=data, headers=headers)
    data = await resp.json()
    assert resp.status == 200
    assert data.get("msg")
