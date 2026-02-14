# RAG Demo Limitations Reports

## 1) Manifest Drift Detection

- Title: Static-vs-runtime manifest drift
- Date: 2026-02-14
- Limitation/Issue: Static `n3 ... ui` output can diverge from runtime-served UI payload.
- Reproduction steps:
  1. Run `n3 apps/rag-demo/app.ai ui > /tmp/rag-static-ui.json`.
  2. Start runtime with `n3 run apps/rag-demo/app.ai --port 7360 --no-open`.
  3. Fetch runtime payload from `/api/v1/ui` (or `/api/ui`) into `/tmp/rag-runtime-ui.json`.
  4. Compare using `diff -u /tmp/rag-static-ui.json /tmp/rag-runtime-ui.json`.
- Impact on rag-demo: Developers can trust compile checks but still hit unexpected runtime behavior.
- DSL-solvable?: no
- If no: required platform/runtime change: Add startup parity gate that compares static manifest hash against served payload hash.
- App-side mitigation implemented: Added deterministic explicit-path checks and hash/compare troubleshooting workflow in `apps/rag-demo/README.md`.
- Status: blocked

## 2) Renderer Registry Visibility

- Title: Missing renderer-registry diagnostics visibility
- Date: 2026-02-14
- Limitation/Issue: No stable renderer health endpoint for app-level confirmation.
- Reproduction steps:
  1. Start runtime with `n3 run apps/rag-demo/app.ai --port 7360 --no-open`.
  2. Probe `curl -i http://127.0.0.1:7360/api/renderer-registry`.
  3. Probe `curl -i http://127.0.0.1:7360/api/renderer_registry`.
- Impact on rag-demo: Renderer failures are harder to triage quickly from app workflow.
- DSL-solvable?: no
- If no: required platform/runtime change: Expose a first-class renderer registry health endpoint with structured status.
- App-side mitigation implemented: Added early endpoint probe steps and expected outcome guidance in `apps/rag-demo/README.md`.
- Status: blocked

## 3) Host/Port Process Conflicts

- Title: Multiple runtime processes on same host/port
- Date: 2026-02-14
- Limitation/Issue: Port collisions can produce non-deterministic runtime behavior.
- Reproduction steps:
  1. Start one runtime on `7360`.
  2. Start another runtime process targeting the same host/port.
  3. Observe unstable or conflicting runtime behavior.
- Impact on rag-demo: Preview reliability drops and symptoms can resemble app defects.
- DSL-solvable?: no
- If no: required platform/runtime change: Enforce single runtime lock per `(host, port)` with explicit CLI failure.
- App-side mitigation implemented: Added lock/conflict troubleshooting flow using `lsof` and deterministic relaunch guidance in `apps/rag-demo/README.md`.
- Status: blocked

## 4) Multi-App Path Targeting

- Title: Multi-app path mis-targeting
- Date: 2026-02-14
- Limitation/Issue: In a multi-app repo, developers can run the wrong app unintentionally.
- Reproduction steps:
  1. Run `n3 check app.ai` from a non-target working directory.
  2. Observe command resolves a different app than `apps/rag-demo/app.ai`.
- Impact on rag-demo: Incorrect app validation/run results waste debug time.
- DSL-solvable?: yes
- App-side mitigation implemented:
  1. Added explicit app identity text in `apps/rag-demo/app.ai` (`App Path` and `Run Target` sections).
  2. Updated `apps/rag-demo/README.md` commands to always use `apps/rag-demo/app.ai`.
- Status: resolved

## 5) Startup Observability Gaps

- Title: Missing startup identity/hash/status banner
- Date: 2026-02-14
- Limitation/Issue: Runtime startup does not consistently expose effective app path and manifest hash.
- Reproduction steps:
  1. Start runtime with `n3 run apps/rag-demo/app.ai --port 7360 --no-open`.
  2. Inspect startup output for explicit app path + manifest hash fields.
  3. Observe those fields are not reliably present as first-class startup diagnostics.
- Impact on rag-demo: Slower diagnosis when startup targets are ambiguous.
- DSL-solvable?: no
- If no: required platform/runtime change: Add startup banner including effective app path, manifest hash, and renderer status.
- App-side mitigation implemented: Added manual startup observability checklist (`app path`, versions, manifest hash command) in `apps/rag-demo/README.md`.
- Status: blocked

## Runtime Target

- `namel3ss==0.1.0a21` (PyPI)

## 6) CLI Version String Mismatch

- Title: Installed package version does not match CLI `--version` output
- Date: 2026-02-14
- Limitation/Issue: During upgrade validation, CLI version output temporarily lagged expected package version.
- Reproduction steps:
  1. Run `apps/rag-demo/.venv/bin/python -m pip install -U namel3ss==0.1.0a21`.
  2. Run `apps/rag-demo/.venv/bin/python -m pip show namel3ss` and confirm `Version: 0.1.0a21`.
  3. Run `apps/rag-demo/.venv/bin/n3 --version`.
  4. Run `apps/rag-demo/.venv/bin/python -m namel3ss --version`.
- Impact on rag-demo: Confusing runtime identity checks during startup/debug workflows.
- DSL-solvable?: no
- If no: required platform/runtime change: Ensure CLI/version command sources installed package version consistently.
- App-side mitigation implemented: Re-ran package install and identity checks (`pip show`, `n3 --version`, `python -m namel3ss --version`), then documented deterministic verification commands in `apps/rag-demo/README.md`.
- Status: resolved

## 7) Manifest Snapshot Drift (Test Artifact)

- Title: `manifest_core.json` drift after intentional DSL layout change
- Date: 2026-02-14
- Limitation/Issue: Adding `Run Identity` section in `apps/rag-demo/app.ai` shifted generated action IDs and caused smoke snapshot mismatch.
- Reproduction steps:
  1. Add a new section before chat composer in `apps/rag-demo/app.ai`.
  2. Run `cd apps/rag-demo && ./smoke.sh`.
  3. Observe diff failure in `tests/snapshots/manifest_core.json` for `composer_action.id`.
- Impact on rag-demo: CI/smoke fails until deterministic snapshot is updated to reflect intended manifest.
- DSL-solvable?: yes
- App-side mitigation implemented: Refreshed `apps/rag-demo/tests/snapshots/manifest_core.json` with current deterministic manifest output.
- Status: resolved
