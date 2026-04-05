# Future Training Plan

## Goals
- Expand the current toy instruction dataset into a multi-task training corpus for citation existence classification, review support classification, and revision suggestion generation.
- Keep every label grounded in retrieval evidence rather than unsupported world knowledge.
- Maintain conservative handling for Chinese references when public evidence is sparse.

## Data Scaling Strategy
- Collect weakly supervised samples from public metadata sources such as OpenAlex, Crossref, Semantic Scholar, DOI landing pages, and open institutional repositories.
- Add human-reviewed hard negatives, including fabricated references, metadata swaps, venue mismatches, and topic-irrelevant but real papers.
- Build bilingual samples with explicit provenance fields so the model learns when to output `uncertain`.

## Task Design
- Task 1: Citation Existence Classification
  Input: raw reference, parsed fields, retrieval candidates.
  Output: `likely_exists`, `possible_match`, `weak_match`, `not_found` with reasons.
- Task 2: Review Support Classification
  Input: review sentence, citation, matched metadata or abstract, rule scores.
  Output: `supported`, `partially_supported`, `unsupported`, `uncertain` with issue types.
- Task 3: Revision Suggestion Generation
  Input: original review sentence, evidence, issue types.
  Output: conservative and evidence-bounded rewrite suggestion.

## Data Quality Controls
- Require at least one retrieval evidence snapshot per sample.
- Store rule-based intermediate outputs for traceability.
- Use double annotation for a subset of edge cases.
- Track disagreement patterns, especially causal claims, overclaims, and Chinese-source misses.

## Evaluation Roadmap
- Exact-match JSON rate.
- Label accuracy for existence and support tasks.
- Issue-type micro F1.
- Human preference on revision suggestions.
- Error buckets for fabricated references, metadata mismatch, irrelevance, and uncertainty calibration.
