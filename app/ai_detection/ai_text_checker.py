from __future__ import annotations

import json
from typing import Optional

from app.ai_detection.ai_risk_scorer import score_ai_risk
from app.ai_detection.feature_extractor import extract_features
from app.core.schemas import AIWritingCheckResult
from app.llm.base_llm import BaseLLMClient


class AITextChecker:
    def __init__(self, llm_client: Optional[BaseLLMClient] = None) -> None:
        self.llm_client = llm_client

    def check(self, review_text: str, mode: str = "rule") -> AIWritingCheckResult:
        features = extract_features(review_text)
        score, label, confidence, patterns, suggestions = score_ai_risk(features)
        result = AIWritingCheckResult(
            ai_risk_score=score,
            ai_risk_label=label,
            confidence=confidence,
            suspicious_patterns=patterns,
            humanization_suggestions=suggestions,
            features=features,
            judge_mode="rule",
        )
        if mode == "rule" or not self.llm_client:
            return result
        try:
            llm_output = json.loads(self.llm_client.generate_json(f"Return AI writing risk JSON for features: {features}"))
            return AIWritingCheckResult(
                ai_risk_score=int(llm_output["ai_risk_score"]),
                ai_risk_label=llm_output["ai_risk_label"],
                confidence=float(llm_output["confidence"]),
                suspicious_patterns=list(llm_output["suspicious_patterns"]),
                humanization_suggestions=list(llm_output["humanization_suggestions"]),
                features=features,
                judge_mode="llm",
            )
        except Exception:
            result.judge_mode = "fallback_rule"
            return result
