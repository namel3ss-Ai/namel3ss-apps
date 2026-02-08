#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from namel3ss.config.loader import load_config
from namel3ss.module_loader.core import load_project
from namel3ss.runtime.backend.upload_store import store_upload
from namel3ss.runtime.storage.factory import resolve_store
from namel3ss.runtime.ui.actions.build import handle_action
from namel3ss.ui.manifest import build_manifest

PROVIDER_ENV_VARS = [
    "N3_ANSWER_PROVIDER",
    "N3_ANSWER_MODEL",
    "NAMEL3SS_OPENAI_API_KEY",
    "OPENAI_API_KEY",
    "NAMEL3SS_ANTHROPIC_API_KEY",
    "ANTHROPIC_API_KEY",
]


@dataclass
class EvalCaseResult:
    id: str
    question: str
    expect_no_source: bool
    answer_mode: str
    answer_text: str
    citations: list[str]
    selected_candidate_ids: list[str]
    citation_coverage: bool
    citation_correctness: bool
    expected_citation_constraints_ok: bool
    theme_score: float
    no_source_behavior_ok: bool


@dataclass
class Thresholds:
    citation_coverage_min: float = 1.0
    citation_correctness_min: float = 1.0
    expected_citation_constraints_min: float = 1.0
    helpfulness_min: float = 0.67
    no_source_behavior_min: float = 1.0
    deterministic_replay_min: float = 1.0


def _prepare_env(*, offline: bool) -> None:
    if not offline:
        return
    # Offline mode is the trust baseline: no networked model calls, same replay every run.
    for key in PROVIDER_ENV_VARS:
        os.environ.pop(key, None)
    os.environ["N3_ANSWER_PROVIDER"] = "none"
    os.environ["N3_ANSWER_MODEL"] = "none"


def _find_action(actions: dict[str, dict[str, Any]], *, type_name: str, flow: str | None = None) -> str:
    for action_id, entry in actions.items():
        if entry.get("type") != type_name:
            continue
        if flow is not None and entry.get("flow") != flow:
            continue
        return action_id
    raise RuntimeError(f"Action not found: type={type_name} flow={flow}")


def _schema_for(program: Any, name: str) -> Any:
    for schema in program.records:
        if schema.name == name:
            return schema
    raise RuntimeError(f"Record schema not found: {name}")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _theme_score(*, answer_text: str, snippets: list[str], expected_themes: list[str]) -> float:
    if not expected_themes:
        return 1.0
    corpus = (answer_text + "\n" + "\n".join(snippets)).lower()
    hits = 0
    for theme in expected_themes:
        token = str(theme or "").strip().lower()
        if not token:
            continue
        if token in corpus:
            hits += 1
    return round(hits / len(expected_themes), 4)


def _citation_constraints_ok(chat_citations: list[dict[str, Any]], expected: list[dict[str, Any]]) -> bool:
    for expected_row in expected:
        source_contains = str(expected_row.get("source_contains") or "").lower()
        page = expected_row.get("page")
        matched = False
        for row in chat_citations:
            source_name = str(row.get("title") or row.get("source_name") or "").lower()
            page_number = row.get("page_number")
            source_ok = source_contains in source_name if source_contains else True
            page_ok = page_number == page if page is not None else True
            if source_ok and page_ok:
                matched = True
                break
        if not matched:
            return False
    return True


def _mean(values: list[float]) -> float:
    if not values:
        return 1.0
    return round(sum(values) / len(values), 4)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return round(numerator / denominator, 4)


def _resolve_app_dir(raw_value: str) -> Path:
    raw = str(raw_value or ".")
    cwd = Path.cwd().resolve()
    script_app_dir = Path(__file__).resolve().parents[1]
    repo_root = Path(__file__).resolve().parents[3]

    candidate_paths = [
        Path(raw).expanduser(),
        cwd / raw,
        script_app_dir,
        repo_root / raw,
    ]

    seen: set[str] = set()
    for candidate in candidate_paths:
        resolved = candidate.resolve()
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        if (resolved / "app.ai").exists():
            return resolved

    raise RuntimeError(
        f"Could not resolve app dir from '{raw_value}'. Expected a directory containing app.ai."
    )


