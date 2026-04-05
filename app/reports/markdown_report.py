from __future__ import annotations

from app.core.schemas import VerifyResponse



def build_markdown_report(response: VerifyResponse) -> str:
    lines = [
        "# Literature Review Verifier Report",
        "",
        "## Review Text",
        "",
        response.review_text,
        "",
        "## Citation Verification Results",
        "",
    ]
    for index, item in enumerate(response.item_results, start=1):
        match = item.existence_result.best_match
        lines.extend(
            [
                f"### Citation {index}",
                f"- Raw reference: {item.citation.raw_text}",
                f"- Parsed title: {item.citation.title or 'N/A'}",
                f"- Parsed authors: {', '.join(item.citation.authors) or 'N/A'}",
                f"- Parsed year: {item.citation.year or 'N/A'}",
                f"- Language: {item.citation.language}",
                f"- Existence label: {item.existence_result.existence_label}",
                f"- Existence score: {item.existence_result.existence_score}",
                f"- Reasons: {'; '.join(item.existence_result.reasons)}",
                f"- Matched source: {match.source if match else 'N/A'}",
                f"- Matched title: {match.title if match else 'N/A'}",
                f"- Matched year: {match.year if match else 'N/A'}",
                f"- Support label: {item.review_check_result.support_label}",
                f"- Issue types: {', '.join(item.review_check_result.issue_types) or 'None'}",
                f"- Explanation: {item.review_check_result.explanation}",
                f"- Suggestion: {item.review_check_result.revision_suggestion}",
                "",
            ]
        )

    ai = response.ai_writing_check
    lines.extend(
        [
            "## AI Writing Risk Detection",
            "",
            f"- AI risk score: {ai.ai_risk_score}",
            f"- AI risk label: {ai.ai_risk_label}",
            f"- Confidence: {ai.confidence}",
            f"- Suspicious patterns: {', '.join(ai.suspicious_patterns) or 'None'}",
            f"- Humanization suggestions: {'; '.join(ai.humanization_suggestions) or 'None'}",
            "",
            "## Summary",
            "",
            f"- Total citations: {response.summary.get('total_citations', 0)}",
            f"- Likely problematic citations: {response.summary.get('problematic_citations', 0)}",
            f"- Manual review recommended: {response.summary.get('manual_review_recommended', False)}",
            "",
            "> This tool is an assistive verifier and cannot replace formal human academic review.",
        ]
    )
    return "\n".join(lines)
