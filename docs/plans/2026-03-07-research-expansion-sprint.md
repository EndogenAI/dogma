# Workplan: Research Expansion Sprint

**Date**: 2026-03-07
**Branch**: feat/implement-research-findings
**Orchestrator**: Executive Orchestrator

---

## Objective

Initiate research across six new knowledge domains identified as foundational to endogenic development methodology. Four domains receive full research sprint treatment (Scout → Synthesizer → Reviewer → Archivist). Two lower-priority domains receive a lighter seed/scout pass for future development. All findings committed to this repo as the authoritative substrate and reused broadly across EndogenAI.

---

## Scope Decisions

| Decision | Value |
|---|---|
| Priority domains (full sprint) | Testing Tools & Frameworks, Dev Workflow Automations, Open-source Docs Best Practices, PM & Dev Team Structures |
| Deferred domains (seed pass) | Product Research & Design Methodologies, Comms / Marketing / Biz Dev |
| New agents | Hybrid: scaffold only where domain has sustained research need |
| Output scope | This repo as substrate; findings broadly reusable |

---

## Phase Plan

### Phase 1 — Initialise Research Tracks

**Owner**: Orchestrator (direct)
**Deliverables**:
- [ ] This workplan committed to `docs/plans/`
- [ ] 6 new items added to `docs/research/OPEN_RESEARCH.md`
- [ ] 4 GitHub issues opened for full-sprint domains (labels: `research`)
- [ ] 2 GitHub issues opened for seed-pass domains (labels: `research`)
- [ ] New specialist agent scaffolded if warranted by domain assessment

**Depends on**: nothing
**Gate**: Phase 2 does not begin until OPEN_RESEARCH.md and GitHub issues are confirmed committed

---

### Phase 2a — Full Sprint: Testing Tools & Frameworks

**Owner**: Executive Researcher (delegates to Research Scout + Synthesizer + Reviewer + Archivist)
**Deliverables**:
- [ ] `docs/research/sources/` — per-source synthesis reports for all surveyed sources
- [ ] `docs/research/testing-tools-frameworks.md` — Status: Final
- [ ] `docs/guides/testing.md` updated with synthesised best practices

**Depends on**: Phase 1
**Gate**: Phase 2b does not begin until 2a deliverables committed

---

### Phase 2b — Full Sprint: Dev Workflow Automations

**Owner**: Executive Researcher
**Deliverables**:
- [ ] `docs/research/sources/` — per-source synthesis reports
- [ ] `docs/research/dev-workflow-automations.md` — Status: Final
- [ ] `docs/guides/workflows.md` updated with synthesised patterns

**Depends on**: Phase 1 (can run parallel with 2a if capacity allows)
**Gate**: Phase 2c does not begin until 2b deliverables committed

---

### Phase 2c — Full Sprint: Open-Source Documentation Best Practices

**Owner**: Executive Researcher
**Deliverables**:
- [ ] `docs/research/sources/` — per-source synthesis reports
- [ ] `docs/research/oss-documentation-best-practices.md` — Status: Final
- [ ] Recommendations applied to `docs/guides/` where actionable

**Depends on**: Phase 1
**Gate**: Phase 2d does not begin until 2c deliverables committed

---

### Phase 2d — Full Sprint: PM & Dev Team Structures

**Owner**: Executive Researcher
**Deliverables**:
- [ ] `docs/research/sources/` — per-source synthesis reports
- [ ] `docs/research/pm-dev-team-structures.md` — Status: Final
- [ ] Recommendations relevant to agent fleet design noted in `docs/guides/agents.md`

**Depends on**: Phase 1
**Gate**: Phase 3a does not begin until 2d deliverables committed

---

### Phase 3a — Seed Pass: Product Research & Design Methodologies

**Owner**: Research Scout (scoped to domain)
**Deliverables**:
- [ ] OPEN_RESEARCH.md item with curated source list
- [ ] `docs/research/sources/` — 2-3 per-source seed reports (no full synthesis)
- [ ] GitHub issue updated with scout findings for future sprint

**Depends on**: Phase 1
**Gate**: Phase 3b does not begin until 3a committed

---

### Phase 3b — Seed Pass: Comms / Marketing / Biz Dev

**Owner**: Research Scout (scoped to domain)
**Deliverables**:
- [ ] OPEN_RESEARCH.md item with curated source list
- [ ] `docs/research/sources/` — 2-3 per-source seed reports (no full synthesis)
- [ ] GitHub issue updated with scout findings for future sprint

**Depends on**: Phase 3a
**Gate**: Phase 4 does not begin until 3b committed

---

### Phase 4 — Review & Commit

**Owner**: Review agent → GitHub agent
**Deliverables**:
- [ ] All new files reviewed against AGENTS.md constraints
- [ ] All changes committed following Conventional Commits
- [ ] OPEN_RESEARCH.md GitHub issues updated to reflect new items
- [ ] `## Session Summary` written in scratchpad + prune_scratchpad.py --force run

**Depends on**: Phases 2a–2d, 3a–3b
**Gate**: Session closes when all commits confirmed pushed

---

## Acceptance Criteria

- [ ] 6 new research domains registered in OPEN_RESEARCH.md with items numbered sequentially from current max
- [ ] 4 + 2 = 6 GitHub issues open with `research` label, each linked to its OPEN_RESEARCH.md item
- [ ] Full synthesis docs committed for 4 priority domains (Status: Final in frontmatter)
- [ ] Seed scout reports committed for 2 lower-priority domains
- [ ] `docs/guides/testing.md` and `docs/guides/workflows.md` updated with actionable findings
- [ ] Session scratchpad has `## Orchestration Plan`, one `## Phase N Output` per phase, and `## Session Summary`
- [ ] All commits pushed to origin

---

## Notes

- OPEN_RESEARCH.md items currently go up to #8 (plus follow-up questions for #10, #12). New items will be numbered 9–14 or continue from the current maximum.
- Issues #13 and #14 are already open (Episodic Memory, AIGNE AFS). New issues will pick up from #16 onwards.
- The `uv run python scripts/fetch_all_sources.py` fetch-before-act step must be run at the start of each Research Scout delegation.
- Recursion: if Scout findings reveal significant new sub-domains or unanswered questions, new OPEN_RESEARCH.md items shall be created and corresponding issues opened — no new immediate sprints unless explicitly approved.
