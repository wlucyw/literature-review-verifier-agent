from app.parsers.citation_parser import parse_citation



def test_parse_english_citation() -> None:
    citation = parse_citation("Smith J, Doe A. Social media and student stress. Journal of Youth Studies. 2020. doi:10.1000/test")
    assert citation.language == "en"
    assert "Social media and student stress" in citation.title
    assert citation.year == 2020
    assert citation.doi == "10.1000/test"



def test_parse_chinese_citation() -> None:
    citation = parse_citation("张三，李四. 数字平台使用与大学生心理压力关系研究[J]. 现代传播，2021.")
    assert citation.language == "zh"
    assert citation.year == 2021
    assert citation.raw_text
