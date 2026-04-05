from typing import Dict, List, Tuple



def score_ai_risk(features: Dict[str, float]) -> Tuple[int, str, float, List[str], List[str]]:
    score = 0.0
    patterns: List[str] = []
    suggestions: List[str] = []

    if features["connector_density"] >= 0.8:
        score += 18
        patterns.append("模板化连接词密度较高")
        suggestions.append("减少“首先、其次、综上”等模板化串联，改为更具体的逻辑转折。")
    if features["abstract_word_ratio"] >= 0.12:
        score += 15
        patterns.append("抽象学术词比例偏高")
        suggestions.append("增加具体研究对象、变量、样本和边界条件。")
    if features["repeated_ngram_ratio"] >= 0.18:
        score += 18
        patterns.append("重复短语较多")
        suggestions.append("替换重复措辞，避免句式和词组反复出现。")
    if features["lexical_diversity"] <= 0.45:
        score += 14
        patterns.append("词汇多样性偏低")
        suggestions.append("用更具体的术语替换高频泛化词汇。")
    if features["sentence_length_std"] <= 6.0 and features["sentence_count"] >= 4:
        score += 12
        patterns.append("句长波动较小，整体节奏较机械")
        suggestions.append("调整长短句搭配，避免每句结构过于整齐。")
    if features["repeated_sentence_pattern_score"] >= 0.3:
        score += 16
        patterns.append("句式骨架重复度较高")
        suggestions.append("改写相邻句结构，加入更自然的人类表达差异。")
    if features["avg_sentence_length"] >= 38:
        score += 10
        patterns.append("平均句长偏长")
        suggestions.append("拆分过长句子，保留关键论断。")

    score = max(0, min(100, int(round(score))))
    label = "high" if score >= 65 else "medium" if score >= 35 else "low"
    confidence = round(min(0.95, 0.45 + score / 100 * 0.4), 4)
    if not patterns:
        suggestions.append("当前文本未见明显模板化风险，但仍建议结合人工风格校对。")
    return score, label, confidence, patterns, suggestions
