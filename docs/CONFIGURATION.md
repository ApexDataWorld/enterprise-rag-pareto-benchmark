# Configuration Guide

Benchmark runs are configured with YAML files under `configs/`.

## Default config

The default config is `configs/default.yaml`:

```yaml
seed: 42
corpus_path: data/corpus/enterprise_docs.jsonl
questions_path: data/questions/enterprise_qa.jsonl
output_dir: results/default

chunk:
  size_tokens: 24
  overlap_tokens: 4

variants:
  - name: lexical_k5
    retriever: lexical
    top_k: 5
    rerank: false
    generator: extractive_small
```

## Top-level keys

| Key | Purpose |
|---|---|
| `seed` | Fixed random seed used for deterministic resampling and run setup. |
| `corpus_path` | JSONL document file. |
| `questions_path` | JSONL query and relevance-label file. |
| `output_dir` | Directory for generated tables, figures, traces, and metadata. |
| `chunk` | Chunk size and overlap configuration. |
| `cost_model` | Estimated cost and latency constants. |
| `dense_retrieval` | Documentation metadata for deterministic dense-hash retrieval. |
| `embedding_provider` | Optional neural embedding provider configuration. |
| `hybrid_weights` | Optional hybrid score weights. |
| `variants` | List of evaluated RAG configurations. |

## Chunk settings

```yaml
chunk:
  size_tokens: 24
  overlap_tokens: 4
```

`overlap_tokens` must be smaller than `size_tokens`.

## Variants

Each variant requires:

| Key | Purpose |
|---|---|
| `name` | Unique variant name used in result files. |
| `retriever` | Retrieval mode. |
| `top_k` | Number of chunks returned. |
| `rerank` | Whether reranking is enabled. |
| `generator` | Extractive generation profile. |

Supported retrievers include:

- `lexical`
- `hybrid`
- `dense_hash`
- `hybrid_dense_hash`
- `dense_neural`
- `hybrid_neural`

The neural retrievers require the optional neural dependency and an
`embedding_provider` block.

## Cost model

The default cost and latency estimates are controlled by:

```yaml
cost_model:
  retrieval_cost_per_chunk: 0.000000015
  rerank_cost_per_document: 0.000004
  dense_embedding_cost_per_query: 0.0000012
  dense_embedding_latency_ms: 12.0
  hybrid_dense_hash_fusion_latency_ms: 4.0
  retrieval_base_latency_ms: 35.0
  retrieval_latency_per_chunk_ms: 1.8
  retrieval_latency_per_topk_ms: 4.5
  rerank_latency_per_document_ms: 18.0
```

These are controlled estimates, not measured production timings.

## Dense-hash metadata

The default config records the deterministic dense-hash retrieval details:

```yaml
dense_retrieval:
  provider: deterministic_hashing_embedding_v1
  model_name: local_hashing_embedding_v1
  embedding_dimension: 96
  similarity: cosine
  index: local_in_memory_exhaustive_scan
```

This is not a production neural embedding model.

## Optional neural embeddings

`configs/neural_embedding_validation.yaml` uses:

```yaml
embedding_provider:
  type: sentence_transformers
  model_name: sentence-transformers/all-MiniLM-L6-v2
  normalize: true
  cache_dir: .cache/embeddings
```

Install optional dependencies before running this config:

```bash
python3 -m pip install -e '.[neural]'
make reproduce-neural
```

## Common mistakes

- `overlap_tokens` must be smaller than `size_tokens`.
- Use a unique `output_dir` for each experiment.
- Neural embeddings require optional dependencies and may require model download
  or a populated local cache.
- Variant names should be unique.
- `top_k` should be positive.
- `relevant_chunk_ids` can become stale if chunk size or overlap changes.
