import pytest

pytestmark = pytest.mark.asyncio

async def test_get_models_initial(client, auth_headers_factory):
    headers = await auth_headers_factory("models1@example.com")
    
    response = await client.get("/models", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

async def test_get_models_with_balances(client, auth_headers_factory, admin_headers_factory):
    admin_headers = await admin_headers_factory()
    user_email = "models2@example.com"
    user_headers = await auth_headers_factory(user_email)
    
    # Retrieve user ID to assign tokens
    users_resp = await client.get("/admin/users", headers=admin_headers)
    user_id = next(u["id"] for u in users_resp.json() if u["email"] == user_email)
    
    # Assign tokens via admin endpoint
    await client.patch(
        f"/admin/users/{user_id}/tokens",
        headers=admin_headers,
        json={"model_name": "qwen", "balance": 1500}
    )
    
    await client.patch(
        f"/admin/users/{user_id}/tokens",
        headers=admin_headers,
        json={"model_name": "llama3", "balance": 500}
    )
    
    # Test the models endpoint for the standard user
    response = await client.get("/models", headers=user_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Sort for consistent assertion
    data_sorted = sorted(data, key=lambda x: x["model_name"])
    assert data_sorted[0] == {"model_name": "llama3", "balance": 500}
    assert data_sorted[1] == {"model_name": "qwen", "balance": 1500}

async def test_get_models_unauthorized(client):
    response = await client.get("/models")
    assert response.status_code == 401