# Workplan: Audit and Normalize Dogma Corpus (March 2026)

**Branch**: `audit/dogma-corpus-2026-03`
**Issues**: #390, #391
**Date**: 2026-03-18
**Orchestrator**: Executive Orchestrator

---

## Objective
Normalize the `governs:` frontmatter to `x-governs:` to eliminate VS Code diagnostic noise (#390) and perform a comprehensive audit of the dogma corpus to resolve structural gaps, clarity issues, and redundancy (#391).

---

## Phase Plan

### Phase 0 — #390 Normalization (`governs:` -> `x-governs:`) ⬜
**Agent**: Executive Docs
**Description**: Rename the proprietary `governs:` frontmatter key to `x-governs:` across all `.agent.md`, `AGENTS.md`, and `SKILL.md` files to satisfy VS Code's schema validator while preserving provenance.
**Deliverables**:
- All `.github/agents/*.agent.md` files updated
- All `.github/skills/*/SKILL.md` files updated
- All `AGENTS.md` files updated
- `scripts/annotate_provenance.py` and `scripts/validate_agent_files.py` updated to support `x-governs:`
**Depends on**: nothing
**Gate**: Phase 1 does not start until `grep -r "governs:" .` (frontmatter only) returns zero matches outside of documentation.
**Status**: Not started

### Phase 1 — #391 Corpus Sweep & Research ⬜
**Agent**: Executive Researcher
**Description**: Execute a full corpus sweep to identify clarity gaps, stale guides, deprecation needs, and consolidation opportunities.
**Deliverables**:
- `docs/research/dogma-corpus-audit-2026-03.md` (Status: Final)
- Synthesis table of all 60+ documents with status (Stable/Stale/Deprecate)
**Depends on**: Phase 0
**Gate**: Phase 2 does not start until the synthesis doc is committed and Status is set to Final.
**Status**: Not started

### Phase 2 — #391 Implementation (Repairs & Consolidation) ⬜
**Agent**: Executive Docs
**Description**: Implement the repairs identified in the Phase 1 audit—fixing clarity, consolidating redundant guides, and marking stale content as deprecated.
**Deliverables**:
- Repaired guides in `docs/guides/`
- Consolidated skill or agent documentation
- All broken markdown fragment links (`#fragment`) identified in recent sessions fixed
**Depends on**: Phase 1
**Gate**: Phase 3 does not start until Reviewer returns APPROVED verdict on the repairs.
**Status**: Not started

### Phase 3 — Validation & Session Close ⬜
**Agent**: Executive Orchestrator → GitHub
**Description**: Run final programmatic substrate checks, synthesize session results, and commit/push.
**Deliverables**:
- Final `CHANGELOG.md` update
- Session Summary in scratchpad
- All changes pushed to origin
- PR body updated with `Closes #390, Closes #391`
**Depends on**: Phase 2
**Status**: Not started

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] No instances of `governs:` remain in frontmatter
- [ ] Sweep report cites 100% of files in `docs/` and `.github/agents/`
- [ ] `uv run python scripts/check_substrate_health.py` returns green
- [ ] All changes pushed and PR is up to date
