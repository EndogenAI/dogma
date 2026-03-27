---
title: "Baseline Data Backlog Seeding"
branch: feat/baseline-data-backlog-seeding
issues: [351, 480, 481, 482]
date: 2026-03-27
status: Active
---

# Workplan: Baseline Data Backlog Seeding

## Objective

Seed the baseline-data backlog on `feat/baseline-data-backlog-seeding` with a lean,
must-have-only implementation sequence across four scoped issues: `#480`, `#481`,
`#482`, and `#351`. Explicitly exclude all RAG scope, including `#355`, `#386`, and
any related RAG instrumentation or evaluation work.

## Scope Constraints

- In scope only: `#351`, `#480`, `#481`, `#482`
- Out of scope: RAG issues, RAG instrumentation, RAG evaluation rubrics, and any work
  not required to establish the baseline-data kickoff path
- Delivery posture: implement only the minimum output needed to unblock the next phase

## Kickoff Decisions

1. **Canonical definition owner**: `#480` owns the canonical baseline-data definition and
   source boundaries because it defines the aggregation substrate and grouping dimensions.
   `#481` is a hardening follow-up that enforces schema and path invariants on the
   `session_cost_log` source and tests.
2. **Minimum acceptable Phase 2 (`#482`) threshold**: one reproducible, non-empty baseline
   output snapshot generated from a seeded or collected `session_cost_log` sample and
   committed as a deterministic artifact or fixture that downstream metrics code can read
   again without manual steps. Full interpretation-guide polish is deferred.
3. **Minimum acceptable `#351` metric scope for this sprint**: role-level aggregation for
   the must-have set only — `tokens_in`, `tokens_out`, and record count by role, with
   optional latency excluded unless already present in the Phase 2 snapshot.

## Ambiguity Resolution

- `#480` / `#481` overlap is resolved as follows:
  - `#480`: define baseline source-of-truth inputs, aggregation boundaries, and the
    acceptance checklist for the first usable baseline output
  - `#481`: enforce regression coverage for schema exactness, path safety, and invalid
    input behavior around the existing `session_cost_log` substrate
- Current `#482` issue text is documentation-oriented, but this kickoff phase will use a
  lean operational threshold: produce the reproducible baseline snapshot needed to inform
  the interpretation guide and to unblock `#351`. Any broader guide refinement beyond that
  threshold is deferred.

## Dependency Map

- **Phase 1 -> Phase 2**: baseline definitions, source boundaries, and acceptance checklist
  must be explicit before any seeding/collection run is valid.
- **Phase 2 -> Phase 3**: `#351` role-based metrics work must consume a concrete baseline
  snapshot, not an inferred or hand-waved dataset.

## Phases

### Phase 0 — Workplan Review ⬜

**Agent**: Review
**Deliverables**:
- APPROVED verdict recorded in scratchpad under `## Workplan Review Output`
- Validation that phase ordering respects the two hard gates and the explicit RAG exclusion

**Depends on**: nothing
**Gate**: Phase 1 does not begin until APPROVED
**Status**: Complete — APPROVED

### Phase 1 — Baseline Definitions and Boundaries (`#480`, `#481`) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- Canonical baseline-data definition recorded in the implementation substrate
- Explicit source boundaries for baseline inputs and outputs
- Lean acceptance checklist for the first usable baseline snapshot
- Any minimal regression coverage needed from `#481` to make the Phase 2 run trustworthy

**Depends on**: Phase 0 APPROVED
**Gate**: Phase 1 Review must return APPROVED before Phase 2 begins
**Status**: Complete — APPROVED

### Phase 1 Review — Validate Baseline Definitions ⬜

**Agent**: Review
**Deliverables**:
- APPROVED verdict covering ownership split, source boundaries, and acceptance checklist

**Depends on**: Phase 1
**Gate**: Phase 2 does not begin until APPROVED
**Status**: Complete — APPROVED

### Phase 2 — Baseline Snapshot Seeding Run (`#482`) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- One reproducible baseline-data snapshot produced from the accepted source boundaries
- Deterministic rerun path documented in the implementation artifact or tests
- Output sufficient to drive Phase 3 must-have role metrics

**Depends on**: Phase 1 Review APPROVED
**Gate**: Phase 2 Review must return APPROVED before Phase 3 begins
**Status**: Ready to start

### Phase 2 Review — Validate Snapshot Threshold ⬜

**Agent**: Review
**Deliverables**:
- APPROVED verdict confirming the snapshot is reproducible, non-empty, and usable by `#351`

**Depends on**: Phase 2
**Gate**: Phase 3 does not begin until APPROVED
**Status**: Not started

### Phase 3 — Lean Role Metrics (`#351`) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- Must-have role metrics only: `tokens_in`, `tokens_out`, record count by role
- Tests covering role grouping and unknown-role handling
- No expansion into RAG, benchmark, or interpretation-only scope

**Depends on**: Phase 2 Review APPROVED
**Gate**: Phase 3 Review must return APPROVED before session close
**Status**: Not started

### Phase 3 Review — Validate Lean Metric Scope ⬜

**Agent**: Review
**Deliverables**:
- APPROVED verdict confirming metric scope stayed lean and within the four scoped issues

**Depends on**: Phase 3
**Gate**: Session close begins only after APPROVED
**Status**: Not started