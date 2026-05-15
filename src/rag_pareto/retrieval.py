"""Deterministic lexical, dense-hash, neural, and hybrid retrieval."""

from __future__ import annotations

import math
from collections import Counter

from .chunking import Chunk
from .embeddings import make_embedding_provider
from .text import cosine, term_counts, tokenize


class Retriever:
    def __init__(self, chunks: list[Chunk], mode: str, embedding_provider_config: dict | None = None, hybrid_weights: dict | None = None):
        aliases = {"dense": "dense_hash", "hybrid_dense": "hybrid_dense_hash"}
        mode = aliases.get(mode, mode)
        if mode not in {"lexical", "hybrid", "dense_hash", "hybrid_dense_hash", "dense_neural", "hybrid_neural"}:
            raise ValueError(f"Unsupported retriever: {mode}")
        self.chunks = chunks
        self.mode = mode
        provider_cfg = embedding_provider_config if "neural" in mode else {"type": "dense_hash"}
        self.embedding_provider = make_embedding_provider(provider_cfg)
        self.hybrid_weights = hybrid_weights or {"lexical": 0.56, "dense": 0.44, "phrase": 0.12}
        self.chunk_terms = {chunk.id: term_counts(f"{chunk.title} {chunk.text}") for chunk in chunks}
        self.idf = _idf(self.chunk_terms.values())
        chunk_texts = [f"{chunk.title} {chunk.text}" for chunk in chunks]
        chunk_vectors = self.embedding_provider.encode(chunk_texts)
        self.chunk_embeddings = {chunk.id: vector for chunk, vector in zip(chunks, chunk_vectors)}

    def search(self, query: str, top_k: int, rerank: bool = False) -> list[tuple[Chunk, float]]:
        query_terms = term_counts(query)
        query_tokens = set(tokenize(query))
        query_embedding = self.embedding_provider.encode([query])[0]
        scored = []
        for chunk in self.chunks:
            lexical = cosine(query_terms, self.chunk_terms[chunk.id], self.idf)
            phrase_overlap = len(query_tokens & set(self.chunk_terms[chunk.id])) / max(len(query_tokens), 1)
            dense = _vector_cosine(query_embedding, self.chunk_embeddings[chunk.id])
            if self.mode == "lexical":
                score = lexical
            elif self.mode == "hybrid":
                score = lexical + 0.18 * phrase_overlap
            elif self.mode in {"dense_hash", "dense_neural"}:
                score = dense
            else:
                score = (
                    float(self.hybrid_weights.get("lexical", 0.56)) * lexical
                    + float(self.hybrid_weights.get("dense", 0.44)) * dense
                    + float(self.hybrid_weights.get("phrase", 0.12)) * phrase_overlap
                )
            scored.append((chunk, score))
        scored.sort(key=lambda item: (-item[1], item[0].id))
        candidates = scored[: max(top_k * (2 if rerank else 1), top_k)]
        if rerank:
            candidates = _rerank(candidates, query_tokens)
        return candidates[:top_k]


def _idf(term_vectors: list[Counter[str]]) -> dict[str, float]:
    doc_count = len(term_vectors)
    dfs: Counter[str] = Counter()
    for vector in term_vectors:
        dfs.update(vector.keys())
    return {term: math.log((doc_count + 1) / (df + 1)) + 1.0 for term, df in dfs.items()}


def _rerank(candidates: list[tuple[Chunk, float]], query_tokens: set[str]) -> list[tuple[Chunk, float]]:
    reranked = []
    for chunk, score in candidates:
        chunk_tokens = set(tokenize(f"{chunk.title} {chunk.text}"))
        exact = len(query_tokens & chunk_tokens)
        title_hit = len(query_tokens & set(tokenize(chunk.title)))
        reranked.append((chunk, score + 0.045 * exact + 0.07 * title_hit))
    reranked.sort(key=lambda item: (-item[1], item[0].id))
    return reranked


def _vector_cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
