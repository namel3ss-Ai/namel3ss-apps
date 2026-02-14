# To: CTO, Namel3ss
## Subject: Incident Report - `N3E_RENDERER_REGISTRY_INVALID` in `rag-demo`
## Date: 2026-02-13

## Executive Summary
The `rag-demo` workspace app compiles successfully but intermittently fails in browser runtime with:

`N3E_RENDERER_REGISTRY_INVALID: renderer registry failed to load.`

This is primarily a runtime consistency problem, not a parser/lint issue in `.ai` files.

## Environment
- Incident runtime: `namel3ss 0.1.0a19`
- Current target runtime: `namel3ss 0.1.0a21`
- Host: Windows 11
- App paths involved:
  - `apps/rag-demo/app.ai`
  - `apps/rag-demo/examples/rag_workspace/app.ai`

## Verified Facts
1. `n3 check apps/rag-demo/examples/rag_workspace/app.ai` returns Parse/Lint/Manifest OK.
2. `n3 ... ui` static output includes expected `rag.*` flows.
3. During failure windows, multiple runtimes were bound to `localhost:7360`.
4. Live `/api/ui` payload sometimes differed from static `n3 ui` output.
5. Registry-related endpoints (`/api/renderer-registry`, `/api/renderer_registry`) returned 404.

## User Impact
- Fatal renderer initialization error blocks UI rendering.
- Operator cannot rely on `n3 check` success as a guarantee of runtime readiness.
- Conflicting runtime processes create non-deterministic behavior at preview URL.

## Technical Limitations Identified
1. Static-vs-runtime manifest drift is possible.
2. Renderer registry diagnostics are not externally observable via stable endpoint.
3. Multiple active runtime processes on the same port are not prevented clearly.
4. App-path resolution in multi-app repos is easy to mis-target operationally.
5. Runtime startup lacks explicit "effective app path + manifest hash" banner.

## Mitigations Applied in `rag-demo`
1. Added deterministic RAG workspace package under:
   - `apps/rag-demo/examples/rag_workspace/modules/rag/*.ai`
   - `apps/rag-demo/examples/rag_workspace/app.ai`
2. Upgraded dependency to `namel3ss==0.1.0a21` in `apps/rag-demo/pyproject.toml`.
3. Reduced risky renderer usage and stabilized action wiring for citation open flow.
4. Added deterministic citation id in record model (`id = citation_id`).
5. Removed temporary non-`.ai` test scaffolding introduced during debugging.

## Namel3ss-Only Constraint
Per implementation policy, changes must be authored in Namel3ss DSL where possible.  
The runtime/process limitations listed above are platform responsibilities and cannot be fully implemented inside `app.ai` alone.

See `apps/rag-demo/LIMITATIONS_REPORT.md` for:
1. feasibility status per limitation,
2. what can be done in Namel3ss today,
3. what must be fixed in runtime/CLI.

## Remaining Platform Risks
1. Renderer registry failures can persist despite valid compile/lint status.
2. Platform-level registry endpoint stability is still not guaranteed.
3. Manifest drift is now detectable quickly but still requires platform fixes to prevent.

## Recommendations
1. Enforce strict single-process lock per `(host, port)` runtime instance.
2. Print effective app path + manifest hash + renderer-pack status on startup.
3. Provide first-class registry health endpoint and startup health gate.
4. Guarantee parity between `n3 ui` and served `/api/ui` for identical session/app.
5. Add explicit CLI warning when multiple app roots are present in workspace.

## Conclusion
The app-level implementation is now deterministic and Namel3ss-native. The persistent browser error is dominated by runtime registry/process consistency limitations and needs platform hardening for reliable preview behavior.
