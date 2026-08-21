import pytest
from config import settings

pytestmark = pytest.mark.asyncio

async def test_get_models_initial(client, auth_headers_factory):
    headers = await auth_headers_factory("models1@example.com")
    
    response = await client.get("/models", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    # It should return all models from settings, initialized to 0
    assert len(data) == len(settings.models_config)
    for item in data:
        assert item["model_name"] in settings.models_config
        assert item["balance"] == 0

async def test_get_models_with_balances(client, auth_headers_factory, admin_headers_factory):
    admin_headers = await admin_headers_factory()
    user_email = "models2@example.com"
    user_headers = await auth_headers_factory(user_email)
    
    # Ensure there are at least two models configured to test this properly
    configured_models = list(settings.models_config.keys())
    if len(configured_models) < 2:
        pytest.skip("Test requires at least 2 models in models.yaml")
        
    model_1, model_2 = configured_models[0], configured_models[1]
    
    users_resp = await client.get("/admin/users", headers=admin_headers)
    user_id = next(u["id"] for u in users_resp.json() if u["email"] == user_email)
    
    await client.patch(
        f"/admin/users/{user_id}/tokens",
        headers=admin_headers,
        json={"model_name": model_1, "balance": 1500}
    )
    
    await client.patch(
        f"/admin/users/{user_id}/tokens",
        headers=admin_headers,
        json={"model_name": model_2, "balance": 500}
    )
    
    response = await client.get("/models", headers=user_headers)
    assert response.status_code == 200
    
    data = response.json()
    
    # Find the specific models in the response
    m1_data = next(m for m in data if m["model_name"] == model_1)
    m2_data = next(m for m in data if m["model_name"] == model_2)
    
    assert m1_data["balance"] == 1500
    assert m2_data["balance"] == 500

async def test_get_models_unauthorized(client):
    response = await client.get("/models")
    assert response.status_code == 401