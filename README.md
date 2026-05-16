# Enterprise RAG Pareto Benchmark

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![CI](https://github.com/ApexDataWorld/enterprise-rag-pareto-benchmark/actions/workflows/ci.yml/badge.svg)

A reproducible benchmark for selecting enterprise retrieval-augmented generation
(RAG) configurations under competing objectives: retrieval quality, answer
faithfulness, latency, cost, and hallucination risk.

Enterprise RAG systems rarely have a single best configuration. A retriever with
better recall may increase latency or cost; a lower-cost configuration may
increase hallucination risk; and reranking may improve evidence quality while
adding operational overhead. This repository provides a reproducible benchmark
for comparing those trade-offs and identifying Pareto-optimal configurations.

This repository is a research benchmark and reproducibility package, not a
production RAG platform.

## Overview

The benchmark runs a deterministic enterprise RAG evaluation pipeline:

```text
ingestion -> chunking -> features/embeddings -> retrieval -> reranking
-> extractive generation -> evaluation -> plots/tables -> metadata
```

The default experiment is intentionally dependency-light. It uses a synthetic
enterprise corpus and deterministic lexical and dense-hash retrieval components
so reviewers can reproduce the main results without external API keys, hosted
vector databases, model-provider services, or neural model downloads.

Optional validation runs add Sentence Transformers neural embeddings and
sensitivity studies, but those are separate from the dependency-free default
benchmark.

## Why this benchmark exists

Enterprise RAG configuration is a systems optimization problem, not a
single-metric leaderboard problem. Different applications optimize for different
constraints:

- internal search may prioritize latency and cost;
- compliance workflows may prioritize faithfulness and lower hallucination risk;
- knowledge assistants may prioritize recall;
- regulated environments may prioritize reproducibility and auditability.

This benchmark makes those trade-offs explicit by evaluating each configuration
across retrieval quality, answer-grounding metrics, estimated latency, estimated
cost, statistical comparisons, and Pareto-frontier labels.

## What the benchmark evaluates

The default benchmark evaluates deterministic configurations including:

- lexical retrieval at different top-k settings;
- reranked lexical retrieval;
- hybrid lexical and phrase-overlap retrieval;
- deterministic `dense_hash_*` retrieval;
- hybrid retrieval that combines lexical, dense-hash, and phrase-overlap scores.

Optional experiments evaluate:

- Sentence Transformers neural embeddings using
  `sentence-transformers/all-MiniLM-L6-v2`;
- chunk-size sensitivity;
- query-type performance;
- hallucination-risk weighting sensitivity;
- hybrid-weight ablation;
- latency/cost sensitivity.

Pareto-optimality is computed separately for each experiment set. See
`results/default/tables/pareto_frontier_data.csv` for the default deterministic
benchmark and `results/neural_embedding_validation/tables/pareto_frontier_data.csv`
for optional neural embedding validation.

## Repository structure

```text
configs/              # Versioned benchmark configurations
data/                 # Synthetic enterprise corpus and question set
src/rag_pareto/       # Benchmark implementation
scripts/              # Reproduction and artifact-generation scripts
results/              # Generated tables, figures, traces, and metadata
tests/                # Unit tests
.github/workflows/    # CI workflows
docs/                 # User and contributor documentation
paper/tables/         # Paper-facing generated table artifacts, if present
```

## Quick start

```bash
git clone https://github.com/ApexDataWorld/enterprise-rag-pareto-benchmark.git
cd enterprise-rag-pareto-benchmark

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .

make test
make reproduce-main
```

Direct Python command:

```bash
PYTHONPATH=src python -m rag_pareto.cli run --config configs/default.yaml
```

## Reproducing the main results

Run:

```bash
make reproduce-main
```

The main deterministic experiment writes outputs to `results/default/`,
including:

- `tables/query_metrics.csv`
- `tables/summary_metrics.csv`
- `tables/statistical_comparisons.csv`
- `tables/confidence_intervals.csv`
- `tables/query_type_summary.csv`
- `tables/pareto_frontier_data.csv`
- `figures/*.pdf`
- `figures/*.svg`
- `traces/retrieval_traces.json`
- `run_metadata.json`
- `final_result_summary.md`
- `v3_consistency_notes.md`

Current checked-in default results report 9 evaluated variants and 7
Pareto-optimal variants. This claim is supported by
`results/default/tables/pareto_frontier_data.csv` and
`results/default/final_result_summary.md`.

From `results/default/tables/summary_metrics.csv`, the checked-in default run
currently reports:

| Result | Variant | Value |
|---|---|---:|
| Lowest latency | `lexical_k3` | 358.1 ms |
| Lowest cost | `lexical_k3` | 0.00002021 USD |
| Highest Recall@k | `hybrid_k8_rerank`, `hybrid_k10_large` | 0.9167 |
| Highest faithfulness | `hybrid_k10_large` | 1.0000 |
| Lowest hallucination risk | `hybrid_dense_hash_k5_rerank` | 0.0369 |

To regenerate a README-safe summary from the checked-in artifacts:

```bash
PYTHONPATH=src python3 scripts/summarize_checked_in_results.py
```

## Optional validation and sensitivity studies

Install optional neural dependencies only if you want to run neural validation:

```bash
python3 -m pip install -e '.[neural]'
make reproduce-neural
```

Other experiment targets:

```bash
make reproduce-chunk-sensitivity
make reproduce-query-type
make reproduce-risk-sensitivity
make reproduce-hybrid-weight-ablation
make reproduce-latency-cost-sensitivity
make reproduce-sensitivity
make paper-artifacts
make artifact-manifest
```

`make reproduce-all` runs the dependency-free main benchmark, query-type
analysis, chunk-size sensitivity, sensitivity studies, and paper artifact
generation. It does not run neural validation because neural validation requires
optional model dependencies.

## Key outputs

| Output | Purpose |
|---|---|
| `summary_metrics.csv` | Variant-level quality, risk, latency, cost, and Pareto labels |
| `query_metrics.csv` | Per-query metrics used for paired statistical comparisons |
| `statistical_comparisons.csv` | Paired tests against the configured baseline |
| `confidence_intervals.csv` | Bootstrap intervals for selected metrics |
| `pareto_frontier_data.csv` | Dominated/non-dominated configuration labels |
| `query_type_summary.csv` | Mean metrics by query type and variant |
| `retrieval_traces.json` | Retrieved chunks, expected evidence, and generated answers |
| `run_metadata.json` | Environment, config, artifact hashes, and reproducibility metadata |
| `results/run_metadata/final_artifact_manifest.json` | Repository-level artifact manifest with hashes |

## Interpreting the results

Pareto-optimality is computed within each experiment set and should be
interpreted as a trade-off result, not as a universal ranking of RAG systems. A
Pareto-optimal configuration is not necessarily globally best. It means that,
within the evaluated experiment set, no other configuration improves all
selected objectives simultaneously under the implemented dominance rule.

Read:

- `docs/RESULTS_INTERPRETATION.md` for metrics and output files;
- `docs/ARCHITECTURE.md` for the pipeline and Pareto rule;
- `results/default/v3_consistency_notes.md` for default-run implementation notes.

## Default benchmark scope

The default benchmark uses:

- a synthetic enterprise corpus;
- deterministic chunking;
- lexical and deterministic dense-hash retrieval;
- optional reranking;
- deterministic extractive generation;
- transparent estimated cost and latency constants;
- automatic proxy hallucination-risk scoring.

The synthetic corpus and extractive generation choices make the artifact
reproducible but limit direct generalization to production deployments. The
benchmark is not a substitute for domain-specific evaluation, human factuality
assessment, production telemetry, or security review.

Dense-hash retrieval uses a deterministic local hashing-embedding provider with
96 dimensions, cosine similarity, and a local in-memory exhaustive scan. It is
not Sentence Transformers, MiniLM, OpenAI embeddings, Cohere embeddings, E5, or
FAISS. Do not describe the dependency-free default benchmark as using MiniLM or
FAISS unless the retrieval adapter is changed.

## Optional neural embedding validation

The optional neural validation path uses Sentence Transformers with
`sentence-transformers/all-MiniLM-L6-v2` when the neural extra is installed. This
is separate from the dependency-free default benchmark.

```bash
python3 -m pip install -e '.[neural]'
make reproduce-neural
```

Outputs are written to `results/neural_embedding_validation/`. The checked-in
neural validation currently evaluates 5 variants, and
`results/neural_embedding_validation/tables/pareto_frontier_data.csv` should be
used for neural Pareto labels. The neural validation is intended to test whether
the qualitative Pareto framing remains useful with a real open-source sentence
embedding model. It does not prove production superiority.

## Configuration guide

The default configuration is `configs/default.yaml`. Common keys include:

- `seed`
- `corpus_path`
- `questions_path`
- `output_dir`
- `chunk.size_tokens`
- `chunk.overlap_tokens`
- `cost_model`
- `dense_retrieval`
- `variants`

Each variant defines a unique `name`, `retriever`, `top_k`, `rerank`, and
`generator`. See `docs/CONFIGURATION.md` for the full configuration guide.

## Using a custom corpus

The benchmark reads JSONL documents and queries. A minimal document row is:

```json
{"id": "doc_001", "title": "Example Policy", "text": "Document text..."}
```

A minimal query row is:

```json
{
  "id": "q_001",
  "question": "What is the policy for escalation?",
  "relevant_doc_ids": ["doc_001"],
  "relevant_chunk_ids": ["doc_001::c000"],
  "answer_terms": ["escalation", "policy"],
  "query_type": "fact_lookup"
}
```

Chunk-level relevance labels depend on the chunking configuration. If you change
chunk size or overlap, review `relevant_chunk_ids` or use document-level labels.
See `docs/CUSTOM_CORPUS.md`.

## Paper and citation

A paper manuscript accompanies this repository. Until a DOI or proceedings link
is available, cite the software repository using `CITATION.cff`.

```bibtex
@misc{gupta2026enterprise_rag_pareto,
  author = {Gupta, Saurabh},
  title = {Enterprise RAG Pareto Benchmark},
  year = {2026},
  howpublished = {\url{https://github.com/ApexDataWorld/enterprise-rag-pareto-benchmark}},
  note = {Software artifact and reproducibility package}
}
```

No DOI, proceedings link, or ACM artifact badge is claimed in this repository
unless it is added later from a verified source.

## Reproducibility checklist

For ACM-style artifact review, start with:

```bash
make test
make reproduce-main
make artifact-manifest
```

Then inspect:

- `results/default/tables/summary_metrics.csv`
- `results/default/tables/pareto_frontier_data.csv`
- `results/default/run_metadata.json`
- `results/run_metadata/final_artifact_manifest.json`

See `docs/REPRODUCIBILITY.md` and `RELEASE_CHECKLIST.md`.

## Development and contributing

Development setup:

```bash
python3 -m pip install -e '.[dev]'
make test
```

Contribution guidelines are in `CONTRIBUTING.md`. Make sure all result claims in
documentation are backed by regenerated artifacts under `results/`.

## License

Apache-2.0. See `LICENSE`.
