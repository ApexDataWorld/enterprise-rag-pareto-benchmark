# Changelog

All notable changes to this repository are documented here.

## [1.0.0] - 2026-05-15

### Added

- Dependency-free deterministic enterprise RAG benchmark.
- Versioned configuration files.
- Synthetic enterprise corpus and query set.
- Retrieval, generation, risk, latency, and cost metrics.
- Pareto-frontier labeling.
- Statistical comparison and bootstrap confidence interval outputs.
- Optional neural embedding validation.
- Chunk-size sensitivity analysis.
- Hybrid-weight ablation.
- Hallucination-risk weighting sensitivity analysis.
- Latency/cost sensitivity analysis.
- Query-type analysis.
- Reproducibility metadata and artifact manifest.
- Paper-facing tables and figures.
- Repository documentation, citation metadata, release checklist, and issue templates.

### Known limitations

- Synthetic corpus and query set.
- Extractive generation rather than hosted or local LLM generation.
- Estimated cost and latency model.
- Optional neural validation depends on external model download/cache.
- Single-pass retrieval is not intended to solve all multi-hop enterprise reasoning cases.
