# Workplan: Sprint 20 Observability Foundation

**Branch**: `feat/sprint-20-observability-foundation`
**Date**: 2026-03-30
**Orchestrator**: Executive Orchestrator
**Milestone**: #21 (Due: 2026-05-15)
**Effort**: M (medium — foundational work, moderate scope)

---

## Objective

Build observability infrastructure (CORS, eval harness, metrics capture, protocol compatibility, fleet audits) that Sprint 22 will use to establish baselines. This is foundational work, not measurement work — focus on infrastructure completeness and integration readiness. Covers 5 issues: #511 (fleet audit), #506 (CORS env var), #505 (inspector protocol), #500 (eval harness), #499 (metrics capture).

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Workplan Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: nothing (pre-execution gate)
**Gate**: No Phase 1 begins until APPROVED
**Status**: Not started

### Phase 1 — Observability Foundation Gap Analysis ⬜
**Agent**: Research Scout
**Deliverables**:
- Gap analysis findings appended to scratchpad under `## Phase 1 Output`
- Bullets only, ≤2000 tokens
- Audit existing MCP observability infrastructure
- Identify gaps between current state and 5 issues' target scope
- Check for overlap/redundancy between #500 (eval harness) and #499 (metrics capture)
- Surface blocker dependencies (e.g., does #506 CORS block #505 protocol work?)
- Sequence recommendations

**Depends on**: Phase 0 APPROVED
**CI**: N/A (research phase)
**Status**: Not started

### Phase 1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 1 Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 1 findings logged to scratchpad
**Gate**: Phase 2 does not start until APPROVED
**Status**: Not started

### Phase 2 — Sprint 20 Replanning ⬜
**Agent**: Executive Planner
**Deliverables**:
- Updated docs/plans/2026-03-30-sprint-20-observability-foundation.md with refined phases
- `## Phase 2 Output` appended to scratchpad
- Group 5 issues into logical implementation phases
- Adjust issue sequencing based on Phase 1 findings
- Return: "Workplan updated — [phase count] implementation phases, sequence: [phase names]"

**Depends on**: Phase 1 Review APPROVED
**CI**: N/A (planning phase)
**Status**: Not started

### Phase 2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 2 Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 2 replanning complete, workplan committed
**Gate**: Phase 3 does not start until APPROVED
**Status**: Not started

### Phase 3A — CORS Environment Variable Support (#506) ⬜
**Agent**: Executive Scripter
**Deliverables**:
- `mcp_server/dogma_server.py` updated with CORS env var handling
- `mcp_server/README.md` updated with CORS configuration instructions
- Test coverage for CORS env var parsing
- `## Phase 3A Output` appended to scratchpad

**Depends on**: Phase 2 Review APPROVED
**CI**: pytest, ruff
**Status**: Not started

### Phase 3A Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3A Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 3A complete
**Gate**: Phase 3B does not start until APPROVED
**Status**: Not started

### Phase 3B — Research: Inspector Protocol Compatibility (#505) ⬜
**Agent**: Research Scout
**Deliverables**:
- External research on MCP Inspector proxy bridge patterns
- Gap analysis: what's missing in our corpus for Inspector integration?
- Findings on session replay/debugging integration contracts
- Source URLs cached in `.cache/sources/`
- `## Phase 3B Output` appended to scratchpad (≤2000 tokens)

**Depends on**: Phase 3A Review APPROVED
**CI**: N/A (research phase)
**Status**: Not started

### Phase 3B Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3B Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 3B research complete
**Gate**: Phase 3C does not start until APPROVED
**Status**: Not started

### Phase 3C — Implementation: Inspector Protocol (#505) ⬜
**Agent**: Executive Scripter or Executive Docs
**Deliverables**:
- Research Inspector's proxy bridge implementation (from Phase 3B findings)
- Design minimal adapter layer for session replay integration
- Document integration contract in ADR-009 or follow-up ADR
- Prototype "Debug This Call" button export format (if time permits)
- `## Phase 3C Output` appended to scratchpad

**Depends on**: Phase 3B Review APPROVED
**CI**: ruff, validate-synthesis (if ADR created)
**Status**: Not started

### Phase 3C Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 3C Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 3C implementation complete
**Gate**: Phase 4A does not start until APPROVED
**Status**: Not started

### Phase 4A — Research: Metrics CI Gate Best Practices (#499) ⬜
**Agent**: Research Scout
**Deliverables**:
- External research on CI quality gates for observability metrics
- Survey alert mechanisms (Slack, GitHub Actions annotations, etc.)
- Gap analysis: what's missing in our corpus for metrics enforcement?
- Source URLs cached in `.cache/sources/`
- `## Phase 4A Output` appended to scratchpad (≤2000 tokens)

**Depends on**: Phase 3C Review APPROVED
**CI**: N/A (research phase)
**Status**: Not started

### Phase 4A Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 4A Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 4A research complete
**Gate**: Phase 4B does not start until APPROVED
**Status**: Not started

### Phase 4B — Implementation: Metrics CI Gate (#499) ⬜
**Agent**: Executive Automator
**Deliverables**:
- CI workflow: `.github/workflows/metrics-quality-gate.yml`
- Quality threshold enforcement (informed by Phase 4A research)
- Alert mechanism (strategy from Phase 4A)
- Documentation: when gate runs, how to respond to failures
- `## Phase 4B Output` appended to scratchpad

**Depends on**: Phase 4A Review APPROVED
**CI**: yaml-lint, workflow validation
**Status**: Not started

### Phase 4B Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 4B Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 4B implementation complete
**Gate**: Phase 5A does not start until APPROVED
**Status**: Not started

### Phase 5A — Research: Fleet Audit Anti-Patterns (#511) ⬜
**Agent**: Research Scout
**Deliverables**:
- External research on lowest-friction anti-patterns in agent fleets
- Survey fleet coupling analysis tools/frameworks
- Gap analysis: what's missing in our corpus for fleet audits?
- Source URLs cached in `.cache/sources/`
- `## Phase 5A Output` appended to scratchpad (≤2000 tokens)

**Depends on**: Phase 4B Review APPROVED
**CI**: N/A (research phase)
**Status**: Not started

### Phase 5A Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 5A Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 5A research complete
**Gate**: Phase 5B does not start until APPROVED
**Status**: Not started

### Phase 5B — Implementation: Fleet Audit Integration (#511) ⬜
**Agent**: Executive Fleet
**Deliverables**:
- Pre-commit hook or CI gate for fleet audit script
- Tool/capability drift detection integration
- Anti-pattern detection (informed by Phase 5A research)
- Documentation: when and how the audit runs
- `## Phase 5B Output` appended to scratchpad

**Depends on**: Phase 5A Review APPROVED
**CI**: pre-commit config validation
**Status**: Not started

### Phase 5B Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 5B Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 5B implementation complete
**Gate**: Phase 6 does not start until APPROVED
**Status**: Not started

### Phase 6 — Cross-Agent Integration Review ⬜
**Agent**: Executive Orchestrator (self)
**Deliverables**:
- `## Phase 6 Output` appended to scratchpad
- Verify all 4 implemented issues' (#506, #505, #499, #511) acceptance criteria satisfied
- Spot-check integration: CORS → inspector protocol → metrics capture
- Flag incomplete issues or new technical debt
- Return: Bullets only — "Issues ready" or "Issues flagged: [list with reason]"

**Depends on**: Phase 5B Review APPROVED
**CI**: N/A (internal QA phase)
**Status**: Not started

### Phase 7A — Research: Metrics Capture/Report Pipeline (#499) ✅
**Agent**: Research Scout
**Deliverables**:
- External research on metrics capture/report patterns for OpenTelemetry/observability systems
- JSONL → structured report transformation patterns
- Gap analysis: what's missing in our corpus for metrics pipeline implementation?
- Source URLs cached in `.cache/sources/`
- `## Phase 7A Output` appended to scratchpad (≤2000 tokens)

**Depends on**: Phase 6 integration review complete (identified #499 partial scope)
**CI**: N/A (research phase)
**Status**: Complete

### Phase 7A Review — Review Gate ✅
**Agent**: Review
**Deliverables**:
- `## Phase 7A Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 7A research complete
**Gate**: Phase 7B does not start until APPROVED
**Status**: Complete — APPROVED

### Phase 7B — Implementation: Capture/Report Pipeline (#499) ✅
**Agent**: Executive Scripter
**Deliverables**:
- `scripts/capture_mcp_metrics.py` — reads `.cache/mcp-metrics/tool_calls.jsonl`, outputs structured metrics
- `scripts/report_mcp_metrics.py` — formats metrics as Markdown report
- Baseline metrics report generated and committed to `docs/metrics/`
- Test coverage for both scripts
- Documentation: usage + integration with quality gate
- `## Phase 7B Output` appended to scratchpad

**Depends on**: Phase 7A Review APPROVED
**CI**: pytest, ruff
**Status**: Complete

### Phase 7B Review — Review Gate ✅
**Agent**: Review
**Deliverables**:
- `## Phase 7B Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 7B implementation complete
**Gate**: Phase 8A does not start until APPROVED
**Status**: Complete — APPROVED

### Phase 8A — Gap Analysis: Sprint 21 Issues (#530-533) ✅
**Agent**: Research Scout
**Deliverables**:
- Corpus gap audit: what do we already have about time-windowed metrics, OTel SDK, Jinja2 templates, Histograms?
- Review existing scripts/docs/patterns for overlap with Sprint 21 requirements
- Identify missing knowledge domains (what external research is needed)
- `## Phase 8A Output` appended to scratchpad (≤2000 tokens)

**Depends on**: Phase 7B Review APPROVED
**CI**: N/A (research phase)
**Status**: Complete

### Phase 8A Review — Review Gate ✅
**Agent**: Review
**Deliverables**:
- `## Phase 8A Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 8A gap analysis complete
**Gate**: Phase 8B does not start until APPROVED
**Status**: Complete — APPROVED

### Phase 8B — Deep Web Research: Sprint 21 External Sources ✅
**Agent**: Research Scout
**Deliverables**:
- Scout external sources for Sprint 21 topics (Phase 8A gaps):
  - Time-windowed aggregation patterns (Prometheus, Grafana time-series queries)
  - OpenTelemetry SDK integration (Python BatchSpanProcessor, exporters)
  - Jinja2 template best practices (observability dashboards, report generation)
  - OTel Histogram semantics (bucket configuration, percentile computation)
- Cache all discovered sources in `.cache/sources/`
- Document canonical examples and anti-patterns from external sources
- `## Phase 8B Output` appended to scratchpad (≤2000 tokens, WITH citations)

**Depends on**: Phase 8A Review APPROVED
**CI**: N/A (research phase)
**Status**: Complete

### Phase 8B Review — Review Gate ✅
**Agent**: Review
**Deliverables**:
- `## Phase 8B Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 8B research complete
**Gate**: Phase 8C does not start until APPROVED
**Status**: Complete — APPROVED

### Phase 8C — Synthesis: Sprint 21 Workplan ✅
**Agent**: Research Synthesizer
**Deliverables**:
- Synthesize Phase 8A (gaps) + Phase 8B (external patterns) into Sprint 21 implementation recommendations
- Draft workplan outline for Sprint 21 (4 issues: #530-533)
- Identify implementation ordering (dependency graph)
- Estimate effort per issue (XS/S/M/L)
- `## Phase 8C Output` appended to scratchpad (≤2000 tokens)

**Depends on**: Phase 8B Review APPROVED
**CI**: N/A (synthesis phase)
**Status**: Complete

### Phase 8C Review — Review Gate ✅
**Agent**: Review
**Deliverables**:
- `## Phase 8C Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 8C synthesis complete
**Gate**: Phase 9 does not start until APPROVED
**Status**: Complete — APPROVED

### Phase 9 — Final Review Gate ✅
**Agent**: Review
**Deliverables**:
- `## Phase 9 Review Output` appended to scratchpad
- Verdict: APPROVED (gates session close)

**Depends on**: Phase 8C Review APPROVED
**Gate**: Session close requires APPROVED
**Status**: Complete — APPROVED (deterministic fallback; subagent rate-limited)

### Phase 10 — PR Open & Review Triage ⬜
**Agent**: Executive Orchestrator + GitHub Agent
**Deliverables**:
- PR opened from `feat/sprint-20-observability-foundation` → `main`
- Copilot review auto-triggered on PR open
- All Copilot inline comments retrieved: `gh pr view <num> --json reviews,reviewThreads` + `gh api .../pulls/<num>/comments`
- Every comment classified: Blocking / Suggestion / Nit / Question
- All Blocking comments addressed with committed fixes
- All comments replied to via `scripts/pr_review_reply.py` batch mode (referencing fix commit SHAs)
- All addressed threads resolved
- Re-request review if state was CHANGES_REQUESTED
- `## Phase 10 Output` appended to scratchpad with PR number + triage summary

**Depends on**: Phase 9 APPROVED
**Gate**: Phase 11 does not start until all Blocking comments are fixed and all threads replied-to
**CI**: All existing hooks must pass before PR open
**Status**: Not started

### Phase 10 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**:
- `## Phase 10 Review Output` appended to scratchpad
- Verdict: APPROVED or REQUEST CHANGES

**Depends on**: Phase 10 PR triage complete, all threads replied-to
**Gate**: Phase 11 does not start until APPROVED
**Status**: Not started

### Phase 11 — Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- Update issue bodies (#506, #505, #499, #511) with completed checkboxes
- Post progress comment on each implemented issue (with PR number + commit range)
- Seed #500 as Sprint 21 deferred work
- Write `## Session Summary` to scratchpad
- Run `uv run python scripts/prune_scratchpad.py --force`
- Confirm all commits pushed

**Depends on**: Phase 10 Review APPROVED
**CI**: N/A
**Status**: Not started

---

## Acceptance Criteria

- [ ] 4 issues (#506, #505, #499, #511) implemented with acceptance criteria satisfied
- [ ] #500 (eval harness) deferred to Sprint 21 — rationale: large effort per Phase 1; accepting incomplete metrics surfaces as tracked technical debt
- [ ] No integration gaps flagged in Phase 5 cross-agent review (CORS → inspector → metrics chain validated)
- [ ] All deliverables committed to feat/sprint-20-observability-foundation branch
- [ ] PR opened from `feat/sprint-20-observability-foundation` → `main`
- [ ] Copilot review triaged: all Blocking comments addressed, all threads replied-to and resolved
- [ ] Issue bodies updated with completed checkboxes for 4 implemented issues
- [ ] Progress comments posted on #506, #505, #499, #511 (with PR number)
- [ ] #500 seeded with "Sprint 21 — deferred from Sprint 20" milestone/label

