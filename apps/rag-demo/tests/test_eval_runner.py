from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_eval_runner_offline(tmp_path: Path) -> None:
    app_dir = Path(__file__).resolve().parents[1]
    report_path = tmp_path / "report.json"

    cmd = [
        sys.executable,
        "eval/run_eval.py",
        "--offline",
        "--app-dir",
        ".",
        "--golden",
        "eval/golden.json",
        "--report",
        str(report_path),
        "--baseline",
        "eval/report_baseline.json",
        "--fail-on-regression",
    ]

    result = subprocess.run(cmd, cwd=app_dir, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr

    report = json.loads(report_path.read_text(encoding="utf-8"))
    metrics = report["metrics"]

    assert report["offline"] is True
    assert report["deterministic_replay_ok"] is True
    assert report["failures"]["threshold"] == []
    assert report["failures"]["regression"] == []

    assert metrics["citation_coverage"] == 1.0
    assert metrics["citation_correctness"] == 1.0
    assert metrics["expected_citation_constraints"] == 1.0
    assert metrics["helpfulness"] >= 0.67
    assert metrics["no_source_behavior"] == 1.0
    assert metrics["deterministic_replay"] == 1.0
