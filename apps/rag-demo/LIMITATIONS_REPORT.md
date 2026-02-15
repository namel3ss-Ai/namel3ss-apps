# RAG Demo Limitations Reports

- Runtime target: `namel3ss==0.1.0a21`
- Last verified: `2026-02-15`
- Current reproducible blockers: `1`

## Renderer registry export contract mismatch (`N3E_RENDERER_REGISTRY_INVALID`)
- Title: Renderer registry export contract mismatch (`N3E_RENDERER_REGISTRY_INVALID`)
- Date: 2026-02-15
- Limitation/Issue:
  - Runtime UI fails with `N3E_RENDERER_REGISTRY_INVALID` even when `/api/renderer-registry/health` reports validated parity.
- Reproduction steps:
  1. `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .`
  3. `curl -sS -o /tmp/renderer_registry_get.js -w '%{http_code}\n' http://127.0.0.1:7360/renderer_registry.js`
  4. `'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' --headless=new --disable-gpu --virtual-time-budget=5000 --dump-dom http://127.0.0.1:7360 > /tmp/rag-dom.html`
  5. `rg "N3E_RENDERER_REGISTRY_INVALID|renderer registry failed to load" /tmp/rag-dom.html`
  6. `curl -sS http://127.0.0.1:7360/renderer_registry.js > /tmp/renderer_registry.js`
  7. `curl -sS http://127.0.0.1:7360/ui_renderer_chat.js > /tmp/ui_renderer_chat.js`
  8. `curl -sS http://127.0.0.1:7360/ui_renderer_rag.js > /tmp/ui_renderer_rag.js`
  9. `sed -n '32,46p' /tmp/renderer_registry.js`
  10. `rg -n "function renderCitationChipsElement|function renderTrustIndicatorElement|root\\.renderCitationChipsElement|root\\.renderTrustIndicatorElement" /tmp/ui_renderer_chat.js /tmp/ui_renderer_rag.js`
- Expected:
  - `health.ok=true`, `registry.status=validated`, and `parity.ok=true` should result in successful UI bootstrap.
- Actual:
  - Startup banner includes `renderer_registry_status":"validated"`.
  - Health JSON includes `"ok": true`, `"registry": {"status": "validated"}`, `"parity": {"ok": true}`.
  - `renderer_registry.js` GET returns `200`.
  - Headless browser DOM contains: `N3E_RENDERER_REGISTRY_INVALID: renderer registry failed to load.`
  - `renderer_registry.js` declares `chat` exports `renderCitationChipsElement` and `renderTrustIndicatorElement`.
  - `ui_renderer_chat.js` only references those symbols.
  - `ui_renderer_rag.js` defines and assigns those symbols.
- Impact on rag-demo:
  - App is not usable in runtime browser UX because rendering aborts before app manifest content is shown.
- DSL-solvable?: no
- If `no`: required platform/runtime change:
  - Fix renderer export ownership/validation contract in runtime assets (`renderer_registry.js` and renderer bootstrap contract/order) so declared exports map to the entrypoint that defines them.
- App-side mitigation implemented:
  - Added deterministic troubleshooting flow in `README.md` with health + asset contract checks.
  - Limited app-side action to diagnostics only; no `.ai` workaround exists for this runtime bootstrap failure.
- Status: blocked

## Startup manifest parity gate
- Title: Startup manifest parity gate
- Date: 2026-02-14
- Limitation/Issue:
  - Historical manifest drift confusion between static and runtime payloads.
- Reproduction steps:
  1. `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq '.parity'`
- Expected:
  - Runtime exposes parity result with manifest hashes.
- Actual:
  - Parity returns `ok=true` with matching `manifest_hash` and `registry_manifest_hash`.
- Impact on rag-demo:
  - Drift triage is now deterministic and quick.
- DSL-solvable?: yes
- If `no`: required platform/runtime change:
  - n/a
- App-side mitigation implemented:
  - README now prioritizes startup parity checks over legacy static-vs-envelope comparisons.
- Status: resolved

