import pytest

pytestmark = pytest.mark.asyncio

async def test_create_chat(client, auth_headers_factory):
    headers = await auth_headers_factory("user1@example.com")
    response = await client.post("/chats", headers=headers)
    assert response.status_code == 200

async def test_create_chat_unauthorized(client):
    response = await client.post("/chats")
    assert response.status_code == 401

async def test_get_chats(client, auth_headers_factory):
    headers = await auth_headers_factory("user2@example.com")
    
    await client.post("/chats", headers=headers)
    
    response = await client.get("/chats", headers=headers)
    assert response.status_code == 200
    assert "chats" in response.json()
    assert len(response.json()["chats"]) > 0

async def test_update_chat(client, auth_headers_factory):
    headers = await auth_headers_factory("user3@example.com")
    
    await client.post("/chats", headers=headers)
    chats_resp = await client.get("/chats", headers=headers)
    chat_id = chats_resp.json()["chats"][0]["chat_id"]
    
    response = await client.patch(
        f"/chats/{chat_id}", 
        headers=headers,
        json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

async def test_delete_chat(client, auth_headers_factory):
    headers = await auth_headers_factory("user4@example.com")
    
    await client.post("/chats", headers=headers)
    chats_resp = await client.get("/chats", headers=headers)
    chat_id = chats_resp.json()["chats"][0]["chat_id"]
    
    response = await client.delete(f"/chats/{chat_id}", headers=headers)
    assert response.status_code == 200
    
    chats_after = await client.get("/chats", headers=headers)
    assert len(chats_after.json()["chats"]) == 0

async def test_access_other_user_chat(client, auth_headers_factory):
    headers_user1 = await auth_headers_factory("user5@example.com")
    headers_user2 = await auth_headers_factory("user6@example.com")
    
    await client.post("/chats", headers=headers_user1)
    chats_resp = await client.get("/chats", headers=headers_user1)
    chat_id = chats_resp.json()["chats"][0]["chat_id"]
    
    response = await client.delete(f"/chats/{chat_id}", headers=headers_user2)
    assert response.status_code in [403, 404]

async def test_update_nonexistent_chat(client, auth_headers_factory):
    headers = await auth_headers_factory("user7@example.com")
    response = await client.patch(
        "/chats/999999", 
        headers=headers,
        json={"title": "Ghost Chat"}
    )
    assert response.status_code == 404