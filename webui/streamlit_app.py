from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.schemas import VerifyRequest
from app.services.verify_service import VerifyService


service = VerifyService()
st.set_page_config(page_title="Literature Review Verifier", layout="wide")

STATUS_COLORS = {
    "likely_exists": ("#d1fae5", "#065f46"),
    "possible_match": ("#fef3c7", "#92400e"),
    "weak_match": ("#fde68a", "#92400e"),
    "not_found": ("#fee2e2", "#991b1b"),
    "supported": ("#d1fae5", "#065f46"),
    "partially_supported": ("#fef3c7", "#92400e"),
    "unsupported": ("#fee2e2", "#991b1b"),
    "uncertain": ("#e5e7eb", "#374151"),
    "low": ("#d1fae5", "#065f46"),
    "medium": ("#fef3c7", "#92400e"),
    "high": ("#fee2e2", "#991b1b"),
    "fabricated_reference": ("#fee2e2", "#991b1b"),
    "mismatched_metadata": ("#fef3c7", "#92400e"),
    "irrelevant_reference": ("#fde68a", "#92400e"),
    "overclaim": ("#fde68a", "#92400e"),
    "causal_overstatement": ("#fee2e2", "#991b1b"),
    "claim_not_supported": ("#fee2e2", "#991b1b"),
}

ISSUE_LABELS = {
    "fabricated_reference": "fabricated_reference / 疑似虚构引用",
    "mismatched_metadata": "mismatched_metadata / 元数据错配",
    "irrelevant_reference": "irrelevant_reference / 文献可能不相关",
    "overclaim": "overclaim / 综述过度概括",
    "causal_overstatement": "causal_overstatement / 因果夸大",
    "claim_not_supported": "claim_not_supported / 结论支撑不足",
    "uncertain": "uncertain / 证据不足需复核",
    "None": "None / 无",
}

PRIORITY = {
    "not_found": 0,
    "weak_match": 1,
    "possible_match": 2,
    "likely_exists": 3,
    "unsupported": 0,
    "uncertain": 1,
    "partially_supported": 2,
    "supported": 3,
}

RISK_ICON = {0: "[HIGH]", 1: "[MED]", 2: "[LOW]", 3: "[OK]"}

ZH_EXPORT_COLUMNS = {
    "raw_reference": "原始引用",
    "parsed_title": "解析标题",
    "parsed_authors": "解析作者",
    "parsed_year": "解析年份",
    "language": "语言",
    "existence_label": "存在性标签",
    "existence_score": "存在性分数",
    "matched_source": "匹配来源",
    "matched_title": "匹配标题",
    "matched_year": "匹配年份",
    "support_label": "支撑性标签",
    "issue_types": "问题类型",
    "suggestion": "修改建议",
    "ai_risk_score": "AI风险分数",
    "ai_risk_label": "AI风险等级",
    "ai_suspicious_patterns": "AI可疑模式",
    "ai_humanization_suggestions": "AI修改建议",
}


def status_badge(label: str, display: str | None = None) -> str:
    bg, fg = STATUS_COLORS.get(label, ("#e5e7eb", "#374151"))
    text = display or label
    return (
        f"<span style='display:inline-block;padding:0.2rem 0.6rem;border-radius:999px;"
        f"background:{bg};color:{fg};font-weight:700;font-size:0.9rem;margin-right:0.35rem;margin-bottom:0.35rem;'>"
        f"{text}</span>"
    )



