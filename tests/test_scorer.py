from app.core.schemas import CitationRecord, RetrievalCandidate, TrainingSample
from app.scoring.existence_scorer import choose_best_match



def test_scorer_distinguishes_match_quality() -> None:
    citation = CitationRecord(raw_text="x", authors=["Jean Twenge"], title="Screen time and adolescent mental health", year=2018, venue="Clinical Psychological Science", doi="10.1/abc", language="en")
    strong = RetrievalCandidate(source="crossref", authors=["Jean Twenge"], title="Screen time and adolescent mental health", year=2018, venue="Clinical Psychological Science", doi="10.1/abc")
    weak = RetrievalCandidate(source="crossref", authors=["Other Author"], title="Urban transport planning", year=2011, venue="City Journal", doi="10.1/zzz")
    strong_result = choose_best_match(citation, [strong])
    weak_result = choose_best_match(citation, [weak])
    assert strong_result.existence_score > weak_result.existence_score
    assert strong_result.existence_label in {"likely_exists", "possible_match"}
    assert weak_result.existence_label in {"weak_match", "not_found"}
