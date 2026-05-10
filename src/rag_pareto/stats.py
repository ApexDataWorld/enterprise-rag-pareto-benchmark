"""Lightweight statistical comparisons for benchmark tables."""

from __future__ import annotations

from statistics import mean


def paired_sign_test(baseline: list[float], candidate: list[float]) -> dict[str, float]:
    """Two-sided exact sign test for paired query-level metric values."""
    if len(baseline) != len(candidate):
        raise ValueError("paired samples must have the same length")
    wins = sum(1 for b, c in zip(baseline, candidate) if c > b)
    losses = sum(1 for b, c in zip(baseline, candidate) if c < b)
    n = wins + losses
    if n == 0:
        p_value = 1.0
    else:
        tail = sum(_comb(n, i) for i in range(0, min(wins, losses) + 1)) / (2**n)
        p_value = min(1.0, 2 * tail)
    deltas = [c - b for b, c in zip(baseline, candidate)]
    return {"mean_delta": mean(deltas), "wins": float(wins), "losses": float(losses), "raw_p_value": p_value}


def benjamini_hochberg(rows: list[dict[str, float | str]], alpha: float = 0.05) -> list[dict[str, float | str | bool]]:
    indexed = sorted(enumerate(rows), key=lambda item: float(item[1]["raw_p_value"]))
    m = len(indexed)
    adjusted = [1.0] * m
    running = 1.0
    for rank_from_end, (original_index, row) in enumerate(reversed(indexed), start=1):
        rank = m - rank_from_end + 1
        value = min(running, float(row["raw_p_value"]) * m / rank)
        adjusted[original_index] = value
        running = value
    output = []
    for row, adj in zip(rows, adjusted):
        enriched = dict(row)
        enriched["bh_adjusted_p_value"] = adj
        enriched["significant_raw"] = float(row["raw_p_value"]) < alpha
        enriched["significant_bh"] = adj < alpha
        output.append(enriched)
    return output


def bootstrap_ci(values: list[float], rng_seed: int, samples: int = 1000) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}
    import random

    rng = random.Random(rng_seed)
    n = len(values)
    means = []
    for _ in range(samples):
        draw = [values[rng.randrange(n)] for _ in range(n)]
        means.append(mean(draw))
    means.sort()
    lower_index = int(0.025 * (samples - 1))
    upper_index = int(0.975 * (samples - 1))
    return {"mean": mean(values), "ci_lower": means[lower_index], "ci_upper": means[upper_index]}


def _comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result