def _ensure_upload_store(app_dir: Path) -> None:
    upload_root = app_dir / ".namel3ss" / "uploads" / "rag_demo"
    upload_root.mkdir(parents=True, exist_ok=True)


def _evaluate_cases(
    *,
    cases: list[dict[str, Any]],
    program: Any,
    store: Any,
    config: Any,
    ask_action: str,
    state: dict[str, Any],
    offline: bool,
) -> tuple[list[EvalCaseResult], dict[str, Any], bool]:
    answer_schema = _schema_for(program, "Answer")
    retrieval_schema = _schema_for(program, "RetrievalCandidate")

    case_results: list[EvalCaseResult] = []
    deterministic_replay_ok = True

    replay_anchor: dict[str, Any] | None = None

    for case in sorted(cases, key=lambda item: str(item.get("id") or "")):
        question = str(case.get("question") or "").strip()
        if not question:
            raise RuntimeError(f"Case {case.get('id')} has empty question")

        payload = {"message": question, "offline": offline}
        response = handle_action(program, action_id=ask_action, payload=payload, store=store, config=config, state=state)
        state = response.get("state") or state

        answers = store.list_records(answer_schema, limit=200)
        latest_answer = answers[-1]

        query_id = int(latest_answer["id"])
        candidate_rows = [
            row for row in store.list_records(retrieval_schema, limit=400) if int(row.get("query_id", -1)) == query_id
        ]
        selected_candidate_ids = [
            str(row.get("chunk_id") or "") for row in candidate_rows if str(row.get("decision") or "") == "selected"
        ]
        selected_candidate_ids = [item for item in selected_candidate_ids if item]

        citations = [str(item) for item in list(latest_answer.get("citations") or []) if str(item)]
        chat_citations = list((state.get("chat") or {}).get("citations") or [])
        snippets = [str(item.get("snippet") or "") for item in chat_citations]

        citation_coverage = len(citations) > 0
        citation_correctness = all(cid in set(selected_candidate_ids) for cid in citations)

        expected_citation_constraints = list(case.get("expected_citations") or [])
        constraints_ok = _citation_constraints_ok(chat_citations, expected_citation_constraints)

        expect_no_source = bool(case.get("expect_no_source"))
        answer_mode = str(state.get("answer_mode") or "")
        no_source_behavior_ok = True
        if expect_no_source:
            no_source_behavior_ok = answer_mode == "no_support" and len(citations) == 0

        score = _theme_score(
            answer_text=str(latest_answer.get("answer_text") or ""),
            snippets=snippets,
            expected_themes=[str(item) for item in list(case.get("expected_answer_themes") or [])],
        )

        case_result = EvalCaseResult(
            id=str(case.get("id") or ""),
            question=question,
            expect_no_source=expect_no_source,
            answer_mode=answer_mode,
            answer_text=str(latest_answer.get("answer_text") or ""),
            citations=citations,
            selected_candidate_ids=selected_candidate_ids,
            citation_coverage=citation_coverage,
            citation_correctness=citation_correctness,
            expected_citation_constraints_ok=constraints_ok,
            theme_score=score,
            no_source_behavior_ok=no_source_behavior_ok,
        )
        case_results.append(case_result)

        if replay_anchor is None and not expect_no_source:
            replay_anchor = {
                "question": question,
                "answer_text": case_result.answer_text,
                "citations": case_result.citations,
            }

    if replay_anchor is not None:
        replay_response = handle_action(
            program,
            action_id=ask_action,
            payload={"message": replay_anchor["question"], "offline": offline},
            store=store,
            config=config,
            state=state,
        )
        replay_state = replay_response.get("state") or state
        replay_answers = store.list_records(answer_schema, limit=300)
        latest_replay = replay_answers[-1]

        deterministic_replay_ok = (
            str(latest_replay.get("answer_text") or "") == str(replay_anchor["answer_text"])
            and list(latest_replay.get("citations") or []) == list(replay_anchor["citations"])
        )
        state = replay_state

    metrics = _build_metrics(case_results, deterministic_replay_ok)
    return case_results, metrics, deterministic_replay_ok


