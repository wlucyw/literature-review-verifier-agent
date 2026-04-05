from __future__ import annotations

import json

from app.core.schemas import ExistenceResult, ReviewCheckResult


SYSTEM_PROMPT = """You are a literature review verification judge.
- Never fabricate bibliographic metadata.
- Always prioritize retrieval evidence and rule-based results.
- If evidence is insufficient, output uncertain.
- Never rewrite correlation as causation.
- Output strict JSON only.
"""

JSON_SCHEMA_INSTRUCTION = """Return JSON only with keys:
{
  "existence_label": "...",
  "support_label": "...",
  "issue_types": [],
  "explanation": "...",
  "revision_suggestion": "..."
}
"""



def build_review_judge_prompt(review_text: str, existence_result: ExistenceResult, rule_result: ReviewCheckResult) -> str:
    payload = {
        "review_text": review_text,
        "retrieval_evidence": existence_result.model_dump(),
        "rule_result": rule_result.model_dump(),
    }
    return f"{SYSTEM_PROMPT}\n{JSON_SCHEMA_INSTRUCTION}\nInput:\n{json.dumps(payload, ensure_ascii=False)}"
