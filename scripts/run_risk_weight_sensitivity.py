from __future__ import annotations

import csv
from pathlib import Path


WEIGHTS = [(0.50, 0.50), (0.65, 0.35), (0.80, 0.20), (0.90, 0.10)]


def main() -> None:
    source = Path("results/default/tables/query_metrics.csv")
    rows = list(csv.DictReader(source.open()))
    output = Path("results/sensitivity/hallucination_weighting.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    out_rows = []
    for fw, cw in WEIGHTS:
        for row in rows:
            risk = max(0.0, 1.0 - (fw * float(row["faithfulness"]) + cw * float(row["answer_term_coverage"])))
            out_rows.append({
                "variant": row["variant"],
                "query_id": row["query_id"],
                "faithfulness_weight": fw,
                "coverage_weight": cw,
                "hallucination_risk": risk,
            })
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()