## Renderer health endpoint visibility
- Title: Renderer health endpoint visibility
- Date: 2026-02-14
- Limitation/Issue:
  - Older docs used stale renderer endpoints and inconsistent probes.
- Reproduction steps:
  1. `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .`
- Expected:
  - Stable endpoint exposes registry status and parity state.
- Actual:
  - Endpoint returns `schema_version=renderer_registry_health@1` and `registry.status=validated`.
- Impact on rag-demo:
  - Renderer diagnostics are now explicit and deterministic.
- DSL-solvable?: yes
- If `no`: required platform/runtime change:
  - n/a
- App-side mitigation implemented:
  - README and runbook now use only `/api/renderer-registry/health`.
- Status: resolved

## Host/port lock collision handling
- Title: Host/port lock collision handling
- Date: 2026-02-14
- Limitation/Issue:
  - Parallel runs on same host/port previously caused confusing startup behavior.
- Reproduction steps:
  1. `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. `lsof -nP -iTCP:7360 -sTCP:LISTEN`
  3. Start a second run on same port.
- Expected:
  - Second launch fails with lock-owner diagnostics.
- Actual:
  - Runtime emits lock-owner details and guidance to stop existing process or change port.
- Impact on rag-demo:
  - Reduces false debugging of app logic when runtime is simply already bound.
- DSL-solvable?: yes
- If `no`: required platform/runtime change:
  - n/a
- App-side mitigation implemented:
  - README includes listener check and deterministic relaunch flow.
- Status: resolved

## Multi-app path mis-targeting
- Title: Multi-app path mis-targeting
- Date: 2026-02-14
- Limitation/Issue:
  - Ambiguous commands from repo root can target the wrong app path.
- Reproduction steps:
  1. `apps/rag-demo/.venv/bin/n3 check app.ai`
  2. `apps/rag-demo/.venv/bin/n3 check apps/rag-demo/app.ai`
- Expected:
  - Ambiguous target fails; explicit target passes.
- Actual:
  - `check app.ai` fails with `App file not found`.
  - Explicit path check passes (`Parse/Lint/Manifest: OK`).
- Impact on rag-demo:
  - Prevents accidental execution against wrong app context.
- DSL-solvable?: yes
- If `no`: required platform/runtime change:
  - n/a
- App-side mitigation implemented:
  - Explicit app path commands in README and in-app run-target copy.
- Status: resolved

## Startup observability fields
- Title: Startup observability fields
- Date: 2026-02-14
- Limitation/Issue:
  - Startup identity fields were previously missing from normal triage workflows.
- Reproduction steps:
  1. `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. Read startup banner line.
- Expected:
  - Startup line includes `app_path`, `manifest_hash`, `renderer_registry_status`, `lock_path`, `lock_pid`.
- Actual:
  - Runtime startup line includes all expected fields.
- Impact on rag-demo:
  - Faster verification that correct app/runtime instance is running.
- DSL-solvable?: yes
- If `no`: required platform/runtime change:
  - n/a
- App-side mitigation implemented:
  - README includes startup-banner verification command.
- Status: resolved

## CLI entrypoint drift (global vs venv)
- Title: CLI entrypoint drift (global vs venv)
- Date: 2026-02-15
- Limitation/Issue:
  - Global `n3` on PATH can point to a different runtime version than rag-demo venv.
- Reproduction steps:
  1. `which n3 && n3 --version`
  2. `apps/rag-demo/.venv/bin/n3 --version`
  3. `apps/rag-demo/.venv/bin/python -m namel3ss --version`
- Expected:
  - All commands resolve to `namel3ss==0.1.0a21`.
- Actual:
  - Global: `/Library/Frameworks/Python.framework/Versions/3.12/bin/n3` -> `namel3ss 0.1.0a15`.
  - Venv CLI/module: `namel3ss 0.1.0a21`.
- Impact on rag-demo:
  - Can produce stale behavior and incorrect blocker attribution.
- DSL-solvable?: yes
- If `no`: required platform/runtime change:
  - n/a
- App-side mitigation implemented:
  - Operational commands pinned to `apps/rag-demo/.venv/bin/n3`.
- Status: resolved
