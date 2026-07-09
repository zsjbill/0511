"""学生行政服务数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_student.dbmodel.models import StudentAdminService
from src.module_student.pdcmodel.schemas import StudentAdminServiceCreate, StudentAdminServiceUpdate

admin_dao = CRUDBase(StudentAdminService, StudentAdminServiceCreate, StudentAdminServiceUpdate)
