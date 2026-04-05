from app.ai_detection.ai_text_checker import AITextChecker



def test_ai_detection_fields_present() -> None:
    result = AITextChecker().check("首先，本研究从多个维度展开分析。其次，研究机制与路径具有重要意义。综上，研究框架与模式值得注意。")
    assert isinstance(result.ai_risk_score, int)
    assert result.ai_risk_label in {"low", "medium", "high"}
    assert "sentence_count" in result.features



def test_template_text_risk_higher_than_natural_text() -> None:
    checker = AITextChecker()
    templated = "首先，研究从多个维度展开。其次，研究从多个维度展开。再次，研究从多个维度展开。最后，综上所述，该研究具有重要意义。"
    natural = "访谈里有些学生提到，自己刷短视频后会分心，但也有人说那只是放松方式，影响并不一致。"
    assert checker.check(templated).ai_risk_score > checker.check(natural).ai_risk_score
