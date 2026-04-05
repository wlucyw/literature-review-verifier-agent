import json

from app.llm.base_llm import BaseLLMClient


class DummyLLMClient(BaseLLMClient):
    def generate_json(self, prompt: str) -> str:
        if "ai_risk_score" in prompt.lower() or "AI writing risk" in prompt:
            return json.dumps(
                {
                    "ai_risk_score": 42,
                    "ai_risk_label": "medium",
                    "confidence": 0.55,
                    "suspicious_patterns": ["dummy_llm_placeholder"],
                    "humanization_suggestions": ["Use the rule-based result as the default local baseline."],
                },
                ensure_ascii=False,
            )
        return json.dumps(
            {
                "existence_label": "possible_match",
                "support_label": "uncertain",
                "issue_types": ["uncertain"],
                "explanation": "Dummy LLM output. Replace with a real model for evidence-grounded judgement.",
                "revision_suggestion": "Revise the claim conservatively and verify the original source manually.",
            },
            ensure_ascii=False,
        )
