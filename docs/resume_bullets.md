# Resume Bullets

## 中文简历项目描述
- 独立搭建 Literature Review Verifier Agent 工程原型，基于 FastAPI、Streamlit、Pydantic 与公开学术元数据源实现文献综述核验、引用存在性打分、规则审查、AI 写作风险提示和结构化报告导出。
- 设计可扩展的 retrieval + rule-based + LLM/LoRA 混合架构，支持 OpenAlex、Crossref、Semantic Scholar 检索链路，以及 Qwen3-4B-Instruct-2507 的 LoRA 微调与适配器推理脚本，满足本地 demo 与后续准生产迭代需求。

## English Resume Bullets
- Built an end-to-end Literature Review Verifier Agent prototype with FastAPI, Streamlit, public scholarly metadata retrieval, explainable citation existence scoring, rule-based review checking, AI writing risk detection, and structured Markdown/Excel reporting.
- Designed an extensible retrieval-plus-judgement architecture that supports rule mode, base LLM mode, and LoRA-adapted Qwen inference, with graceful fallback, training data formatting, toy PEFT scripts, and Windows-friendly local development.

## GitHub README Summary
Literature Review Verifier Agent is an engineering-focused prototype for checking whether cited references likely exist, whether metadata may be mismatched, whether review claims appear overclaimed or weakly supported, and whether a passage shows elevated AI writing risk patterns. The system prioritizes retrieval evidence from public metadata sources, degrades safely to rule-based judgement, and leaves clear extension points for LoRA fine-tuning on Qwen3-4B-Instruct-2507.
