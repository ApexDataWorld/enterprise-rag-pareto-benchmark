"""Text normalization shared by retrieval, generation, and evaluation."""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def term_counts(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def cosine(left: Counter[str], right: Counter[str], idf: dict[str, float] | None = None) -> float:
    if not left or not right:
        return 0.0
    weights = idf or {}
    keys = set(left) | set(right)
    dot = sum(left.get(k, 0) * right.get(k, 0) * weights.get(k, 1.0) ** 2 for k in keys)
    left_norm = math.sqrt(sum((left.get(k, 0) * weights.get(k, 1.0)) ** 2 for k in keys))
    right_norm = math.sqrt(sum((right.get(k, 0) * weights.get(k, 1.0)) ** 2 for k in keys))
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0

