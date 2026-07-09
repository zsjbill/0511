"""学生成绩数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_enterprise.dbmodel.models import StudentScore
from src.module_enterprise.pdcmodel.schemas import StudentScoreCreate, StudentScoreUpdate

__all__ = ["score_dao"]

score_dao = CRUDBase(StudentScore, StudentScoreCreate, StudentScoreUpdate)
