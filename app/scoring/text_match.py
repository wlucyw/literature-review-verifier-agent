import re
from collections import Counter
from typing import Iterable, List

from rapidfuzz import fuzz



def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\u4e00-\u9fff]+", " ", (text or "").lower())).strip()



def title_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return fuzz.token_sort_ratio(normalize_text(left), normalize_text(right)) / 100.0



def venue_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return fuzz.partial_ratio(normalize_text(left), normalize_text(right)) / 100.0



def author_overlap(left: Iterable[str], right: Iterable[str]) -> float:
    left_tokens = _author_tokens(left)
    right_tokens = _author_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = left_tokens & right_tokens
    union = left_tokens | right_tokens
    return len(intersection) / len(union)



def doi_match(left: str | None, right: str | None) -> float:
    if not left or not right:
        return 0.0
    return 1.0 if left.strip().lower() == right.strip().lower() else 0.0



def keyword_overlap_score(text: str, abstract: str | None) -> float:
    if not text or not abstract:
        return 0.0
    left = Counter(_keywords(text))
    right = Counter(_keywords(abstract))
    if not left or not right:
        return 0.0
    overlap = sum((left & right).values())
    base = min(sum(left.values()), sum(right.values()))
    return overlap / base if base else 0.0



def _author_tokens(authors: Iterable[str]) -> set[str]:
    tokens = set()
    for author in authors:
        normalized = normalize_text(author)
        for token in normalized.split():
            if len(token) > 1:
                tokens.add(token)
    return tokens



def _keywords(text: str) -> List[str]:
    return [token for token in normalize_text(text).split() if len(token) > 1][:100]
