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

## Phase Plan

### Phase 1 — Research: MCP Server Architecture ⬜

**Agent**: Executive Researcher
**Issues**: #303 (pre-implementation architecture scan)
**Deliverables**:
- `docs/research/mcp-server-governance-tools.md` — architecture decision (transport, tool schema, auth) — Status: Final

**Depends on**: nothing
**Gate**: Phase 1 Review APPROVED before Phase 2 begins
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 1 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 1 committed
**Status**: Not started

---

### Phase 2 — Implementation: MCP Server (#303) ⬜

**Agent**: Executive Scripter
**Issues**: #303
**Deliverables**:
- `scripts/mcp_server.py` — FastMCP server exposing governance tools (validate_agent_files, validate_synthesis, fetch_source, check_substrate_health)
- `pyproject.toml` — MCP server entry point + dependencies
- `docs/guides/mcp-server.md` — usage guide
- Tests in `tests/test_mcp_server.py` (≥80% coverage)

**Depends on**: Phase 1 Review APPROVED
**Gate**: Phase 2 Review APPROVED before Phase 3 begins
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 2 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 2 committed
**Status**: Not started

---

### Phase 3 — Implementation: Pre-commit Bundle (#305) ⬜

**Agent**: Executive Scripter
**Issues**: #305
**Deliverables**:
- `pyproject.toml` updated — standalone installable `dogma-precommit` package or `.pre-commit-hooks.yaml` configuration
- `docs/guides/precommit-bundle.md` — installation and usage guide
- Tests verifying bundle configuration is valid

**Depends on**: Phase 2 Review APPROVED (shares pyproject.toml; coordinate edits)
**Gate**: Phase 3 Review APPROVED before Phase 4 begins
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 3 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 3 committed
**Status**: Not started

---

### Phase 4 — Implementation: AFS FTS5 Index + Scripting Tools (#129, #291, #292) ⬜

**Agent**: Executive Scripter
**Issues**: #129, #291, #292
**Deliverables**:
- `scripts/afs_index.py` (or extend existing AFS scripts) — SQLite FTS5 keyword index for session content (#129)
- `scripts/analyse_fleet_coupling.py` — NK K-coupling analysis per agent, high-K nodes, modularity Q (#291)
- `scripts/suggest_routing.py` — GPS-style delegation routing from task description (#292)
- Tests for each script in `tests/`
- `scripts/README.md` updated with new scripts

**Depends on**: Phase 3 Review APPROVED
**Gate**: Phase 4 Review APPROVED before Phase 5 begins
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 4 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` in scratchpad, verdict: APPROVED
**Depends on**: Phase 4 committed
**Status**: Not started

---

### Phase 5 — Docs & Sprint Close ⬜

**Agent**: Executive Docs
**Deliverables**:
- `CHANGELOG.md` updated with Sprint 17 section
- `docs/guides/` cross-references updated (MCP server, pre-commit bundle)
- Sprint 17 workplan phases all marked ✅
- Issue body checkboxes updated for all 5 sprint issues

**Depends on**: Phase 4 Review APPROVED
**Gate**: Phase 5 Review APPROVED
**CI**: Tests, Auto-validate
**Status**: Not started

---

### Phase 5 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 5 Review Output` in scratchpad, verdict: APPROVED
**Status**: Not started

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

- [ ] #303: MCP server implemented, tested (≥80% coverage), usage guide committed
- [ ] #305: Pre-commit bundle installable via pip/uv, guide committed
- [ ] #129: SQLite AFS FTS5 index script implemented and tested
- [ ] #291: `analyse_fleet_coupling.py` implemented and tested
- [ ] #292: `suggest_routing.py` implemented and tested (stretch — include if capacity allows)
- [ ] All scripts have docstring with purpose, inputs, outputs, usage
- [ ] `CHANGELOG.md` Sprint 17 section added
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
