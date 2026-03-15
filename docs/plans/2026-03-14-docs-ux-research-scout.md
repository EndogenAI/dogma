# Workplan: Docs UX Research & Restructuring Scout

**Branch**: `task/docs-restructuring-scout`
**Date**: 2026-03-14
**Orchestrator**: Executive Orchestrator

---

## Objective

Scout best practices for documentation structures in open source projects and documentation for agents, then assess the current repository structure against these findings to recommend improvements for both human and agent navigation.

---

## Phase Plan

### Phase 1 — Research & Scouting ⬜
**Agent**: Executive Researcher
**Deliverables**:
- Scout findings logged in scratchpad: OSS docs patterns, Agent-specific docs patterns.
- Comparative analysis: Current `dogma` structure vs. patterns.
- Identification of gaps and redundant "token burn" in current navigation.

**Depends on**: nothing
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Review Output` in scratchpad, verdict: APPROVED.

**Depends on**: Phase 1 findings complete.
**Status**: Not started

### Phase 2 — Strategy & Recommendation ⬜
**Agent**: Executive Docs
**Deliverables**:
- Proposed `D4` Research Synthesis: `docs/research/docs-ux-restructuring-strategy.md`.
- Recommendations for TOC, folder structure (D1-D5), and agent discovery.

**Depends on**: Phase 1 Review APPROVED.
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Review Output` in scratchpad, verdict: APPROVED.

**Depends on**: Phase 2 draft complete.
**Status**: Not started

### Phase 3 — Sprint Close ⬜
**Agent**: GitHub
**Deliverables**:
- Research synthesis committed.
- Session summary written and issues updated.

**Depends on**: Phase 2 Review APPROVED.
**Status**: Not started

---

## Acceptance Criteria

- [ ] Scout findings cover OSS best practices and agent-first documentation patterns.
- [ ] Gap analysis highlights specific areas for improvement in human/agent navigation.
- [ ] Strategy document provides concrete, actionable recommendations (TOC, structure, etc.).
- [ ] Research doc adheres to D4 schema (`title`, `status`, required headings).
- [ ] Final deliverables committed and session summarized.
