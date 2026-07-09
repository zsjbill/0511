import logging
from fastapi import APIRouter
from src.common.schemas_enterprise import APIResponse, NL2SQLRequest
from src.module_enterprise.nl2sql_engine import NL2SQLEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/enterprise/nl2sql", tags=["Enterprise - NL2SQL"])
engine = NL2SQLEngine()

@router.post("/query", response_model=APIResponse)
async def nl2sql_query(request: NL2SQLRequest):
    try:
        result = await engine.query(request.query)
        return APIResponse(data=result)
    except ValueError as e:
        return APIResponse(code=400, message=str(e))
    except Exception as e:
        logger.exception("NL2SQL error")
        return APIResponse(code=500, message=f"Internal error: {str(e)}")
