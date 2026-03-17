# Workplan: Sprint 17 — MCP Packaging & Scripting Tools

**Branch**: `feat/sprint-17-mcp-packaging-scripting-tools`
**Date**: 2026-03-17
**Milestone**: [Sprint 17 — MCP Packaging & Scripting Tools](https://github.com/EndogenAI/dogma/milestone/17)
**Orchestrator**: Executive Orchestrator

---

## Objective

Sprint 17 completes the external-packaging arc started in Sprint 15: shipping dogma's
governance toolchain as a standalone MCP server (#303) and pip/uv-installable pre-commit
bundle (#305) so external projects can adopt dogma's governance stack without forking the
full repo. Alongside packaging, the sprint completes the Sprint 16 carry-over AFS FTS5
scripting item (#129) and adds two fleet observability/routing scripts (#291, #292) that
improve the delegation decision loop. The shared throughline is *production readiness for
external use* — packaging, discoverability, and fleet intelligence tooling.

**Sprint capacity**: M (normal sprint, ~19 effort units)

| # | Title | Priority | Effort | Cluster |
|---|-------|----------|--------|---------|
| #303 | dogma governance tools as MCP server | high | XL | packaging |
| #305 | Standalone pip/uv pre-commit bundle | medium | L | ci/packaging |
| #129 | SQLite AFS FTS5 Keyword Index | medium | M | scripting |
| #291 | analyse_fleet_coupling.py | medium | M | scripting |
| #292 | suggest_routing.py (stretch) | medium | M | scripting |

---

## Architecture Decisions (2026-03-17)

1. **MCP SDK**: official `mcp>=1.0` (includes FastMCP high-level API). Added as `[project.optional-dependencies] mcp = ["mcp>=1.0"]` — users enable with `uv sync --extra mcp`. No Tasks API — synchronous request/response only per `docs/research/mcp-production-pain-points.md` Rec 2.
2. **Phase ordering**: Scripting tools (#129, #291, #292) deliver in Phase 2 before MCP server (Phase 3). Required by #303 acceptance criteria gate: scratchpad tools depend on B' FTS5 index (#129) shipping first.
3. **`dogma-governance` package**: Option A — standalone with schemas embedded as package data. Zero imports from `scripts/` or `data/`. Validation logic extracted into `packages/dogma-governance/dogma_governance/` with YAML schemas as embedded package data.

---

## Phase Plan

### Phase 1 — Research: MCP Server Architecture ✅ (pre-done)

**Note**: Three Final research docs already cover all architecture decisions. Skipping delegation.
- `docs/research/mcp-production-pain-points.md` (Status: Final, closes #285)
- `docs/research/mcp-state-architecture.md` (Status: Final)
- `docs/research/mcp-a2a-scratchpad-query.md` (Status: Final)

**Status**: Complete — pre-existing research docs

---

### Phase 2 — Implementation: Scripting Tools (#129, #291, #292) ✅

**Agent**: Executive Scripter
**Issues**: #129, #291, #292
**Deliverables**:
- `scripts/afs_index.py` — SQLite FTS5 B' hybrid index for scratchpad session content (#129)
- `scripts/analyse_fleet_coupling.py` — NK K-coupling per agent, high-K nodes, modularity Q (#291)
- `scripts/suggest_routing.py` — GPS-style delegation routing from task description (#292)
- `data/task-type-classifier.yml` — keyword-to-task-type mapping for suggest_routing.py
- Tests for each script in `tests/` (≥80% coverage)
- `scripts/README.md` updated with new scripts

**Depends on**: Phase 1 (pre-done)
**Gate**: Phase 2 Review APPROVED before Phase 3 begins
**CI**: Tests, Auto-validate
**Status**: Complete

---

### Phase 2 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 2 committed
**Status**: Complete — APPROVED

---

### Phase 3 — Implementation: MCP Server (#303) ✅

**Agent**: Executive Scripter
**Issues**: #303
**Deliverables**:
- `mcp_server/dogma_server.py` — FastMCP server using official `mcp>=1.0` SDK
- `mcp_server/tools/` — tool modules (validation, scaffolding, query)
- `mcp_server/README.md` — quickstart (Claude Desktop + Cursor config snippets)
- `mcp_server/.well-known/mcp-servers.json` — discovery stub
- `.env.example` — `DOGMA_MCP_PORT`, `DOGMA_MCP_AUTH_TOKEN`
- `pyproject.toml` updated — `[project.optional-dependencies] mcp = ["mcp>=1.0"]`
- Tests in `tests/test_mcp_server.py` (≥80% coverage, mock MCP client)

**Depends on**: Phase 2 Review APPROVED (scratchpad tools require #129 FTS5 index)
**Gate**: Phase 3 Review APPROVED before Phase 4 begins
**CI**: Tests, Auto-validate
**Status**: Complete

---

### Phase 3 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 3 committed
**Status**: Complete — APPROVED

---

### Phase 4 — Implementation: Pre-commit Bundle (#305) ✅

**Agent**: Executive Scripter
**Issues**: #305
**Deliverables**:
- `packages/dogma-governance/` — standalone Python package (Option A: embedded schemas, zero dogma-internal deps)
- `packages/dogma-governance/dogma_governance/` — extracted validator modules
- `packages/dogma-governance/dogma_governance/data/` — embedded YAML schema data
- `packages/dogma-governance/pyproject.toml` — packaging metadata + CLI entry points
- `packages/dogma-governance/.pre-commit-hooks.yaml` — hook definitions
- `packages/dogma-governance/tests/` — full test suite (≥80% coverage)
- `packages/dogma-governance/README.md` — installation + quickstart
- `.github/workflows/release-governance-package.yml` — PyPI publish on tag

**Depends on**: Phase 3 Review APPROVED
**Gate**: Phase 4 Review APPROVED before Phase 5 begins
**CI**: Tests, Auto-validate
**Status**: Complete

---

### Phase 4 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 4 committed
**Status**: Complete — APPROVED

---

### Phase 5 — Docs & Sprint Close ✅

**Agent**: Executive Docs
**Deliverables**:
- `CHANGELOG.md` updated with Sprint 17 section
- `docs/guides/` cross-references updated (MCP server, pre-commit bundle)
- Sprint 17 workplan execution phases (1–5) marked ✅
- Issue body checkboxes updated for all 5 sprint issues

**Depends on**: Phase 4 Review APPROVED
**Gate**: Phase 5 Review APPROVED
**CI**: Tests, Auto-validate
**Status**: Complete

---

### Phase 5 Review — Review Gate ⏳

**Agent**: Review
**Deliverables**: `## Phase 5 Review Output` in scratchpad, verdict: APPROVED
**Status**: In progress

---

### Phase 6 — Commit, PR & Release ⬜

**Agent**: GitHub Agent
**Deliverables**:
- All phases committed to `feat/sprint-17-mcp-packaging-scripting-tools`
- PR opened: "feat(sprint-17): MCP server, pre-commit bundle, AFS FTS5, fleet scripting tools"
- PR body contains `Closes #303, Closes #305, Closes #129, Closes #291, Closes #292`
- CI green before review requested

**Depends on**: Phase 5 Review APPROVED
**Status**: Not started

---

## Acceptance Criteria

- [x] #303: MCP server implemented, tested (≥80% coverage), usage guide committed
- [x] #305: Pre-commit bundle installable via pip/uv, guide committed
- [x] #129: SQLite AFS FTS5 index script implemented and tested
- [x] #291: `analyse_fleet_coupling.py` implemented and tested
- [x] #292: `suggest_routing.py` implemented and tested (stretch — include if capacity allows)
- [x] All scripts have docstring with purpose, inputs, outputs, usage
- [x] `CHANGELOG.md` Sprint 17 section added
- [ ] CI green on PR
- [ ] All 5 sprint issues closed via PR merge

## PR Description Template

```
feat(sprint-17): MCP packaging, pre-commit bundle, AFS FTS5, fleet scripting tools

Closes #303, Closes #305, Closes #129, Closes #291, Closes #292

## Summary
- #303: dogma governance tools exposed as FastMCP server
- #305: standalone pip/uv installable pre-commit bundle
- #129: SQLite FTS5 keyword index for AFS session content
- #291: analyse_fleet_coupling.py — NK K-coupling per-agent analysis
- #292: suggest_routing.py — GPS-style delegation routing (stretch)
```
