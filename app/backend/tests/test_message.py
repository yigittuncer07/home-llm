import pytest
from unittest.mock import patch, AsyncMock
from core.exceptions import AppException
from core.helpers import ensure_positive_balance as real_ensure_positive_balance

pytestmark = pytest.mark.asyncio

# Mock Redis task queueing
@pytest.fixture(autouse=True)
def mock_enqueue_task():
    with patch("services.messages.enqueue_task") as mock:
        yield mock

# globally mock the token check to allow standard tests to pass
@pytest.fixture(autouse=True)
def mock_token_check():
    with patch("services.messages.ensure_positive_balance", new_callable=AsyncMock) as mock:
        yield mock

async def test_send_message(client, auth_headers_factory):
    headers = await auth_headers_factory("msg1@example.com")
    
    chat_resp = await client.post("/chats", headers=headers)
    chat_id = chat_resp.json()["chat_id"]
    
    payload = {"prompt": "Hello", "model": "qwen"}
    response = await client.post(f"/chats/{chat_id}/messages", headers=headers, json=payload)
    
    assert response.status_code == 202
    assert response.json()["message"] == "Message enqueued successfully"

async def test_send_message_insufficient_tokens(client, auth_headers_factory):
    headers = await auth_headers_factory("msg_tokens@example.com")
    
    chat_resp = await client.post("/chats", headers=headers)
    chat_id = chat_resp.json()["chat_id"]
    
    # overwrite the global mock with the real function to hit the test database
    # this works because default token balance for new users is 0, so the test should trigger the 402 error
    with patch("services.messages.ensure_positive_balance", side_effect=real_ensure_positive_balance):
        payload = {"prompt": "Hello", "model": "qwen"}
        response = await client.post(f"/chats/{chat_id}/messages", headers=headers, json=payload)
        
        assert response.status_code == 402
        assert "Token balance depleted" in response.text

async def test_get_chat_history(client, auth_headers_factory):
    headers = await auth_headers_factory("msg2@example.com")
    
    chat_resp = await client.post("/chats", headers=headers)
    chat_id = chat_resp.json()["chat_id"]
    
    payload = {"prompt": "History test", "model": "qwen"}
    await client.post(f"/chats/{chat_id}/messages", headers=headers, json=payload)
    
    response = await client.get(f"/chats/{chat_id}/messages", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["chat_id"] == chat_id
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "History test"
    assert data["messages"][0]["role"] == "user"

async def test_send_message_unauthorized(client):
    payload = {"prompt": "No auth", "model": "qwen"}
    response = await client.post("/chats/1/messages", json=payload)
    assert response.status_code == 401
    
    response = await client.get("/chats/1/messages")
    assert response.status_code == 401

async def test_access_nonexistent_chat(client, auth_headers_factory):
    headers = await auth_headers_factory("msg3@example.com")
    payload = {"prompt": "Ghost chat", "model": "qwen"}
    
    post_resp = await client.post("/chats/999999/messages", headers=headers, json=payload)
    assert post_resp.status_code == 404
    
    get_resp = await client.get("/chats/999999/messages", headers=headers)
    assert get_resp.status_code == 404

async def test_access_other_user_messages(client, auth_headers_factory):
    headers_user1 = await auth_headers_factory("msg4@example.com")
    headers_user2 = await auth_headers_factory("msg5@example.com")
    
    chat_resp = await client.post("/chats", headers=headers_user1)
    chat_id = chat_resp.json()["chat_id"]
    
    payload = {"prompt": "Intruder test", "model": "qwen"}
    
    post_resp = await client.post(f"/chats/{chat_id}/messages", headers=headers_user2, json=payload)
    assert post_resp.status_code in [403, 404]
    
    get_resp = await client.get(f"/chats/{chat_id}/messages", headers=headers_user2)
    assert get_resp.status_code in [403, 404]