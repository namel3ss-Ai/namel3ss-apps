#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANDATORY_CONSTITUTION_SECTIONS = [
    "Article I - Determinism Is a First-Class Invariant",
    "Article II - AI Boundaries Must Be Explicit",
    "Article III - Citations and Provenance Are Product Requirements",
    "Article VI - Failure Must Be Honest and Visible",
    "Non-Amendable Clauses",
    "Amendment Process",
]

FORBIDDEN_NONDETERMINISTIC_TOKENS = [
    "random",
    "uuid",
    "timestamp",
    "now(",
    "current_time",
]

REQUIRED_MODE_MARKERS = [
    '"provider_fallback"',
    '"citations_only"',
    '"no_support"',
    'mode is text must be present',
]

REQUIRED_NOTICE_MARKERS = [
    "Provider unavailable. Running in citations-only mode.",
    "I couldn't find support in your selected sources.",
    "Citations-only mode is active.",
]


@dataclass
class CheckResult:
    check_id: str
    principle: str
    passed: bool
    reason: str
    recovery: str


def _load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _check_constitution(path: Path) -> CheckResult:
    try:
        text = _load_text(path)
    except FileNotFoundError:
        return CheckResult(
            check_id="constitution_present",
            principle="Constitution integrity",
            passed=False,
            reason=f"Missing constitution file: {path}",
            recovery="Create docs/constitution.md with mandatory constitutional sections.",
        )

    missing = [section for section in MANDATORY_CONSTITUTION_SECTIONS if section not in text]
    if missing:
        return CheckResult(
            check_id="constitution_present",
            principle="Constitution integrity",
            passed=False,
            reason=f"Constitution missing required sections: {missing}",
            recovery="Restore required sections or amend through the constitutional process.",
        )

    return CheckResult(
        check_id="constitution_present",
        principle="Constitution integrity",
        passed=True,
        reason="Constitution file present with required sections.",
        recovery="None",
    )


def _check_deterministic_replay(report: dict[str, Any]) -> CheckResult:
    metric = float((report.get("metrics") or {}).get("deterministic_replay", 0.0))
    if metric < 1.0:
        return CheckResult(
            check_id="deterministic_replay_required",
            principle="Article I: Determinism default",
            passed=False,
            reason=f"deterministic_replay metric is {metric:.4f}; expected 1.0000",
            recovery="Run offline eval, inspect changed ordering/state, and restore deterministic replay behavior.",
        )
    return CheckResult(
        check_id="deterministic_replay_required",
        principle="Article I: Determinism default",
        passed=True,
        reason="deterministic_replay metric is 1.0000",
        recovery="None",
    )


def _check_citation_contract(report: dict[str, Any]) -> CheckResult:
    metrics = report.get("metrics") or {}
    coverage = float(metrics.get("citation_coverage", 0.0))
    correctness = float(metrics.get("citation_correctness", 0.0))
    if coverage < 1.0 or correctness < 1.0:
        return CheckResult(
            check_id="citation_contract_required",
            principle="Article III: Citation-first answers",
            passed=False,
            reason=(
                f"Citation contract failed: coverage={coverage:.4f}, "
                f"correctness={correctness:.4f}; expected both 1.0000"
            ),
            recovery="Fix retrieval/answer citation wiring and rerun eval gate.",
        )
    return CheckResult(
        check_id="citation_contract_required",
        principle="Article III: Citation-first answers",
        passed=True,
        reason="citation_coverage and citation_correctness are both 1.0000",
        recovery="None",
    )


