"""
CRUD Integration Tests — 8 endpoints across enterprise and student modules.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


class TestEnterpriseCRUD:
    """Enterprise module CRUD list endpoint tests."""

    @pytest.mark.asyncio
    async def test_list_customers(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/enterprise/customers?page=1&page_size=5")
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert "items" in data["data"]

    @pytest.mark.asyncio
    async def test_list_reports(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/enterprise/reports?page=1&page_size=5")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_complaints(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/enterprise/complaints?page=1&page_size=5")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_scores(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/enterprise/scores?page=1&page_size=5")
            assert response.status_code == 200


class TestStudentCRUD:
    """Student module CRUD list endpoint tests."""

    @pytest.mark.asyncio
    async def test_list_admin_services(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/student/admin-services?page=1&page_size=5")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_mental_health(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/student/mental-health?page=1&page_size=5")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_alerts(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/student/alerts?page=1&page_size=5")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_tickets(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/student/tickets?page=1&page_size=5")
            assert response.status_code == 200