def build_export_dataframe(response) -> pd.DataFrame:
    rows = []
    ai = response.ai_writing_check
    for item in response.item_results:
        match = item.existence_result.best_match
        rows.append(
            {
                "raw_reference": item.citation.raw_text,
                "parsed_title": item.citation.title,
                "parsed_authors": "; ".join(item.citation.authors),
                "parsed_year": item.citation.year,
                "language": item.citation.language,
                "existence_label": item.existence_result.existence_label,
                "existence_score": item.existence_result.existence_score,
                "matched_source": match.source if match else "",
                "matched_title": match.title if match else "",
                "matched_year": match.year if match else "",
                "support_label": item.review_check_result.support_label,
                "issue_types": "; ".join(item.review_check_result.issue_types),
                "suggestion": item.review_check_result.revision_suggestion,
                "ai_risk_score": ai.ai_risk_score,
                "ai_risk_label": ai.ai_risk_label,
                "ai_suspicious_patterns": "; ".join(ai.suspicious_patterns),
                "ai_humanization_suggestions": "; ".join(ai.humanization_suggestions),
            }
        )
    return pd.DataFrame(rows)


st.title("Literature Review Verifier Agent / 文献综述审核智能体")
st.caption("Assistive verification only. This demo does not replace formal human academic review. 该工具仅用于辅助核验，不能替代正式人工学术审查。")

with st.expander("Bilingual Support / 双语支持说明", expanded=True):
    st.markdown(
        """
This demo supports both English and Chinese input, but the automated coverage is intentionally asymmetric.

- English: stronger automated metadata verification through OpenAlex, Crossref, and Semantic Scholar.
- Chinese: supported in parsing, routing, conservative rule-based checking, and AI writing risk detection.
- For Chinese references that are not matched automatically, the system is designed to prefer `uncertain` instead of making an aggressive fake-reference judgement.

本 Demo 支持中英文输入，但自动核验能力是刻意做成“非对称”的。

- 英文：自动元数据检索链路更完整，核验能力更强。
- 中文：支持解析、路由、保守规则判断和 AI 写作风险检测。
- 中文文献如果自动未命中，系统会优先输出 `uncertain`，而不是激进地判定为虚构文献。
"""
    )

sample_path = ROOT_DIR / "data" / "samples" / "sample_input.json"
sample_data = json.loads(sample_path.read_text(encoding="utf-8-sig")) if sample_path.exists() else {"review_text": "", "references": []}

review_text = st.text_area("Review Text / 综述文本", value=sample_data.get("review_text", ""), height=220)
references_text = st.text_area("References (one per line) / 参考文献（每行一条）", value="\n".join(sample_data.get("references", [])), height=220)
mode = st.selectbox("Mode / 模式", options=["rule", "base_llm", "lora_llm"], index=0)

