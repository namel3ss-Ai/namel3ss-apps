# RAG Demo Runtime Limitations Report

Date: 2026-02-13  
Scope: `apps/rag-demo`  
Runtime target: `namel3ss==0.1.0a20`

## Constraint

Implementation changes are Namel3ss-first.  
If a limitation cannot be implemented in Namel3ss DSL, it is documented here for platform/runtime action.

## Limitation Feasibility Matrix

1. Static-vs-runtime manifest drift
- Namel3ss DSL feasibility: **No (platform responsibility)**
- Reason: `app.ai` cannot enforce server startup parity checks between static compile output and served runtime payload.
- Required platform fix: runtime startup gate that compares `n3 ui` hash with served UI hash and fails fast on mismatch.

2. Missing renderer-registry diagnostics endpoint
- Namel3ss DSL feasibility: **No (platform responsibility)**
- Reason: endpoint exposure is owned by runtime/HTTP server, not app DSL flows.
- Required platform fix: stable registry health endpoint with structured status.

3. Multiple runtime processes bound to same host/port
- Namel3ss DSL feasibility: **No (platform responsibility)**
- Reason: process lifecycle and port locking happen before app DSL execution.
- Required platform fix: single-process lock per `(host, port)` with clear CLI error.

4. Multi-app path mis-targeting
- Namel3ss DSL feasibility: **Partial**
- Reason: app copy can clarify identity, but command target resolution is runtime/CLI behavior.
- Required platform fix: explicit effective app path banner and warning when multiple app roots are present.

5. Missing startup banner (`effective app path + manifest hash`)
- Namel3ss DSL feasibility: **No (platform responsibility)**
- Reason: startup banner is emitted by runtime CLI before UI/session initialization.
- Required platform fix: print effective app path, manifest hash, and renderer-pack status at startup.

## App-Level Status

1. Dependency updated to `namel3ss==0.1.0a20` in:
- `apps/rag-demo/pyproject.toml`
- `.github/workflows/rag-demo-ci.yml`
- `apps/rag-demo/README.md`
- `apps/rag-demo/PHASE1_SPEC.md`

2. Incident documentation updated with current runtime target and feasibility split:
- `apps/rag-demo/CTO_RENDERER_REGISTRY_INCIDENT.md`
