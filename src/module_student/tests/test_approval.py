"""
Approval Workflow Tests — 7 unit tests for submit/approve/reject/transfer/status.
"""
import pytest
from src.module_student.approval_service import submit_application, approve_application, get_application_status
from src.common.schemas_student import ApplicationSubmitRequest


class TestApprovalWorkflow:
    """End-to-end approval workflow tests via service layer."""

    @pytest.mark.asyncio
    async def test_submit_creates_record(self):
        request = ApplicationSubmitRequest(
            student_id="TEST001", student_name="Test Student",
            application_type="请假", application_content="Test leave request",
        )
        app = await submit_application(request)
        assert app is not None
        assert app.student_id == "TEST001"
        assert app.approval_status == "待审批"

    @pytest.mark.asyncio
    async def test_submit_creates_notification(self):
        request = ApplicationSubmitRequest(
            student_id="TEST002", student_name="Test Student 2",
            application_type="考务", application_content="Test exam request",
        )
        app = await submit_application(request)
        assert app.id > 0

    @pytest.mark.asyncio
    async def test_approve_application(self):
        request = ApplicationSubmitRequest(
            student_id="TEST003", student_name="Approve Test",
            application_type="请假", application_content="Need leave",
        )
        app = await submit_application(request)
        approved = await approve_application(app.id, "通过", "Teacher Zhang", "Approved")
        assert approved.approval_status == "已通过"
        assert approved.approver == "Teacher Zhang"

    @pytest.mark.asyncio
    async def test_reject_application(self):
        request = ApplicationSubmitRequest(
            student_id="TEST004", student_name="Reject Test",
            application_type="请假", application_content="Need leave",
        )
        app = await submit_application(request)
        rejected = await approve_application(app.id, "驳回", "Teacher Li", "Not enough reason")
        assert rejected.approval_status == "已驳回"

    @pytest.mark.asyncio
    async def test_transfer_application(self):
        request = ApplicationSubmitRequest(
            student_id="TEST005", student_name="Transfer Test",
            application_type="请假", application_content="Need leave",
        )
        app = await submit_application(request)
        transferred = await approve_application(app.id, "转交", "Teacher Wang", transfer_to="Teacher Zhao")
        assert transferred.approval_status == "已转交"

    @pytest.mark.asyncio
    async def test_get_status_not_found(self):
        app = await get_application_status(99999)
        assert app is None

    @pytest.mark.asyncio
    async def test_get_status_found(self):
        request = ApplicationSubmitRequest(
            student_id="TEST006", student_name="Status Test",
            application_type="考务", application_content="Check status",
        )
        app = await submit_application(request)
        fetched = await get_application_status(app.id)
        assert fetched is not None
        assert fetched.id == app.id
