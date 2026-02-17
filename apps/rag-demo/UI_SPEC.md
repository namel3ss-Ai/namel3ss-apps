# RAG Demo UI Specification

## Objective
Provide a professional, deterministic RAG workspace where users can:
- manage project-scoped knowledge,
- route files between library and projects,
- ask grounded questions with citation visibility.

## Primary Layout
The Chat page uses a three-pane workspace:
- Left pane: project switching.
- Center pane: assistant-first workflow and project intake.
- Right pane: citation evidence.

## Information Architecture
### Header
- Title and concise context only (`RAG Workspace`)

### Left Pane
- `Projects` list
- Project actions: open, rename, duplicate, share, archive, delete
- `Create project`
- `Question Files`
  - Upload: `question_files`

### Center Pane
- `Assistant`
  - Action: `Create chat`
  - Chat composer bound to `rag_engine.ask_question`
- `Project Intake`
  - Upload: `project_files`
  - Actions: `Create project index`, `View file status`
  - Web source input routed to `rag_engine.ingest_web_source`
- `Project Files`
  - Project-scoped list with actions: rename, move, remove-from-project, delete

### Right Pane
- `Source Evidence` list with actions: open in source drawer, rename, move, delete

## Interaction Contracts
### Ingestion path
1. Upload into `project_files` or `question_files`.
2. Run `rag_engine.sync_library`.
3. Run `rag_engine.ingest_selected`.
4. Ask via `rag_engine.ask_question`.

### Routing path
1. Uploads route to the active project by default in Chat.
2. Project scope is managed through `Project Files` row actions (`move`, `remove`).
3. Active project membership controls retrieval scope by default.

### Answer path
1. Chat response returns deterministic answer mode and citations.
2. Source actions open preview drawer and support source lifecycle actions.

## Naming and Copy Rules
- Action labels are verb-first (`Create`, `View`, `Reset`, `Open`, `Delete`).
- Section titles are noun-based and operational (`Assistant`, `Project Intake`, `Project Files`).
- Avoid ambiguous labels such as `Add New`.

## UX Quality Guardrails
- Keep visible scope context (project-first workflow).
- Keep file actions available at row-level menus.
- Keep ingestion status discoverable through notices and status labels.
- Keep citation actions available in the same screen as chat.
- Avoid persistent instructional paragraphs; rely on clear labels and direct actions.

## Non-goals
- No hidden auto-routing outside declared flows.
- No AI-only retrieval decisions without deterministic trace context.
