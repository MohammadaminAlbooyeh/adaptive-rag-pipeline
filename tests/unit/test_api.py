import pytest
from httpx import AsyncClient
from backend.main import app


@pytest.mark.asyncio
class TestAPI:
    async def test_health(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
