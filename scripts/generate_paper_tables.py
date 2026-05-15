from __future__ import annotations

import csv
from pathlib import Path


def csv_to_markdown(csv_path: Path, md_path: Path, limit: int | None = None) -> None:
    rows = list(csv.DictReader(csv_path.open()))
    if limit:
        rows = rows[:limit]
    if not rows:
        return
    md_path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def csv_to_latex(csv_path: Path, tex_path: Path, limit: int | None = None) -> None:
    rows = list(csv.DictReader(csv_path.open()))
    if limit:
        rows = rows[:limit]
    if not rows:
        return
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys())
    lines = [
        "% Auto-generated table. Copy into manuscript or \\input{} as needed.",
        "\\begin{tabular}{" + "l" * len(headers) + "}",
        "\\toprule",
        " & ".join(headers).replace("_", "\\_") + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        values = [str(row[h]).replace("_", "\\_") for h in headers]
        lines.append(" & ".join(values) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    tex_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    mappings = [
        ("results/default/tables/summary_metrics.csv", "paper/tables/main_summary_metrics"),
        ("results/default/tables/query_type_summary.csv", "paper/tables/query_type_performance"),
        ("results/default/tables/pareto_frontier_data.csv", "paper/tables/pareto_frontier"),
        ("results/sensitivity/hallucination_weighting.csv", "paper/tables/hallucination_weighting_sensitivity"),
        ("results/sensitivity/hybrid_weight_ablation.csv", "paper/tables/hybrid_weight_ablation"),
        ("results/sensitivity/latency_cost_sensitivity.csv", "paper/tables/latency_cost_sensitivity"),
        ("results/chunk_size_sensitivity/summary_metrics.csv", "paper/tables/chunk_size_sensitivity"),
        ("results/neural_embedding_validation/summary_metrics.csv", "paper/tables/neural_embedding_validation"),
    ]
    for source, target in mappings:
        path = Path(source)
        if path.exists():
            csv_to_markdown(path, Path(target + ".md"), limit=30)
            csv_to_latex(path, Path(target + ".tex"), limit=30)
    print("wrote paper table markdown artifacts")


if __name__ == "__main__":
    main()
