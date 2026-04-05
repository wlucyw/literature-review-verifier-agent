from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from app.ai_detection.ai_text_checker import AITextChecker
from app.core.config import get_settings
from app.core.schemas import VerifyItemResult, VerifyRequest, VerifyResponse
from app.llm.dummy_llm import DummyLLMClient
from app.llm.hf_qwen_client import HFQwenClient
from app.llm.lora_qwen_client import LoRAQwenClient
from app.parsers.citation_parser import parse_references
from app.reports.excel_report import export_review_table
from app.reports.markdown_report import build_markdown_report
from app.retrievers.chinese_sources import ChinesePublicSourceClient
from app.retrievers.crossref_client import CrossrefClient
from app.retrievers.openalex_client import OpenAlexClient
from app.retrievers.semanticscholar_client import SemanticScholarClient
from app.review.review_checker import ReviewChecker
from app.routing.source_router import build_search_query, route_sources
from app.scoring.existence_scorer import choose_best_match


class VerifyService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.retrievers = {
            "openalex": OpenAlexClient(),
            "crossref": CrossrefClient(),
            "semanticscholar": SemanticScholarClient(),
            "chinese_public": ChinesePublicSourceClient(),
            "doi_fallback": CrossrefClient(),
        }

    def verify(self, request: VerifyRequest) -> VerifyResponse:
        llm_client = self._build_llm_client(request.mode)
        review_checker = ReviewChecker(llm_client=llm_client)
        ai_checker = AITextChecker(llm_client=llm_client)

        item_results: List[VerifyItemResult] = []
        for citation in parse_references(request.references):
            query = build_search_query(citation)
            candidates = []
            for source in route_sources(citation):
                candidates.extend(self.retrievers[source].search(query))
            unique_candidates = _deduplicate_candidates(candidates)
            existence_result = choose_best_match(citation, unique_candidates)
            review_result = review_checker.check(request.review_text, existence_result, mode=request.mode)
            item_results.append(
                VerifyItemResult(
                    citation=citation,
                    retrieval_candidates=unique_candidates,
                    existence_result=existence_result,
                    review_check_result=review_result,
                )
            )

        ai_result = ai_checker.check(request.review_text, mode=request.mode)
        response = VerifyResponse(
            review_text=request.review_text,
            item_results=item_results,
            ai_writing_check=ai_result,
            summary=self._build_summary(item_results, ai_result),
        )

        if request.generate_reports:
            markdown_content = build_markdown_report(response)
            response.markdown_content = markdown_content
            output_base = self.settings.report_output_dir / "verify_result"
            response.markdown_report_path = self._save_markdown(markdown_content, output_base.with_suffix(".md"))
            response.excel_report_path = export_review_table(response, output_base.with_suffix(".xlsx"))
        return response

    def _build_llm_client(self, mode: str):
        if mode == "base_llm":
            return HFQwenClient() if self.settings.llm_backend == "hf_qwen" else DummyLLMClient()
        if mode == "lora_llm":
            return LoRAQwenClient() if self.settings.llm_backend == "lora_qwen" else DummyLLMClient()
        return None

    @staticmethod
    def _build_summary(item_results: List[VerifyItemResult], ai_result) -> Dict[str, object]:
        problematic = sum(
            1
            for item in item_results
            if item.existence_result.existence_label in {"not_found", "weak_match"} or item.review_check_result.issue_types
        )
        return {
            "total_citations": len(item_results),
            "problematic_citations": problematic,
            "manual_review_recommended": problematic > 0 or ai_result.ai_risk_label != "low",
            "bilingual_support_note": {
                "status": "supported_with_asymmetric_coverage",
                "english": "English references have the strongest automated retrieval coverage via OpenAlex, Crossref, and Semantic Scholar.",
                "chinese": "Chinese references are supported in parsing and conservative rule-based checking, but public-source automated coverage is incomplete and missed hits should remain uncertain.",
            },
        }

    @staticmethod
    def _save_markdown(content: str, path: Path) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)



def _deduplicate_candidates(candidates):
    seen = set()
    unique = []
    for candidate in candidates:
        key = (candidate.source, candidate.title.lower(), candidate.year, (candidate.doi or "").lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique
