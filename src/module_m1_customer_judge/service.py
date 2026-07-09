"""
M1: Customer Judge — Core business logic.
"""
import logging

from src.common.schemas import CustomerJudgeRequest, CustomerJudgeResponse
from src.module_m1_customer_judge.rule_engine import RuleEngine

logger = logging.getLogger(__name__)
rule_engine = RuleEngine()


async def judge_customer(request: CustomerJudgeRequest) -> CustomerJudgeResponse:
    """
    Analyze customer profile against rules and return score + recommendation.
    """
    # Extract features
    features = {
        "source": request.source,
        "has_phone": bool(request.phone),
        "has_wechat": bool(request.wechat),
        "extra": request.extra_info or {},
    }

    # Run rule engine
    score = rule_engine.calculate_score(features)
    tags = rule_engine.match_tags(features)
    recommendation = rule_engine.recommend(score, tags)

    return CustomerJudgeResponse(
        profile_score=score,
        tags=tags,
        recommended_service=recommendation.get("service"),
        match_reason=recommendation.get("reason", "基于画像规则匹配"),
    )