def _build_metrics(case_results: list[EvalCaseResult], deterministic_replay_ok: bool) -> dict[str, float]:
    no_source_cases = [case for case in case_results if case.expect_no_source]
    sourced_cases = [case for case in case_results if case not in no_source_cases]

    citation_coverage = _ratio(
        sum(1 for case in sourced_cases if case.citation_coverage),
        len(sourced_cases),
    )
    citation_correctness = _ratio(
        sum(1 for case in sourced_cases if case.citation_correctness),
        len(sourced_cases),
    )
    constraints_ok = _ratio(
        sum(1 for case in sourced_cases if case.expected_citation_constraints_ok),
        len(sourced_cases),
    )
    helpfulness = _mean([case.theme_score for case in sourced_cases])
    no_source_behavior = _ratio(
        sum(1 for case in no_source_cases if case.no_source_behavior_ok),
        len(no_source_cases),
    )

    return {
        "citation_coverage": citation_coverage,
        "citation_correctness": citation_correctness,
        "expected_citation_constraints": constraints_ok,
        "helpfulness": helpfulness,
        "no_source_behavior": no_source_behavior,
        "deterministic_replay": 1.0 if deterministic_replay_ok else 0.0,
    }


def _compare_with_baseline(report_metrics: dict[str, float], baseline_metrics: dict[str, float]) -> list[str]:
    failures: list[str] = []
    soft_drop = {"helpfulness": 0.1}

    for key, current in report_metrics.items():
        if key not in baseline_metrics:
            continue
        baseline = float(baseline_metrics[key])
        drop = baseline - float(current)
        allowed_drop = soft_drop.get(key, 0.0)
        if drop > allowed_drop:
            failures.append(
                f"metric {key} regressed from {baseline:.4f} to {float(current):.4f} (allowed drop {allowed_drop:.4f})"
            )
    return failures


