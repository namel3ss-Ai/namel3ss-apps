# RAG Demo Limitations Reports

- Runtime target: `namel3ss==0.1.0a22`
- Last verified: `2026-02-15`

## Runtime Limitation Status (Updated)

1. Static-vs-runtime manifest drift
- Status: resolved in current runtime startup parity guard.

2. Renderer-registry diagnostics endpoint
- Status: resolved.
- Canonical endpoint: `GET /api/renderer-registry/health`.

3. Multiple processes on same host/port
- Status: resolved via runtime lock conflict handling.

4. Multi-app path mis-targeting
- Status: resolved/mitigated.
- Mitigation: explicit app-path commands + workspace warnings.

5. Startup banner identity/hash/status
- Status: resolved.
- Banner includes app path, manifest hash, renderer status/hash, lock metadata.

## Remaining Truly Open Platform Issue

### Renderer registry bootstrap mismatch (`N3E_RENDERER_REGISTRY_INVALID`)
- Date: 2026-02-15
- Status: open (platform-owned)
- Repro:
  1. `PATH="apps/rag-demo/.venv/bin:$PATH" n3 run apps/rag-demo/app.ai --port 7360 --no-open`
  2. `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .`
  3. `'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' --headless=new --disable-gpu --virtual-time-budget=5000 --dump-dom http://127.0.0.1:7360 > /tmp/rag-dom.html`
  4. `rg "N3E_RENDERER_REGISTRY_INVALID|renderer registry failed to load" /tmp/rag-dom.html`
- Expected:
  - Validated registry health should render UI without registry bootstrap failure.
- Actual:
  - Health reports `ok=true`, `registry.status=validated`, `parity.ok=true`.
  - Browser DOM still reports `N3E_RENDERER_REGISTRY_INVALID`.
  - Observed output: `<div>N3E_RENDERER_REGISTRY_INVALID: renderer registry failed to load.</div>`
- App-side mitigation:
  - README troubleshooting points to doctor + health + startup checks.
  - No Namel3ss DSL (`.ai`) fix available for runtime renderer bootstrap behavior.
