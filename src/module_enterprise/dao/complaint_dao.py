"""投诉反馈数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_enterprise.dbmodel.models import ComplaintFeedback
from src.module_enterprise.pdcmodel.schemas import ComplaintFeedbackCreate, ComplaintFeedbackUpdate

__all__ = ["complaint_dao"]

complaint_dao = CRUDBase(ComplaintFeedback, ComplaintFeedbackCreate, ComplaintFeedbackUpdate)
