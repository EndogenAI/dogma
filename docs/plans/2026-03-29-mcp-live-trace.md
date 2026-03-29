# Workplan: MCP Live Trace Capture (Issue #509)

**Branch**: `feat/sprint-21-mcp-trace`
**Date**: 2026-03-29
**Orchestrator**: Executive Orchestrator
**Issue**: #509
**Milestone**: Sprint 20 — RAG & Observability

---

## Objective

Instrument `mcp_server/dogma_server.py` to append real JSONL records to `.cache/mcp-metrics/tool_calls.jsonl` on every tool invocation, replacing the current 800 synthetic-seeded records. Includes research phase for design decisions (atomicity, transition strategy, rotation, metrics schema), implementation with non-blocking append, observability for the capture mechanism itself, documentation updates, and comprehensive testing. Total estimated effort: M–L (10–15 hours across 6 phases).

---

## Phase Plan

### Phase 0 — Workplan Review Gate ✅
**Agent**: Review  
**Deliverables**:
- `## Workplan Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: workplan committed  
**Gate**: Phase 1 does not begin until Review returns APPROVED  
**Status**: ✅ Complete — APPROVED 2026-03-29

---

### Phase 1 — Research & Design Decisions ✅
**Agent**: Executive Researcher  
**Effort**: S (2–3 hours)  
**Deliverables**:
- D1.1: `docs/research/mcp-live-trace-design.md` (Status: Final) — documents atomicity approach, transition strategy, rotation policy, and quality metrics schema decision with rationale for each
- D1.2: Research doc includes canonical examples of the chosen append pattern (e.g., file locking pseudocode or queue+thread architecture)
- D1.3: Explicit decision on synthetic data handling (delete, archive, or keep+append with metadata flag)

**Depends on**: Phase 0 APPROVED  
**Gate**: Phase 2 does not start until `docs/research/mcp-live-trace-design.md` is committed with all 4 design questions answered and recommendation for each marked ADOPT or DEFER.  
**Script opportunity**: `uv run python scripts/query_docs.py "file I/O atomicity Python"` to check if prior research exists.  
**Status**: ✅ Complete — `docs/research/mcp-live-trace-design.md` committed (992d25f)

---

### Phase 1 Review — Review Gate ✅
**Agent**: Review  
**Deliverables**:
- `## Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: Phase 1 committed  
**Gate**: Phase 2 does not begin until Review returns APPROVED  
**Status**: ✅ Complete — APPROVED 2026-03-29

---

### Phase 2 — Instrumentation Implementation ⬜
**Agent**: Executive Scripter  
**Effort**: M (4–5 hours)  
**Deliverables**:
- D2.1: `mcp_server/dogma_server.py` modified — `queue.Queue` writer injected into both `finally:` blocks of `_run_with_mcp_telemetry()`; daemon thread started at module load
- D2.2: `mcp_server/_version.py` created — `BRANCH_COUNTER: int = 0`; `_TOOL_VERSION = f"{pkg}.{BRANCH_COUNTER}"`
- D2.3: `scripts/migrate_tool_calls.py` — one-time archive: `tool_calls.jsonl` → `tool_calls.synthetic.bak.jsonl`; `--dry-run` guard
- D2.4: Live records include `timestamp_utc`, `error_type`, `error_message`, `source: "live"`, `tool_version`; quality fields omitted
- D2.5: `data/mcp-metrics-schema.yml` updated with `per_record_jsonl` section
- D2.6: Pre-push hook warns when `BRANCH_COUNTER != 0` on a push to `main` (merge warning)
- D2.7: Error handling for write failures (log, do not crash tool execution)

**Depends on**: Phase 1 Review APPROVED  
**Gate**: Phase 3 does not start until records appear in `tool_calls.jsonl` with `"source": "live"` after one real tool call; `BRANCH_COUNTER` exists in `mcp_server/_version.py`.  
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜
**Agent**: Review  
**Deliverables**:
- `## Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: Phase 2 committed  
**Gate**: Phase 3 does not begin until Review returns APPROVED  
**Status**: ⬜ Not started

---

### Phase 3 — Observability for Capture Mechanism ⬜
**Agent**: Executive Scripter  
**Effort**: S (2 hours)  
**Deliverables**:
- D3.1: Internal counter for successful vs failed appends (log or expose as tool result metadata)
- D3.2: Log warning on write failure with details (path, error type)
- D3.3: Optional: Add `capture_health` field to `.cache/mcp-metrics/dashboard_state.json` showing last write success timestamp

**Depends on**: Phase 2 Review APPROVED  
**Gate**: Phase 4 does not start until observability code is committed and a manual test confirms write failures produce visible warnings.  
**Script opportunity**: Extend `scripts/check_mcp_quality_gate.py` to include capture health check.  
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate ⬜
**Agent**: Review  
**Deliverables**:
- `## Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: Phase 3 committed  
**Gate**: Phase 4 does not begin until Review returns APPROVED  
**Status**: ⬜ Not started

