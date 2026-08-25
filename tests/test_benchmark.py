from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rag_eval_workbench.benchmark import run_benchmark

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data/v1/corpus.jsonl"
QUERIES = ROOT / "data/v1/queries.jsonl"
THRESHOLDS = ROOT / "config/regression.json"


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        self.value += 0.001
        return self.value


class BenchmarkTest(unittest.TestCase):
    def test_benchmark_passes_and_is_deterministic_except_metadata(self) -> None:
        first = run_benchmark(CORPUS, QUERIES, k=3, thresholds_path=THRESHOLDS, clock=FakeClock())
        second = run_benchmark(CORPUS, QUERIES, k=3, thresholds_path=THRESHOLDS, clock=FakeClock())
        self.assertTrue(first.passed)
        self.assertEqual(first.payload["metrics"], second.payload["metrics"])
        self.assertEqual(first.payload["queries"], second.payload["queries"])
        self.assertEqual(first.payload["dataset"]["query_count"], 10)

    def test_cli_returns_two_when_regression_gate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            thresholds = root / "impossible.json"
            output = root / "result.json"
            thresholds.write_text(
                json.dumps({"minimum": {"recall_at_k": 1.1}, "maximum": {}}),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rag_eval_workbench.cli",
                    "benchmark",
                    "--corpus",
                    str(CORPUS),
                    "--queries",
                    str(QUERIES),
                    "--thresholds",
                    str(thresholds),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
            self.assertFalse(json.loads(output.read_text(encoding="utf-8"))["regression_gate"]["passed"])


if __name__ == "__main__":
    unittest.main()
