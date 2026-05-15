import shutil
from pathlib import Path

from rag_pareto.cli import main


if __name__ == "__main__":
    main(["run", "--config", "configs/neural_embedding_validation.yaml"])
    out = Path("results/neural_embedding_validation")
    aliases = {
        out / "tables" / "query_metrics.csv": out / "query_metrics.csv",
        out / "tables" / "summary_metrics.csv": out / "summary_metrics.csv",
        out / "tables" / "pareto_frontier_data.csv": out / "pareto_frontier.csv",
        out / "tables" / "statistical_comparisons.csv": out / "statistical_tests.csv",
        out / "tables" / "confidence_intervals.csv": out / "bootstrap_ci.csv",
    }
    for source, target in aliases.items():
        if source.exists():
            shutil.copyfile(source, target)
