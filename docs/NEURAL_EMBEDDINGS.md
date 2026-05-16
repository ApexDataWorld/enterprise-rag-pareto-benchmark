# Neural Embeddings

The default benchmark is dependency-free and uses deterministic dense-hash
embeddings. Optional neural embedding validation is provided separately.

## Install

```bash
python3 -m pip install -e '.[neural]'
```

This installs Sentence Transformers and its dependencies.

## Run

```bash
make reproduce-neural
```

Direct command:

```bash
PYTHONPATH=src python3 scripts/run_neural_embedding_validation.py
```

## Output directory

Neural validation writes to:

```text
results/neural_embedding_validation/
```

Key files include:

- `tables/summary_metrics.csv`
- `tables/pareto_frontier_data.csv`
- `tables/query_metrics.csv`
- `tables/statistical_comparisons.csv`
- `tables/confidence_intervals.csv`
- `traces/retrieval_traces.json`
- `run_metadata.json`

## Model

The checked-in neural validation config uses:

```yaml
embedding_provider:
  type: sentence_transformers
  model_name: sentence-transformers/all-MiniLM-L6-v2
  normalize: true
  cache_dir: .cache/embeddings
```

The expected embedding dimension for this model is 384.

## Interpretation

The neural validation is intended to test whether the qualitative Pareto
framing remains useful when deterministic dense-hash embeddings are replaced
with a real open-source sentence embedding model.

It is not the dependency-free default path, and it does not prove production
superiority. Production systems should validate embeddings on their own data,
latency budgets, cost model, privacy constraints, and governance requirements.
