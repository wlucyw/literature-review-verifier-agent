from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from app.core.schemas import VerifyResponse



def export_review_table(response: VerifyResponse, output_path: Path) -> str:
    rows: List[dict] = []
    ai = response.ai_writing_check
    for item in response.item_results:
        match = item.existence_result.best_match
        rows.append(
            {
                "raw_reference": item.citation.raw_text,
                "parsed_title": item.citation.title,
                "parsed_authors": "; ".join(item.citation.authors),
                "parsed_year": item.citation.year,
                "language": item.citation.language,
                "existence_label": item.existence_result.existence_label,
                "existence_score": item.existence_result.existence_score,
                "matched_source": match.source if match else "",
                "matched_title": match.title if match else "",
                "matched_year": match.year if match else "",
                "support_label": item.review_check_result.support_label,
                "issue_types": "; ".join(item.review_check_result.issue_types),
                "suggestion": item.review_check_result.revision_suggestion,
                "ai_risk_score": ai.ai_risk_score,
                "ai_risk_label": ai.ai_risk_label,
                "ai_suspicious_patterns": "; ".join(ai.suspicious_patterns),
                "ai_humanization_suggestions": "; ".join(ai.humanization_suggestions),
            }
        )
    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".csv":
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
    else:
        df.to_excel(output_path, index=False)
    return str(output_path)
