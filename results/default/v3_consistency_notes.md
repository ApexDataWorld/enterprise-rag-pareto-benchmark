# V3 Consistency Notes

## Experiment Scope

The generated benchmark executes 9 configurations: lexical_k3, lexical_k5, lexical_k5_rerank, hybrid_k5_rerank, hybrid_k8_rerank, hybrid_k10_large, dense_hash_k5, dense_hash_k5_rerank, hybrid_dense_hash_k5_rerank.
The current repo does not contain LaTeX source, so this run cannot directly edit or validate manuscript tables.
The uploaded PDF should be treated as stale if it still says six configurations or lists dense-hash retrieval as future work.

## Dense Retrieval Implementation

- Model/provider: `local_hashing_embedding_v1`.
- Dimension: `96`.
- Similarity: `cosine`.
- Index: `local_in_memory_exhaustive_scan`.
- External dependencies/API keys: none.
- Important: this is a deterministic local hashing-embedding provider, not Sentence Transformers, MiniLM, or FAISS.
- Hybrid dense fusion: `hybrid_dense_hash = 0.56 * lexical_cosine + 0.44 * dense_cosine + 0.12 * phrase_overlap`.
- Reranking: exact token overlap plus title-hit bonus over the expanded candidate set.
- Dense latency includes the configured `dense_embedding_latency_ms` estimate in `configs/default.yaml`.

## Pareto Verification

Pareto-optimal configurations after recomputation: 7 of 9.
Dominated and non-dominated labels are written to `tables/pareto_frontier_data.csv`.
A configuration is dominated only if another configuration has greater-or-equal recall and faithfulness, lower-or-equal latency/cost/risk, and is strictly better on at least one of those objectives.

## Paper-Side Required Fixes

- Table I and appendix config should list all 9 generated configurations.
- Methods should describe deterministic hashing embeddings, 96 dimensions, cosine similarity, and local exhaustive scan unless the code is changed to use MiniLM/FAISS.
- Figure references should use the generated PDFs, not SVGs.
- Dense-hash retrieval should not be described as future work in V3.
