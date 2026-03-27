# Workplan: Sprint 21 — Governance & Infrastructure

**Branch**: `feat/sprint-21-governance-infra`
**Date**: 2026-03-28
**Orchestrator**: Executive Orchestrator
**Milestone**: Sprint 21 — Governance & Infrastructure (#36)

---

## Objective

Harden governance guardrails with intent-bound readiness contracts (#445), pre-branch domain overlap detection (#434), and gh CLI validation (#416). Standardize MCP as the preferred tool layer (#336, #333, #429) and codify recently-validated practices in documentation (#385, #428). Optional research recommendations (#474, #473) if capacity allows. This sprint consolidates production readiness from Q2 Wave research outputs and prepares the substrate for companion-repo adoption.

**Total effort**: 18 units (must-have) + 6 units (optional) = 24 units

---

## Phase Plan

### Phase 0 — Workplan Review ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict logged under `## Workplan Review Output` in scratchpad
- Phase ordering validated (no violations of research-first or documentation-first)
- All dependencies explicit and correct

**Depends on**: nothing
**Gate**: Phase 1 does not start until APPROVED verdict is recorded in scratchpad
**CI**: N/A (review only)
**Status**: Not started

---

### Phase 1 — Governance Guardrails ⬜
**Agent**: Executive Scripter + Executive Docs
**Issues**: #445 (intent-bound readiness contract), #434 (pre-branch domain overlap check), #416 (gh --body validation)
**Deliverables**:
- #445: `scripts/check_readiness_contract.py` or integration into existing scripts; tests added
- #434: `scripts/check_domain_overlap.py` or pre-branch gate script; tests added
- #416: Update scripts to enforce `--body-file` usage; add validation to catch multi-line --body patterns
- All changes committed with issue references in commit messages

**Depends on**: Phase 0 APPROVED
**Gate**: All three issues implemented, tests pass, commits pushed
**CI**: Tests (`uv run pytest tests/ -m "not slow and not integration"`), ruff check/format, validate-agent-files
**Status**: Not started

---

### Phase 1 Review — Validate Governance Guardrails ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for all Phase 1 changes
- Test coverage confirmed for each new script (≥80%)

**Depends on**: Phase 1
**Gate**: Phase 2 does not start until APPROVED verdict is recorded in scratchpad
**CI**: N/A (review only)
**Status**: Not started

---

### Phase 2 — MCP Standardization ⬜
**Agent**: Executive Scripter
**Issues**: #336 (standardize cross-platform tools via MCP), #333 (multi-provider inference abstraction)
**Deliverables**:
- #336: MCP tool wrappers standardized; platform-specific conditionals removed or isolated
- #333: `mcp_server/tools/inference.py` or equivalent abstraction added; provider routing logic implemented
- Update `data/inference-providers.yml` with multi-provider routing schema if needed
- Tests added for both MCP tool standardization and inference abstraction
- All changes committed with issue references

**Depends on**: Phase 1 Review APPROVED
**Gate**: Both issues implemented, tests pass, commits pushed
**CI**: Tests, ruff, MCP server validation
**Status**: Not started

---

### Phase 2 Review — Validate MCP Standardization ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for Phase 2 changes
- MCP tool invocation patterns verified against existing usage
- Inference provider routing tested with sample calls

**Depends on**: Phase 2
**Gate**: Phase 3 does not start until APPROVED verdict is recorded in scratchpad
**CI**: N/A (review only)
**Status**: Not started

---

### Phase 3 — Documentation ⬜
**Agent**: Executive Docs
**Issues**: #385 (add Measurability to ethical rubric), #429 (document MCP as preferred tool layer), #428 (document harness-first testing pattern)
**Deliverables**:
- #385: `docs/governance/ethical-values-procurement.md` updated with Measurability as criterion #6
- #429: `docs/guides/architecture.md` or equivalent updated to document MCP as preferred tool layer; cite decision rationale
- #428: `docs/guides/testing.md` updated with harness-first testing pattern; canonical examples included
- All changes committed with issue references

**Depends on**: Phase 2 Review APPROVED
**Gate**: All three docs updated, links validated (lychee), commits pushed
**CI**: lychee, ruff, validate-synthesis (if applicable)
**Status**: Not started

---

### Phase 3 Review — Validate Documentation ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for Phase 3 changes
- All internal links verified (no 404s)
- Canonical examples in #428 testing doc confirmed accurate

**Depends on**: Phase 3
**Gate**: Phase 4 does not start until APPROVED verdict (OR Phase 4 skipped if capacity insufficient)
**CI**: N/A (review only)
**Status**: Not started

---

### Phase 4 — Research Recommendations (OPTIONAL) ⬜
**Agent**: Executive Researcher or Executive Scripter
**Issues**: #474 (track provider diversity in health checks), #473 (update task-type-classifier with model routing)
**Note**: OPTIONAL — may be deferred if total effort exceeds M capacity (20 units)
**Deliverables**:
- #474: Update `scripts/check_substrate_health.py` to track provider diversity in health checks
- #473: Update `data/task-type-classifier.yml` with model routing logic
- Tests added for both changes
- All changes committed with issue references

**Depends on**: Phase 3 Review APPROVED
**Gate**: Both issues implemented, tests pass, commits pushed (OR phase skipped with documented rationale)
**CI**: Tests, ruff, YAML lint
**Status**: Not started (OPTIONAL)

---

### Phase 4 Review — Validate Research Recommendations (OPTIONAL) ⬜
**Agent**: Review
**Deliverables**:
- APPROVED verdict for Phase 4 changes (or N/A if Phase 4 skipped)

**Depends on**: Phase 4 (if executed)
**Gate**: Phase 5 does not start until APPROVED verdict or documented skip
**CI**: N/A (review only)
**Status**: Not started (OPTIONAL)

---

### Phase 5 — PR and Close ⬜
**Agent**: GitHub Agent + Executive Orchestrator
**Deliverables**:
- PR created on `feat/sprint-21-governance-infra` with comprehensive body listing all issues and changes
- Copilot review retrieved and triaged (follow `.github/skills/pr-review-triage/SKILL.md`)
- All blocking review comments fixed and replied to (use `scripts/pr_review_reply.py`)
- CI passes (all checks green)
- PR merged
- All closed issues confirmed via `gh issue view <num>` (auto-closed via PR body `Closes #NNN`)
- Sprint 21 milestone closed
- Session summary written to scratchpad; session archived

**Depends on**: Phase 3 Review APPROVED (and Phase 4 Review APPROVED if executed, or documented skip)
**Gate**: All issues closed, PR merged, session archived
**CI**: All automated checks must pass before merge
**Status**: Not started

---

## Parallelisation Notes

No phases can be parallelized — each domain builds on prior review gates.

---

## Capacity Decision

**Must-Have (18 units)**: Phases 1-3 are required and on-target for normal M capacity.
**Optional (6 units)**: Phase 4 research recommendations can be deferred if earlier phases overrun.
**Total with Phase 4**: 24 units — slightly over M capacity ceiling; recommend proceeding with caution or deferring Phase 4.

---

## Open Questions

1. Should Phase 4 (#474, #473) be included or deferred?
2. Milestone closure timing — close Sprint 21 after all issues confirmed closed or at PR merge?

---

## References

- Sprint planning analysis: `.tmp/main/2026-03-27.md`
- Sprint 21 milestone: https://github.com/EndogenAI/dogma/milestone/36
- Reference workplan template: `docs/plans/2026-03-27-q2-wave1-phase1.md`
