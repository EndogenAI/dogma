# Workplan: Sprint 15 — Fleet Intelligence & Local RAG

**Branch**: `feat/sprint-15-fleet-intelligence-local-rag`
**Milestone**: Sprint 15 — Fleet Intelligence & Local RAG
**Date**: 2026-03-16
**Orchestrator**: Executive Orchestrator
**Capacity**: M (≤20 effort units) | Sprint total: 16 units

---

## Objective

Sprint 15 advances two parallel tracks. The **Fleet Intelligence** track delivers two
high-value scripts from Sprint 12 synthesis: `analyse_fleet_coupling.py` (#291) makes
NK K-coupling and modularity metrics observable and auditable; `suggest_routing.py` (#292)
turns the topological delegation sequence into a GPS-style routing tool agents can invoke
by task description. The **Local RAG & MCP** track first surveys MCP production pain points
(#285 — research gates the RAG companion-repo decisions), then plans and scaffolds the
LanceDB + BGE-Small local RAG greenfield companion repo (#294). A quick process win (#298,
`priority:low`) is included as Phase 4 because it is effort:S with zero dependencies and
rounds the sprint without displacing any higher-priority work. Phase ordering follows the
*Research-First (phase-specific)* constraint: #285 MCP research runs as Phase 2
(N-1 before Phase 3 Local RAG implementation).

**Capacity**: 3 (M) + 3 (M) + 3 (M) + 5 (L) + 2 (S) = 16 pts against 20pt medium target.

---

## Issue Inventory (5 sprint-scoped)

| # | Title | Type | Priority | Effort | Cluster |
|---|-------|------|----------|--------|---------|
| #291 | feat(scripts): analyse_fleet_coupling.py — NK K-coupling per agent | feature | medium | M | scripting |
| #292 | feat(scripts): suggest_routing.py — GPS-style delegation routing | feature | medium | M | scripting |
| #285 | research: MCP production pain points — implications for dogma architecture | research | medium | M | research |
| #294 | research: Local RAG adoption — LanceDB + BGE-Small greenfield companion repo | research | medium | L | research |
| #298 | chore(process): HGT ingestion sprint cadence + task-regime FSM annotation | chore | low | S | docs |

---

## Deferred Issues (10 — explicit defer)

| # | Title | Reason |
|---|-------|--------|
| #297 | research: MCP-mediated scratchpad query as A2A minimal viable surface | priority:low; depends on #285 and #294 outputs — natural next-sprint pick-up |
| #296 | docs: greenfield-decision.md — 5-criterion framework guide | priority:low; natural follow-on after #294 ships |
| #295 | docs: platform-migration.md + MANIFESTO.md Platform Infrastructure section | priority:low; no implementation gate |
| #284 | research: Claude Code CLI tool productivity patterns | priority:low; no blocking dependency |
| #283 | research: Emojis as ultra-high-context tokens | priority:low; no blocking dependency |
| #234 | research: Empirical session studies — substrate commit ratio (Q2) | priority:low; standalone research sprint item |
| #131 | Cognee Library Adoption | status:blocked; depends on local compute baseline |
| #129 | SQLite-only Pattern A1 for AFS — FTS5 Keyword Index | priority:low; needs further scoping |
| #128 | Phase 1 AFS Integration — Index Session to AFS on Session Close | priority:low; depends on #129 |
| #113 | Tier 2 Behavioral Testing — Drift Detection | priority:low; deferred repeatedly |

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜

**Agent**: Review
**Deliverables**: Verdict logged under `## Workplan Review Output` in session scratchpad — must return APPROVED before Phase 1 begins
**Depends on**: nothing (review this doc)
**Gate**: Phase 1 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 1 — Fleet Intelligence Scripts ⬜

**Agent**: Executive Scripter
**Issues**: #291 (effort:m, priority:medium), #292 (effort:m, priority:medium)
**Deliverables**:
- D1: `scripts/analyse_fleet_coupling.py` — parse `.github/agents/*.agent.md` (using the `handoffs` YAML frontmatter field as the canonical source) and `data/delegation-gate.yml` to build delegation graph; compute K per agent; flag high-K nodes (K > 6); compute Newman-Girvan modularity Q via NetworkX (optional dep with graceful degradation); output JSON + human-readable table; `--threshold` flag
- D2: `tests/test_analyse_fleet_coupling.py` — ≥80% coverage; mocked graph fixtures; graceful-degradation test for missing NetworkX (closes #291)
- D3: `data/task-type-classifier.yml` — **new file** to be created; ≥10 task-type entries covering: research, docs, scripting, fleet, CI, review, commit
- D4: `scripts/suggest_routing.py` — accept free-text task description; map keywords via `data/task-type-classifier.yml` (new, D3); read `data/delegation-gate.yml` (existing) and `data/phase-gate-fsm.yml` (existing); output topological delegation sequence + FSM gate requirements; `--format json|markdown` flag; annotate each step with governing axiom from `data/amplification-table.yml` (existing)
- D5: `tests/test_suggest_routing.py` — ≥80% coverage (closes #292)
- D6: `docs/guides/session-management.md` updated with quarterly coupling-audit cadence under substrate health section

**Depends on**: Phase 0 APPROVED
**CI**: `ruff check scripts/ tests/`, `pytest tests/test_analyse_fleet_coupling.py tests/test_suggest_routing.py --cov ≥80%`
**Gate**: Both scripts pass ruff + ≥80% coverage before Phase 1 Review
**Status**: ⬜ Not started

---

### Phase 1 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` in scratchpad
**Depends on**: Phase 1 deliverables committed
**Gate**: Phase 2 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — MCP Production Pain Points Research ⬜

**Agent**: Executive Researcher (Research Scout → Synthesizer → Reviewer pipeline)
**Issues**: #285 (effort:m, priority:medium)
**Deliverables**:
- D1: Source cached via `uv run python scripts/fetch_source.py <url>` (The New Stack article + any MCP spec roadmap references)
- D2: Research triage note added to #285: relevance to dogma MCP plans (high/medium/low) and any updated architecture recommendations
- D3: If pain points significantly affect Tier 2/3 recommendations in `docs/research/intelligence-architecture-synthesis.md`, a brief amendment note committed to that doc
- D4: Scratchpad entry `## Phase 2 MCP Research Findings` summarising: documented pain points, dogma impact assessment, roadmap status, and Gate recommendation for #294 RAG MCP server design

**Depends on**: Phase 1 Review APPROVED (research placed N-1 before Phase 3 Local RAG per Sprint Phase Ordering Constraints)
**CI**: `uv run python scripts/validate_synthesis.py` if any D4 research doc is modified
**Gate**: Phase 2 Review APPROVED gates Phase 3 — Local RAG implementation must not begin until MCP pain-point findings are available
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` in scratchpad
**Depends on**: Phase 2 deliverables committed
**Gate**: Phase 3 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — Local RAG Greenfield Companion Repo ⬜

**Agent**: Executive Scripter + Executive Researcher
**Issues**: #294 (effort:l, priority:medium)
**Deliverables**:
- D1: Greenfield companion repo created via `cookiecutter gh:EndogenAI/dogma` if the template is available and complete; if not, scaffold a minimal repo manually using the structure defined in `docs/research/local-inference-rag.md` and `docs/research/greenfield-repo-candidates.md` — verify template existence as first action before this phase begins
- D2: `companion-repos.yml` in dogma root with schema: `name`, `url`, `description`, `greenfield-score`, `decision-date`
- D3: MCP server in companion repo exposing `rag_query(query: str)` and `rag_reindex()` tool endpoints (LanceDB + BGE-Small-EN-v1.5 + H2-level chunking); `rag-index/` added to `.gitignore` with `.gitkeep` exemption
- D4: Post-commit hook trigger for `rag_reindex` on new commits to `docs/` (companion repo)
- D5: README in companion repo links back to `docs/research/local-inference-rag.md` as rationale; design decisions reference Phase 2 MCP pain-point findings

**Depends on**: Phase 2 Review APPROVED (MCP server design informed by #285 findings)
**CI**: `uv run python scripts/validate_synthesis.py` if any dogma research doc touched; `ruff` on any new dogma scripts
**Gate**: `rag_query` returns top-5 relevant doc chunks for a test query; `rag_reindex` completes full re-index of `docs/` within the time bound documented in `docs/research/local-inference-rag.md` (reference benchmark: < 30s on Apple Silicon M-series — equivalent bound on other architectures to be measured and documented during Phase 3)
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` in scratchpad
**Depends on**: Phase 3 deliverables committed
**Gate**: Phase 4 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 4 — Process Cadence & HGT FSM Annotation ⬜

**Agent**: Executive Docs
**Issues**: #298 (effort:s, priority:low)
**Deliverables**:
- D1: `docs/guides/session-management.md` updated with HGT ingestion sprint cadence — dedicated "HGT ingestion" sprint schedule recommendation from Sprint 12 synthesis
- D2: Phase-gate FSM task-regime annotations added to `data/phase-gate-fsm.yml` (or wherever the FSM is encoded — confirm target file before editing) — annotating each FSM transition with the HGT task-regime type
- D3: AGENTS.md updated if any process constraints are clarified by the above changes

**Depends on**: Phase 3 Review APPROVED
**CI**: `uv run python scripts/validate_agent_files.py --all` (if AGENTS.md touched)
**Gate**: Changes pass ruff and validate_synthesis (if any research doc touched)
**Status**: ⬜ Not started

---

### Phase 4 Review — Review Gate ⬜

**Agent**: Review
**Deliverables**: `## Phase 4 Review Output` in scratchpad
**Depends on**: Phase 4 deliverables committed
**Gate**: Phase 5 does not begin until APPROVED
**Status**: ⬜ Not started

---

### Phase 5 — Commit, PR & Session Close ⬜

**Agent**: GitHub (commits/push/PR) + Executive Orchestrator (session close)
**Deliverables**:
- D1: All sprint branch changes pushed to `origin/feat/sprint-15-fleet-intelligence-local-rag`
- D2: PR opened from sprint branch → main, body includes `Closes #285 Closes #291 Closes #292 Closes #294 Closes #298`
- D3: Sprint milestone `Sprint 15 — Fleet Intelligence & Local RAG` created and all 5 sprint issues assigned to it
- D4: Sprint-assignment comment posted on each of the 5 sprint issues
- D5: `## Session Summary` written to scratchpad
- D6: CHANGELOG.md updated with Sprint 15 entries

**Depends on**: Phase 4 Review APPROVED
**Gate**: `git status` clean; `gh pr view` returns PR URL; `gh milestone list --state open` shows Sprint 15
**Status**: ⬜ Not started

---

## Issue Clusters

| Cluster | Issues | Pts |
|---------|--------|-----|
| Fleet Intelligence | #291, #292 | 6 |
| MCP/RAG Research | #285, #294 | 8 |
| Process/Docs | #298 | 2 |
| **Total** | **5 issues** | **16 pts** |

---

## Acceptance Criteria

- [ ] Phase 0 — Workplan Review: APPROVED logged in scratchpad under `## Workplan Review Output`
- [ ] Phase 1 — `analyse_fleet_coupling.py` and `suggest_routing.py` committed with ≥80% test coverage; `data/task-type-classifier.yml` present (#291, #292 closed)
- [ ] Phase 2 — MCP research triage note posted to #285; phase findings summary in scratchpad
- [ ] Phase 3 — `companion-repos.yml` present in dogma root; companion repo publicly accessible with MCP server (#294 closed)
- [ ] Phase 4 — HGT cadence and FSM task-regime annotations committed (#298 closed)
- [ ] Phase 5 — PR opened with all `Closes #N` lines; sprint milestone created; progress comments posted on all 5 issues; CHANGELOG updated
- [ ] All new scripts pass `ruff check` and have ≥80% test coverage
- [ ] No heredocs used in any file write (pre-commit hook passes)

---

## Workplan Review Output

<!-- Review agent verdict logged here before Phase 1 begins -->

---

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #285, Closes #291, Closes #292, Closes #294, Closes #298
