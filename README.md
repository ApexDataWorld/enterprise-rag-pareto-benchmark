# Enterprise RAG Pareto Benchmark

Reproducible benchmark code for Paper 5, **A Reproducible Benchmark for Enterprise RAG: Pareto Trade-offs Among Retrieval Quality, Latency, Cost, and Hallucination Risk**.

The repository runs a deterministic enterprise RAG experiment pipeline:

`ingestion -> chunking -> embeddings/features -> vector-style retrieval -> reranking -> extractive generation -> evaluation -> plots/tables -> reproducibility metadata`

The default benchmark is intentionally dependency-free so the paper artifact can run in a clean Python environment. Optional scientific packages are listed in `requirements.txt` for notebook analysis or alternate plotting.

## Quick Start

```bash
PYTHONPATH=src python -m rag_pareto.cli run --config configs/default.yaml
```

Or use Make:

```bash
make test
make reproduce-main
make reproduce-chunk-sensitivity
make reproduce-sensitivity
make paper-artifacts
```

Optional neural validation uses Sentence Transformers and may download model weights:

```bash
python3 -m pip install '.[neural]'
make reproduce-neural
```

Outputs are written to `results/default`:

- `tables/query_metrics.csv`
- `tables/summary_metrics.csv`
- `tables/statistical_comparisons.csv`
- `tables/confidence_intervals.csv`
- `tables/query_type_summary.csv`
- `tables/pareto_frontier_data.csv`
- `tables/final_latex_table_values.tex`
- `figures/latency_vs_quality.svg`
- `figures/latency_vs_quality.pdf`
- `figures/cost_vs_quality.svg`
- `figures/cost_vs_quality.pdf`
- `figures/pareto_frontier.svg`
- `figures/pareto_frontier.pdf`
- `figures/reranker_impact.svg`
- `figures/reranker_impact.pdf`
- `figures/risk_vs_faithfulness.svg`
- `figures/risk_vs_faithfulness.pdf`
- `figures/topk_sensitivity.svg`
- `figures/topk_sensitivity.pdf`
- `figures/query_type_performance.svg`
- `figures/query_type_performance.pdf`
- `traces/retrieval_traces.json`
- `run_metadata.json`
- `final_result_summary.md`
- `v3_consistency_notes.md`

## Metrics

The benchmark reports:

- Retrieval quality: `recall_at_k`, `mrr`, `ndcg_at_k`
- Context quality: `context_precision`, `context_recall`
- Generation risk: `faithfulness`, `answer_term_coverage`, `hallucination_risk`
- System trade-offs: `latency_ms`, `cost_usd`, component cost, and component latency
- Pareto flag: `pareto_optimal`
- Bootstrap confidence intervals and Benjamini-Hochberg adjusted p-values

## Configuration

Edit `configs/default.yaml` to change:

- fixed seed
- corpus and question files
- chunk size and overlap
- retriever type
- top-k setting
- reranker on/off
- generation profile
- transparent cost and latency constants
- output directory

## Environment Variables

No `.env` file is required for the default benchmark. It runs locally with the Python standard library and the bundled synthetic dataset.

For real external embedding, vector database, or LLM backends, copy `.env.example` to `.env` and fill in only the services you use. `.env` is ignored by git so secrets stay local.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Docker

```bash
docker build -t enterprise-rag-pareto-benchmark .
docker run --rm -v "$PWD/results:/app/results" enterprise-rag-pareto-benchmark
```

## Artifact Notes

The bundled corpus is synthetic and spans security policy, access control, finance approvals, legal retention, HR benefits, IT runbooks, incident response, cost governance, RAG evaluation, data privacy, vendor risk, model governance, and cloud operations. It is suitable for validating the pipeline, result schema, plots, and reproducibility metadata. For manuscript claims about external systems or vendor models, replace the JSONL corpus/questions and add real backend adapters while preserving the same output tables.

Dense-hash retrieval is implemented as a deterministic local hashing-embedding provider with 96 dimensions, cosine similarity, and a local in-memory exhaustive scan. It gives the benchmark dense-hash retrieval variants without requiring model downloads or API keys during artifact review. Do not describe the default repo as using MiniLM or FAISS unless the retrieval adapter is replaced.

## Reproduction Targets

- `make install`
- `make test`
- `make reproduce-main`
- `make reproduce-neural`
- `make reproduce-chunk-sensitivity`
- `make reproduce-query-type`
- `make reproduce-risk-sensitivity`
- `make reproduce-cost-sensitivity`
- `make reproduce-hybrid-ablation`
- `make reproduce-sensitivity`
- `make reproduce-all`
- `make paper-tables`
- `make paper-figures`
- `make paper-pdf`
- `make artifact-manifest`
