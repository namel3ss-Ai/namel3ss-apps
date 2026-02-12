import json
import os
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
N3_BIN = os.environ.get("N3_BIN", str(ROOT_DIR / ".venv" / "bin" / "n3"))
PY_BIN = os.environ.get("PY_BIN", str(ROOT_DIR / ".venv" / "bin" / "python"))


def ensure_provider_manifests() -> None:
    subprocess.run(
        [PY_BIN, "tools/ensure_provider_manifests.py"],
        cwd=ROOT_DIR,
        check=True,
        capture_output=True,
        text=True,
    )


def run_action(action_id: str, payload: dict | None = None) -> dict:
    ensure_provider_manifests()
    cmd = [N3_BIN, "app.ai", action_id, "--json", json.dumps(payload or {})]
    env = dict(os.environ)
    env["N3_IDENTITY_ID"] = "rag-demo-tester"
    proc = subprocess.run(
        cmd,
        cwd=ROOT_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def action_id_for_flow(flow_name: str, *, contains: str | None = None) -> str:
    ensure_provider_manifests()
    proc = subprocess.run(
        [N3_BIN, "app.ai", "ui"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    manifest = json.loads(proc.stdout)
    actions = manifest.get("actions", {})
    for action_id in sorted(actions.keys()):
        entry = actions[action_id]
        if entry.get("type") != "call_flow":
            continue
        if entry.get("flow") != flow_name:
            continue
        if contains and contains not in action_id:
            continue
        return action_id
    raise AssertionError(f"No call_flow action found for {flow_name}")


def test_upload_ingest_ready_via_guided_flow() -> None:
    guided_action = action_id_for_flow("rag_engine.run_demo_mode_path")
    data = run_action(guided_action)
    assert data["result"]["status"] == "seeded"
    assert data["state"]["ready_documents"] >= 1
    assert data["state"]["chunk_count"] >= 1


def test_answer_and_citations_via_guided_flow() -> None:
    guided_action = action_id_for_flow("rag_engine.run_demo_mode_path")
    data = run_action(guided_action)
    assert data["result"]["mode"] == "guided"
    assert data["state"]["answer"]["answer_text"]
    assert len(data["state"]["answer"]["citations"]) >= 1
    assert data["state"]["answer"]["trusted"] is True


def test_open_citation_selects_source() -> None:
    citation_action = action_id_for_flow("rag_engine.open_citation", contains="open_in_source_drawer")
    data = run_action(
        citation_action,
        {"row": {"source_id": "guided-product", "chunk_id": "guided-product-1", "page_number": 1}},
    )
    assert data["result"] == "ok"
    assert data["state"]["selected_citation_source"] == "guided-product"
    assert data["state"]["drawer"]["has_selection"] is True


def test_guided_flow_deterministic_snapshot() -> None:
    guided_action = action_id_for_flow("rag_engine.run_demo_mode_path")
    first = run_action(guided_action)
    second = run_action(guided_action)

    first_view = {
        "status": first["result"]["status"],
        "mode": first["result"]["mode"],
        "answer": first["result"]["answer_text"],
        "citation_count": len(first["state"]["answer"]["citations"]),
        "selected_source": first["state"]["selected_citation_source"],
        "ready_documents": first["state"]["ready_documents"],
        "chunk_count": first["state"]["chunk_count"],
    }
    second_view = {
        "status": second["result"]["status"],
        "mode": second["result"]["mode"],
        "answer": second["result"]["answer_text"],
        "citation_count": len(second["state"]["answer"]["citations"]),
        "selected_source": second["state"]["selected_citation_source"],
        "ready_documents": second["state"]["ready_documents"],
        "chunk_count": second["state"]["chunk_count"],
    }
    assert first_view == second_view


def test_composer_appends_assistant_message_when_no_selection() -> None:
    composer_action = action_id_for_flow("rag_engine.ask_question")
    data = run_action(composer_action, {"message": "what is this doc about"})
    messages = data["state"]["chat"]["messages"]
    assert len(messages) >= 2
    last_message = messages[-1]
    assert last_message["role"] == "assistant"
    assert last_message["content"] == data["result"]["answer_text"]
