import csv
import subprocess
import sys
import unittest
from pathlib import Path


class SensitivityArtifactTests(unittest.TestCase):
    def test_risk_weighting_script_writes_rows(self):
        subprocess.run(
            [sys.executable, "scripts/run_main_benchmark.py"],
            check=True,
            env={"PYTHONPATH": "src"},
        )
        subprocess.run(
            [sys.executable, "scripts/run_risk_weight_sensitivity.py"],
            check=True,
            env={"PYTHONPATH": "src"},
        )
        path = Path("results/sensitivity/hallucination_weighting.csv")
        self.assertTrue(path.exists())
        with path.open() as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()

