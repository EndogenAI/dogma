# Workplan: Sprint 22 Baseline Stabilization

**Branch**: `feat/sprint-22-baseline-stabilization`
**Date**: 2026-03-31
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprint 22 establishes empirical baselines for the dogma project by executing a formal deep-dive research phase (per-topic source notes feeding a unified D4 synthesis) that directly informs all downstream planning and implementation decisions. The sprint closes 8 open issues: optimization effects research (#497), instruction format study (#491), KPI interpretation docs (#482), canonical scripts friction audit (#529), observability maturation (#534, #425), carry-in items (#430, #506). **#527 (Repositioning) is out of scope for this sprint.**

**Phase ordering decisions**:
- Phase 1 (Carry-ins) runs before research: #430 and #506 do not depend on research output
- Phase 2 (Research) is cross-cutting: per-topic source notes per issue cluster feed a single unified D4 synthesis; gates all implementation phases
- Phase 3 (Planning) is informed entirely by Phase 2 research and populates Phases 4-N
- Agents run **sequentially** (no parallel delegations) to manage rate-limit exposure
- All agents write findings directly to `.tmp/feat-sprint-22-baseline-stabilization/2026-03-31.md`
- **PAUSE POINT** after Phase 2 Review: Orchestrator surfaces findings to human; Phase 3 requires explicit human confirmation

---

## Phase Plan

### Phase 0 — Workplan Review Gate ✅
**Agent**: Review
**Verdict**: APPROVED

**Depends on**: nothing (workplan committed)
**Status**: Complete

---

### Phase 1 — Carry-Ins (#430, #506) ✅
**Agent**: Executive Scripter (for #506 test verification); Executive Docs (for #430 closure)
**Deliverables**:
- Verify #506 CORS env var is fully implemented and tested in `web/server.py`; confirm test coverage passes
- Close #430 [ADOPTED] with a formal adoption-summary comment linking to PR #535; create `docs/guides/webmcp-integration.md` stub if not already present
- `## Phase 1 Output` written to scratchpad by each agent

**Depends on**: Phase 0 APPROVED
**CI**: Tests, Lint, Auto-validate
**Status**: ✅ Complete

### Phase 1 Review Gate ✅
**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 1 deliverables committed
**Status**: ✅ Complete — APPROVED

---

### Phase 2 — Deep-Dive Research: Per-Topic Source Notes + Unified D4 Synthesis ✅
**Agent**: Executive Researcher -> Research Scout (per topic) -> Research Synthesizer -> Research Reviewer -> Research Archivist
**Deliverables**:
- Per-topic source notes in `docs/research/sources/` (one file per issue cluster):
  - `sprint-22-independent-optimization-effects.md` (for #497)
  - `sprint-22-instruction-format-efficiency.md` (for #491)
  - `sprint-22-metrics-kpi-interpretation.md` (for #482)
  - `sprint-22-canonical-scripts-friction.md` (for #529)
  - `sprint-22-observability-patterns.md` (for #534, #425)
- `docs/research/sprint-22-baseline-stabilization.md` — unified D4 synthesis (status: Final) drawing across all per-topic sources; formal Recommendations section
- `## Phase 2 Output` written to scratchpad: findings summary + key recommendations per topic
- Closes #497

**Depends on**: Phase 1 Review APPROVED
**CI**: Tests, Lint, Auto-validate (synthesis schema)
**Status**: ✅ Complete — commits df6b05b, b060ea7

### Phase 2 Review Gate ✅
**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 2 D4 synthesis doc committed
**Status**: ✅ Complete — APPROVED

### PAUSE POINT — Surface Research Findings to Human
_After Phase 2 Review APPROVED_: Orchestrator reads `## Phase 2 Output` from scratchpad and surfaces findings summary, D4 Recommendations, and emergent decision points to the human. **Phase 3 does not begin without explicit human confirmation.**

---

### Phase 3 — Sprint Planning (informed by Phase 2) ✅
**Agent**: Executive Planner
**Deliverables**:
- `## Sprint Execution Plan` section added to this workplan (Phases 4-N) with agent assignments, effort estimates (XS/S/M/L), sequencing rationale from Phase 2 D4 recommendations
- Specific phases for: #491, #482, #529, #534, #425
- New issues seeded if Phase 2 reveals untracked gaps
- `## Phase 3 Output` written to scratchpad

**Depends on**: Phase 2 Review APPROVED + human confirmation after PAUSE POINT
**CI**: Tests, Lint, Auto-validate
**Status**: ✅ Complete — Phases 4-8 + Final Review + GitHub Phase defined below

### Phase 3 Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 3 sprint execution plan committed
**Status**: Not started

---

### Phase 4 — OTel Instrumentation, Docker Stack, Prometheus Metrics (#534, #531, #533) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- `mcp_server/dogma_server.py`: spans for every tool call; attributes `mcp.server.operation.duration`, `gen_ai.operation.name`, `error.type`; semconv pinned to v1.40.0
- `DOGMA_OTEL_EXPORTER` env var: `otlp` default, `jsonl` fallback — resolves #531 (JSONL capture → OTel span export migration)
- OTel Histogram for MCP tool latency emitted per span — resolves #533
- `docker-compose.yml`: OTel Collector + Jaeger stack
- `scripts/start_otel_stack.py` + VS Code task (⚠️ seed **New Issue A** via `gh issue create` before Phase 4 execution begins)
- Tests updated; CI green
- `## Phase 4 Output` written to scratchpad

**Depends on**: Phase 3 Review APPROVED
**CI**: Tests, Lint, Auto-validate
**Effort**: L
**Status**: Not started

### Phase 4 Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 4 deliverables committed
**Status**: Not started

---

### Phase 5 — Scripts Friction Audit + Rename (#529, #539) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- Deprecation convention in place: `# DEPRECATED: superseded by <script>` at docstring line 2 + `sys.exit(1)` with human-readable message on invocation
- `scripts/DEPRECATED.md` register created and populated
- Non-conformant script names renamed per OQ-3 (breaking — all callers, `scripts/README.md`, and agent file references updated)
- Inline documentation audit against encoded standard — resolves #539
- Tests updated; CI green
- `## Phase 5 Output` written to scratchpad

**Depends on**: Phase 4 Review APPROVED
**CI**: Tests, Lint, Auto-validate
**Effort**: M
**Status**: Not started

### Phase 5 Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 5 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 5 deliverables committed
**Status**: Not started

---

### Phase 6 — KPI Calibration Baseline (#482) ⬜

**Agent**: Executive Docs + Executive Scripter
**Deliverables**:
- Control set curated manually: 5–10 known-good + 5 known-bad tool call runs (per OQ-4)
- `scripts/check_mcp_quality_gate.py`: calibration run step added; gate trigger requires delta to exceed calibration variance (noise-floor guard)
- `data/governance-thresholds.yml`: calibration baseline values committed
- `## Phase 6 Output` written to scratchpad

**Depends on**: Phase 5 Review APPROVED (transitively requires Phase 4 — #534 must precede #482)
**CI**: Tests, Lint, Auto-validate
**Effort**: S
**Status**: Not started

### Phase 6 Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 6 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 6 deliverables committed
**Status**: Not started

---

### Phase 7 — Quality Gate + RAGAS Complement (#425) ⬜

**Agent**: Executive Scripter
**Deliverables**:
- `scripts/check_mcp_quality_gate.py`: RAGAS + Nielsen quality complement integrated; gate logic reads calibration baseline from Phase 6 `governance-thresholds.yml`
- Structured JSON output added to gate script
- Tests updated; CI green
- `## Phase 7 Output` written to scratchpad

**Depends on**: Phase 6 Review APPROVED (transitively requires Phases 4 and 6)
**CI**: Tests, Lint, Auto-validate
**Effort**: M
**Status**: Not started

### Phase 7 Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 7 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 7 deliverables committed
**Status**: Not started

---

### Phase 8 — Instruction Format Front-Loading, Observability Guide, R6 Encoding (#491) ⬜

**Agent**: Executive Docs + Executive Fleet
**Deliverables**:
- `.github/agents/*.agent.md`: task-critical constraints front-loaded per R7 + Cluster 2 Pattern Catalog guidance
- `docs/guides/`: factorial/sequential experiment design note added (R6 from #497 — no new issue required)
- `docs/guides/observability.md`: OTel stack startup + instrumentation guide (⚠️ seed **New Issue B** via `gh issue create` before Phase 8 execution begins; include `Closes #<NewB>` in PR body)
- `## Phase 8 Output` written to scratchpad

**Depends on**: Phase 7 Review APPROVED (requires Phase 5 renames before agent file updates; requires Phase 4 for observability guide)
**CI**: Tests, Lint, Auto-validate
**Effort**: S
**Status**: Not started

### Phase 8 Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 8 Review Output` appended to scratchpad with verdict: APPROVED

**Depends on**: Phase 8 deliverables committed
**Status**: Not started

---

### Final Review Phase — Cross-Fleet Intensive Review ⬜

**Agent**: Review + Executive Docs + Executive Scripter + Executive Fleet + Security Researcher
**Deliverables**:
- Each agent appends `## Final Review — <AgentName> Output` to scratchpad with their domain verdict
- All blocking findings resolved before GitHub phase begins
- `## Final Cross-Fleet Review Output` aggregated in scratchpad

**Depends on**: Phases 4–8 Review gates all APPROVED
**CI**: Tests, Lint, Auto-validate
**Effort**: M
**Status**: Not started

### GitHub Phase — PR Open ⬜

**Agent**: GitHub
**Deliverables**:
- PR opened against `main` from `feat/sprint-22-baseline-stabilization`
- PR body includes: `Closes #534, Closes #531, Closes #533, Closes #529, Closes #539, Closes #482, Closes #425, Closes #491` + `Closes #<NewIssueA>, Closes #<NewIssueB>` (fill after seeding at Phases 4 and 8)
- Session scratchpad archived

**Depends on**: Final Cross-Fleet Review APPROVED
**Status**: Not started

---

## Acceptance Criteria

- [x] Phase 0 Workplan Review APPROVED
- [x] Phase 1 carry-ins complete and committed (#430 closed, #506 verified)
- [x] Phase 1 Review APPROVED
- [x] Phase 2 D4 synthesis committed (status: Final, commits df6b05b, b060ea7) with 5 per-topic source notes
- [x] Phase 2 Review APPROVED
- [x] Human confirmed continuation after PAUSE POINT (OQ-1 through OQ-4 resolved)
- [x] Phase 3 sprint execution plan committed to this workplan (Phases 4–8 + Final + GitHub)
- [ ] Phase 3 Review APPROVED
- [ ] New Issue A seeded (docker-compose.yml + start_otel_stack.py) before Phase 4
- [ ] New Issue B seeded (docs/guides/observability.md) before Phase 8
- [ ] Phase 4 (#534, #531, #533) complete and reviewed
- [ ] Phase 5 (#529, #539) complete and reviewed
- [ ] Phase 6 (#482) complete and reviewed
- [ ] Phase 7 (#425) complete and reviewed
- [ ] Phase 8 (#491) complete and reviewed
- [ ] Final cross-fleet review APPROVED (5+ agents)
- [ ] All changes pushed and PR opened against main

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #497, Closes #491, Closes #482, Closes #529, Closes #430, Closes #425, Closes #534, Closes #506, Closes #531, Closes #533, Closes #539, Closes #<NewIssueA>, Closes #<NewIssueB>
