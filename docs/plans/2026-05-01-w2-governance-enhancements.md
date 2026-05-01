# Workplan: W2 Governance Enhancements

**Branch**: `feat/w2-governance-enhancements-567-569-573-574`
**Date**: 2026-05-01
**Orchestrator**: Executive Orchestrator
**Issues**: #567, #569, #573, #574

---

## Objective

Consolidate two emergent governance findings (#573, #574) with two remaining W2 content items (#567, #569) into a single coherent sprint. Governing axiom: **Programmatic-First** — #573 and #574 must produce deterministic enforcement artifacts (script, AGENTS.md convention, SKILL.md update, research doc append), not merely textual recommendations. Content phases (#567, #569) follow governance phases so any new conventions in force are respected throughout.

**Chicken-and-egg resolution**: Governance conventions (#574) precede the script (#573) because the convention defines what the script enforces. Script precedes docs updates (#573 B2) because docs reference the script by name. Content phases follow governance to respect new conventions.

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜
**Agent**: Review
**Deliverables**:
- D1: Review verdict (`APPROVED` or `REQUEST CHANGES — [reason]`)

**Depends on**: nothing (this workplan committed)
**Gate**: No domain phase begins until Phase 0 returns `APPROVED`
**Status**: ⬜ Not started

---

### Phase A — #574: Workplan-Drift Convention Encoding ⬜
**Agent**: Executive Docs
**Description**: Encode the workplan-drift convention in `AGENTS.md` § `docs/plans/` — Tracked Workplans section (or `session-management` SKILL.md) and add a companion note to GitHub agent delegation guidance. Validate `docs/guides/session-management.md` consistency.
**Deliverables**:
- D1: `AGENTS.md` updated — convention stating emergent in-scope issues must be added to workplan before PR is opened; workplan is source of truth for PR body `Closes` lines
- D2: `AGENTS.md` companion note in GitHub agent delegation section (Subagent Commit Authority or Verify-After-Act) — PR `Closes` lines must reflect current workplan scope
- D3: `docs/guides/session-management.md` reviewed for consistency; updated if needed
- D4: Committed with message `docs(agents): encode workplan-drift convention (#574)`

**Depends on**: Phase 0 `APPROVED`
**Gate**: Phase A Review must return `APPROVED` before Phase B1 begins
**Status**: ⬜ Not started

### Phase A Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase A Review Output` in scratchpad, verdict: `APPROVED`
**Depends on**: Phase A D4 committed
**Gate**: Phase B1 does not start until `APPROVED`
**Status**: ⬜ Not started

---

### Phase B1 — #573: `check_merge_authorization.py` Script ⬜
**Agent**: Executive Scripter
**Description**: Author `scripts/check_merge_authorization.py` with full tests per issue #573 AC1. Script queries PR state and outputs `MERGE AUTHORIZED` (exit 0) or `MERGE BLOCKED — [reason]` (exit 1).
**Deliverables**:
- D1: `scripts/check_merge_authorization.py` — module docstring, checks PR OPEN + no CHANGES_REQUESTED + no pending reviewRequests + all non-nit threads resolved
- D2: `--dry-run` mode (print full check table, always exit 0), `--allow-nit-unresolved` flag (default on), `--repo owner/repo` option
- D3: `scripts/README.md` updated with new script entry
- D4: `tests/test_check_merge_authorization.py` — happy path, each blocked scenario, nit-exemption, `--dry-run`, API error (exit 2); min 80% coverage
- D5: `uv run ruff check scripts/` and `uv run ruff format --check scripts/` pass
- D6: Committed with message `feat(scripts): add check_merge_authorization.py (#573)`

**Depends on**: Phase A Review `APPROVED`
**Gate**: Phase B1 Review must return `APPROVED` before Phase B2 begins
**Status**: ⬜ Not started

### Phase B1 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase B1 Review Output` in scratchpad, verdict: `APPROVED`
**Depends on**: Phase B1 D6 committed
**Gate**: Phase B2 does not start until `APPROVED`
**Status**: ⬜ Not started

---

### Phase B2 — #573: Governance Docs Updates ⬜
**Agent**: Executive Docs
**Description**: Three governance doc updates completing #573: AGENTS.md Merge Authorization section, pr-review-triage SKILL.md Step 0 addition, orchestrator-autopilot-failure.md Pattern 6 append.
**Deliverables**:
- D1: `AGENTS.md` — add `## Merge Authorization — PR #NNN` 5-checkbox template to PR Review Triage Gate section; document final human-gate checkbox
- D2: `.github/skills/pr-review-triage/SKILL.md` — add `check_merge_authorization.py` as Step 0 (pre-merge check); reference scratchpad `## Merge Authorization` requirement
- D3: `docs/research/orchestrator-autopilot-failure.md` — append Pattern 6 (Heuristic Closure) to Pattern Catalog (definition, anti-pattern, canonical example, MANIFESTO violation ref); add Recommendation 6 "Merge Authorization Gate (Track F)"; update frontmatter `updated` field
- D4: `uv run python scripts/validate_synthesis.py docs/research/orchestrator-autopilot-failure.md` passes
- D5: All changes committed with message `docs(governance): add Pattern 6 Heuristic Closure + merge auth convention (#573)`

**Depends on**: Phase B1 Review `APPROVED` (docs reference the script by name)
**Gate**: Phase B2 Review must return `APPROVED` before Phase C begins
**Status**: ⬜ Not started

### Phase B2 Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase B2 Review Output` in scratchpad, verdict: `APPROVED`
**Depends on**: Phase B2 D5 committed
**Gate**: Phase C does not start until `APPROVED`
**Status**: ⬜ Not started

---

### Phase C — #567: Glossary Audit and README Linking ⬜
**Agent**: Executive Docs
**Description**: Audit `docs/glossary.md` — add `Sovereignty` entry, review `Endogenous-First` and `Endogenic Development`, audit README terms, improve README→glossary inline linking.
**Deliverables**:
- D1: `Sovereignty` entry added to glossary (definition, source citation, related terms)
- D2: `Endogenous-First` and `Endogenic Development` entries reviewed — confirm they sufficiently define `endogenous` for README readers
- D3: README terms audit complete — all prominent README terms without glossary entries added
- D4: README inline links to glossary for key terms (e.g., `endogenous` in tagline/intro → glossary anchor)
- D5: All glossary internal cross-reference links validated (no broken links)
- D6: Committed with message `docs(glossary): audit glossary + improve README linking (#567)`

**Depends on**: Phase B2 Review `APPROVED`
**Gate**: Phase C Review must return `APPROVED` before Phase D begins
**Status**: ⬜ Not started

### Phase C Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase C Review Output` in scratchpad, verdict: `APPROVED`
**Depends on**: Phase C D6 committed
**Gate**: Phase D does not start until `APPROVED`
**Status**: ⬜ Not started

---

### Phase D — #569: AccessiTech Case Study ⬜
**Agent**: Executive Docs
**Description**: Add AccessiTech case study to README (dedicated section or expanded Use Cases entry). Distill 11-point narrative into clean accessible text with collective "we" language. References four-substrate model (from prior sprint) if it exists; otherwise self-contained. **Requires Conor sign-off on final draft before commit.**
**Deliverables**:
- D1: Case study section drafted in README — collective "we" voice, laypeople-accessible, distilled from 11-point narrative
- D2: `dA11y` defined or linked
- D3: Section references four-substrate model if Phase 1A from prior sprint was committed; otherwise self-contained
- D4: **Human gate**: Conor reviews and approves wording — this step surfaces the draft to the user before commit
- D5: Committed (after D4 approval) with message `docs(readme): add AccessiTech case study (#569)`

**Depends on**: Phase C Review `APPROVED`
**Gate**: Phase D Review must return `APPROVED` before Final Review begins; D4 (human sign-off) must precede D5 (commit)
**Status**: ⬜ Not started

### Phase D Review — Review Gate ⬜
**Agent**: Review
**Deliverables**: `## Phase D Review Output` in scratchpad, verdict: `APPROVED`
**Depends on**: Phase D D5 committed
**Gate**: Final Review does not start until `APPROVED`
**Status**: ⬜ Not started

---

### Phase Final — Final Review & PR Open ⬜
**Agent**: Review → GitHub
**Description**: Validate all changes across all phases, confirm all acceptance criteria satisfied, push, open PR with all 4 `Closes` lines.
**Deliverables**:
- D1: Review verdict `APPROVED`
- D2: All changes pushed to `feat/w2-governance-enhancements-567-569-573-574`
- D3: PR opened with `Closes #567`, `Closes #569`, `Closes #573`, `Closes #574` in body
- D4: CI passing

**Depends on**: All domain phase Reviews `APPROVED`
**Gate**: Sprint not complete until D4 confirmed (CI green) and PR Review Triage Gate complete
**Status**: ⬜ Not started

---

## Success Criteria

Sprint is complete when:

- [ ] #574: `AGENTS.md` has workplan-drift convention; session-management SKILL.md consistent
- [ ] #573: `scripts/check_merge_authorization.py` committed with tests (≥80% coverage, ruff clean)
- [ ] #573: `AGENTS.md` Merge Authorization 5-checkbox template added to PR Review Triage Gate
- [ ] #573: `.github/skills/pr-review-triage/SKILL.md` updated with `check_merge_authorization.py` as Step 0
- [ ] #573: `docs/research/orchestrator-autopilot-failure.md` Pattern 6 appended + Recommendation 6 added
- [ ] #567: `Sovereignty` entry added to glossary; README→glossary linking improved
- [ ] #569: AccessiTech case study in README, collective "we" voice, Conor-approved
- [ ] All Review gates returned `APPROVED`
- [ ] All commits follow Conventional Commits format
- [ ] CI passes on branch
- [ ] PR opened with `Closes #567`, `Closes #569`, `Closes #573`, `Closes #574`

---

## Emergent Issue Tracking

If any issue is discovered mid-sprint that addresses a problem not in original scope, add it here **immediately**, add `Closes #NNN` to Phase Final deliverables, and document the addition in the scratchpad. (This section implements #574's workplan-drift convention.)

---

## Acceptance Criteria

- [ ] All phases complete and committed
- [ ] All changes pushed and PR is up to date

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #567, Closes #569, Closes #573, Closes #574
