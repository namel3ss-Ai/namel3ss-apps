# RAG Demo Phase 1 Specification

Status: Proposed for implementation  
Date: February 10, 2026  
Owner: `apps/rag-demo`

## 1. Objective

Phase 1 upgrades the current deterministic RAG demo into a production-grade UX and architecture baseline:

- Batch ingestion with deterministic progress and bulk actions.
- Retrieval tuning that is visual, explainable, and immediately inspectable.
- Citation and trust UX that surfaces evidence inline.
- Diagnostics tables that are deterministic, sortable, and filterable.
- A strict black/white theme token system with consistent spacing.
- Modular source layout with clear ownership and <= 500 LOC per file.
- Dependency target moved to `namel3ss==0.1.0a21`.

## 2. Scope

In scope:

- UI manifest changes in the demo app.
- Record changes for tags, progress, diagnostics controls.
- Ingestion/retrieval flow changes.
- Modular decomposition plan and file boundaries.
- Dependency and local runtime baseline update.

Out of scope:

- New language grammar or primitives.
- New retrieval algorithms beyond deterministic tuning and rerank controls.
- Non-deterministic UI behaviors.

## 3. Baseline and Upgrade Requirements

Current baseline in repo before this spec:

- `app.ai` monolith (~2200 LOC).
- `namel3ss==0.1.0a21`.

Target baseline for Phase 1:

- `namel3ss==0.1.0a21`.
- Python runtime `>=3.14` (required by `namel3ss-0.1.0a21` wheel metadata).
- Local `n3` commands executed from project venv where possible.

Dependency acceptance checks:

1. `python -m namel3ss --version` returns `namel3ss 0.1.0a21`.
2. `n3 check apps/rag-demo/app.ai` succeeds.
3. `python -m pytest -q apps/rag-demo/tests` succeeds in the same venv.

## 4. Determinism Contracts

Every new feature must obey the following contracts.

### 4.1 Ingestion state machine

Per document, ingestion stage is exactly one of:

- `queued`
- `parsing`
- `chunking`
- `embedding`
- `indexing`
- `indexed`
- `failed_parsing`
- `failed_chunking`
- `failed_embedding`
- `failed_indexing`

Allowed transitions:

- `queued -> parsing -> chunking -> embedding -> indexing -> indexed`
- `parsing -> failed_parsing`
- `chunking -> failed_chunking`
- `embedding -> failed_embedding`
- `indexing -> failed_indexing`
- Retry only from `failed_*` back to the corresponding active stage.

No stage skipping is permitted.

### 4.2 Retrieval/ranking determinism

- Candidate IDs are stable (`chunk_id`-anchored).
- Sorting tie-breaker order is fixed and explicit:
  1. `merged_score` (desc)
  2. `semantic_rank` (asc)
  3. `lexical_rank` (asc)
  4. `source_weight` (desc)
  5. `chunk_id` (asc)
- Slider and k-controls only change deterministic weighting/limits; no randomness.

### 4.3 Diagnostics determinism

- Sorting and filtering are pure state transforms.
- Given the same query, corpus, settings, and filters, resulting row order is identical.
- UI defaults are explicit and static.

### 4.4 Theme determinism

- All colors and spacing values are fixed constants.
- No runtime-generated colors, no random variation.

## 5. Functional Requirements

## 5.1 Batch ingestion and tagging

### User-facing behavior

- Support selecting multiple uploads in one action.
- Support bulk actions from a deterministic selection set:
  - `Bulk tag`
  - `Bulk re-index`
  - `Bulk delete`
- Show progress per document and aggregate progress for the batch.
- Expose retry for failed stage(s) per document.

### Data model additions

`DocumentLibrary` additions/changes:

- `tags is json must be present` (array of strings; replace singular `tag` semantics)
- `ingestion_stage is text must be present`
- `progress_percent is number must be present` (0/25/50/75/100)
- `last_error is text must be present`
- `last_indexed_at is number must be present`

`IngestionTask` record (new):

- `task_id` text
- `document_id` text
- `stage` text
- `status` text (`pending|running|failed|completed`)
- `retry_count` number
- `updated_at` number

Bulk selection state:

- `state.library.selected_ids` as deterministic ordered list by `document_id`.

### Flow requirements

- Add dedicated bulk flows (single responsibility):
  - `bulk_tag_documents`
  - `bulk_reindex_documents`
  - `bulk_delete_documents`
- `filter_tags` support must be compatible with multi-tag documents.

## 5.2 Retrieval filtering and tuning

### User-facing behavior

- Replace free numeric lexical/semantic inputs with one slider:
  - Range: `0..100`
  - Meaning: `0 = lexical only`, `100 = semantic only`
- Add live ranking preview that updates when slider or k-values change.
- Expose `semantic_k` and `lexical_k` controls with bounds `1..50`.
- Add tag filters for retrieval scope (`filter_tags` array).

### Ranking math

Let:

- `semantic_weight = slider_value / 100`
- `lexical_weight = 1 - semantic_weight`
- `semantic_norm` and `lexical_norm` are deterministic normalized scores in `[0,1]`

Then:

- `merged_score = (semantic_weight * semantic_norm) + (lexical_weight * lexical_norm) + source_weight_bonus`

