from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from namel3ss.config.loader import load_config
from namel3ss.module_loader.core import load_project
from namel3ss.runtime.backend.upload_store import store_upload
from namel3ss.runtime.ui.actions.build import handle_action
from namel3ss.ui.manifest import build_manifest

OFFLINE_EXPLAIN_MESSAGE = "Explain validation unavailable in citations-only mode."
FALLBACK_EXPLAIN_MESSAGE = "Provider unavailable. Validation metadata not produced."
PROVIDER_ENV_VARS = [
    "N3_ANSWER_PROVIDER",
    "N3_ANSWER_MODEL",
    "NAMEL3SS_OPENAI_API_KEY",
    "OPENAI_API_KEY",
    "NAMEL3SS_ANTHROPIC_API_KEY",
    "ANTHROPIC_API_KEY",
]


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> None:
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


def _schema_for(program, name: str):
    for record_schema in program.records:
        if record_schema.name == name:
            return record_schema
    raise AssertionError(f"Record schema not found: {name}")


def _prepare_test_env(*, persist_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["N3_PERSIST_ROOT"] = str(persist_root)
    env["N3_PERSIST_TARGET"] = "memory"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    # Keep smoke tests deterministic and fully offline.
    for key in PROVIDER_ENV_VARS:
        env.pop(key, None)
        os.environ.pop(key, None)

    env["N3_ANSWER_PROVIDER"] = "none"
    env["N3_ANSWER_MODEL"] = "none"

    os.environ.update(env)
    return env


def test_rag_demo_smoke(tmp_path: Path) -> None:
    sys.dont_write_bytecode = True

    app_dir = Path(__file__).resolve().parents[1]
    repo_root = app_dir.parent.parent
    app_path = app_dir / "app.ai"

    persist_root = tmp_path / "persist"
    persist_root.mkdir(parents=True, exist_ok=True)

    env = _prepare_test_env(persist_root=persist_root)
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
    sync_action = _find_action(actions, type_name="call_flow", flow="sync_library")
    ingest_action = _find_action(actions, type_name="call_flow", flow="ingest_selected")
    ask_action = _find_action(actions, type_name="call_flow", flow="ask_question")

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

    sync_resp = handle_action(program, action_id=sync_action, payload={}, store=store, config=config, state=state)
    state = sync_resp.get("state") or state

    ingest_resp = handle_action(program, action_id=ingest_action, payload={}, store=store, config=config, state=state)
    state = ingest_resp.get("state") or state

    doc_schema = _schema_for(program, "DocumentLibrary")
    docs = store.list_records(doc_schema, limit=10)
    assert docs, "Expected at least one document in library"
    assert docs[0]["upload_id"]
    assert docs[0]["selected"] is True
    assert docs[0]["status"] in {"uploaded", "indexed", "blocked"}

    query = "runtime enforces citations"
    payload = {"message": query, "offline": True}

    first_resp = handle_action(program, action_id=ask_action, payload=payload, store=store, config=config, state=state)
    state = first_resp.get("state") or state
    second_resp = handle_action(program, action_id=ask_action, payload=payload, store=store, config=config, state=state)
    state = second_resp.get("state") or state

    answer_schema = _schema_for(program, "Answer")
    answers = store.list_records(answer_schema, limit=20)
    assert len(answers) >= 2

    prev = answers[-2]
    latest = answers[-1]
    assert latest["query"] == query
    assert latest["answer_text"], "Expected a non-empty answer"
    assert latest["answer_text"] == prev["answer_text"]
    assert latest["citations"] == prev["citations"]
    assert latest["source_count"] == prev["source_count"]
    assert latest["confidence"] == prev["confidence"]
    assert isinstance(latest["citations"], list)
    assert latest["citations"], "Expected citations for the answer"
    assert all(isinstance(cid, str) and cid for cid in latest["citations"])

    chat = state.get("chat") or {}
    chat_citations = chat.get("citations") or []
    chat_chunk_ids = [row.get("chunk_id") for row in chat_citations]
    assert chat_chunk_ids == latest["citations"], "Citation ids must stay in stable order"

    citation_schema = _schema_for(program, "CitationCard")
    citation_cards = store.list_records(citation_schema, limit=50)
    assert citation_cards, "Expected citation cards after answer"
    assert [row["id"] for row in citation_cards] == list(range(1, len(citation_cards) + 1))
    assert [row["chunk_id"] for row in citation_cards] == latest["citations"]

    assert state.get("loading") is False
    assert len(chat.get("messages") or []) >= 4

    explain_schema = _schema_for(program, "ExplainSummary")
    explain_rows = store.list_records(explain_schema, limit=5)
    if explain_rows:
        latest_explain = explain_rows[-1]
        assert latest_explain["query"] == query
        assert latest_explain["citation_count"] >= 0
    else:
        assert state.get("answer_error") == OFFLINE_EXPLAIN_MESSAGE

    provider_fallback_resp = handle_action(
        program,
        action_id=ask_action,
        payload={"message": query},
        store=store,
        config=config,
        state=state,
    )
    provider_fallback_state = provider_fallback_resp.get("state") or {}
    assert provider_fallback_state.get("answer_text")
    assert provider_fallback_state.get("answer_citations") == latest["citations"]
    assert provider_fallback_state.get("answer_error") == FALLBACK_EXPLAIN_MESSAGE

    notice_schema = _schema_for(program, "Notice")
    notices = store.list_records(notice_schema, limit=5)
    assert notices, "Expected a UI notice message"
    assert notices[-1]["message"]

    final_status = _git_status_lines(repo_root)
    assert final_status == baseline_status
