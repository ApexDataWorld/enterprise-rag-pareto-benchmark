"""Deterministic hashing embedding provider."""

from __future__ import annotations

import math
from hashlib import blake2b

from rag_pareto.text import tokenize


class HashEmbeddingProvider:
    name = "local_hashing_embedding_v1"

    def __init__(self, dimensions: int = 96):
        self.dimensions = dimensions

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [self.encode_one(text) for text in texts]

    def encode_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
            if len(token) > 5:
                stem = token[:5]
                stem_digest = blake2b(stem.encode("utf-8"), digest_size=8).digest()
                stem_bucket = int.from_bytes(stem_digest[:4], "big") % self.dimensions
                vector[stem_bucket] += 0.45 * sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

