from typing import List

import httpx

from app.core.config import get_settings
from app.core.schemas import RetrievalCandidate, SearchQuery


class SemanticScholarClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: SearchQuery) -> List[RetrievalCandidate]:
        if not query.title and not query.doi:
            return []
        params = {
            "query": query.doi or query.title,
            "limit": self.settings.max_retrieval_candidates,
            "fields": "title,authors,year,venue,abstract,externalIds,url",
        }
        try:
            with httpx.Client(timeout=self.settings.api_timeout_seconds, headers={"User-Agent": self.settings.user_agent}) as client:
                response = client.get(self.settings.semanticscholar_base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []

        results = []
        for item in payload.get("data", [])[: self.settings.max_retrieval_candidates]:
            external_ids = item.get("externalIds", {}) or {}
            results.append(
                RetrievalCandidate(
                    source="semanticscholar",
                    title=item.get("title", ""),
                    authors=[author.get("name", "") for author in item.get("authors", []) if author.get("name")],
                    year=item.get("year"),
                    venue=item.get("venue", ""),
                    doi=external_ids.get("DOI"),
                    abstract=item.get("abstract"),
                    url=item.get("url"),
                    raw_payload=item,
                )
            )
        return results
