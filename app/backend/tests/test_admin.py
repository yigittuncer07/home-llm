import pytest
from config import settings

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def admin_headers(client):
    response = await client.post(
        "/auth/login", 
        json={"email": settings.admin_email, "password": settings.admin_password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

async def test_admin_register_user(client, admin_headers):
    response = await client.post(
        "/admin/users", 
        headers=admin_headers,
        json={"email": "newuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@example.com"

async def test_admin_register_existing_user(client, admin_headers):
    await client.post(
        "/admin/users", 
        headers=admin_headers,
        json={"email": "existing@example.com", "password": "password123"}
    )
    
    response = await client.post(
        "/admin/users", 
        headers=admin_headers,
        json={"email": "existing@example.com", "password": "password123"}
    )
    assert response.status_code == 400

async def test_get_all_users(client, admin_headers):
    response = await client.get("/admin/users", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    # Verify token_balances relationship is present in the list
    assert "token_balances" in users[0]

async def test_delete_user(client, admin_headers):
    create_resp = await client.post(
        "/admin/users", 
        headers=admin_headers,
        json={"email": "delete_me@example.com", "password": "password123"}
    )
    user_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/admin/users/{user_id}", headers=admin_headers)
    assert delete_resp.status_code == 200

    get_resp = await client.get("/admin/users", headers=admin_headers)
    users = get_resp.json()
    assert not any(u["id"] == user_id for u in users)

async def test_admin_endpoints_unauthorized(client):
    # No token
    resp1 = await client.get("/admin/users")
    assert resp1.status_code == 401

    # Standard user token
    admin_login = await client.post(
        "/auth/login", 
        json={"email": settings.admin_email, "password": settings.admin_password}
    )
    admin_token = admin_login.json()["access_token"]
    
    await client.post(
        "/admin/users", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": "regular@example.com", "password": "password123"}
    )
    
    user_login = await client.post(
        "/auth/login", 
        json={"email": "regular@example.com", "password": "password123"}
    )
    user_token = user_login.json()["access_token"]

    resp2 = await client.get("/admin/users", headers={"Authorization": f"Bearer {user_token}"})
    assert resp2.status_code in [401, 403]

async def test_update_and_get_user_tokens(client, admin_headers):
    # Create user
    create_resp = await client.post(
        "/admin/users", 
        headers=admin_headers,
        json={"email": "token_user@example.com", "password": "password123"}
    )
    user_id = create_resp.json()["id"]

    # Set tokens
    patch_resp = await client.patch(
        f"/admin/users/{user_id}/tokens",
        headers=admin_headers,
        json={"model_name": "qwen", "balance": 1500}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["balance"] == 1500
    assert patch_resp.json()["model_name"] == "qwen"

    # Fetch user details to verify tokens eager-loaded correctly
    get_resp = await client.get(f"/admin/users/{user_id}", headers=admin_headers)
    assert get_resp.status_code == 200
    user_data = get_resp.json()
    
    assert len(user_data["token_balances"]) == 1
    assert user_data["token_balances"][0]["balance"] == 1500

async def test_admin_chat_management(client, admin_headers, auth_headers_factory):
    # Create a normal user via the factory and authenticate them
    user_headers = await auth_headers_factory("chat_user@example.com")
    
    # Create a chat acting as the normal user
    chat_resp = await client.post("/chats", headers=user_headers)
    chat_id = chat_resp.json()["chat_id"]

    # Find the user ID from the admin endpoint
    users_resp = await client.get("/admin/users", headers=admin_headers)
    user_id = next(u["id"] for u in users_resp.json() if u["email"] == "chat_user@example.com")

    # Admin views the user's chats
    admin_chats_resp = await client.get(f"/admin/chats/{user_id}", headers=admin_headers)
    assert admin_chats_resp.status_code == 200
    chats = admin_chats_resp.json()
    assert len(chats) >= 1
    assert chats[0]["chat_id"] == chat_id

    # Admin deletes the chat
    delete_chat_resp = await client.delete(f"/admin/chat/{chat_id}", headers=admin_headers)
    assert delete_chat_resp.status_code == 200

    # Verify deletion
    admin_chats_resp_after = await client.get(f"/admin/chats/{user_id}", headers=admin_headers)
    assert len(admin_chats_resp_after.json()) == 0

async def test_admin_not_found_errors(client, admin_headers):
    # User details 404
    resp1 = await client.get("/admin/users/999999", headers=admin_headers)
    assert resp1.status_code == 404

    # Token patch 404
    resp2 = await client.patch(
        "/admin/users/999999/tokens",
        headers=admin_headers,
        json={"model_name": "qwen", "balance": 100}
    )
    assert resp2.status_code == 404

    # Chat delete 404
    resp3 = await client.delete("/admin/chat/999999", headers=admin_headers)
    assert resp3.status_code == 404