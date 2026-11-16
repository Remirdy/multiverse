import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.session import init_db

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "Multiverse"
        assert "Multiple minds" in data["tagline"]

@pytest.mark.asyncio
async def test_list_models():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
        assert "default_models" in data

@pytest.mark.asyncio
async def test_route_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/route", json={"prompt": "Write a fast binary search algorithm in Python"})
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "programming"
        assert len(data["recommended_model_ids"]) > 0

@pytest.mark.asyncio
async def test_create_and_list_conversations():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        create_res = await client.post("/api/conversations", json={"title": "Test Chat"})
        assert create_res.status_code == 201
        created_data = create_res.json()
        conv_id = created_data["id"]
        assert created_data["title"] == "Test Chat"

        # List
        list_res = await client.get("/api/conversations")
        assert list_res.status_code == 200
        conv_ids = [c["id"] for c in list_res.json()]
        assert conv_id in conv_ids

        # Get detail
        get_res = await client.get(f"/api/conversations/{conv_id}")
        assert get_res.status_code == 200
        detail = get_res.json()
        assert detail["id"] == conv_id

        # Delete
        del_res = await client.delete(f"/api/conversations/{conv_id}")
        assert del_res.status_code == 204

@pytest.mark.asyncio
async def test_compare_prompt():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/compare",
            json={
                "prompt": "Hello in one word",
                "model_ids": ["poolside/laguna-xs-2.1"],
                "timeout": 15.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        res = data["results"][0]
        assert res["model_id"] == "poolside/laguna-xs-2.1"
        assert res["status"] in ["success", "timeout", "error"]
