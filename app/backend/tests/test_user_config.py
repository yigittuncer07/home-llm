import pytest

pytestmark = pytest.mark.asyncio

async def test_get_user_config_initial(client, auth_headers_factory):
    headers = await auth_headers_factory("user1@example.com")
    
    response = await client.get("/user/config", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"personalized_prompt": ""}

async def test_update_user_config(client, auth_headers_factory):
    headers = await auth_headers_factory("user2@example.com")
    
    response = await client.patch(
        "/user/config",
        headers=headers,
        json={"personalized_prompt": "Always reply in Python."}
    )
    assert response.status_code == 200
    assert response.json() == {"personalized_prompt": "Always reply in Python."}

async def test_get_user_config_after_update(client, auth_headers_factory):
    headers = await auth_headers_factory("user3@example.com")
    
    await client.patch(
        "/user/config",
        headers=headers,
        json={"personalized_prompt": "Keep it concise."}
    )
    
    response = await client.get("/user/config", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"personalized_prompt": "Keep it concise."}

async def test_user_config_unauthorized(client):
    get_response = await client.get("/user/config")
    assert get_response.status_code == 401

    patch_response = await client.patch(
        "/user/config",
        json={"personalized_prompt": "test"}
    )
    assert patch_response.status_code == 401