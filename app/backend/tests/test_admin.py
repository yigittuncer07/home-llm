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