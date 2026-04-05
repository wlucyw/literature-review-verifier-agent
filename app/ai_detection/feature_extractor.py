from __future__ import annotations

import re
from collections import Counter
from statistics import mean, pstdev
from typing import Dict, List


CONNECTORS = ["首先", "其次", "再次", "最后", "综上", "总之", "由此可见", "不难发现", "值得注意的是", "在一定程度上"]
ABSTRACT_WORDS = ["研究", "影响", "机制", "路径", "水平", "维度", "视角", "框架", "因素", "作用", "意义", "特征", "模式", "趋势"]



def split_sentences(text: str) -> List[str]:
    sentences = [segment.strip() for segment in re.split(r"[。！？!?；;\n]+", text) if segment.strip()]
    return sentences or [text.strip()]



def extract_features(text: str) -> Dict[str, float]:
    sentences = split_sentences(text)
    lengths = [len(sentence) for sentence in sentences if sentence]
    tokens = re.findall(r"[\u4e00-\u9fffA-Za-z]+", text)
    unique_tokens = {token.lower() for token in tokens}
    ngrams = Counter(tuple(tokens[i : i + 3]) for i in range(max(len(tokens) - 2, 0)))
    repeated_ngrams = sum(count for count in ngrams.values() if count > 1)

    sentence_count = len(sentences)
    avg_sentence_length = mean(lengths) if lengths else 0.0
    sentence_length_std = pstdev(lengths) if len(lengths) > 1 else 0.0
    connector_hits = sum(text.count(connector) for connector in CONNECTORS)
    abstract_hits = sum(text.count(word) for word in ABSTRACT_WORDS)

    skeletons = []
    for sentence in sentences:
        normalized = re.sub(r"\d+", "<num>", sentence)
        normalized = re.sub(r"[A-Za-z]+", "<en>", normalized)
        normalized = re.sub(r"[\u4e00-\u9fff]", "<zh>", normalized)
        skeletons.append(normalized[:60])
    skeleton_counter = Counter(skeletons)
    repeated_sentence_score = sum(count for count in skeleton_counter.values() if count > 1) / max(len(sentences), 1)

    return {
        "sentence_count": float(sentence_count),
        "avg_sentence_length": round(avg_sentence_length, 4),
        "sentence_length_std": round(sentence_length_std, 4),
        "repeated_ngram_ratio": round(repeated_ngrams / max(len(ngrams), 1), 4),
        "connector_density": round(connector_hits / max(sentence_count, 1), 4),
        "abstract_word_ratio": round(abstract_hits / max(len(tokens), 1), 4),
        "lexical_diversity": round(len(unique_tokens) / max(len(tokens), 1), 4),
        "repeated_sentence_pattern_score": round(repeated_sentence_score, 4),
    }
