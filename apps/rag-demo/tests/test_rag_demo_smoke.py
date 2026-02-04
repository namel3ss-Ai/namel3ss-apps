from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from namel3ss.config.loader import load_config
from namel3ss.ir.lowering.records import _lower_record
from namel3ss.module_loader.core import load_project
from namel3ss.runtime.backend.upload_store import store_upload
from namel3ss.runtime.ui.actions.build import handle_action
from namel3ss.ui.manifest import build_manifest


def _run(cmd: list[str], *, cwd: Path, env: dict) -> None:
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(
            "Command failed: {}\nstdout:\n{}\nstderr:\n{}".format(
                " ".join(cmd), result.stdout.strip(), result.stderr.strip()
            )
        )


def _git_status_lines(root: Path) -> list[str]:
    result = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _find_action(actions: dict, *, type_name: str, flow: str | None = None) -> str:
    for action_id, entry in actions.items():
        if entry.get("type") != type_name:
            continue
        if flow is not None and entry.get("flow") != flow:
            continue
        return action_id
    raise AssertionError(f"Action not found: type={type_name} flow={flow}")


def _schema_for(project, name: str):
    for record in project.app_ast.records:
        if record.name == name:
            return _lower_record(record)
    raise AssertionError(f"Record schema not found: {name}")


def test_rag_demo_smoke(tmp_path: Path) -> None:
    sys.dont_write_bytecode = True

    app_dir = Path(__file__).resolve().parents[1]
    repo_root = app_dir.parent.parent
    app_path = app_dir / "app.ai"

    persist_root = tmp_path / "persist"
    persist_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["N3_PERSIST_ROOT"] = str(persist_root)
    env["N3_PERSIST_TARGET"] = "memory"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ.update(env)

    baseline_status = _git_status_lines(repo_root)

    _run(["n3", "check", "app.ai"], cwd=app_dir, env=env)

    project = load_project(app_path)
    program = project.program
    config = load_config(app_path=str(app_path), root=str(app_dir))

    from namel3ss.runtime.storage.factory import resolve_store

    store = resolve_store(None, config=config)

    manifest = build_manifest(program, config=config, state={}, store=store)
    actions = manifest.get("actions", {})
    upload_action = _find_action(actions, type_name="upload_select")
    ingest_action = _find_action(actions, type_name="call_flow", flow="ingest_latest")
    answer_action = _find_action(actions, type_name="call_flow", flow="answer_question")

    sample_pdf = app_dir / "assets" / "sample.pdf"
    with sample_pdf.open("rb") as handle:
        metadata = store_upload(
            SimpleNamespace(project_root=str(app_dir), app_path=str(app_path)),
            filename="sample.pdf",
            content_type="application/pdf",
            stream=handle,
        )

    upload_resp = handle_action(program, action_id=upload_action, payload=metadata, store=store, config=config)
    state = upload_resp.get("state") or {}
    store.save_state(state)

    ingest_resp = handle_action(program, action_id=ingest_action, payload={}, store=store, config=config, state=state)
    state = ingest_resp.get("state") or state

    query = "runtime enforces citations"
    payload = {"message": query, "offline": True}
    answer_resp = handle_action(program, action_id=answer_action, payload=payload, store=store, config=config, state=state)
    state = answer_resp.get("state") or state
    handle_action(program, action_id=answer_action, payload=payload, store=store, config=config, state=state)

    answer_schema = _schema_for(project, "Answer")
    answers = store.list_records(answer_schema, limit=10)
    assert len(answers) >= 2

    prev = answers[-2]
    latest = answers[-1]
    assert latest["query"] == query
    assert latest["answer_text"] == prev["answer_text"]
    assert latest["citations"] == prev["citations"]
    assert latest["source_count"] == prev["source_count"]
    assert latest["confidence"] == prev["confidence"]
    assert isinstance(latest["citations"], list)
    assert latest["citations"], "Expected citations for the answer"

    final_status = _git_status_lines(repo_root)
    assert final_status == baseline_status
