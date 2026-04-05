from __future__ import annotations

import json
from typing import List, Optional

from app.core.schemas import ExistenceResult, LLMJudgementOutput, ReviewCheckResult
from app.llm.base_llm import BaseLLMClient
from app.llm.prompts import build_review_judge_prompt
from app.scoring.text_match import keyword_overlap_score


CAUSAL_WORDS = ["证明", "显著导致", "决定了", "必然导致", "直接导致", "cause", "caused", "proves", "determine"]
ASSOCIATION_WORDS = ["association", "relation", "correlation", "linked", "associated", "影响", "关联", "相关"]
OVERCLAIM_WORDS = ["普遍认为", "一致证明", "完全说明", "明确表明", "all studies", "definitely", "clearly proves"]


class ReviewChecker:
    def __init__(self, llm_client: Optional[BaseLLMClient] = None) -> None:
        self.llm_client = llm_client

    def check(self, review_text: str, existence_result: ExistenceResult, mode: str = "rule") -> ReviewCheckResult:
        rule_result = self._rule_check(review_text, existence_result)
        if mode == "rule" or not self.llm_client:
            return rule_result

        try:
            prompt = build_review_judge_prompt(review_text, existence_result, rule_result)
            llm_output = self.llm_client.generate_json(prompt)
            parsed = LLMJudgementOutput.model_validate(json.loads(llm_output))
            return ReviewCheckResult(
                support_label=parsed.support_label,
                issue_types=parsed.issue_types,
                explanation=parsed.explanation,
                revision_suggestion=parsed.revision_suggestion,
                evidence_overlap_score=rule_result.evidence_overlap_score,
                judge_mode="llm",
            )
        except Exception:
            rule_result.judge_mode = "fallback_rule"
            return rule_result

    def _rule_check(self, review_text: str, existence_result: ExistenceResult) -> ReviewCheckResult:
        issues: List[str] = []
        best_match = existence_result.best_match
        evidence_text = " ".join(
            part for part in [best_match.title if best_match else "", best_match.abstract if best_match else "", best_match.venue if best_match else ""] if part
        )
        overlap = keyword_overlap_score(review_text, evidence_text)

        if existence_result.existence_label == "not_found":
            issue = "uncertain" if "中文公开资源覆盖有限" in " ".join(existence_result.reasons) else "fabricated_reference"
            explanation = "未找到足够文献证据，当前仅能保守判断为需人工复核。" if issue == "uncertain" else "未检索到可信候选，存在疑似虚构引用风险。"
            return ReviewCheckResult(
                support_label="uncertain" if issue == "uncertain" else "unsupported",
                issue_types=[issue],
                explanation=explanation,
                revision_suggestion="补充 DOI、期刊信息或原始文献链接，并改写为更保守的描述。",
                evidence_overlap_score=round(overlap, 4),
            )

        if overlap < 0.12:
            issues.append("irrelevant_reference")
        if any(word in review_text for word in CAUSAL_WORDS) and any(word in evidence_text for word in ASSOCIATION_WORDS):
            issues.append("causal_overstatement")
        if any(word in review_text for word in OVERCLAIM_WORDS) and overlap < 0.3:
            issues.append("overclaim")
        if overlap < 0.08:
            issues.append("claim_not_supported")

        if existence_result.existence_label in {"weak_match", "possible_match"}:
            component_scores = existence_result.component_scores
            if component_scores.get("title_similarity", 0.0) > 0.75 and component_scores.get("year_match", 0.0) == 0.0:
                issues.append("mismatched_metadata")

        issues = list(dict.fromkeys(issues))
        if not issues and overlap >= 0.25:
            return ReviewCheckResult(
                support_label="supported",
                issue_types=[],
                explanation="综述表述与检索到的标题或摘要关键词有较高重合，暂未发现明显问题。",
                revision_suggestion="保留当前表述，可在需要时补充更具体的研究边界。",
                evidence_overlap_score=round(overlap, 4),
            )

        if "claim_not_supported" in issues or "irrelevant_reference" in issues:
            support_label = "unsupported"
        elif any(issue in issues for issue in ["causal_overstatement", "overclaim", "mismatched_metadata"]):
            support_label = "partially_supported"
        else:
            support_label = "uncertain"

        return ReviewCheckResult(
            support_label=support_label,
            issue_types=issues or ["uncertain"],
            explanation=f"规则系统检测到的问题包括：{', '.join(issues or ['uncertain'])}。证据关键词重合度为 {overlap:.2f}。",
            revision_suggestion=_build_revision_suggestion(issues),
            evidence_overlap_score=round(overlap, 4),
        )



def _build_revision_suggestion(issues: List[str]) -> str:
    if "causal_overstatement" in issues:
        return "将因果表述改为“相关”“关联”或“可能影响”，避免超出文献证据强度。"
    if "irrelevant_reference" in issues:
        return "替换为与当前论点主题更贴近的文献，或缩小该句主张范围。"
    if "mismatched_metadata" in issues:
        return "核对作者、年份、题名和 DOI，并在修订前确认引用条目是否对应同一篇论文。"
    if "fabricated_reference" in issues:
        return "删除该引用或补充可核验的元数据与访问链接。"
    return "将表述调整为更保守的结论，并补充原始证据或更多高相关文献。"
