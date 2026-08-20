import pytest

pytestmark = pytest.mark.asyncio
from config import settings

async def test_register_deprecated(client):
    response = await client.post(
        "/auth/register", 
        json={"email": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 404

async def test_login(client):
    # Authenticate using the default admin from Alembic migration
    admin_login = await client.post(
        "/auth/login", 
        json={"email": settings.admin_email, "password": settings.admin_password}
    )
    admin_token = admin_login.json()["access_token"]
    
    # Create the test user via admin endpoint
    await client.post(
        "/admin/users", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": "user2@example.com", "password": "password123"}
    )
    
    # Test standard login
    response = await client.post(
        "/auth/login", 
        json={"email": "user2@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

async def test_login_invalid_credentials(client):
    response = await client.post(
        "/auth/login", 
        json={"email": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == 401