from __future__ import annotations

import csv
import shutil
from pathlib import Path

from rag_pareto.config import load_config
from rag_pareto.pipeline import run_benchmark


def main() -> None:
    cfg = load_config("configs/chunk_size_sensitivity.yaml")
    base = load_config(cfg["base_config"])
    output_dir = Path(cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    requested = {item["name"] for item in cfg["variants"]}
    rows = []
    query_rows = []
    baseline_order: list[str] | None = None
    for chunk_cfg in cfg["chunk_sizes"]:
        run_cfg = dict(base)
        run_cfg["chunk"] = chunk_cfg
        run_cfg["variants"] = [variant for variant in base["variants"] if variant["name"] in requested]
        label = f"chunk_{chunk_cfg['size_tokens']}"
        artifacts = run_benchmark(run_cfg, output_dir_override=str(output_dir / label))
        with Path(artifacts["summary_metrics"]).open() as handle:
            summary = list(csv.DictReader(handle))
        with Path(artifacts["query_metrics"]).open() as handle:
            for query_row in csv.DictReader(handle):
                query_row["chunk_size_tokens"] = chunk_cfg["size_tokens"]
                query_row["overlap_tokens"] = chunk_cfg["overlap_tokens"]
                query_rows.append(query_row)
        ranked = sorted(summary, key=lambda row: (-float(row["recall_at_k"]), float(row["hallucination_risk"]), float(row["latency_ms"])))
        if baseline_order is None:
            baseline_order = [row["variant"] for row in ranked]
        for rank, row in enumerate(ranked, start=1):
            row["chunk_size_tokens"] = chunk_cfg["size_tokens"]
            row["overlap_tokens"] = chunk_cfg["overlap_tokens"]
            row["rank"] = rank
            row["baseline_rank"] = baseline_order.index(row["variant"]) + 1 if row["variant"] in baseline_order else ""
            row["rank_shift"] = int(row["baseline_rank"]) - rank if row["baseline_rank"] else ""
            rows.append(row)
    summary_path = output_dir / "summary_metrics.csv"
    if rows:
        with summary_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    shutil.copyfile(summary_path, output_dir / "rank_stability.csv")
    query_path = output_dir / "query_metrics.csv"
    if query_rows:
        with query_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(query_rows[0].keys()))
            writer.writeheader()
            writer.writerows(query_rows)
    print(f"wrote chunk-size sensitivity artifacts to {output_dir}")


if __name__ == "__main__":
    main()
