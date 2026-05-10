"""Deterministic lexical, dense, and hybrid retrieval."""

from __future__ import annotations

import math
from collections import Counter
from hashlib import blake2b

from .chunking import Chunk
from .text import cosine, term_counts, tokenize


class Retriever:
    def __init__(self, chunks: list[Chunk], mode: str):
        if mode not in {"lexical", "hybrid", "dense", "hybrid_dense"}:
            raise ValueError(f"Unsupported retriever: {mode}")
        self.chunks = chunks
        self.mode = mode
        self.chunk_terms = {chunk.id: term_counts(f"{chunk.title} {chunk.text}") for chunk in chunks}
        self.idf = _idf(self.chunk_terms.values())
        self.chunk_embeddings = {
            chunk.id: _dense_embedding(f"{chunk.title} {chunk.text}")
            for chunk in chunks
        }

    def search(self, query: str, top_k: int, rerank: bool = False) -> list[tuple[Chunk, float]]:
        query_terms = term_counts(query)
        query_tokens = set(tokenize(query))
        query_embedding = _dense_embedding(query)
        scored = []
        for chunk in self.chunks:
            lexical = cosine(query_terms, self.chunk_terms[chunk.id], self.idf)
            phrase_overlap = len(query_tokens & set(self.chunk_terms[chunk.id])) / max(len(query_tokens), 1)
            dense = _vector_cosine(query_embedding, self.chunk_embeddings[chunk.id])
            if self.mode == "lexical":
                score = lexical
            elif self.mode == "hybrid":
                score = lexical + 0.18 * phrase_overlap
            elif self.mode == "dense":
                score = dense
            else:
                score = 0.56 * lexical + 0.44 * dense + 0.12 * phrase_overlap
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


def _dense_embedding(text: str, dimensions: int = 96) -> list[float]:
    """Deterministic mock dense embedding.

    This provides a stable local dense retrieval condition without downloading
    sentence-transformers models during artifact review. Tokens are projected
    into signed hashing buckets and L2 normalized.
    """
    vector = [0.0] * dimensions
    for token in tokenize(text):
        digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
        if len(token) > 5:
            stem = token[:5]
            stem_digest = blake2b(stem.encode("utf-8"), digest_size=8).digest()
            stem_bucket = int.from_bytes(stem_digest[:4], "big") % dimensions
            vector[stem_bucket] += 0.45 * sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def _vector_cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
