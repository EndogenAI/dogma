---
title: "MCP Server — Dogma Governance Tools"
status: "Active"
closes_issue: 303
date: 2026-03-17
sprint: 15
related_research:
  - docs/research/mcp-state-architecture.md
  - docs/research/mcp-production-pain-points.md
  - docs/research/mcp-a2a-scratchpad-query.md
  - docs/research/claude-code-cli-productivity-patterns.md
---

## Objective

Implement `scripts/mcp_governance_server.py` — a FastMCP stdio server exposing dogma governance scripts as MCP tools. Initial tool surface: scratchpad queries (#297) + validation gates + health checks. Auth-aware design for future enterprise readiness (pain point P4 from [mcp-production-pain-points.md](../research/mcp-production-pain-points.md)).

## Prerequisites

1. **Soft dependency**: B' SQLite scratchpad index (#129) — required for full FTS5 query performance. Phase 1 degrades gracefully to heading-grep fallback when absent; full performance requires B' to be complete before enabling production use.
2. #297 research doc APPROVED (defines the 3-tool interface spec)

## Phases

### Phase 1 — Scaffold and Tool Interface

**Agent**: Executive Scripter
**Description**: Implement the FastMCP server scaffold and the three scratchpad query tools from the #297 spec.

**Tasks**:
- `scripts/mcp_governance_server.py`: `FastMCP("dogma-governance")`
- Implement tools: `get_phase_status`, `get_section`, `get_blockers`
- Security controls: path allowlist to `.tmp/`, parameterized FTS5 queries, `audience: ["user"]` on all content tools
- Fallback: if B' SQLite index not present, degrade to heading-grep with explicit warning in tool output
- Test: `pytest tests/test_mcp_governance_server.py` using FastMCP test client

**Deliverables**:
- D1: `scripts/mcp_governance_server.py` with three tools implemented
- D2: `tests/test_mcp_governance_server.py` green; fallback path tested

**Depends on**: nothing (fallback covers absent B' index)
**Gate**: Phase 2 does not start until D1 and D2 confirmed; security controls reviewed.

---

### Phase 2 — Validation Tools

**Agent**: Executive Scripter
**Description**: Add validation-gate tools that wrap existing governance scripts.

**Tasks**:
- `validate_synthesis_tool`: calls `validate_synthesis.py` on a file, returns PASS/FAIL JSON
- `validate_agent_tool`: calls `validate_agent_files.py` on a file, returns PASS/FAIL JSON
- `check_scratchpad_health`: checks scratchpad exists + has `## Session Start` + not > 2000 lines
- All tools: `audience: ["user"]` annotations; exit code mapped to boolean `passed` field
- Test: extend `tests/test_mcp_governance_server.py`

**Deliverables**:
- D1: Three validation tools implemented and returning structured JSON
- D2: Extended tests green; PASS/FAIL mapping verified for non-zero exit codes

**Depends on**: Phase 1 (server scaffold must exist)
**Gate**: Phase 3 does not start until all validation tools return structured JSON and tests pass.

---

### Phase 3 — Auth Awareness

**Agent**: Executive Scripter
**Description**: Add `DOGMA_MCP_TOKEN` bearer check and optional SSE/HTTP transport.

**Tasks**:
- `X-Governance-Token` bearer check: read from `DOGMA_MCP_TOKEN` env var; skip if unset (local dev mode)
- HTTP transport option: `mcp.run(transport="sse")` with token middleware for remote access
- Document: `docs/guides/mcp-governance-server.md`

**Deliverables**:
- D1: Auth middleware implemented; unit tests cover token-present and token-absent branches
- D2: `docs/guides/mcp-governance-server.md` committed

**Depends on**: Phase 2
**Gate**: Phase 4 does not start until auth test matrix passes and guide is committed.

---

### Phase 4 — VS Code Integration

**Agent**: Executive Docs
**Description**: Wire server into `.mcp.json` and add forward-compatible discovery stub.

**Tasks**:
- `.mcp.json` at repo root: add `dogma-governance` server entry
- Optional: `.well-known/mcp-servers.json` discovery stub (forward-compatible with P3 pain point from #285)
- Verify: `claude --mcp-config .mcp.json -p "get blockers from current scratchpad"` returns output

**Deliverables**:
- D1: `.mcp.json` updated and committed
- D2: `.well-known/mcp-servers.json` stub present
- D3: End-to-end query confirmed working

**Depends on**: Phase 3
**Gate**: All three deliverables confirmed before closing issue.

---

### Phase 5 — Review & Commit

**Agent**: Review → GitHub
**Description**: Validate all changed files; commit and push.

**Deliverables**: All phases committed; PR updated; CI green.
**Depends on**: All prior phases.

## Acceptance Criteria

- [ ] `get_phase_status`, `get_section`, `get_blockers` tools functional; all content tools annotated `audience: ["user"]`
- [ ] `validate_synthesis_tool` and `validate_agent_tool` return structured PASS/FAIL JSON
- [ ] Security: path traversal and SQL injection tests pass (`tests/test_mcp_security.py`)
- [ ] Auth-aware: server accepts `DOGMA_MCP_TOKEN` env var; skips auth if unset (local dev mode)
- [ ] `.mcp.json` integration tested end-to-end; `.well-known/mcp-servers.json` stub present
- [ ] Test coverage ≥ 80%; all tests pass `uv run pytest tests/ -x`

## Risks

- FastMCP API may change across MCP SDK patch versions; pin `mcp>=1.0,<2.0`.
- B' SQLite (#129) is a hard prerequisite for full FTS5 functionality — degrade gracefully to heading-grep (documented fallback) if it slips.
- MCP spec §7 sanitization: ensure no raw scratchpad content passes through without `audience: ["user"]`.
