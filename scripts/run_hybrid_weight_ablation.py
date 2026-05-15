from __future__ import annotations

import csv
from pathlib import Path

from rag_pareto.config import load_config
from rag_pareto.pipeline import run_benchmark


SCENARIOS = {
    "baseline": {"lexical": 0.56, "dense": 0.44, "phrase": 0.12},
    "lexical_dominant": {"lexical": 0.70, "dense": 0.20, "phrase": 0.10},
    "dense_dominant": {"lexical": 0.20, "dense": 0.70, "phrase": 0.10},
    "equal": {"lexical": 0.33, "dense": 0.33, "phrase": 0.33},
    "no_phrase": {"lexical": 0.56, "dense": 0.44, "phrase": 0.00},
}


def main() -> None:
    base = load_config("configs/default.yaml")
    base["variants"] = [v for v in base["variants"] if v["name"] == "hybrid_dense_hash_k5_rerank"]
    output_dir = Path("results/sensitivity/hybrid_weight_ablation_runs")
    rows = []
    for name, weights in SCENARIOS.items():
        cfg = dict(base)
        cfg["hybrid_weights"] = weights
        artifacts = run_benchmark(cfg, output_dir_override=str(output_dir / name))
        with Path(artifacts["summary_metrics"]).open() as handle:
            row = next(csv.DictReader(handle))
            row["scenario"] = name
            row.update({f"weight_{key}": value for key, value in weights.items()})
            rows.append(row)
    target = Path("results/sensitivity/hybrid_weight_ablation.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()

