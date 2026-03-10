# Workplan: Milestone 9 — Action Items from Research

**Milestone**: [#9 — Action Items from Research](https://github.com/EndogenAI/Workflows/milestone/9)
**Branch**: `main`
**Date**: 2026-03-10
**Orchestrator**: Executive Orchestrator

---

## Objective

Execute all actionable items from the research sprint (Issues #112–#147). Milestone 9 contains 29 open issues derived directly from completed research syntheses in `docs/research/`. The goal is to systematically close this backlog by grouping related work into coherent execution phases, unblocking high-priority scripting work first, and deferring blocked items with explicit dependency tracking.

---

## Milestone Assessment

### Issue Breakdown

| Category | Count |
|---|---|
| Total open | 35 |
| `priority:high` | 8 |
| `priority:medium` | 18 |
| `priority:low` | 9 |
| `type:feature` (scripts/tools) | 16 |
| `type:docs` | 12 |
| `type:chore` | 6 |
| `type:research` | 2 |
| Blocked by external issue | 10 |
| Actionable immediately | 25 |

**6 new issues added 2026-03-10** — #150, #151, #152, #156, #157, #158 (derived from programmatic governors session insight; see parallel track below).

### Priority:High Issues (resolve first)

| # | Title | Type | Domain |
|---|---|---|---|
| #112 | validate_session.py — LLM Behavioral Testing Framework | feature | scripts |
| #115 | Membrane Permeability Specifications in AGENTS.md | docs | AGENTS.md |
| #118 | Operationalize generate_agent_manifest.py Connectivity Atlas | feature | scripts |
| #121 | Propose_dogma_edit.py — Programmatic Back-Propagation Enforcer | feature | scripts |
| #122 | Skill File Validation (validate_skill_files.py) | feature | scripts |
| #133 | Documentation Site Improvements | chore | docs/CI |
| #138 | Deterministic Components: YAML FSM Specifications & Validators | feature | scripts |
| #151 | Deep Research: Shifting AI behavioral constraints from tokens to code | research | docs/CI |

### Parallel Track — Programmatic Governors (tracked in separate workplan)

Issues #150, #151, #152 are being executed under [`docs/plans/2026-03-10-programmatic-governors.md`](2026-03-10-programmatic-governors.md). They live in milestone 9 but their phase sequencing is governed by that workplan, not this one. Issues #156, #157, #158 are blocked by #151 and are tracked in Phase 6 below.

| # | Title | Status in this workplan |
|---|---|---|
| [#150](https://github.com/EndogenAI/Workflows/issues/150) | Research: Shell PREEXEC hook as project-scoped command governor | Parallel track |
| [#151](https://github.com/EndogenAI/Workflows/issues/151) | Deep Research: Shifting AI behavioral constraints from tokens to code | Parallel track |
| [#152](https://github.com/EndogenAI/Workflows/issues/152) | Audit fleet guardrails for programmatic enforcement | Parallel track (blocked by #151) |

### Blocked Issues (defer — do not schedule)

| # | Title | Blocked By |
|---|---|---|
| #113 | Tier 2 Behavioral Testing — Drift Detection | #13 + local compute |
| #124 | Extended Agent Documentation Standard | #65 |
| #125 | Adopt Wizard Integration with client-values.yml | #56 |
| #128 | Phase 1 AFS Integration | #14 + local compute |
| #129 | SQLite-only Pattern A1 for AFS — FTS5 Keyword Index | #14 |
| #131 | Cognee Library Adoption (After Local Compute Baseline) | #13 + local compute |
| #152 | Audit fleet guardrails for programmatic enforcement | #151 (parallel track) |
| #156 | Token-spinning detection and rate-limiting (T4 runtime gate) | #151 |
| #157 | Subshell audit logging in PREEXEC governor | #150 + #151 |
| #158 | Capability-aware agent registry design | #151 (high effort, deferred) |

### Implementation State Notes

- `scripts/propose_dogma_edit.py` — **already exists**; #121 may require enhancement + tests
- `data/phase-gate-fsm.yml` — **already exists**; #138 needs validators, not the data file
- `data/link_registry.yml` — **already exists**; #120 needs `weave_links.py` completion
- `scripts/validate_agent_files.py` — **already exists**; #127 requires extension only
- `scripts/validate_synthesis.py` — **already exists** (comparable pattern for #122)
- `CHANGELOG.md` — **already done** (R1 in #133 is complete)

---

## Execution Phases

### Phase 1 — XS Documentation Wins ⬜

**Agent**: Executive Docs
**Estimated effort**: XS (all items are one-line or one-section additions)
**Deliverables**:
- [ ] #116 — Add "AI-as-Pressurizing-Medium" one-sentence note to session-start encoding checkpoint in `AGENTS.md`
- [ ] #126 — Add conditional step to `AGENTS.md §Session Start` for reading `client-values.yml` if it exists
- [ ] #130 — Add `## Session History` table to scratchpad template in `docs/guides/session-management.md`
- [ ] #136 — Add one-line forward reference to `docs/research/values-encoding.md` Related section
- [ ] #140 — Annotate orchestrator steps in `docs/research/async-process-handling.md` with `<!-- D -->` / `<!-- L -->` comments

**Depends on**: nothing
**Gate**: Phase 1 Review does not start until all changes are committed
**Status**: ⬜ Not started

---

### Phase 1 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 1 deliverables committed
**Gate**: Phase 2 does not start until Review returns APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — Substantive Documentation Updates ⬜

**Agent**: Executive Docs
**Deliverables**:
- [ ] #115 — Add Membrane Permeability Specifications (Boundary Spec tables for Scout→Synthesizer, Synthesizer→Reviewer, Reviewer→Archivist handoffs) to `AGENTS.md`
- [ ] #114 — Add Value Fidelity Test Taxonomy table to `AGENTS.md §Validate & Gate` section
- [ ] #137 — Draft Engelbart H-LAM/T substance-vs-substrate distinction in `docs/guides/mental-models.md`; add Engelbart citation to `MANIFESTO.md`
- [ ] #135 — Rename `.agent.md` sections to BDI framing (Beliefs / Desired Outcomes / Intentions) in the agent-file-authoring skill and AGENTS.md guidance
- [ ] #117 — Document evolutionary pressure test protocol for fleet agent audit in `docs/guides/agents.md`
- [ ] #123 — Verify all Tier 1/T2 agent skills committed; update status in `docs/guides/agents.md`

**Depends on**: Phase 1 APPROVED
**Gate**: Phase 2 Review does not start until all changes are committed
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 2 deliverables committed
**Gate**: Phase 3 does not start until Review returns APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — Core Script Tooling (priority:high) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- [ ] #112 — Implement `scripts/validate_session.py` (7-check Tier 1 post-commit scratchpad audit; ≥80% test coverage)
- [ ] #121 — Audit/extend `scripts/propose_dogma_edit.py` to match spec (inputs, tier enforcement, ADR output, exit codes); add/complete tests ≥80%
- [ ] #122 — Implement `scripts/validate_skill_files.py` (frontmatter schema, name format, dir-name match, cross-ref density, min body length); add to CI lint job
- [ ] #138 — Implement `scripts/validate_delegation_routing.py` (reads `data/delegation-gate.yml`, create file first) + `scripts/validate_session_state.py` (reads `data/phase-gate-fsm.yml`) + `scripts/pre_review_sweep.py` (extracts sweep from AGENTS.md); tests ≥80% each
- [ ] #118 — Document `scripts/generate_agent_manifest.py` in `scripts/README.md`; add manifest validation CI step on PRs touching `.github/agents/`; define density threshold policy in `AGENTS.md`

**Depends on**: Phase 2 APPROVED
**Gate**: Phase 3 Review does not start until all scripts committed with passing tests
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 3 deliverables committed
**Gate**: Phase 4 does not start until Review returns APPROVED
**Status**: ⬜ Not started

---

### Phase 4 — Medium Priority Scripts ⬜

**Agent**: Executive Scripter
**Deliverables**:
- [ ] #127 — Extend `scripts/validate_agent_files.py` with Core Layer Impermeability check (flag `client-values.yml` cited at higher priority than `MANIFESTO.md`/`AGENTS.md`)
- [ ] #119 — Extend `scripts/query_docs.py` to include `toolchain` and `skills` scopes; add tests (≥80% coverage)
- [ ] #120 — Ensure `scripts/weave_links.py` has `--dry-run`, idempotency guard, `--scope` filter; validate against `data/link_registry.yml` seed concepts
- [ ] #134 — Commit `.vscode/mcp.json` with GitHub MCP + endogenic filesystem server; document `scripts/mcp_server.py` design spec in `docs/guides/` (implementation deferred to a child issue)

**Depends on**: Phase 3 APPROVED
**Gate**: Phase 4 Review does not start until all changes are committed with passing tests
**Status**: ⬜ Not started

---

### Phase 4 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 4 deliverables committed
**Gate**: Phase 5 does not start until Review returns APPROVED
**Status**: ⬜ Not started

---

### Phase 5 — Documentation Site & GitHub/PM ⬜

**Agent**: Executive Docs (docs sub-tasks) + Executive PM (GitHub/PM sub-tasks)
**Deliverables**:
- [ ] #133 — Complete remaining Documentation Site subtasks:
  - R2: Add CI badge + TOC to `README.md`
  - R3: Add dev environment setup to `CONTRIBUTING.md`
  - R4: Add MkDocs Material docsite (or open a scoped child issue if >2 hrs)
  - R5: Add lychee link-checker to CI
  - R6: Confirm `validate_synthesis.py` runs in CI lint job
- [ ] #139 — Extend GitHub Project Management:
  - R2: Create GitHub Project with Priority field + Board view
  - R3: Migrate issue templates to YAML forms
  - R4: Add `area:` auto-label workflow via `.github/labeler.yml`
  - R5: Add stale bot
  - R6: Document `gh auth refresh -s project` in `CONTRIBUTING.md`
- [ ] #132 — Confirm child issues #142–#147 each have correct milestone + labels; close parent #132 when all 6 children are closed or scheduled

**Depends on**: Phase 4 APPROVED
**Gate**: Phase 5 Review does not start until all changes are committed
**Status**: ⬜ Not started

---

### Phase 5 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 5 Review Output` appended to scratchpad, verdict: APPROVED
**Depends on**: Phase 5 deliverables committed
**Gate**: Milestone 9 closure assessment follows
**Status**: ⬜ Not started

---

### Phase 6 — Blocked Issues (Deferred — Track Only) ⬜

These issues are actionable only after external blockers are resolved. No execution scheduled in this workplan.

**Original blocked issues (external blockers):**

| # | Title | Blocker | Next action when unblocked |
|---|---|---|---|
| #113 | Tier 2 Behavioral Testing — Drift Detection | #13 + local compute | Add to sprint after #13 closes |
| #124 | Extended Agent Documentation Standard | #65 | Add to sprint after #65 closes |
| #125 | Adopt Wizard Integration with client-values.yml | #56 | Add to sprint after #56 closes |
| #128 | Phase 1 AFS Integration | #14 + local compute | Add to sprint after #14 closes |
| #129 | SQLite-only Pattern A1 for AFS — FTS5 Keyword Index | #14 | Add to sprint after #14 closes |
| #131 | Cognee Library Adoption | #13 + local compute | Add to sprint after #13 closes |

**New blocked issues (blocked by #151 deep research — added 2026-03-10):**

| # | Title | Blocker | Next action when unblocked |
|---|---|---|---|
| #156 | Token-spinning detection and rate-limiting (T4 runtime gate) | #151 | Add to Phase 4 after #151 closes; Effort: Low |
| #157 | Subshell audit logging in PREEXEC governor | #150 + #151 | Add to Phase 4 after #150 + #151 close; Effort: Low |
| #158 | Capability-aware agent registry design | #151 | Schedule as standalone sprint after #151 closes; Effort: High — may warrant own workplan |

**Action**: Add `status:blocked` label to all blocked issues and post a blocking comment citing the dependency.

_Note_: #152 is also blocked by #151 but is tracked under the programmatic-governors workplan.

---

## Dependency Graph

```
Phase 1 (XS docs)
    └── Phase 2 (substantive docs)
            └── Phase 3 (high-priority scripts)
                    └── Phase 4 (medium scripts)
                            └── Phase 5 (docs site + GitHub PM)
                                    └── Close Milestone 9 (25 actionable issues)

Phase 6: Blocked (unblocks independently when external blockers close)
    ├── Original 6 issues: gate on #13/#14/#56/#65 + local compute
    └── New 3 issues (#156, #157, #158): gate on #151 research sprint closing

Parallel Track (programmatic-governors workplan):
    #151 (deep research) → #152 (fleet audit) + #156/#157/#158 (governor impl)
    #150 (PREEXEC research) → #157 (subshell audit)
```

---

## Acceptance Criteria

- [ ] All 25 actionable issues closed or in a PR targeting `main`
- [ ] 10 blocked issues have `status:blocked` label and dependency comment
- [ ] #150, #151, #152 closed per the programmatic-governors workplan
- [ ] Every new script has ≥80% test coverage and a docstring
- [ ] Every new script is documented in `scripts/README.md`
- [ ] CI passes on all phases (lint, format, tests, validate_synthesis, validate_agent_files)
- [ ] `validate_skill_files.py` added to CI lint job (#122)
- [ ] Manifest validation step added to CI for `.github/agents/` PRs (#118)
- [ ] No phase advances without a committed Review gate verdict of APPROVED

---

## Notes

- **#121 (`propose_dogma_edit.py`)**: Script already exists. Begin with a coverage run (`uv run pytest tests/test_propose_dogma_edit.py --cov=scripts/propose_dogma_edit.py`) to establish baseline before spec-gap analysis.
- **#133 (Documentation Site)**: R4 (MkDocs setup) is a significant effort; if it exceeds 2 hours, create a scoped child issue and close #133 for the remaining subtasks.
- **#132 (Product User Research)**: This is a parent tracker. Do not close it directly — close the 6 child issues (#142–#147) and the parent auto-closes per its description.
- **#135 (BDI framing)**: Pure design/naming change. Confirm with Conor before renaming sections — it affects every `.agent.md` file and validate_agent_files.py section-name checks.