`source_weight_bonus` must be deterministic and bounded.

### Flow requirements

- Retrieval flow contract accepts:
  - `filter_tags` (json array)
  - `semantic_k` (number)
  - `lexical_k` (number)
  - `weight_slider` (number)
- Any invalid k-value is clamped deterministically to `[1,50]`.

## 5.3 Citation and answer presentation

### User-facing behavior

- Show citation snippets inline in assistant messages (collapsible section).
- Keep right-side drawer as optional deep inspection, not the primary path.
- Add trust indicator with deterministic rubric.

### Trust rubric

Trust score is deterministic weighted sum:

- `0.5 * retrieval_overlap_score`
- `0.3 * source_quality_score`
- `0.2 * ranking_margin_score`

Trust tiers:

- `>= 0.80`: `High`
- `0.60 - 0.79`: `Medium`
- `< 0.60`: `Low`

All sub-scores must be derived from logged retrieval/ranking evidence only.

## 5.4 Diagnostics improvements

### User-facing behavior

- Retrieval candidate tables are sortable and filterable by:
  - score
  - source
  - tag
  - decision/tier
- Toggle views:
  - semantic candidates
  - lexical candidates
  - merged/final ranking
- Studio-only panels expose:
  - assembled generation context
  - final prompt sent to model

### Data model additions

`DiagnosticsView` state/record fields:

- `candidate_mode` (`semantic|lexical|merged`)
- `sort_by`
- `sort_order`
- `filter_source`
- `filter_tag`
- `score_min`
- `score_max`

Defaults are fixed and deterministic.

## 6. Theme and Spacing Specification

Required token values:

```text
background_primary: #FFFFFF
background_secondary: #F8F8F8
text_primary: #0A0A0A
text_secondary: #4A4A4A
border_color: #E0E0E0
accent_color: #000000

spacing_xs: 4px
spacing_sm: 8px
spacing_md: 16px
spacing_lg: 24px
spacing_xl: 32px
```

Application rules:

- All page background surfaces must use only `background_primary` or `background_secondary`.
- All text must use `text_primary` or `text_secondary`.
- Borders/dividers must use `border_color`.
- Primary action emphasis uses `accent_color` only.
- Spacing across margins/paddings/gaps must use only the spacing scale above.

## 7. Modular Manifest Plan

Target source decomposition (authoritative files):

- `theme_tokens.ai`
- `records.ai`
- `ingestion_flows.ai`
- `retrieval_flows.ai`
- `ui_layout.ai`

Constraints:

- Each file must remain <= 500 LOC.
- Single responsibility per file.
- Avoid generic names (`v1`, `v2`, `misc`, `utils`).

### File responsibilities

`theme_tokens.ai`

- Theme constants and spacing contract.
- No business logic.

`records.ai`

- Record declarations and schema comments.
- No UI blocks.

`ingestion_flows.ai`

- Upload sync, batch ingestion, retry, bulk action flows.
- Progress state transitions.

`retrieval_flows.ai`

- Query profiling, retrieval, ranking, trust scoring.
- Diagnostics materialization flows.

`ui_layout.ai`

- Page layout, controls, chat/citations, diagnostics widgets.
- Binds UI controls to deterministic state.

Implementation note:

- If runtime modular import constraints prevent direct flow/theme splitting, use a deterministic build composition step that assembles these files into `app.ai` in fixed order.

## 8. Phase 1 Acceptance Criteria

1. Multiple uploads can be ingested in one deterministic batch run.
2. Bulk tag/delete/re-index actions operate on deterministic selection set.
3. Progress and retry are visible per stage per document.
4. Retrieval accepts and honors `filter_tags`.
5. Slider updates ranking preview live with deterministic ordering.
6. `semantic_k` and `lexical_k` are user-configurable with `1..50` bounds.
7. Citations are visible inline in chat without requiring drawer open.
8. Trust indicator is computed from retrieval/ranking evidence and rendered with tier label.
9. Diagnostics tables are sortable/filterable and mode-toggleable.
10. Studio-only context/prompt visibility is implemented.
11. Theme and spacing tokens above are applied consistently.
12. Manifest source is modularized into the five target files with <=500 LOC each.
13. Project dependency target is `namel3ss==0.1.0a21` and runtime checks pass in a Python 3.14 environment.

## 9. Test Strategy

Required automated checks:

- Manifest snapshot update for new UI blocks and controls.
- Deterministic replay test for identical query/settings run twice.
- Ingestion transition tests for all valid and invalid stage transitions.
- Retrieval sort/filter tests with explicit tie cases.
- Trust score test vectors (fixed inputs -> fixed outputs).
- Studio visibility tests for context/prompt panels.

Required smoke checks:

- `n3 check apps/rag-demo/app.ai`
- core action invocation path for no-selection and indexed-selection scenarios
- repeated run equality assertions for diagnostics ordering

## 10. Rollout

Phase 1 rollout sequence:

1. Land dependency/runtime baseline (`0.1.0a21`, Python 3.14).
2. Land data model and ingestion state machine.
3. Land retrieval tuning + tag filtering + trust rubric.
4. Land citation inline UX and diagnostics controls.
5. Land final theme token pass and spacing consistency pass.
6. Refresh snapshots and deterministic replay artifacts.
