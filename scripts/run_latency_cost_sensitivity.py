from __future__ import annotations

import csv
from pathlib import Path


SCENARIOS = {
    "local_low_cost": (0.80, 0.80),
    "managed_vector_db": (1.15, 1.25),
    "hosted_llm_expensive": (1.00, 2.00),
    "neural_embedding_cpu": (1.35, 1.20),
    "neural_embedding_gpu_assumed": (0.95, 1.15),
    "high_volume_enterprise": (1.10, 0.75),
}


def main() -> None:
    rows = list(csv.DictReader(Path("results/default/tables/summary_metrics.csv").open()))
    out = []
    for scenario, (latency_multiplier, cost_multiplier) in SCENARIOS.items():
        for row in rows:
            item = dict(row)
            item["scenario"] = scenario
            item["scenario_latency_ms"] = float(row["total_latency_ms"]) * latency_multiplier
            item["scenario_cost"] = float(row["total_cost"]) * cost_multiplier
            out.append(item)
    target = Path("results/sensitivity/latency_cost_sensitivity.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0].keys()))
        writer.writeheader()
        writer.writerows(out)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()

