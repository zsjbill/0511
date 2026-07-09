"""员工日报数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_enterprise.dbmodel.models import EmployeeDailyReport
from src.module_enterprise.pdcmodel.schemas import EmployeeDailyReportCreate, EmployeeDailyReportUpdate

__all__ = ["report_dao"]

report_dao = CRUDBase(EmployeeDailyReport, EmployeeDailyReportCreate, EmployeeDailyReportUpdate)
