from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class CitationRecord(BaseModel):
    raw_text: str
    authors: List[str] = Field(default_factory=list)
    title: str = ""
    year: Optional[int] = None
    venue: str = ""
    doi: Optional[str] = None
    language: Literal["zh", "en", "unknown"] = "unknown"


class SearchQuery(BaseModel):
    title: str = ""
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    language: Literal["zh", "en", "unknown"] = "unknown"
    raw_reference: str = ""


class RetrievalCandidate(BaseModel):
    source: str
    title: str = ""
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: str = ""
    doi: Optional[str] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    score_hint: float = 0.0
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class ExistenceResult(BaseModel):
    existence_score: float = 0.0
    existence_label: Literal["likely_exists", "possible_match", "weak_match", "not_found"] = "not_found"
    reasons: List[str] = Field(default_factory=list)
    best_match: Optional[RetrievalCandidate] = None
    candidate_count: int = 0
    component_scores: Dict[str, float] = Field(default_factory=dict)


class ReviewCheckResult(BaseModel):
    support_label: Literal["supported", "partially_supported", "unsupported", "uncertain"] = "uncertain"
    issue_types: List[str] = Field(default_factory=list)
    explanation: str = ""
    revision_suggestion: str = ""
    evidence_overlap_score: float = 0.0
    judge_mode: Literal["rule", "llm", "fallback_rule"] = "rule"


class AIWritingCheckResult(BaseModel):
    ai_risk_score: int
    ai_risk_label: Literal["low", "medium", "high"]
    confidence: float
    suspicious_patterns: List[str] = Field(default_factory=list)
    humanization_suggestions: List[str] = Field(default_factory=list)
    features: Dict[str, float] = Field(default_factory=dict)
    judge_mode: Literal["rule", "llm", "fallback_rule"] = "rule"


class VerifyItemResult(BaseModel):
    citation: CitationRecord
    retrieval_candidates: List[RetrievalCandidate] = Field(default_factory=list)
    existence_result: ExistenceResult
    review_check_result: ReviewCheckResult


class VerifyRequest(BaseModel):
    review_text: str
    references: List[str]
    mode: Literal["rule", "base_llm", "lora_llm"] = "rule"
    generate_reports: bool = True


class VerifyResponse(BaseModel):
    review_text: str
    item_results: List[VerifyItemResult]
    ai_writing_check: AIWritingCheckResult
    markdown_content: Optional[str] = None
    markdown_report_path: Optional[str] = None
    excel_report_path: Optional[str] = None
    summary: Dict[str, Any] = Field(default_factory=dict)


class TrainingSample(BaseModel):
    instruction: str
    input: Dict[str, Any]
    output: Dict[str, Any]


class LLMJudgementOutput(BaseModel):
    existence_label: Literal["likely_exists", "possible_match", "weak_match", "not_found"]
    support_label: Literal["supported", "partially_supported", "unsupported", "uncertain"]
    issue_types: List[str] = Field(default_factory=list)
    explanation: str
    revision_suggestion: str
