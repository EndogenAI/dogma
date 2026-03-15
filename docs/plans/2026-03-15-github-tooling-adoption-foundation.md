# Workplan: GitHub Bulk Tooling + Adoption Foundation + Phase 10 Research

**Branch**: `feat/sprint-2026-03-15-github-tooling-adoption`
**Date**: 2026-03-15
**Orchestrator**: Executive Orchestrator
**Milestone context**: Milestone #5 (Adoption), Milestone #9 (Action Items), Milestone #10 (Phase 10 Research)

---

## Objective

Deliver two high-priority bulk GitHub operations scripts (#260, #261), lay the adoption foundation by shipping the product-fork initialization guide and research (#207, #204), advance the Greenfield onboarding wizard (#57), ship a batch of quick-win scripts and CI tooling (#259, #105, #223), and seed Phase 10 research (#196, #197). Sprint is capped at 10 issues; 15 remaining open issues are explicitly deferred. A separate sprint is recommended for Phase 10 deep-dive execution and AFS integration.

---

## Issue Inventory (10 sprint-scoped)

| # | Title | Type | Priority | Effort | Milestone |
|---|-------|------|----------|--------|-----------|
| #261 | feat(scripts): bulk_github_read.py — batch issue/PR metadata read | feature | high | M | — |
| #260 | feat(scripts): bulk_github_operations.py — batch write ops with rate-limit throttling | feature | high | M | — |
| #259 | feat(ci): pre-commit hook for stale GitHub URL detection | feature | medium | S | — |
| #223 | docs: create reusable corpus-sweep skill for large-corpus scouting | docs | low | S | — |
| #207 | research(adoption): product-fork-initialization guide | research | medium | S | — |
| #204 | docs: add product fork initialization guide and update README | docs | medium | M | — |
| #57 | feat: implement Greenfield onboarding wizard (cookiecutter template) | feature | medium | M-L | #5 |
| #105 | feat(scripts): implement scripts/amplify_context.py | feature | medium | M | #9 |
| #196 | Topological-Temporal Coherence Joint Specification — Phase 10 Research | research | high | L | #10 |
| #197 | Programmatic Governance Coverage Asymmetry — Semantic Drift Detection | research | high | L | #10 |

---

## Deferred Issues (15 — explicit defer)

| # | Title | Reason |
|---|-------|--------|
| #221 | GitHub Actions caching patterns — XL effort | Needs dedicated research sprint |
| #206 | FrankenBrAIn benchmark | Adoption milestone, defer after #57 |
| #202 | MkDocs Material docsite | Low priority, separate chore sprint |
| #158 | capability-aware agent registry design | Action item, M effort, next sprint |
| #157 | subshell audit logging in PREEXEC governor | S effort, next scripts sprint |
| #156 | token-spinning detection and rate-limiting | S effort, next scripts sprint |
| #231 | H1 empirical baseline — encode-before-act comparison | Research sprint #11 |
| #230 | Validate explicit output format constraint driver | Research sprint #11 |
| #234 | Empirical session studies — substrate commit ratio | Research sprint #11 |
| #232 | H2 NK model Kauffman K-coupling graph | Research sprint #11 |
| #128 | Phase 1 AFS Integration — Index Session to AFS | Complex, depends on #129 |
| #129 | SQLite-only Pattern A1 for AFS — FTS5 Index | Complex, further research needed |
| #131 | Cognee Library Adoption | Blocked |
| #113 | Tier 2 Behavioral Testing — Drift Detection | Low, deferred |
| #253 | parse_fsm_to_graph.py — FSM-to-NetworkX | Low, deferred |

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜

**Agent**: Review
**Deliverables**: Verdict logged under `## Workplan Review Output` in session scratchpad — must return APPROVED before Phase 1 begins
**Depends on**: this workplan committed
**Gate**: Phase 1 does not begin until Review returns APPROVED
**Status**: ⬜ Not started

---

### Phase 1 — Sprint Triage & Label Hygiene ⬜

**Agent**: Executive PM
**Deliverables**:
- D1: #204 and #207 assigned appropriate `type:`, `priority:`, and `area:` labels
- D2: #204 and #207 assigned to a milestone (Adoption: Scripts & Tooling #5 or new)
- D3: Sprint branch `feat/sprint-2026-03-15-github-tooling-adoption` created from main
- D4: Triage log appended to session scratchpad

**Depends on**: Phase 0 APPROVED
**Gate**: Labels verified via `gh issue view <num> --json labels` before Phase 2 begins
**Status**: ⬜ Not started

---

### Phase 1 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` in scratchpad — verdict APPROVED
**Depends on**: Phase 1 deliverables complete
**Gate**: Phase 2 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — Bulk GitHub Operations Scripts ⬜

**Agent**: Executive Scripter
**Deliverables**:
- D1: `scripts/bulk_github_operations.py` — batch write ops (create/edit/close issues, PRs, labels) with rate-limit throttling, `--dry-run` guard, docstring, usage example (closes #260)
- D2: `scripts/bulk_github_read.py` — batch read of issue/PR metadata with structured output formatting (closes #261)
- D3: `tests/test_bulk_github_operations.py` and `tests/test_bulk_github_read.py` — ≥80% coverage; happy path, error cases, exit codes
- D4: Both scripts committed on sprint branch

**Depends on**: Phase 1 Review APPROVED
**Script note**: Scripts must open with docstring (purpose, inputs, outputs, usage). `--dry-run` on bulk_github_operations.py is mandatory (AGENTS.md script safety).
**Gate**: Tests pass (`uv run pytest tests/test_bulk_github_*.py`) before Phase 2 Review
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` in scratchpad — verdict APPROVED
**Depends on**: Phase 2 deliverables committed + tests passing
**Gate**: Phase 3 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — CI & Quick-Win Scripts ⬜

**Agent**: Executive Scripter + Executive Automator (coordinate on #259)
**Deliverables**:
- D1: Pre-commit hook for stale GitHub URL detection in committed docs (closes #259) — added to `.pre-commit-config.yaml`, tested via `uv run pre-commit run --all-files`
- D2: `scripts/amplify_context.py` — Phase 2 Programmatic-First encoding of context-sensitive axiom amplification from AGENTS.md table (closes #105) + test coverage
- D3: `.github/skills/corpus-sweep/SKILL.md` — reusable skill for large-corpus scouting (>20 docs); CI-validated via `uv run python scripts/validate_skill_files.py` (closes #223)

**Depends on**: Phase 2 Review APPROVED
**Gate**: `uv run pre-commit run --all-files` clean; `uv run pytest tests/test_amplify_context.py` pass before Phase 3 Review
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` in scratchpad — verdict APPROVED
**Depends on**: Phase 3 deliverables committed
**Gate**: Phase 4 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 4 — Adoption Research ⬜

**Agent**: Executive Researcher (Scout → Synthesizer pattern)
**Deliverables**:
- D1: Per-source synthesis stubs in `docs/research/sources/` (at least 3 sources on fork-initialization / dogma adoption patterns)
- D2: `docs/research/product-fork-initialization.md` — D4 synthesis doc with frontmatter (`title`, `status: Draft`), Pattern Catalog with ≥1 canonical example and ≥1 anti-pattern (closes #207)
- D3: Research doc committed on sprint branch

**Depends on**: Phase 3 Review APPROVED
**Research gate**: This is phase-specific research (informs only Phase 5 / #204) — placed N-1 as required by sprint phase ordering constraints
**Gate**: D2 committed before Phase 4 Review
**Status**: ⬜ Not started

---

### Phase 4 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` in scratchpad
**Depends on**: Phase 4 deliverables committed
**Gate**: Phase 5 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 5 — Adoption Documentation ⬜

**Agent**: Executive Docs
**Deliverables**:
- D1: `docs/guides/product-fork-initialization.md` — complete procedure guide drawing from Phase 4 research; includes: pre-fork checklist, `client-values.yml` setup, agent fleet customization steps, README update hook (closes #204)
- D2: `README.md` updated with link to fork initialization guide in "Getting Started" section
- D3: Both files committed on sprint branch

**Depends on**: Phase 4 Review APPROVED (research gates this doc)
**Gate**: Doc passes `uv run python scripts/validate_synthesis.py` if it has D4 frontmatter; link check clean
**Status**: ⬜ Not started

---

### Phase 5 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 5 Review Output` in scratchpad
**Depends on**: Phase 5 deliverables committed
**Gate**: Phase 6 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 6 — Greenfield Onboarding Wizard ⬜

**Agent**: Executive Scripter
**Deliverables**:
- D1: `scripts/adopt_wizard.py` — interactive CLI wizard that scaffolds a new repo using cookiecutter template; prompts for project name, domain, tech stack; writes `client-values.yml` and initialises agent fleet stubs (closes #57)
- D2: `tests/test_adopt_wizard.py` — ≥80% coverage; happy path, dry-run, invalid input
- D3: Wizard documented in `docs/guides/product-fork-initialization.md` (link from Phase 5 doc)
- D4: Committed on sprint branch

**Depends on**: Phase 5 Review APPROVED (wizard guide exists before wizard ships)
**Gate**: `uv run pytest tests/test_adopt_wizard.py` passes before Phase 6 Review
**Status**: ⬜ Not started

---

### Phase 6 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 6 Review Output` in scratchpad
**Depends on**: Phase 6 deliverables committed
**Gate**: Phase 7 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 7 — Phase 10 Research Sprint ✅

**Agent**: Executive Researcher (full Scout → Synthesizer → Reviewer pipeline)
**Deliverables**:
- D1: `docs/research/topological-temporal-coherence.md` — D4 synthesis with Pattern Catalog, Hypothesis Validation, Recommendations; `status: Draft`; closes #196
- D2: `docs/research/semantic-drift-detection.md` — D4 synthesis for Programmatic Governance Coverage Asymmetry + Semantic Drift Detection; `status: Draft`; closes #197
- D3: Both research docs committed on sprint branch; source stubs under `docs/research/sources/`

**Depends on**: Phase 6 Review APPROVED
**Note**: Phase 10 research (#196, #197) is the final phase — placed last because it is self-contained and does not gate any implementation phase in this sprint. If context window pressure is high after Phase 6, this phase may be deferred to the next sprint with a recorded decision in the scratchpad.
**Gate**: Both docs pass `uv run python scripts/validate_synthesis.py` before Phase 7 Review
**Status**: ✅ Complete — `308c2e9`

---

### Phase 7 Review — Review Gate ✅

**Agent**: Review
**Deliverables**: `## Phase 7 Review Output` in scratchpad
**Depends on**: Phase 7 deliverables committed
**Gate**: Phase 8 does not begin until APPROVED
**Status**: ✅ APPROVED (first pass)

---

### Phase 8 — Commit, PR & Session Close ✅

**Agent**: GitHub (commits/push/PR) + Executive Orchestrator (session close)
**Deliverables**:
- D1: All sprint branch changes pushed to `origin/feat/sprint-2026-03-15-github-tooling-adoption`
- D2: PR opened from sprint branch → main, body includes `Closes #261 Closes #260 Closes #259 Closes #223 Closes #207 Closes #204 Closes #57 Closes #105 Closes #196 Closes #197`
- D3: `## Session Summary` written to scratchpad
- D4: Progress comment posted on every actively-worked issue

**Depends on**: Phase 7 Review APPROVED (or Phase 6 Review APPROVED if Phase 7 deferred)
**Gate**: `git status` clean; `gh pr view` returns PR URL
**Status**: ✅ Complete — PR #263 opened

---

## Acceptance Criteria

- [ ] Phase 0 — Workplan Review: APPROVED logged in scratchpad
- [ ] Phase 1 — #204 and #207 labelled and milestoned; sprint branch created
- [ ] Phase 2 — `bulk_github_operations.py` and `bulk_github_read.py` shipped with ≥80% test coverage (#260, #261 closed)
- [ ] Phase 3 — stale-URL pre-commit hook live; `amplify_context.py` shipped; corpus-sweep skill committed (#259, #105, #223 closed)
- [ ] Phase 4 — `docs/research/product-fork-initialization.md` committed as D4 Draft (#207 closed)
- [ ] Phase 5 — `docs/guides/product-fork-initialization.md` committed; README updated (#204 closed)
- [ ] Phase 6 — `scripts/adopt_wizard.py` shipped with tests (#57 closed)
- [x] Phase 7 — Two Phase 10 D4 research docs committed (or deferral decision recorded) (#196, #197 closed or deferred with note)
- [x] Phase 8 — PR opened with all `Closes #N` lines; progress comments posted on all 10 issues
- [ ] All changes pushed and PR is up to date

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #261, Closes #260, Closes #259, Closes #223, Closes #207, Closes #204, Closes #57, Closes #105, Closes #196, Closes #197
