# RAG Demo Limitations Reports

- Runtime target: `namel3ss==0.1.0a21`
- Verification date: `2026-02-14`
- Current reproducible blockers: none

## Startup manifest parity gate
- Date: 2026-02-14
- Status: resolved
- Repro:
  1. Start runtime: `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. Check parity payload: `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .`
- Expected:
  - Runtime exposes a first-class parity signal for renderer manifest vs registry wiring.
- Actual:
  - Endpoint returned `"ok": true`.
  - Payload included `"parity": {"ok": true, "manifest_hash": "0a319f93b39ba8da937f385da754c10b71f4ce89bd21a16040c64180884b9c20", "registry_manifest_hash": "0a319f93b39ba8da937f385da754c10b71f4ce89bd21a16040c64180884b9c20", "renderer_count": 19}`.
- App-side fix:
  - Troubleshooting flow now starts with parity/health validation, not static-vs-runtime manifest diffing.
- Platform dependency (if any):
  - none

## Renderer health endpoint (`/api/renderer-registry/health`)
- Date: 2026-02-14
- Status: resolved
- Repro:
  1. Start runtime: `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. Call health endpoint: `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .`
- Expected:
  - Stable endpoint returns renderer registry validation state.
- Actual:
  - Payload returned `"schema_version": "renderer_registry_health@1"`.
  - Payload returned `"registry": {"ok": true, "status": "validated", "renderer_count": 19}`.
- App-side fix:
  - README and in-app run-target guidance now use this endpoint as the canonical renderer diagnostic.
- Platform dependency (if any):
  - none

## Host/port lock collision handling
- Date: 2026-02-14
- Status: resolved
- Repro:
  1. Start runtime: `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. Verify listener: `lsof -nP -iTCP:7360 -sTCP:LISTEN`
  3. Attempt second runtime on same port: `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open`
- Expected:
  - Second launch fails deterministically with lock-owner diagnostics.
- Actual:
  - Listener check output: `Python ... TCP 127.0.0.1:7360 (LISTEN)`.
  - Second launch output:
    - `What happened: Runtime already running on local:7360.`
    - `Why: Active lock owner pid=71290 command='apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open'.`
    - `Fix: Stop the running process or choose another port.`
- App-side fix:
  - README troubleshooting keeps `lsof` pre-check and explicit-path relaunch guidance.
- Platform dependency (if any):
  - none

## Multi-app targeting warnings and explicit-path workflow
- Date: 2026-02-14
- Status: resolved
- Repro:
  1. Run an ambiguous/non-explicit command from repo root: `apps/rag-demo/.venv/bin/n3 check app.ai`
  2. Run explicit target command: `apps/rag-demo/.venv/bin/n3 check apps/rag-demo/app.ai`
- Expected:
  - Non-explicit command should fail with correction guidance.
  - Explicit app path should pass.
- Actual:
  - Non-explicit command output:
    - `Parse: FAIL`
    - `What happened: App file not found: /Users/disanssebowabasalidde/Documents/GitHub/namel3ss-apps/app.ai`
    - `Fix: Check the path or run commands from the project directory.`
  - Explicit command output:
    - `Parse: OK`
    - `Lint: OK`
    - `Manifest: OK`
    - `Actions: 49 discovered`
- App-side fix:
  - `app.ai` contains explicit run-target instructions.
  - README uses explicit `apps/rag-demo/app.ai` in all run/check commands.
- Platform dependency (if any):
  - none

## Startup banner fields (app path/hash/renderer/lock)
- Date: 2026-02-14
- Status: resolved
- Repro:
  1. `apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7361 --no-open --dry 2>&1 | tee /tmp/rag-start.log`
  2. `rg "Runtime startup|manifest_hash|renderer_registry_status|lock_path|lock_pid" /tmp/rag-start.log`
- Expected:
  - Startup banner includes app identity and diagnostic fields for fast triage.
- Actual:
  - Startup line:
    - `Runtime startup {"app_path":"/Users/disanssebowabasalidde/Documents/GitHub/namel3ss-apps/apps/rag-demo/app.ai","bind_host":"127.0.0.1","bind_port":7361,"headless":false,"lock_path":"/var/folders/z_/8w_d_2vj7zq09fwlvhd8js_80000gn/T/namel3ss_runtime_locks/runtime_port_local_7361.lock.json","lock_pid":71248,"manifest_hash":"92fe0b6c4967c11e698eb0d6f4b262a91179d004ed01d8b7c438282b76fa15a7","mode":"run","renderer_registry_hash":"0a319f93b39ba8da937f385da754c10b71f4ce89bd21a16040c64180884b9c20","renderer_registry_status":"validated"}`
- App-side fix:
  - README startup checks now use banner-field verification.
- Platform dependency (if any):
  - none
