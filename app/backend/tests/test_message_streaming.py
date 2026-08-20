import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

# A finite dummy generator to replace the infinite Redis listener
async def mock_chat_stream_generator(chat_id: int):
    yield 'data: {"token": "hello", "is_finished": false}\n\n'
    yield 'data: {"token": "", "is_finished": true}\n\n'

async def test_stream_chat_success(client, auth_headers_factory):
    headers = await auth_headers_factory("stream1@example.com")
    
    chat_resp = await client.post("/chats", headers=headers)
    chat_id = chat_resp.json()["chat_id"]
    
    # Patch the generator directly in the router where it is used
    with patch("routers.chats.chat_stream_generator", side_effect=mock_chat_stream_generator):
        response = await client.get(f"/chats/{chat_id}/stream", headers=headers)
        
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # httpx AsyncClient buffers the finite streaming response into .text
        content = response.text
        assert 'data: {"token": "hello", "is_finished": false}' in content
        assert 'data: {"token": "", "is_finished": true}' in content

async def test_stream_chat_unauthorized(client):
    response = await client.get("/chats/1/stream")
    assert response.status_code == 401

async def test_stream_chat_other_user_forbidden(client, auth_headers_factory):
    headers_user1 = await auth_headers_factory("stream2@example.com")
    headers_user2 = await auth_headers_factory("stream3@example.com")
    
    chat_resp = await client.post("/chats", headers=headers_user1)
    chat_id = chat_resp.json()["chat_id"]
    
    response = await client.get(f"/chats/{chat_id}/stream", headers=headers_user2)
    assert response.status_code in [403, 404]