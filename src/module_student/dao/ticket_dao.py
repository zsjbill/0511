"""售后工单数据访问层"""
from src.common.crud_base import CRUDBase
from src.module_student.dbmodel.models import AfterSalesTicket
from src.module_student.pdcmodel.schemas import AfterSalesTicketCreate, AfterSalesTicketUpdate

ticket_dao = CRUDBase(AfterSalesTicket, AfterSalesTicketCreate, AfterSalesTicketUpdate)
