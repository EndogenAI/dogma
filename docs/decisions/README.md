# Architecture Decision Records

This directory records significant architectural and methodological decisions made for the EndogenAI Workflows project, following the [ADR pattern](https://adr.github.io/).

## What is an ADR?

An Architecture Decision Record captures a single decision: the context that forced the decision, the options considered, the choice made, and the consequences. ADRs are:

- **Lightweight**: a few paragraphs, not a full design doc
- **Immutable**: once accepted, an ADR is never edited — superseded decisions get a new ADR with `superseded-by` status
- **Discoverable**: sequentially numbered, filed here, cross-referenced from research docs

## When to write an ADR

Write an ADR when:
- A technology or tool is adopted (and there were real alternatives)
- A methodology or process is chosen over an industry alternative
- A constraint is imposed that future contributors might question
- A decision is likely to be revisited if not recorded

## Status vocabulary

| Status | Meaning |
|--------|---------|
| `Proposed` | Under discussion, not yet accepted |
| `Accepted` | Decision in effect |
| `Superseded` | Replaced by a newer ADR (link provided) |
| `Deprecated` | No longer relevant |

## Decision Log

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-uv-package-manager.md) | Adopt `uv` as sole Python package manager | Accepted | 2026-03-07 |
| [ADR-002](ADR-002-kanban-not-scrum.md) | Kanban over Scrum for project planning | Accepted | 2026-03-07 |
| [ADR-003](ADR-003-xml-hybrid-agent-format.md) | XML-hybrid format for agent instruction files | Proposed | 2026-03-07 |
