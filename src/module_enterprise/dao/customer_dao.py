"""意向客户数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_enterprise.dbmodel.models import IntentCustomer
from src.module_enterprise.pdcmodel.schemas import IntentCustomerCreate, IntentCustomerUpdate

__all__ = ["customer_dao"]

customer_dao = CRUDBase(IntentCustomer, IntentCustomerCreate, IntentCustomerUpdate)