---

### Phase 4 — Documentation Updates ⬜
**Agent**: Executive Docs  
**Effort**: S (2 hours)  
**Deliverables**:
- D4.1: `mcp_server/README.md` — section on live trace capture (record shape, `tool_version` format, `BRANCH_COUNTER` increment/reset convention)
- D4.2: `docs/mcp/api-reference.md` — `tool_version` field documented in per-record JSONL shape; format: `{pkg}.{BRANCH_COUNTER}`
- D4.3: `docs/guides/mcp-dashboard.md` — note that dashboard shows live data post-migration; Errors tab shows real timestamps
- D4.4: `CONTRIBUTING.md § Commit Discipline` — `BRANCH_COUNTER` reset rule: must be `0` before merging to main; pre-push hook enforces
- D4.5: All docs link to `docs/research/mcp-live-trace-design.md` for design rationale

**Depends on**: Phase 3 Review APPROVED  
**Gate**: Phase 5 does not start until `git log --oneline -5` shows commits for D4.1–D4.4.  
**Script opportunity**: Run `uv run python scripts/validate_synthesis.py docs/research/mcp-live-trace-design.md` before documenting to ensure research is compliant.  
**Status**: ⬜ Not started

---

### Phase 4 Review — Review Gate ⬜
**Agent**: Review  
**Deliverables**:
- `## Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: Phase 4 committed  
**Gate**: Phase 5 does not begin until Review returns APPROVED  
**Status**: ⬜ Not started

---

### Phase 5 — Testing (Unit + Integration) ⬜
**Agent**: Executive Scripter  
**Effort**: M (3–4 hours)  
**Deliverables**:
- D5.1: `tests/test_dogma_server_trace.py` — unit tests for append logic (success, error, write failure)
- D5.2: Integration test: invoke a tool via MCP, confirm JSONL record appears with expected fields
- D5.3: All tests pass locally: `uv run pytest tests/ -k trace -v`
- D5.4: Coverage ≥80% on new instrumentation code

**Depends on**: Phase 4 Review APPROVED  
**Gate**: Phase 6 does not start until all tests pass and coverage report confirms ≥80% on `mcp_server/dogma_server.py` changes.  
**Script opportunity**: `uv run pytest tests/ -x -m "not slow and not integration"` for fast feedback loop.  
**Status**: ⬜ Not started

---

### Phase 5 Review — Review Gate ⬜
**Agent**: Review  
**Deliverables**:
- `## Review Output` appended to scratchpad, verdict: APPROVED

**Depends on**: Phase 5 committed  
**Gate**: Phase 6 does not begin until Review returns APPROVED  
**Status**: ⬜ Not started

---

### Phase 6 — Final Review & Commit ⬜
**Agent**: Review → GitHub  
**Effort**: XS (1 hour)  
**Deliverables**:
- D6.1: Review agent returns APPROVED verdict
- D6.2: All changes committed with Conventional Commits format: `feat(mcp): add live JSONL trace capture to dogma_server`
- D6.3: PR updated or created linking to issue #509
- D6.4: CI passes (lychee, ruff, pytest)

**Depends on**: Phase 5 Review APPROVED  
**Gate**: No gate after this — PR ready for merge once CI green and human review (if any) completes.  
**Status**: ⬜ Not started

---

## Open Questions for Orchestrator
1. **Branch naming**: Using `feat/sprint-21-mcp-trace` (matches feat type)
2. **Transition strategy for synthetic data**: Phase 1 research will recommend; Orchestrator must approve before Phase 2 proceeds
3. **File rotation**: If Phase 1 recommends bounded JSONL with rotation, should Phase 2 implement rotation in same commit or defer to follow-up? **Lean toward defer** unless trivial (<20 lines)

---

## Acceptance Criteria

- [ ] `mcp_server/dogma_server.py` appends JSONL record for every tool call (D2.1)
- [ ] Each record includes `timestamp_utc`, `tool_name`, `latency_ms`, `is_error` (D2.1)
- [ ] Error records include `error_type` and `error_message` (D2.1)
- [ ] Appending is non-blocking and does not affect tool response latency (D2.3)
- [ ] Write is atomic/append-safe per Phase 1 design (D2.3)
- [ ] Unit test coverage for JSONL append (D5.1)
- [ ] Dashboard Errors tab shows real timestamps and error messages after live session (D3.1 + D5.2)
- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date
