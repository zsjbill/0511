from fastapi import APIRouter
from src.common.schemas_student import APIResponse, KBSearchRequest
from src.module_student.kb_service import search_kb

router = APIRouter(prefix="/api/v1/student/kb", tags=["Student - Knowledge Base"])

@router.post("/search", response_model=APIResponse)
async def kb_search(request: KBSearchRequest):
    try:
        results = await search_kb(request.query, request.top_k)
        return APIResponse(data={"results": results, "query": request.query})
    except Exception as e:
        return APIResponse(code=500, message=str(e))
