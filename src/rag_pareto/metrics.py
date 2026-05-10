"""Benchmark metrics used by the Paper 5 result tables."""

from __future__ import annotations

import math
from statistics import mean

from .chunking import Chunk
from .data import Query
from .text import tokenize


def retrieval_metrics(query: Query, retrieved: list[Chunk], k: int) -> dict[str, float]:
    ranked_chunks = retrieved[:k]
    hits = []
    seen_relevant: set[str] = set()
    for chunk in ranked_chunks:
        key = _relevance_key(query, chunk)
        is_new_relevant = key is not None and key not in seen_relevant
        hits.append(1 if is_new_relevant else 0)
        if is_new_relevant:
            seen_relevant.add(key)
    relevant_hits = {_relevance_key(query, chunk) for chunk in ranked_chunks if _relevance_key(query, chunk) is not None}
    recall = len(relevant_hits) / _relevance_total(query)
    mrr = next((1.0 / (idx + 1) for idx, hit in enumerate(hits) if hit), 0.0)
    dcg = sum(hit / math.log2(idx + 2) for idx, hit in enumerate(hits))
    ideal_hits = [1] * min(_relevance_total(query), k)
    idcg = sum(hit / math.log2(idx + 2) for idx, hit in enumerate(ideal_hits))
    ndcg = dcg / idcg if idcg else 0.0
    precision = sum(hits) / len(hits) if hits else 0.0
    return {"recall_at_k": recall, "mrr": mrr, "ndcg_at_k": ndcg, "context_precision": precision}


def generation_metrics(query: Query, answer: str, retrieved: list[Chunk]) -> dict[str, float]:
    answer_tokens = set(tokenize(answer))
    context_tokens = set(tokenize(" ".join(chunk.text for chunk in retrieved)))
    answer_terms = set(query.answer_terms)
    supported_terms = answer_terms & answer_tokens & context_tokens
    relevant_hits = {_relevance_key(query, chunk) for chunk in retrieved if _relevance_key(query, chunk) is not None}
    context_recall = len(relevant_hits) / _relevance_total(query)
    faithfulness = len(answer_tokens & context_tokens) / max(len(answer_tokens), 1)
    answer_term_coverage = len(supported_terms) / max(len(answer_terms), 1)
    hallucination_risk = max(0.0, 1.0 - (0.65 * faithfulness + 0.35 * answer_term_coverage))
    return {
        "context_recall": context_recall,
        "faithfulness": faithfulness,
        "answer_term_coverage": answer_term_coverage,
        "hallucination_risk": hallucination_risk,
    }


def aggregate(rows: list[dict[str, float | str]]) -> dict[str, float]:
    metric_keys = [key for key, value in rows[0].items() if isinstance(value, float)]
    return {key: mean(float(row[key]) for row in rows) for key in metric_keys}


def _is_relevant_chunk(query: Query, chunk: Chunk) -> bool:
    return _relevance_key(query, chunk) is not None


def _relevance_key(query: Query, chunk: Chunk) -> str | None:
    if query.relevant_chunk_ids:
        return chunk.id if chunk.id in set(query.relevant_chunk_ids) else None
    if chunk.doc_id not in set(query.relevant_doc_ids):
        return None
    chunk_tokens = set(tokenize(f"{chunk.title} {chunk.text}"))
    return chunk.doc_id if chunk_tokens & set(query.answer_terms) else None


def _relevance_total(query: Query) -> int:
    return max(len(set(query.relevant_chunk_ids or query.relevant_doc_ids)), 1)