def _check_no_silent_degradation(app_text: str) -> CheckResult:
    missing_modes = [marker for marker in REQUIRED_MODE_MARKERS if marker not in app_text]
    missing_notices = [marker for marker in REQUIRED_NOTICE_MARKERS if marker not in app_text]
    if missing_modes or missing_notices:
        return CheckResult(
            check_id="explicit_failure_modes_required",
            principle="Article VI: No silent degradation",
            passed=False,
            reason=(
                "Missing explicit degradation markers: "
                f"modes={missing_modes or 'ok'}, notices={missing_notices or 'ok'}"
            ),
            recovery="Add explicit mode fields and user-visible fallback/no-support notices.",
        )
    return CheckResult(
        check_id="explicit_failure_modes_required",
        principle="Article VI: No silent degradation",
        passed=True,
        reason="Failure modes and notices are explicit in app contract.",
        recovery="None",
    )


def _check_no_nondeterministic_tokens(app_text: str, *, allow_nondeterminism: bool) -> CheckResult:
    if allow_nondeterminism:
        return CheckResult(
            check_id="nondeterministic_tokens_forbidden",
            principle="Article I: No nondeterminism without explicit opt-in",
            passed=True,
            reason="Nondeterminism opt-in enabled for this run.",
            recovery="Disable opt-in for constitutional mode.",
        )

    found: list[str] = []
    lower = app_text.lower()
    for token in FORBIDDEN_NONDETERMINISTIC_TOKENS:
        if token in lower:
            found.append(token)

    if found:
        return CheckResult(
            check_id="nondeterministic_tokens_forbidden",
            principle="Article I: No nondeterminism without explicit opt-in",
            passed=False,
            reason=f"Potential nondeterministic tokens found in app.ai: {sorted(set(found))}",
            recovery="Remove nondeterministic constructs or use an explicit opt-in profile outside constitutional mode.",
        )

    return CheckResult(
        check_id="nondeterministic_tokens_forbidden",
        principle="Article I: No nondeterminism without explicit opt-in",
        passed=True,
        reason="No forbidden nondeterministic tokens detected.",
        recovery="None",
    )


def run_checks(*, app_path: Path, report_path: Path, constitution_path: Path, allow_nondeterminism: bool) -> list[CheckResult]:
    app_text = _load_text(app_path)
    report = _load_json(report_path)

    return [
        _check_constitution(constitution_path),
        _check_deterministic_replay(report),
        _check_citation_contract(report),
        _check_no_nondeterministic_tokens(app_text, allow_nondeterminism=allow_nondeterminism),
        _check_no_silent_degradation(app_text),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run constitutional invariants for namel3ss reference apps.")
    parser.add_argument("--app-dir", default="apps/rag-demo", help="Path to app directory containing app.ai")
    parser.add_argument("--report", default="eval/report.json", help="Path to eval report JSON (relative to app-dir when not absolute)")
    parser.add_argument("--constitution", default="docs/constitution.md", help="Path to constitution markdown")
    parser.add_argument("--out", default="", help="Optional output report path")
    parser.add_argument(
        "--allow-nondeterminism",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Explicit opt-in for nondeterministic token allowance",
    )
    args = parser.parse_args()

    app_dir = Path(args.app_dir).resolve()
    app_path = app_dir / "app.ai"
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = (app_dir / report_path).resolve()
    constitution_path = Path(args.constitution)
    if not constitution_path.is_absolute():
        constitution_path = constitution_path.resolve()

    try:
        results = run_checks(
            app_path=app_path,
            report_path=report_path,
            constitution_path=constitution_path,
            allow_nondeterminism=bool(args.allow_nondeterminism),
        )
    except Exception as err:
        payload = {
            "status": "fail",
            "error": str(err),
            "checks": [],
            "violations": ["invariant execution error"],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    checks_payload = [
        {
            "check_id": item.check_id,
            "principle": item.principle,
            "passed": item.passed,
            "reason": item.reason,
            "recovery": item.recovery,
        }
        for item in results
    ]

    violations = [entry for entry in checks_payload if not entry["passed"]]
    payload = {
        "status": "pass" if not violations else "fail",
        "checks": checks_payload,
        "violations": violations,
    }

    out_path = Path(args.out) if args.out else None
    if out_path is not None:
        if not out_path.is_absolute():
            out_path = (app_dir / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
