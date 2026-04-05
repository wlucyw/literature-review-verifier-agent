# API Examples

## Overview
This document provides copy-ready request and response examples for the `POST /verify` endpoint.

Base URL for local development:
```text
http://127.0.0.1:8000
```

Start the API first:
```bash
uvicorn app.main:app --reload
```

---

## Example 1: Rule-Based Verification

### Request
```bash
curl -X POST "http://127.0.0.1:8000/verify" ^
  -H "Content-Type: application/json" ^
  -d "{\"review_text\":\"Twenge et al. discussed associations between screen time and adolescent mental health, but the evidence is correlational rather than strictly causal.\",\"references\":[\"Twenge J M, Joiner T E, Rogers M L, Martin G N. Increases in depressive symptoms, suicide-related outcomes, and suicide rates among U.S. adolescents after 2010 and links to increased new media screen time. Clinical Psychological Science. 2018. doi:10.1177/2167702617723376\",\"张三，李四. 数字平台使用与大学生心理压力关系研究[J]. 现代传播，2021.\"],\"mode\":\"rule\",\"generate_reports\":true}"
```

### Request Body
```json
{
  "review_text": "Twenge et al. discussed associations between screen time and adolescent mental health, but the evidence is correlational rather than strictly causal.",
  "references": [
    "Twenge J M, Joiner T E, Rogers M L, Martin G N. Increases in depressive symptoms, suicide-related outcomes, and suicide rates among U.S. adolescents after 2010 and links to increased new media screen time. Clinical Psychological Science. 2018. doi:10.1177/2167702617723376",
    "张三，李四. 数字平台使用与大学生心理压力关系研究[J]. 现代传播，2021."
  ],
  "mode": "rule",
  "generate_reports": true
}
```

### Response Excerpt
```json
{
  "review_text": "Twenge et al. discussed associations between screen time and adolescent mental health, but the evidence is correlational rather than strictly causal.",
  "item_results": [
    {
      "citation": {
        "raw_text": "Twenge J M, Joiner T E, Rogers M L, Martin G N. ...",
        "authors": ["Twenge J M", "Joiner T E", "Rogers M L", "Martin G N"],
        "title": "Increases in depressive symptoms, suicide-related outcomes, and suicide rates among U.S. adolescents after 2010 and links to increased new media screen time",
        "year": 2018,
        "venue": "Clinical Psychological Science",
        "doi": "10.1177/2167702617723376",
        "language": "en"
      },
      "existence_result": {
        "existence_score": 0.84,
        "existence_label": "likely_exists",
        "reasons": ["标题高度相似", "作者部分匹配", "年份一致", "venue 基本一致", "DOI 一致"]
      },
      "review_check_result": {
        "support_label": "partially_supported",
        "issue_types": ["uncertain"],
        "explanation": "The claim stays close to correlation-oriented evidence, but further manual review is still recommended.",
        "revision_suggestion": "Keep causal language conservative and cite the evidence boundary explicitly."
      }
    }
  ],
  "ai_writing_check": {
    "ai_risk_score": 28,
    "ai_risk_label": "low",
    "confidence": 0.56,
    "suspicious_patterns": [],
    "humanization_suggestions": ["当前文本未见明显模板化风险，但仍建议结合人工风格校对。"]
  },
  "summary": {
    "total_citations": 2,
    "problematic_citations": 1,
    "manual_review_recommended": true,
    "bilingual_support_note": {
      "status": "supported_with_asymmetric_coverage",
      "english": "English references have the strongest automated retrieval coverage via OpenAlex, Crossref, and Semantic Scholar.",
      "chinese": "Chinese references are supported in parsing and conservative rule-based checking, but public-source automated coverage is incomplete and missed hits should remain uncertain."
    }
  }
}
```

---

## Example 2: Minimal Request

### Request Body
```json
{
  "review_text": "The cited paper reports an association between social media use and stress among college students.",
  "references": [
    "Smith A. Social media and stress in college students. Journal of Youth Studies. 2020."
  ],
  "mode": "rule",
  "generate_reports": false
}
```

### Response Shape
```json
{
  "review_text": "...",
  "item_results": [
    {
      "citation": {...},
      "retrieval_candidates": [...],
      "existence_result": {...},
      "review_check_result": {...}
    }
  ],
  "ai_writing_check": {
    "ai_risk_score": 0,
    "ai_risk_label": "low|medium|high",
    "confidence": 0.0,
    "suspicious_patterns": [],
    "humanization_suggestions": [],
    "features": {},
    "judge_mode": "rule|llm|fallback_rule"
  },
  "markdown_content": null,
  "markdown_report_path": null,
  "excel_report_path": null,
  "summary": {}
}
```

---

## Example 3: Bilingual Note Interpretation

The API intentionally surfaces a bilingual support note in `summary`:

```json
{
  "bilingual_support_note": {
    "status": "supported_with_asymmetric_coverage",
    "english": "English references have the strongest automated retrieval coverage via OpenAlex, Crossref, and Semantic Scholar.",
    "chinese": "Chinese references are supported in parsing and conservative rule-based checking, but public-source automated coverage is incomplete and missed hits should remain uncertain."
  }
}
```

Interpretation:
- English metadata verification is currently stronger.
- Chinese parsing and conservative checking are supported.
- Chinese misses should usually be read as `uncertain`, not immediately treated as fabricated references.

---

## 中文说明

### 示例 1：规则模式核验

#### 请求体
```json
{
  "review_text": "Twenge 等人的研究讨论了屏幕时间与青少年心理健康之间的关联，但这类证据更接近相关关系，而不是严格因果。",
  "references": [
    "Twenge J M, Joiner T E, Rogers M L, Martin G N. Increases in depressive symptoms, suicide-related outcomes, and suicide rates among U.S. adolescents after 2010 and links to increased new media screen time. Clinical Psychological Science. 2018. doi:10.1177/2167702617723376",
    "张三，李四. 数字平台使用与大学生心理压力关系研究[J]. 现代传播，2021."
  ],
  "mode": "rule",
  "generate_reports": true
}
```

#### 返回片段
```json
{
  "item_results": [
    {
      "existence_result": {
        "existence_label": "likely_exists"
      },
      "review_check_result": {
        "support_label": "partially_supported"
      }
    },
    {
      "existence_result": {
        "existence_label": "not_found"
      },
      "review_check_result": {
        "support_label": "uncertain",
        "issue_types": ["uncertain"]
      }
    }
  ],
  "summary": {
    "manual_review_recommended": true,
    "bilingual_support_note": {
      "status": "supported_with_asymmetric_coverage"
    }
  }
}
```

### 如何理解返回结果
- `existence_label` 用于判断文献是否可能真实存在。
- `support_label` 用于判断综述表述是否被当前证据支持。
- `issue_types` 用于指出具体风险类型，比如 `fabricated_reference`、`irrelevant_reference`、`causal_overstatement`、`uncertain`。
- `ai_writing_check` 用于提示 AI 写作痕迹风险，而不是作者身份鉴定。
- `summary.bilingual_support_note` 用于提醒调用方：当前英文自动核验覆盖强于中文，中文未命中时应优先保守处理。