def _threshold_failures(metrics: dict[str, float], thresholds: Thresholds) -> list[str]:
    failures: list[str] = []
    if metrics["citation_coverage"] < thresholds.citation_coverage_min:
        failures.append("citation_coverage below threshold")
    if metrics["citation_correctness"] < thresholds.citation_correctness_min:
        failures.append("citation_correctness below threshold")
    if metrics["expected_citation_constraints"] < thresholds.expected_citation_constraints_min:
        failures.append("expected_citation_constraints below threshold")
    if metrics["helpfulness"] < thresholds.helpfulness_min:
        failures.append("helpfulness below threshold")
    if metrics["no_source_behavior"] < thresholds.no_source_behavior_min:
        failures.append("no_source_behavior below threshold")
    if metrics["deterministic_replay"] < thresholds.deterministic_replay_min:
        failures.append("deterministic_replay below threshold")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic evals for apps/rag-demo")
    parser.add_argument("--app-dir", default="apps/rag-demo", help="rag-demo directory")
    parser.add_argument("--golden", default="eval/golden.json", help="golden dataset path relative to app dir")
    parser.add_argument("--report", default="eval/report.json", help="output report path relative to app dir")
    parser.add_argument("--baseline", default="eval/report_baseline.json", help="baseline report path relative to app dir")
    parser.add_argument(
        "--offline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="force offline/citations-only mode",
    )
    parser.add_argument("--fail-on-regression", action="store_true", help="fail when metrics regress vs baseline")
    args = parser.parse_args()

    app_dir = _resolve_app_dir(args.app_dir)
    app_path = app_dir / "app.ai"
    golden_path = app_dir / args.golden
    report_path = app_dir / args.report
    baseline_path = app_dir / args.baseline

    _prepare_env(offline=args.offline)

    project = load_project(app_path)
    program = project.program
    config = load_config(app_path=str(app_path), root=str(app_dir))
    store = resolve_store(None, config=config)

    manifest = build_manifest(program, config=config, state={}, store=store)
    actions = manifest.get("actions", {})
    upload_action = _find_action(actions, type_name="upload_select")
    sync_action = _find_action(actions, type_name="call_flow", flow="sync_library")
    ingest_action = _find_action(actions, type_name="call_flow", flow="ingest_selected")
    ask_action = _find_action(actions, type_name="call_flow", flow="ask_question")
    _ensure_upload_store(app_dir)

    sample_files = [
        ("sample.pdf", "application/pdf"),
        ("sample.md", "text/markdown"),
        ("sample.txt", "text/plain"),
    ]

    state: dict[str, Any] = {}
    for file_name, content_type in sample_files:
        path = app_dir / "assets" / file_name
        if not path.exists():
            continue
        with path.open("rb") as handle:
            metadata = store_upload(
                SimpleNamespace(project_root=str(app_dir), app_path=str(app_path)),
                filename=file_name,
                content_type=content_type,
                stream=handle,
            )
        upload_resp = handle_action(program, action_id=upload_action, payload=metadata, store=store, config=config, state=state)
        state = upload_resp.get("state") or state

    sync_resp = handle_action(program, action_id=sync_action, payload={}, store=store, config=config, state=state)
    state = sync_resp.get("state") or state

    ingest_resp = handle_action(program, action_id=ingest_action, payload={}, store=store, config=config, state=state)
    state = ingest_resp.get("state") or state

    golden = _load_json(golden_path)
    cases = list(golden.get("cases") or [])

    case_results, metrics, deterministic_replay_ok = _evaluate_cases(
        cases=cases,
        program=program,
        store=store,
        config=config,
        ask_action=ask_action,
        state=state,
        offline=args.offline,
    )

    thresholds = Thresholds()
    threshold_failures = _threshold_failures(metrics, thresholds)
    baseline_failures: list[str] = []

    if args.fail_on_regression and baseline_path.exists():
        baseline_report = _load_json(baseline_path)
        baseline_metrics = dict((baseline_report.get("metrics") or {}))
        baseline_failures = _compare_with_baseline(metrics, baseline_metrics)

    report = {
        "version": 1,
        "offline": bool(args.offline),
        "deterministic_replay_ok": bool(deterministic_replay_ok),
        "metrics": metrics,
        "thresholds": {
            "citation_coverage_min": thresholds.citation_coverage_min,
            "citation_correctness_min": thresholds.citation_correctness_min,
            "expected_citation_constraints_min": thresholds.expected_citation_constraints_min,
            "helpfulness_min": thresholds.helpfulness_min,
            "no_source_behavior_min": thresholds.no_source_behavior_min,
            "deterministic_replay_min": thresholds.deterministic_replay_min,
        },
        "cases": [
            {
                "id": case.id,
                "question": case.question,
                "expect_no_source": case.expect_no_source,
                "answer_mode": case.answer_mode,
                "answer_text": case.answer_text,
                "citations": case.citations,
                "selected_candidate_ids": case.selected_candidate_ids,
                "citation_coverage": case.citation_coverage,
                "citation_correctness": case.citation_correctness,
                "expected_citation_constraints_ok": case.expected_citation_constraints_ok,
                "theme_score": case.theme_score,
                "no_source_behavior_ok": case.no_source_behavior_ok,
            }
            for case in case_results
        ],
        "failures": {
            "threshold": threshold_failures,
            "regression": baseline_failures,
        },
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    # Sorted keys keep report diffs stable and human-reviewable in CI.
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if threshold_failures or baseline_failures:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print(json.dumps({"report": report_path.as_posix(), "metrics": metrics}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
