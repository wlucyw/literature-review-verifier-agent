from typing import List

import httpx

from app.core.config import get_settings
from app.core.schemas import RetrievalCandidate, SearchQuery


class CrossrefClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: SearchQuery) -> List[RetrievalCandidate]:
        params = {"rows": self.settings.max_retrieval_candidates}
        if query.doi:
            url = f"{self.settings.crossref_base_url}/{query.doi}"
            try:
                with httpx.Client(timeout=self.settings.api_timeout_seconds, headers={"User-Agent": self.settings.user_agent}) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    message = response.json().get("message", {})
            except Exception:
                return []
            return [self._convert(message)]

        if not query.title:
            return []
        params["query.title"] = query.title
        try:
            with httpx.Client(timeout=self.settings.api_timeout_seconds, headers={"User-Agent": self.settings.user_agent}) as client:
                response = client.get(self.settings.crossref_base_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception:
            return []
        return [self._convert(item) for item in payload.get("message", {}).get("items", [])[: self.settings.max_retrieval_candidates]]

    @staticmethod
    def _convert(item: dict) -> RetrievalCandidate:
        authors = []
        for author in item.get("author", []):
            name = " ".join(part for part in [author.get("given"), author.get("family")] if part)
            if name:
                authors.append(name)
        title = item.get("title", [""])
        venue = item.get("container-title", [""])
        published = item.get("published-print") or item.get("published-online") or item.get("issued") or {}
        date_parts = published.get("date-parts", [[None]])
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        return RetrievalCandidate(
            source="crossref",
            title=title[0] if title else "",
            authors=authors,
            year=year,
            venue=venue[0] if venue else "",
            doi=item.get("DOI"),
            abstract=item.get("abstract"),
            url=item.get("URL"),
            raw_payload=item,
        )
