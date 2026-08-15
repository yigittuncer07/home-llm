import pytest

pytestmark = pytest.mark.asyncio

async def test_register(client):
    response = await client.post(
        "/auth/register", 
        json={"email": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "message" in response.json()

async def test_login(client):
    await client.post(
        "/auth/register", 
        json={"email": "user2@example.com", "password": "password123"}
    )
    
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

async def test_register_existing_user(client):
    await client.post(
        "/auth/register", 
        json={"email": "user3@example.com", "password": "password123"}
    )
    response = await client.post(
        "/auth/register", 
        json={"email": "user3@example.com", "password": "password123"}
    )
    assert response.status_code == 400