"""
Tests — workflow start and status endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_start_workflow_invalid_type():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/workflows/start", json={
            "workflow_type": "invalid_type",
            "input_payload": {},
            "user_context": {"user_id": "u1", "role": "pm"},
        })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_workflow_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/workflows/does-not-exist")
    assert response.status_code == 404
