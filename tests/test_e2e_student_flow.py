"""
E2E Test: Full Approval Flow — submit -> approve -> status -> notification
"""
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


class TestE2EApprovalFlow:
    """End-to-end approval workflow via HTTP API."""

    @pytest.mark.asyncio
    async def test_full_approval_flow(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Step 1: Student submits application
            submit_resp = await client.post("/api/v1/student/application/submit", json={
                "student_id": "E2E001", "student_name": "E2E Test Student",
                "application_type": "请假", "application_content": "E2E test leave request",
            })
            assert submit_resp.status_code == 201
            app_data = submit_resp.json()["data"]
            app_id = app_data["id"]
            assert app_data["approval_status"] == "待审批"

            # Step 2: Teacher approves
            approve_resp = await client.post("/api/v1/student/application/approve", json={
                "application_id": app_id, "action": "通过",
                "approver": "Teacher E2E", "comment": "E2E approved",
            })
            assert approve_resp.status_code == 200
            assert approve_resp.json()["data"]["approval_status"] == "已通过"

            # Step 3: Verify status
            status_resp = await client.get(f"/api/v1/student/application/{app_id}/status")
            assert status_resp.status_code == 200
            assert status_resp.json()["data"]["approval_status"] == "已通过"

            # Step 4: Verify notification for student
            notif_resp = await client.get("/api/v1/student/notifications/pending", params={
                "recipient_id": "E2E001", "recipient_type": "student",
            })
            assert notif_resp.status_code == 200
            notifications = notif_resp.json()["data"]["notifications"]
            assert any(n["type"] == "approval_result" for n in notifications)

    @pytest.mark.asyncio
    async def test_health_check(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
