# Workplan: Sprint Planning — Self Improvement Sprint (Milestone #11)

**Branch**: `feat/sprint-planning-self-improvement`
**Date**: 2026-03-13
**Orchestrator**: Executive Orchestrator

---

## Objective

Produce a fully sequenced, phase-gated execution plan for the **Self Improvement Sprint** (GitHub milestone #11). The milestone contains 28 open issues spanning research, documentation, feature work, and chores. This workplan chunks them into parallelisable phases with effort estimates, priority ordering, and agent assignments so that future sessions can execute without additional planning overhead.

---

## Issue Inventory (28 open)

| # | Title | Type | Priority |
|---|-------|------|----------|
| #250 | docs(skills): create PR review triage workflow as a reusable SKILL.md | docs | medium |
| #249 | feat(scripts): enforce MANIFESTO §-reference citation format in validate_synthesis.py | feature | medium |
| #248 | feat(ci): add CRD health check to substrate audit CI | feature | medium |
| #247 | Research: corpus-wide automated action item extraction from research docs | research | medium |
| #246 | Research + implement: scripts documentation generation and maintenance | research | medium |
| #245 | Research: LCF axiom positioning — standalone core axiom vs structural enabler | research | medium |
| #242 | Scratchpad Architecture Maturation — From Ephemeral Pruning to Permanent Session Lineage | research | high |
| #236 | docs: Add F2 canonical examples and F3 anti-patterns for Programmatic-First, Documentation-First, Minimal Posture | docs | high |
| #235 | docs: Add Endogenous-First F2 canonical example to MANIFESTO.md | docs | high |
| #234 | research: Empirical session studies — substrate commit ratio (Q2) and CRD vs output quality (Q4) | research | low |
| #233 | docs: H4 BDD primary source gap — add independent Adzic/North citations | docs | medium |
| #229 | Add entry IDs to back-propagation proposal format | docs | medium |
| #228 | Encode proposal-as-specification as zero-risk Phase 3 design in back-prop methodology | docs | medium |
| #227 | docs(guides): add back-propagation methodology section to workflows.md | docs | medium |
| #203 | Research: Dynamic AI Agent Navigation — Graph Routing Algorithms | research | medium |
| #200 | Elevate GitHub Agent to Executive Tier | chore | high |
| #195 | docs(pattern): generalize three-tier safeguard model across codebase | docs | high |
| #194 | docs(agent): enhance delegation signal encoding and measurability | docs | high |
| #152 | Audit fleet guardrails for programmatic enforcement opportunities | chore | medium |
| #146 | Implement prompt archaeology as a post-sprint ritual | chore | low |
| #145 | Adopt README-driven development convention for new scripts | chore | medium |
| #143 | Add legibility and idempotency checklist items to CONTRIBUTING.md | chore | medium |
| #142 | Add JTBD job statement to each entry in scripts/README.md | chore | medium |
| #131 | Cognee Library Adoption (After Local Compute Baseline) | research | low |
| #128 | Phase 1 AFS Integration — Index Session to AFS on Session Close | feature | low |
| #124 | Extended Agent Documentation Standard | docs | medium |
| #107 | ci(lint): wire detect_drift.py into CI lint job | chore | medium |
| #48 | Chore: Investigate GitHub sub-issues API and feature availability | chore | medium |

---

## Phase Plan

### Phase 1 — Sprint Planning ⬜

**Agent**: Executive Planner
**Deliverables**:
- Phases 2–N of this workplan populated with sequenced, effort-sized issue groups
- Agent assignments and parallelisation annotations for each phase
- Dependency graph between issue groups noted

**Depends on**: nothing
**Status**: ✅ Complete — `10dccac`

---

### Phase 2 — High-Priority Research Sprints ⬜

**Agent**: Executive Researcher
**Parallel with**: Phase 3, Phase 4, Phase 6 (separate file domains)
**Issues**:
- #242 `Scratchpad Architecture Maturation — From Ephemeral Pruning to Permanent Session Lineage` — effort: XL — foundational research sprint; outputs directly inform session tooling and scratchpad lifecycle improvements fleet-wide
- #245 `Research: LCF axiom positioning — standalone core axiom vs structural enabler` — effort: XL — determines how Local Compute-First is positioned in MANIFESTO; informs MANIFESTO edits in Phase 4

**Depends on**: Phase 1; outputs soft-gate Phase 4 (LCF framing) and Phase 11 (#242 informs #146 ritual design)
**Status**: ✅ Complete — `c1996af` + `ee4bb8a` (closes #242 scratchpad-architecture-maturation, closes #245 lcf-axiom-positioning)

---

### Phase 3 — Fleet Elevation & Agent Tier Changes ✅

**Agent**: Executive Fleet
**Parallel with**: Phase 2, Phase 4, Phase 6 (agent files vs research docs / MANIFESTO vs workflows — distinct domains)
**Issues**:
- #200 `Elevate GitHub Agent to Executive Tier` — effort: L — modifies `.github/agents/github.agent.md` and Executive Fleet Privileges table in `AGENTS.md`; must complete before Phase 5 edits AGENTS.md delegation content
- #152 `Audit fleet guardrails for programmatic enforcement opportunities` — effort: M — fleet read-analysis; natural companion to tier restructuring in #200; produces scripting-gap list for Executive Scripter
- #48 `Chore: Investigate GitHub sub-issues API and feature availability` — effort: S — small investigation; GitHub domain pairs cleanly with #200

**Depends on**: Phase 1; **gates Phase 5** (AGENTS.md must stabilize after #200 before delegation signal updates begin)
**Status**: ✅ Complete — `ff9bf83` (closes #200, #48; #152 deferred to future session — M effort audit, #151 dependency confirmed closed)

---

### Phase 4 — MANIFESTO Core Documentation ✅

**Agent**: Executive Docs
**Parallel with**: Phase 3 (MANIFESTO vs agent files), Phase 6 (MANIFESTO vs workflows.md)
**Issues**:
- #235 `docs: Add Endogenous-First F2 canonical example to MANIFESTO.md` — effort: S — single-file MANIFESTO edit; adds one canonical pattern example
- #236 `docs: Add F2 canonical examples and F3 anti-patterns for Programmatic-First, Documentation-First, Minimal Posture` — effort: M — extends MANIFESTO with multiple pattern entries; natural batch with #235 on same file
- #233 `docs: H4 BDD primary source gap — add independent Adzic/North citations` — effort: S — citation addition to existing docs section; same Executive Docs domain, efficient to batch

**Depends on**: Phase 1; soft: Phase 2 (#245 LCF output may refine MANIFESTO axiom framing — not a hard gate); **gates Phase 9** (MANIFESTO citation patterns must stabilize before CI enforcement)
**Status**: ✅ Complete — `3db96a8` (closes #235, #236, #233)

---

### Phase 5 — AGENTS.md Delegation & Agent Documentation Standards ⬜

**Agent**: Executive Docs
**Parallel with**: Phase 6 (AGENTS.md vs workflows.md — distinct files; only valid once Phase 3 gate clears)
**Issues**:
- #194 `docs(agent): enhance delegation signal encoding and measurability` — effort: L — multi-section AGENTS.md update; requires reading current delegation section before editing
- #195 `docs(pattern): generalize three-tier safeguard model across codebase` — effort: L — cross-codebase pattern docs; touches AGENTS.md and multiple guide/research files
- #124 `Extended Agent Documentation Standard` — effort: M — defines extended documentation standard for agent files; naturally follows structural improvements from #194 and #195

**Depends on**: Phase 3 (AGENTS.md must stabilize after GitHub agent tier elevation); **gates Phase 9** (AGENTS.md patterns must stabilize before CI enforcement)
**Status**: ✅ Complete — `b4cea44` (closes #194, #195, #124)

---

### Phase 6 — Back-Propagation Methodology ✅

**Agent**: Executive Docs
**Parallel with**: Phase 2, Phase 3, Phase 4, Phase 5 (distinct file domain: methodology docs + `docs/guides/workflows.md`)
**Issues**:
- #229 `Add entry IDs to back-propagation proposal format` — effort: S — format-spec change to existing proposal structure; must precede #228 and #227 within the phase
- #228 `Encode proposal-as-specification as zero-risk Phase 3 design in back-prop methodology` — effort: M — methodology doc update encoding the Phase 3 design pattern; builds on #229 format change
- #227 `docs(guides): add back-propagation methodology section to workflows.md` — effort: M — new guide section in `docs/guides/workflows.md`; depends on #229 and #228 completing first within the phase

**Depends on**: Phase 1 (#229 and #228 are independent; #227 requires #229 and #228 within-phase)
**Status**: ✅ Complete — `0bc63b4` (closes #229, #228, #227)

---

### Phase 7 — Scripts Documentation Research ⬜

**Agent**: Executive Researcher
**Parallel with**: Phase 4, Phase 5, Phase 6 (research docs domain is separate from docs/guides edits)
**Issues**:
- #246 `Research + implement: scripts documentation generation and maintenance` — effort: XL — research phase must produce output before Phase 8 scripts-doc chores begin
- #247 `Research: corpus-wide automated action item extraction from research docs` — effort: XL — companion research sprint; no Phase 8 downstream dependency but batched for research fleet efficiency

**Depends on**: Phase 1; **gates Phase 8** (for #142 and #145)
**Status**: ✅ Complete — `cc42e08` + `d0a67c9` (closes #246 scripts-documentation-generation, closes #247 action-item-extraction; scripts/docs/ scaffolded)

---

### Phase 8 — Documentation Chores & Convention Implementation ⬜

**Agent**: Executive Docs
**Parallel with**: Phase 9 (docs chores vs CI/scripts features — distinct files)
**Issues**:
- #142 `Add JTBD job statement to each entry in scripts/README.md` — effort: M — applies job-statement convention from #246 research output to existing README entries
- #145 `Adopt README-driven development convention for new scripts` — effort: M — encodes README-driven convention from #246 research; produces guide or CONTRIBUTING update
- #143 `Add legibility and idempotency checklist items to CONTRIBUTING.md` — effort: S — independent checklist addition to existing file; batched for doc-editing efficiency
- #250 `docs(skills): create PR review triage workflow as a reusable SKILL.md` — effort: M — new SKILL.md file; independent of Phase 7 research but benefits from agent standard (#124) in Phase 5

**Depends on**: Phase 7 (for #142 and #145); soft: Phase 5 (for #250 agent-standard context); #143 unblocked after Phase 1
**Status**: ✅ Complete — `2f5f41d` (closes #142 JTBD statements, closes #145 README-driven convention, closes #143 legibility/idempotency checklist, closes #250 pr-review-triage skill)

---

### Phase 9 — CI & Scripts Feature Work ⬜

**Agent**: Executive Scripter
**Parallel with**: Phase 8 (CI/scripts vs docs chores — distinct files)
**Issues**:
- #249 `feat(scripts): enforce MANIFESTO §-reference citation format in validate_synthesis.py` — effort: M — script modification + test update; requires MANIFESTO citation patterns from Phase 4 to stabilize before enforcement is written
- #248 `feat(ci): add CRD health check to substrate audit CI` — effort: M — CI workflow addition; natural companion to #107
- #107 `ci(lint): wire detect_drift.py into CI lint job` — effort: S — CI config addition; batched with #248 for single CI-workflow review pass

**Depends on**: Phase 4 (MANIFESTO citation patterns stabilized), Phase 5 (AGENTS.md patterns stabilized)
**Status**: ✅ Complete — `8203208` (closes #249, #248, #107; fleet_avg 0.1435→0.2084)

---

### Phase 10 — Standalone Research Sprints ✅

**Agent**: Executive Researcher
**Parallel with**: Phase 8, Phase 9 (independent research domain; no shared files)
**Issues**:
- #203 `Research: Dynamic AI Agent Navigation — Graph Routing Algorithms` — effort: XL — independent research sprint; no downstream gates within this milestone
- #234 `research: Empirical session studies — substrate commit ratio (Q2) and CRD vs output quality (Q4)` — effort: XL — low-priority independent research; may produce inputs for a future milestone
- #131 `Cognee Library Adoption (After Local Compute Baseline)` — effort: XL — exploratory research; gated externally on local compute baseline; lowest execution priority in this phase

**Depends on**: Phase 1 (no inter-phase dependencies within the milestone)
**Status**: ✅ Complete — `af49037` + `d091a73` (closes #203; #234 scoped/deferred; #131 triaged; #252 filed for Q4 study)

---

### Phase 11 — Low-Priority Features & Chores ✅

**Agent**: Executive Orchestrator
**Parallel with**: Phase 10 (independent work streams)
**Issues**:
- #128 `Phase 1 AFS Integration — Index Session to AFS on Session Close` — effort: L — feature implementation; low priority; no hard upstream gate within this milestone
- #146 `Implement prompt archaeology as a post-sprint ritual` — effort: M — define and document ritual; benefits from scratchpad architecture research (#242 in Phase 2) completing first
- #252 `research: Execute Q4 empirical study — CRD vs output quality (Spearman ρ)` — effort: M — filed from Phase 10 output; retrospective rubric study; tractable now with `validate_agent_files.py` CRD extraction
- **scripting follow-on from #203**: `feat(scripts): parse_fsm_to_graph.py — FSM-to-NetworkX path analysis + CI invariant check` — effort: S — recommendation from dynamic-agent-navigation.md; filed as #253

**Depends on**: Phase 1; soft: Phase 2 (#242 scratchpad architecture research informs #146 ritual design)
**Status**: ✅ Complete — `0e605aa` + `a7acf14` + `e9861ee` (closes #252 crd-output-quality-study; closes #146 prompt-archaeology skill; #253 filed for parse_fsm_to_graph.py scripting; #128 deferred — AFS dependency unresolved)

---

## Dependency Graph

```
Phase 1 (Planning)
├── Phase 2 (Research Sprints — high priority) ─── soft-gates Phase 4, Phase 11
├── Phase 3 (Fleet Elevation) ──────────────────── hard-gates Phase 5
├── Phase 4 (MANIFESTO Docs) ───────────────────┐
│   └── soft-gate from Phase 2                  ├─ both gate Phase 9
├── Phase 5 (AGENTS.md + Agent Standards) ──────┘
│   └── depends on Phase 3
├── Phase 6 (Back-Propagation Docs) ─── parallel with Phase 2–5
├── Phase 7 (Scripts Research) ──────── hard-gates Phase 8
│   └── Phase 8 (Doc Chores & Conventions) ─── parallel with Phase 9
├── Phase 9 (CI & Scripts Features) ─── depends on Phase 4 + Phase 5
├── Phase 10 (Standalone Research) ──── parallel with Phase 8, Phase 9
└── Phase 11 (Low-Priority Features) ── parallel with Phase 10
```

**Sequencing layers**:
- **Layer 1 (parallel)**: Phase 2 ‖ Phase 3 ‖ Phase 4 ‖ Phase 6 ‖ Phase 7 ‖ Phase 10 ‖ Phase 11
- **Layer 2**: Phase 5 (after Phase 3); Phase 8 (after Phase 7)
- **Layer 3**: Phase 9 (after Phase 4 + Phase 5)

---

## Acceptance Criteria

- [ ] All 28 issues assigned to a named execution phase with effort label (XS/S/M/L/XL)
- [ ] Phase dependencies are explicit — no phase begins before its prerequisite phase
- [ ] Agent assignments are named for each phase
- [ ] Parallelisable phases are explicitly annotated
- [ ] Workplan committed to `docs/plans/`
- [ ] Review gate APPROVED before session closes
