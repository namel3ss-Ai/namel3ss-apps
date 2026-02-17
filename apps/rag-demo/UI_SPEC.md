# RAG Demo UI Specification

## Objective
Provide a professional, deterministic RAG workspace where users can:
- manage project-scoped knowledge,
- route files between library and projects,
- ask grounded questions with citation visibility.

## Primary Layout
The Chat page uses a three-pane workspace:
- Left pane: project scope and operational notices.
- Center pane: intake, routing, and chat workflow.
- Right pane: active project files and answer sources.

## Information Architecture
### Header
- `Create project`
- `View workspace status`
- `Create project index`
- `Create chat`

### Left Pane
- `Projects` list
- Project actions: open, rename, duplicate, share, archive, delete
- `Session Notes` list (ingestion and routing notices)
- `Reset chat`

### Center Pane
- `Project Intake`
  - Upload: `project_files`
  - Actions: `View project files`, `Create project index`
  - Web source input routed to `rag_engine.ingest_web_source`
- `Library Routing`
  - Library list with actions: assign, move, rename, delete
- `Ask`
  - Upload: `question_files`
  - Composer bound to `rag_engine.ask_question`

### Right Pane
- `Active Project Files` list with actions: rename, move, remove-from-project, delete
- `Answer Sources` list with actions: open in source drawer, rename, move, delete
- `Workflow` checklist text

## Interaction Contracts
### Ingestion path
1. Upload into `project_files` or `question_files`.
2. Run `rag_engine.sync_library`.
3. Run `rag_engine.ingest_selected`.
4. Ask via `rag_engine.ask_question`.

### Routing path
1. Library receives all uploaded assets.
2. Project assignment is explicit through row actions.
3. Active project membership controls retrieval scope by default.

### Answer path
1. Chat response returns deterministic answer mode and citations.
2. Source actions open preview drawer and support source lifecycle actions.

## Naming and Copy Rules
- Action labels are verb-first (`Create`, `View`, `Reset`, `Open`, `Delete`).
- Section titles are noun-based and operational (`Project Intake`, `Library Routing`).
- Avoid ambiguous labels such as `Add New`.

## UX Quality Guardrails
- Keep visible scope context (project-first workflow).
- Keep file actions available at row-level menus.
- Keep ingestion status discoverable through notices and status labels.
- Keep citation actions available in the same screen as chat.

## Non-goals
- No hidden auto-routing outside declared flows.
- No AI-only retrieval decisions without deterministic trace context.
