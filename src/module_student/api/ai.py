"""学生端 AI 能力 API 端点。

提供心理风险检测、投诉摘要、营销文案生成等 AI 驱动接口。
"""

from fastapi import APIRouter
from src.module_student.pdcmodel.schemas import (
    APIResponse, RiskDetectRequest, SummarizeRequest, MarketingGenerateRequest,
)
from src.module_student.service.risk import detect_risk
from src.module_student.service.summarizer import summarize_complaint
from src.module_student.service.marketing import generate_marketing

router = APIRouter(prefix="/api/v1/student/ai", tags=["Student - AI"])

@router.post("/risk-detect", response_model=APIResponse,
             summary="心理风险检测", description="调用大模型分析学生对话内容，识别心理风险信号并返回风险级别。")
async def risk_detect(request: RiskDetectRequest):
    """检测学生对话中的心理风险信号。

    调用大模型分析对话内容，识别高/中/低风险级别。
    中高风险自动创建预警记录并通知辅导员。
    """
    try:
        result = await detect_risk(request.student_id, request.student_name, request.conversation_text)
        return APIResponse(data=result)
    except Exception as e:
        return APIResponse(code=500, message=str(e))

@router.post("/summarize", response_model=APIResponse,
             summary="投诉摘要生成", description="调用大模型对投诉文本进行摘要，提取核心问题、紧急程度和建议处理人。")
async def summarize(request: SummarizeRequest):
    """生成投诉文本的摘要信息。

    调用大模型提取投诉人、核心问题、紧急程度、
    建议处理部门和中文摘要（不超过100字）。
    """
    try:
        result = await summarize_complaint(request.complaint_text)
        return APIResponse(data=result)
    except Exception as e:
        return APIResponse(code=500, message=str(e))

@router.post("/marketing", response_model=APIResponse,
             summary="营销文案生成", description="根据学生画像生成三档（保守/适中/强力）营销文案。")
async def marketing(request: MarketingGenerateRequest):
    """根据学生画像生成个性化营销文案。

    基于学生的情绪标签、成绩、学习兴趣等信息，
    生成三档风格（保守/适中/强力）的营销推送文案，
    每版不超过100个中文字符。
    """
    try:
        result = await generate_marketing(
            request.student_id, request.student_name,
            request.emotion_tags, request.scores, request.study_interest,
        )
        return APIResponse(data=result)
    except Exception as e:
        return APIResponse(code=500, message=str(e))
