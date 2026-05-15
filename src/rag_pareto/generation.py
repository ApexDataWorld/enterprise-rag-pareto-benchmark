"""Extractive generation and deterministic cost/latency accounting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .chunking import Chunk
from .data import Query


MODEL_PROFILES = {
    "extractive_small": {"output_tokens": 70, "latency_ms": 180, "input_cost": 0.00000008, "output_cost": 0.00000020},
    "extractive_medium": {"output_tokens": 100, "latency_ms": 310, "input_cost": 0.00000012, "output_cost": 0.00000045},
    "extractive_large": {"output_tokens": 130, "latency_ms": 520, "input_cost": 0.00000020, "output_cost": 0.00000090},
}


DEFAULT_COST_MODEL = {
    "retrieval_cost_per_chunk": 0.000000015,
    "rerank_cost_per_document": 0.000004,
    "dense_embedding_cost_per_query": 0.0000012,
    "dense_embedding_latency_ms": 12.0,
    "hybrid_dense_hash_fusion_latency_ms": 4.0,
    "retrieval_base_latency_ms": 35.0,
    "retrieval_latency_per_chunk_ms": 1.8,
    "retrieval_latency_per_topk_ms": 4.5,
    "rerank_latency_per_document_ms": 18.0,
}


@dataclass(frozen=True)
class CostLatencyEstimate:
    retrieval_cost: float
    rerank_cost: float
    generation_cost: float
    total_cost: float
    retrieval_latency_ms: float
    rerank_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float


def generate_answer(query: Query, retrieved: list[Chunk], model: str) -> str:
    if model not in MODEL_PROFILES:
        raise ValueError(f"Unsupported generator: {model}")
    snippets = []
    for chunk in retrieved[:3]:
        snippets.append(chunk.text)
    base = " ".join(snippets)
    if model == "extractive_small":
        return base[:360]
    if model == "extractive_medium":
        return base[:520]
    return base[:700]


def estimate_latency_ms(top_k: int, rerank: bool, model: str, corpus_chunks: int) -> float:
    return estimate_cost_latency(top_k, rerank, model, corpus_chunks, 0, "lexical").total_latency_ms


def estimate_cost_usd(top_k: int, rerank: bool, model: str, input_tokens: int) -> float:
    return estimate_cost_latency(top_k, rerank, model, 0, input_tokens, "lexical").total_cost


def estimate_cost_latency(
    top_k: int,
    rerank: bool,
    model: str,
    corpus_chunks: int,
    input_tokens: int,
    retriever: str,
    cost_model: dict[str, Any] | None = None,
) -> CostLatencyEstimate:
    profile = MODEL_PROFILES[model]
    cfg = {**DEFAULT_COST_MODEL, **(cost_model or {})}
    embedding_latency = 0.0
    fusion_latency = 0.0
    embedding_cost = 0.0
    if retriever in {"dense", "dense_hash", "dense_neural"}:
        embedding_latency = float(cfg["dense_embedding_latency_ms"])
        embedding_cost = float(cfg["dense_embedding_cost_per_query"])
    elif retriever in {"hybrid_dense", "hybrid_dense_hash", "hybrid_neural"}:
        embedding_latency = float(cfg["dense_embedding_latency_ms"])
        fusion_latency = float(cfg.get("hybrid_dense_hash_fusion_latency_ms", cfg.get("hybrid_dense_fusion_latency_ms", 4.0)))
        embedding_cost = float(cfg["dense_embedding_cost_per_query"])

    retrieval_latency = (
        float(cfg["retrieval_base_latency_ms"])
        + corpus_chunks * float(cfg["retrieval_latency_per_chunk_ms"])
        + top_k * float(cfg["retrieval_latency_per_topk_ms"])
        + embedding_latency
        + fusion_latency
    )
    rerank_latency = top_k * float(cfg["rerank_latency_per_document_ms"]) if rerank else 0.0
    generation_latency = float(profile["latency_ms"])

    retrieval_cost = corpus_chunks * float(cfg["retrieval_cost_per_chunk"]) + embedding_cost
    rerank_cost = top_k * float(cfg["rerank_cost_per_document"]) if rerank else 0.0
    generation_cost = input_tokens * profile["input_cost"] + profile["output_tokens"] * profile["output_cost"]
    total_cost = retrieval_cost + rerank_cost + generation_cost
    total_latency = retrieval_latency + rerank_latency + generation_latency
    return CostLatencyEstimate(
        retrieval_cost=round(retrieval_cost, 8),
        rerank_cost=round(rerank_cost, 8),
        generation_cost=round(generation_cost, 8),
        total_cost=round(total_cost, 8),
        retrieval_latency_ms=round(retrieval_latency, 3),
        rerank_latency_ms=round(rerank_latency, 3),
        generation_latency_ms=round(generation_latency, 3),
        total_latency_ms=round(total_latency, 3),
    )
