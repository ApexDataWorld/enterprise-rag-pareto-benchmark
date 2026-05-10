import tempfile
import unittest
from pathlib import Path

from rag_pareto.config import load_config
from rag_pareto.pipeline import run_benchmark


class PipelineTests(unittest.TestCase):
    def test_default_pipeline_writes_artifacts(self):
        config = load_config("configs/default.yaml")
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = run_benchmark(config, output_dir_override=tmp)
            for key in (
                "summary_metrics",
                "query_metrics",
                "statistical_comparisons",
                "confidence_intervals",
                "query_type_summary",
                "pareto_frontier_data",
                "final_summary",
                "consistency_notes",
                "traces",
            ):
                self.assertTrue(Path(artifacts[key]).exists(), key)
            self.assertTrue((Path(tmp) / "figures" / "latency_vs_quality.svg").exists())
            self.assertTrue((Path(tmp) / "figures" / "latency_vs_quality.pdf").exists())
            self.assertTrue((Path(tmp) / "figures" / "query_type_performance.pdf").exists())
            self.assertTrue((Path(tmp) / "run_metadata.json").exists())


if __name__ == "__main__":
    unittest.main()
