# Custom Corpus Guide

The benchmark can run on custom JSONL documents and queries.

## Document format

Each line in the document file must be a JSON object:

```json
{"id": "doc_001", "title": "Example Policy", "text": "Document text..."}
```

Required fields:

| Field | Meaning |
|---|---|
| `id` | Stable document ID. |
| `title` | Document title used by retrieval and traces. |
| `text` | Document text to chunk and retrieve. |

## Query format

Each line in the query file must be a JSON object:

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

Required fields:

| Field | Meaning |
|---|---|
| `id` | Stable query ID. |
| `question` | User question. |
| `relevant_doc_ids` | Expected relevant documents. |
| `answer_terms` | Terms expected in a supported answer. |

Optional fields:

| Field | Meaning |
|---|---|
| `relevant_chunk_ids` | Expected chunk IDs. If present, chunk-level labels are used. |
| `query_type` | Query category. Defaults to `fact_lookup` if omitted. |

## Relevance labels

`relevant_doc_ids` provide document-level relevance. `relevant_chunk_ids`
provide stricter chunk-level relevance. If `relevant_chunk_ids` are present, the
metric code uses them first.

Chunk IDs depend on the chunking configuration. If you change chunk size or
overlap, review or regenerate chunk-level relevance labels.

## Running a custom config

Create a config such as `configs/my_custom_config.yaml`:

```yaml
seed: 42
corpus_path: data/custom/documents.jsonl
questions_path: data/custom/questions.jsonl
output_dir: results/custom

chunk:
  size_tokens: 256
  overlap_tokens: 26

variants:
  - name: lexical_k5
    retriever: lexical
    top_k: 5
    rerank: false
    generator: extractive_small
```

Run:

```bash
PYTHONPATH=src python -m rag_pareto.cli run --config configs/my_custom_config.yaml
```

Do not commit secrets, private customer records, PHI, or proprietary documents.
