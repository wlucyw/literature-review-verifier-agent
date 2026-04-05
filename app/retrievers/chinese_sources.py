from typing import List

from app.core.schemas import RetrievalCandidate, SearchQuery


class ChinesePublicSourceClient:
    def search(self, query: SearchQuery) -> List[RetrievalCandidate]:
        note = (
            "Chinese public-source coverage is incomplete. Please manually verify via DOI, publisher page, "
            "institutional repository, or open public portals when automated retrieval misses a record."
        )
        return [
            RetrievalCandidate(
                source="chinese_public",
                title=query.title,
                authors=query.authors,
                year=query.year,
                venue="",
                doi=query.doi,
                abstract=None,
                url=None,
                score_hint=0.2 if query.doi else 0.0,
                raw_payload={"note": note, "raw_reference": query.raw_reference},
            )
        ]
