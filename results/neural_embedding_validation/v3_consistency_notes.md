# V3 Consistency Notes

## Experiment Scope

The generated benchmark executes 5 configurations: hybrid_k5_rerank_hash, dense_neural_k5, dense_neural_k5_rerank, hybrid_neural_k5_rerank, hybrid_neural_k8_rerank.
The current repo does not contain LaTeX source, so this run cannot directly edit or validate manuscript tables.
The uploaded PDF should be treated as stale if it still says six configurations or lists dense-hash retrieval as future work.

## Dense Retrieval Implementation

- Model/provider: `local_hashing_embedding_v1`.
- Dimension: `96`.
- Similarity: `cosine`.
- Index: `local_in_memory_exhaustive_scan`.
- External dependencies/API keys: none.
- Important: this is a deterministic local hashing-embedding provider, not Sentence Transformers, MiniLM, or FAISS.
- Hybrid dense fusion: `see retrieval.py`.
- Reranking: exact token overlap plus title-hit bonus over the expanded candidate set.
- Dense latency includes the configured `dense_embedding_latency_ms` estimate in `configs/default.yaml`.

## Pareto Verification

Pareto-optimal configurations after recomputation: 5 of 5.
Dominated and non-dominated labels are written to `tables/pareto_frontier_data.csv`.
A configuration is dominated only if another configuration has greater-or-equal recall and faithfulness, lower-or-equal latency/cost/risk, and is strictly better on at least one of those objectives.

## Paper-Side Required Fixes

- Table I and appendix config should list all 9 generated configurations.
- Methods should describe deterministic hashing embeddings, 96 dimensions, cosine similarity, and local exhaustive scan unless the code is changed to use MiniLM/FAISS.
- Figure references should use the generated PDFs, not SVGs.
- Dense-hash retrieval should not be described as future work in V3.
