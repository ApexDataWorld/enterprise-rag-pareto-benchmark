"""Print a concise summary from checked-in benchmark artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


def main() -> None:
    summarize_experiment("Default benchmark", Path("results/default/tables/summary_metrics.csv"))
    summarize_experiment(
        "Neural embedding validation",
        Path("results/neural_embedding_validation/tables/summary_metrics.csv"),
    )


def summarize_experiment(label: str, summary_path: Path) -> None:
    print(f"{label}:")
    if not summary_path.exists():
        print(f"- missing: {summary_path}")
        return
    rows = list(csv.DictReader(summary_path.open("r", encoding="utf-8")))
    if not rows:
        print(f"- no rows in {summary_path}")
        return

    pareto_count = sum(_bool(row["pareto_optimal"]) for row in rows)
    print(f"- source: {summary_path}")
    print(f"- variants: {len(rows)}")
    print(f"- Pareto-optimal variants: {pareto_count}")
    _print_extreme("lowest latency", rows, "latency_ms", min)
    _print_extreme("lowest cost", rows, "cost_usd", min)
    _print_extreme("highest recall", rows, "recall_at_k", max)
    _print_extreme("highest faithfulness", rows, "faithfulness", max)
    _print_extreme("lowest hallucination risk", rows, "hallucination_risk", min)
    print()


def _print_extreme(label: str, rows: list[dict[str, str]], key: str, selector) -> None:
    values = [float(row[key]) for row in rows]
    selected_value = selector(values)
    variants = [row["variant"] for row in rows if float(row[key]) == selected_value]
    joined = ", ".join(variants)
    print(f"- {label}: {joined} ({selected_value:.8g})")


def _bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


if __name__ == "__main__":
    main()
