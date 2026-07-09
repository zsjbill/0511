"""心理预警数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_student.dbmodel.models import PsychologicalAlert
from src.module_student.pdcmodel.schemas import PsychologicalAlertCreate, PsychologicalAlertUpdate

alert_dao = CRUDBase(PsychologicalAlert, PsychologicalAlertCreate, PsychologicalAlertUpdate)
