# Reproducibility Guide

This repository is designed to be documented, consistent with the paper
manuscript, complete enough to exercise, and verifiable through generated
artifacts. It does not claim an ACM artifact badge unless one is granted later.

## Artifact inventory

Important artifact groups:

- `configs/` - versioned experiment configurations.
- `data/` - synthetic corpus and query labels.
- `src/rag_pareto/` - benchmark implementation.
- `scripts/` - reproduction and artifact-generation scripts.
- `results/default/` - dependency-free default benchmark outputs.
- `results/neural_embedding_validation/` - optional neural validation outputs.
- `results/chunk_size_sensitivity/` - chunk-size sensitivity outputs.
- `results/sensitivity/` - risk, hybrid-weight, and latency/cost sensitivity outputs.
- `results/run_metadata/final_artifact_manifest.json` - artifact manifest.

## Environment

The package declares Python 3.10+ support. The default benchmark uses only the
Python standard library. Optional development and neural dependencies are
declared in `pyproject.toml`.

## Dependency-free default run

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .

make test
make reproduce-main
```

Expected default output directory:

```text
results/default/
```

## Optional neural run

```bash
python3 -m pip install -e '.[neural]'
make reproduce-neural
```

The neural run may download or load the configured Sentence Transformers model.
It is not required for dependency-free default reproduction.

## Sensitivity studies

```bash
make reproduce-chunk-sensitivity
make reproduce-query-type
make reproduce-risk-sensitivity
make reproduce-hybrid-weight-ablation
make reproduce-latency-cost-sensitivity
make artifact-manifest
```

## Expected outputs

Default outputs include:

- `results/default/tables/summary_metrics.csv`
- `results/default/tables/query_metrics.csv`
- `results/default/tables/statistical_comparisons.csv`
- `results/default/tables/confidence_intervals.csv`
- `results/default/tables/pareto_frontier_data.csv`
- `results/default/traces/retrieval_traces.json`
- `results/default/run_metadata.json`

## Metadata and hashes

Run metadata is written by the benchmark pipeline. Repository-level hashes are
generated with:

```bash
make artifact-manifest
```

This writes:

```text
results/run_metadata/final_artifact_manifest.json
```

## How to verify results

1. Run `make test`.
2. Run `make reproduce-main`.
3. Compare `results/default/tables/summary_metrics.csv` with the checked-in file.
4. Inspect `results/default/tables/pareto_frontier_data.csv`.
5. Regenerate `results/run_metadata/final_artifact_manifest.json`.

For a concise checked-in artifact summary:

```bash
PYTHONPATH=src python3 scripts/summarize_checked_in_results.py
```

## Known limitations

- The corpus and query set are synthetic.
- Generation is extractive rather than hosted or local LLM generation.
- Cost and latency are estimated from transparent constants.
- Hallucination risk is an automatic proxy, not human factuality evaluation.
- Optional neural validation depends on external model availability or cache.
- Single-pass retrieval is a stress case for multi-hop and ambiguous queries.