if st.button("Verify / 开始核验", type="primary"):
    references = [line.strip() for line in references_text.splitlines() if line.strip()]
    response = service.verify(VerifyRequest(review_text=review_text, references=references, mode=mode, generate_reports=True))

    enriched_rows = []
    for idx, item in enumerate(response.item_results, start=1):
        match = item.existence_result.best_match
        issues = item.review_check_result.issue_types or []
        existence_priority = PRIORITY.get(item.existence_result.existence_label, 9)
        support_priority = PRIORITY.get(item.review_check_result.support_label, 9)
        enriched_rows.append(
            {
                "index": idx,
                "priority": (existence_priority, support_priority, item.existence_result.existence_score),
                "risk_level": min(existence_priority, support_priority),
                "language": item.citation.language,
                "parsed_title": item.citation.title,
                "parsed_year": item.citation.year,
                "existence_label": item.existence_result.existence_label,
                "existence_score": item.existence_result.existence_score,
                "support_label": item.review_check_result.support_label,
                "issue_types": issues,
                "issue_types_text": " | ".join(ISSUE_LABELS.get(issue, issue) for issue in issues) if issues else "None / 无",
                "matched_source": match.source if match else "",
                "matched_title": match.title if match else "",
                "item": item,
            }
        )

    enriched_rows.sort(key=lambda row: (row["priority"][0], row["priority"][1], row["priority"][2]))

    st.subheader("Overview / 总览")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Citations / 引用总数", response.summary.get("total_citations", 0))
    col2.metric("Problematic / 风险引用", response.summary.get("problematic_citations", 0))
    col3.markdown(f"**AI Risk / AI 风险**  "+ status_badge(response.ai_writing_check.ai_risk_label), unsafe_allow_html=True)
    col4.metric("Manual Review / 人工复核", "Yes" if response.summary.get("manual_review_recommended") else "No")

    top_risk = enriched_rows[0] if enriched_rows else None
    if top_risk:
        top_title = top_risk["parsed_title"] or f"Citation {top_risk['index']}"
        top_issue = top_risk["issue_types_text"]
        st.warning(
            f"Most urgent manual-review target / 本次最需要人工复核的引用: Citation {top_risk['index']} - {top_title}\n\n"
            f"Primary risk / 主要风险: {top_issue}"
        )

    bilingual_note = response.summary.get("bilingual_support_note", {})
    if bilingual_note:
        st.info(
            "English retrieval coverage is currently stronger than Chinese coverage. "
            "Chinese misses should be interpreted conservatively as uncertain when public evidence is incomplete.\n\n"
            "当前英文自动核验覆盖强于中文；中文未命中时应结合公开证据不足这一现实，保守理解为 uncertain。"
        )

    st.subheader("Citation Results / 引用核验结果")
    available_existence = sorted({row["existence_label"] for row in enriched_rows})
    available_support = sorted({row["support_label"] for row in enriched_rows})
    available_issues = sorted({issue for row in enriched_rows for issue in row["issue_types"]})

    quick_col, filter_col1, filter_col2, filter_col3 = st.columns([1.1, 1.2, 1.2, 1.5])
    high_risk_only = quick_col.checkbox("High Risk Only / 仅看高风险", value=False)
    selected_existence = filter_col1.multiselect("Existence Filter / 存在性筛选", options=available_existence, default=available_existence)
    selected_support = filter_col2.multiselect("Support Filter / 支撑性筛选", options=available_support, default=available_support)
    selected_issues = filter_col3.multiselect(
        "Issue Filter / 问题类型筛选",
        options=available_issues,
        default=available_issues,
        format_func=lambda issue: ISSUE_LABELS.get(issue, issue),
    )

    filtered_rows = []
    for row in enriched_rows:
        issue_ok = True if not row["issue_types"] else any(issue in selected_issues for issue in row["issue_types"])
        risk_ok = row["risk_level"] <= 1 if high_risk_only else True
        if row["existence_label"] in selected_existence and row["support_label"] in selected_support and issue_ok and risk_ok:
            filtered_rows.append(row)

    table_rows = [
        {
            "risk": RISK_ICON.get(row["risk_level"], "[?]"),
            "#": row["index"],
            "language": row["language"],
            "parsed_title": row["parsed_title"],
            "parsed_year": row["parsed_year"],
            "existence_label": row["existence_label"],
            "existence_score": row["existence_score"],
            "support_label": row["support_label"],
            "issue_types": row["issue_types_text"],
            "matched_source": row["matched_source"],
            "matched_title": row["matched_title"],
        }
        for row in filtered_rows
    ]
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.subheader("AI Writing Risk / AI 写作风险")
    ai_col1, ai_col2, ai_col3 = st.columns(3)
    ai_col1.metric("Risk Score / 风险分数", response.ai_writing_check.ai_risk_score)
    ai_col2.markdown(f"**Risk Label / 风险等级**  "+ status_badge(response.ai_writing_check.ai_risk_label), unsafe_allow_html=True)
    ai_col3.metric("Confidence / 置信度", response.ai_writing_check.confidence)

    with st.expander("AI Risk Details / AI 风险详情", expanded=True):
        st.write("Suspicious Patterns / 可疑模式")
        st.write(response.ai_writing_check.suspicious_patterns or ["None / 无明显模式"])
        st.write("Humanization Suggestions / 修改建议")
        st.write(response.ai_writing_check.humanization_suggestions or ["None / 暂无建议"])
        st.write("Features / 特征")
        st.json(response.ai_writing_check.features)

    st.subheader("Report Snapshot / 报告摘要卡片")
    snap_cols = st.columns(3)
    for i, row in enumerate(filtered_rows[:3]):
        item = row["item"]
        with snap_cols[i % 3]:
            st.markdown(
                "<div style='padding:0.9rem;border:1px solid #e5e7eb;border-radius:14px;background:#fafaf9;min-height:200px;'>"
                f"<div style='font-weight:700;margin-bottom:0.5rem;'>{RISK_ICON.get(row['risk_level'], '[?]')} Citation {row['index']}</div>"
                f"<div style='font-size:0.95rem;margin-bottom:0.6rem;'>{(row['parsed_title'] or 'Untitled')[:110]}</div>"
                f"<div style='margin-bottom:0.5rem;'>{status_badge(item.existence_result.existence_label)} {status_badge(item.review_check_result.support_label)}</div>"
                f"<div style='font-size:0.88rem;color:#374151;'>{row['issue_types_text']}</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    st.subheader("Detailed Review / 逐条详情")
    for row in filtered_rows:
        item = row["item"]
        idx = row["index"]
        title = item.citation.title or item.citation.raw_text[:80]
        with st.expander(f"{RISK_ICON.get(row['risk_level'], '[?]')} Citation {idx} / 引用 {idx}: {title}"):
            st.markdown(f"**Raw Reference / 原始引用**\n\n{item.citation.raw_text}")
            st.markdown(
                "<div style='padding:0.8rem 1rem;border:1px solid #e5e7eb;border-radius:12px;margin:0.5rem 0 1rem 0;'>"
                f"<div style='margin-bottom:0.5rem;'><strong>Existence / 存在性</strong> {status_badge(item.existence_result.existence_label)}</div>"
                f"<div><strong>Support / 支撑性</strong> {status_badge(item.review_check_result.support_label)}</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Score / 分数**: `{item.existence_result.existence_score}`")
            st.markdown(f"**Reasons / 原因**: {'; '.join(item.existence_result.reasons)}")
            issues = item.review_check_result.issue_types or ["None"]
            st.markdown("**Issue Types / 问题类型**")
            st.markdown(" ".join(status_badge(issue, ISSUE_LABELS.get(issue, issue)) for issue in issues), unsafe_allow_html=True)
            st.markdown(f"**Explanation / 解释**\n\n{item.review_check_result.explanation}")
            st.markdown(f"**Revision Suggestion / 修改建议**\n\n{item.review_check_result.revision_suggestion}")
            if item.existence_result.best_match:
                st.markdown("**Best Match / 最佳匹配**")
                st.json(item.existence_result.best_match.model_dump())

    if response.markdown_content:
        st.subheader("Markdown Report Preview / Markdown 报告预览")
        st.markdown(response.markdown_content)

    st.subheader("Downloads / 下载")
    export_df = build_export_dataframe(response)
    zh_export = st.checkbox("Chinese Export Columns / 导出中文字段名", value=False)
    csv_df = export_df.rename(columns=ZH_EXPORT_COLUMNS) if zh_export else export_df
    st.download_button(
        "Download CSV / 下载 CSV",
        data=csv_df.to_csv(index=False, encoding="utf-8-sig"),
        file_name="verify_result_zh.csv" if zh_export else "verify_result.csv",
        mime="text/csv",
    )

    if response.markdown_content:
        st.download_button("Download Markdown", data=response.markdown_content, file_name="verify_report.md", mime="text/markdown")

    if response.excel_report_path:
        excel_bytes = Path(response.excel_report_path).read_bytes()
        st.download_button("Download Excel", data=excel_bytes, file_name=Path(response.excel_report_path).name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.caption(
    "Disclaimer: This interface is for assistive verification, self-check, and revision support only. "
    "It does not replace formal peer review, editorial screening, or academic integrity investigation. "
    "免责声明：本界面仅用于辅助核验、自查与修改建议，不替代正式同行评审、编辑审查或学术诚信认定。"
)
