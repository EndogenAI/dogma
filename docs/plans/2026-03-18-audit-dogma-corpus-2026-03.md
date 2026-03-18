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

### Phase 1A — #391 Agentic Fleet Sweep ⬜
**Agent**: Executive Researcher
**Description**: Audit the agent fleet substrate: `.github/agents/` and `.github/skills/`. Identify missing provenance, tool/permission drift, and redundant help prose.
**Deliverables**:
- Detailed audit findings for the fleet in scratchpad
- List of consolidate/deprecate candidates for agents and skills
**Depends on**: Phase 0
**Gate**: Phase 1A Review APPROVED
**Status**: Not started

### Phase 1B — #391 Docs Substrate Sweep ⬜
**Agent**: Executive Researcher
**Description**: Audit the documentation substrate: `docs/guides/` and `docs/research/`. Identify stale guides, lack of D4 synthesis compliance, and orphan files.
**Deliverables**:
- Detailed audit findings for documentation in scratchpad
- Synthesis table of all 60+ documents with status (Stable/Stale/Deprecate)
**Depends on**: Phase 1A
**Gate**: Phase 1B Review APPROVED
**Status**: Not started

### Phase 1C — #391 Synthesis & Implementation Roadmap ⬜
**Agent**: Executive Researcher
**Description**: Synthesize findings from 1A and 1B into a final audit report and prioritized repair backlog.
**Deliverables**:
- `docs/research/dogma-corpus-audit-2026-03.md` (Status: Final)
- Finalized Repair Backlog mapped to Phase 2 sub-phases
**Depends on**: Phase 1B
**Gate**: Synthesis doc committed and Status: Final
**Status**: Not started

### Phase 2A — #391 Structural Repairs (Governance Layer) ⬜
**Agent**: Executive Docs
**Description**: Implement repairs to high-level governance files: `AGENTS.md`, `MANIFESTO.md`, and core guides. Fix structural hierarchy and missing cross-references.
**Deliverables**:
- Updated root `AGENTS.md` and `MANIFESTO.md`
- Core guide restructuring complete
**Depends on**: Phase 1C
**Gate**: Phase 2A Review APPROVED
**Status**: Not started

### Phase 2B — #391 Content Repairs (Consolidation) ⬜
**Agent**: Executive Docs
**Description**: Consolidate stale or redundant guides into authoritative versions as mapped in Phase 1C. Mark remaining stale files as `[Deprecated]`.
**Deliverables**:
- Consolidated skills/agents documentation
- Deprecated files moved or tagged correctly
**Depends on**: Phase 2A
**Gate**: Phase 2B Review APPROVED
**Status**: Not started

### Phase 2C — #391 Fidelity Repairs (Link Integrity) ⬜
**Agent**: Executive Docs
**Description**: Execute a comprehensive fix for all broken markdown fragment links (`#fragment`) and path links identified across the corpus.
**Deliverables**:
- All broken links in `docs/` and `.github/` resolved
- Final `validate_synthesis` pass across all research docs
**Depends on**: Phase 2B
**Gate**: Phase 2C Review APPROVED
**Status**: Not started

### Phase 3 — Validation & Session Close ⬜
**Agent**: Executive Orchestrator → GitHub
**Description**: Run final programmatic substrate checks, synthesize session results, and commit/push.
**Deliverables**:
- Final `CHANGELOG.md` update
- Session Summary in scratchpad
- All changes pushed to origin
- PR body updated with `Closes #390, Closes #391`
**Depends on**: Phase 2C
**Status**: Not started

---

## Acceptance Criteria

- [ ] All sub-phases complete and committed
- [ ] No instances of `governs:` remain in frontmatter
- [ ] Sweep report cites 100% of files in `docs/` and `.github/agents/`
- [ ] `uv run python scripts/check_substrate_health.py` returns green
- [ ] All changes pushed and PR is up to date
