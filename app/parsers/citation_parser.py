import re
from typing import List

from app.core.schemas import CitationRecord


DOI_PATTERN = re.compile(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")



def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    if re.search(r"[A-Za-z]", text):
        return "en"
    return "unknown"



def _split_authors(author_block: str, language: str) -> List[str]:
    if not author_block:
        return []
    if language == "zh":
        parts = re.split(r"[，,、；;和与]\s*", author_block)
    else:
        parts = re.split(r"\s*(?:,|;| and )\s*", author_block)
    return [part.strip(" .") for part in parts if part.strip(" .")][:8]



def parse_citation(raw_text: str) -> CitationRecord:
    text = " ".join(raw_text.strip().split())
    language = detect_language(text)
    doi_match = DOI_PATTERN.search(text)
    doi = doi_match.group(1) if doi_match else None
    years = YEAR_PATTERN.findall(text)
    year = int(years[-1]) if years else None

    title = ""
    venue = ""
    authors: List[str] = []

    if language == "en":
        cleaned = text.replace(f"doi:{doi}", "").replace(doi or "", "").strip(" .")
        segments = [segment.strip(" .") for segment in re.split(r"\.\s+(?=[A-Z])", cleaned) if segment.strip()]
        if segments:
            authors = _split_authors(segments[0], language)
        if len(segments) >= 3:
            title = segments[1]
            venue = segments[2]
        elif len(segments) >= 2:
            title = segments[1]
        if year:
            title = title.replace(str(year), "").strip(" .")
            venue = venue.replace(str(year), "").strip(" .")
    elif language == "zh":
        title_match = re.search(r"\.\s*(.+?)\[J\]", text)
        if title_match:
            title = title_match.group(1).strip()
        else:
            segments = [segment.strip(" 。") for segment in re.split(r"[。]", text) if segment.strip()]
            if segments:
                first_parts = re.split(r"\s+", segments[0], maxsplit=1)
                if len(first_parts) > 1:
                    title = first_parts[1]
        author_block = text.split(".", 1)[0]
        authors = _split_authors(author_block, language)
        venue_match = re.search(r"\[J\]\.\s*([^,，]+)", text)
        if venue_match:
            venue = venue_match.group(1).strip()
    else:
        parts = [part.strip() for part in re.split(r"\.", text) if part.strip()]
        if len(parts) >= 2:
            authors = _split_authors(parts[0], language)
            title = parts[1]

    if not venue and year:
        venue_guess = text.rsplit(str(year), 1)[0].split(".")[-1].strip(" .,;")
        venue = venue_guess[:120]

    return CitationRecord(raw_text=raw_text, authors=authors, title=title, year=year, venue=venue, doi=doi, language=language)



def parse_references(references: List[str]) -> List[CitationRecord]:
    return [parse_citation(reference) for reference in references if reference.strip()]
