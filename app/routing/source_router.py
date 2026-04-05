from typing import List

from app.core.schemas import CitationRecord, SearchQuery



def build_search_query(citation: CitationRecord) -> SearchQuery:
    return SearchQuery(
        title=citation.title,
        authors=citation.authors,
        year=citation.year,
        doi=citation.doi,
        language=citation.language,
        raw_reference=citation.raw_text,
    )



def route_sources(citation: CitationRecord) -> List[str]:
    if citation.language == "zh":
        sources = ["chinese_public", "doi_fallback"]
    else:
        sources = ["openalex", "crossref", "semanticscholar"]
    if citation.doi and "crossref" not in sources:
        sources.append("crossref")
    return sources
