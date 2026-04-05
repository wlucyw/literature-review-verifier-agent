from typing import List

import httpx

from app.core.config import get_settings
from app.core.schemas import RetrievalCandidate, SearchQuery


class OpenAlexClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: SearchQuery) -> List[RetrievalCandidate]:
        params = {"per-page": self.settings.max_retrieval_candidates, "mailto": "local@example.com"}
        if query.doi:
            params["filter"] = f"doi:{query.doi.lower()}"
        elif query.title:
            params["search"] = query.title
        else:
            return []
        try:
            with httpx.Client(timeout=self.settings.api_timeout_seconds, headers={"User-Agent": self.settings.user_agent}) as client:
                response = client.get(self.settings.openalex_base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []

        results = []
        for item in payload.get("results", [])[: self.settings.max_retrieval_candidates]:
            results.append(
                RetrievalCandidate(
                    source="openalex",
                    title=item.get("display_name", ""),
                    authors=[author.get("author", {}).get("display_name", "") for author in item.get("authorships", []) if author.get("author")],
                    year=item.get("publication_year"),
                    venue=item.get("primary_location", {}).get("source", {}).get("display_name", "") if item.get("primary_location") else "",
                    doi=(item.get("doi") or "").replace("https://doi.org/", "") or None,
                    abstract=None,
                    url=item.get("id"),
                    raw_payload=item,
                )
            )
        return results
