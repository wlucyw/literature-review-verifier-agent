from typing import List

from app.core.schemas import CitationRecord, ExistenceResult, RetrievalCandidate
from app.scoring.text_match import author_overlap, doi_match, title_similarity, venue_similarity



def score_candidate(citation: CitationRecord, candidate: RetrievalCandidate) -> ExistenceResult:
    title_score = title_similarity(citation.title, candidate.title)
    author_score = author_overlap(citation.authors, candidate.authors)
    year_score = 1.0 if citation.year and candidate.year and citation.year == candidate.year else 0.0
    venue_score = venue_similarity(citation.venue, candidate.venue)
    doi_score = doi_match(citation.doi, candidate.doi)

    existence_score = 0.45 * title_score + 0.20 * author_score + 0.15 * year_score + 0.10 * venue_score + 0.10 * doi_score
    reasons = [
        "标题高度相似" if title_score >= 0.85 else "标题相似度有限" if title_score >= 0.5 else "标题不匹配",
        "作者部分匹配" if author_score >= 0.3 else "作者匹配较弱",
        "年份一致" if year_score == 1.0 else "年份不一致或缺失",
        "venue 基本一致" if venue_score >= 0.7 else "venue 不一致",
        "DOI 一致" if doi_score == 1.0 else "DOI 缺失或不一致",
    ]

    if candidate.source == "chinese_public" and not candidate.doi and not candidate.url:
        existence_score *= 0.4
        reasons.append("中文占位 provider 仅提供保守线索，不能视为强存在证据")

    if existence_score >= 0.8:
        label = "likely_exists"
    elif existence_score >= 0.6:
        label = "possible_match"
    elif existence_score >= 0.35:
        label = "weak_match"
    else:
        label = "not_found"

    return ExistenceResult(
        existence_score=round(existence_score, 4),
        existence_label=label,
        reasons=reasons,
        best_match=candidate,
        candidate_count=1,
        component_scores={
            "title_similarity": round(title_score, 4),
            "author_overlap": round(author_score, 4),
            "year_match": round(year_score, 4),
            "venue_similarity": round(venue_score, 4),
            "doi_match": round(doi_score, 4),
        },
    )



def choose_best_match(citation: CitationRecord, candidates: List[RetrievalCandidate]) -> ExistenceResult:
    if not candidates:
        return ExistenceResult(existence_score=0.0, existence_label="not_found", reasons=["未检索到候选结果"], best_match=None, candidate_count=0, component_scores={})
    scored = [score_candidate(citation, candidate) for candidate in candidates]
    best = max(scored, key=lambda item: item.existence_score)
    best.candidate_count = len(candidates)
    if citation.language == "zh" and best.existence_label == "not_found":
        best.reasons.append("中文公开资源覆盖有限，建议保守人工复核")
    return best
