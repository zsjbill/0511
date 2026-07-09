"""心理健康档案数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_student.dbmodel.models import MentalHealthProfile
from src.module_student.pdcmodel.schemas import MentalHealthProfileCreate, MentalHealthProfileUpdate

mental_dao = CRUDBase(MentalHealthProfile, MentalHealthProfileCreate, MentalHealthProfileUpdate)
