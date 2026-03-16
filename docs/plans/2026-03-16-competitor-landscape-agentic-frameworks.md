---
governs: [research]
issue: 301
branch: research/301-competitor-landscape-agentic-frameworks
created: 2026-03-16
---

# Workplan: Competitor Landscape — Agentic Coding Frameworks

## Objective

Research and synthesize the competitive landscape of agentic coding frameworks (as mapped in the ["Spec-Driven Development is eating Software Engineering — A Map of 30 Agentic Coding Frameworks"](https://medium.com/@visrow/spec-driven-development-is-eating-software-engineering-a-map-of-30-agentic-coding-frameworks-6ac0b5e2b484) article), then positioning EndogenAI's dogma against the field.

**Governing axiom**: Endogenous-First — read `MANIFESTO.md` axioms and `docs/research/` corpus before reaching outward. The fetch-before-act posture applies: cache sources first, research from disk.

**Primary deliverable**: `docs/research/competitor-landscape-agentic-frameworks.md` — a D4 synthesis doc following the D4 schema (Executive Summary, Hypothesis Validation, Pattern Catalog, Recommendations, Sources).

**Closes**: #301

---

## Phases

### Workplan Review Gate
**Agent**: Review
**Deliverables**: Verdict logged under `## Workplan Review Output` in scratchpad
**Gate**: Phase 1 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 1 — Research Scout
**Agent**: Research Scout
**Deliverables**:
- Primary source (Medium article) cached in `.cache/sources/`
- ≥10 competitor frameworks identified + raw findings (bullets) in scratchpad under `## Scout Output`
- Framework axes catalogued: spec-first, local model, orchestration, autonomy
- Raw findings include: competitor names, positioning claims, adoption signals, gap observations
- All source URLs listed for Synthesizer

**Depends on**: Workplan Review APPROVED
**Gate**: Phase 1 Review does not start until Scout deliverables are in scratchpad
**Status**: ⬜ Not started

### Phase 1 Review — Review Gate
**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad, verdict APPROVED
**Depends on**: Phase 1 Scout deliverables present
**Gate**: Phase 2 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 2 — Research Synthesizer
**Agent**: Research Synthesizer
**Deliverables**:
- `docs/research/competitor-landscape-agentic-frameworks.md` written (D4 schema)
- Document includes: Executive Summary, Hypothesis Validation, Pattern Catalog (≥1 canonical example, ≥1 anti-pattern), Gap/Differentiation Matrix, Recommendations (adopt/discard/double-down), Sources
- ≥2 MANIFESTO.md axiom citations present
- Passes `uv run python scripts/validate_synthesis.py docs/research/competitor-landscape-agentic-frameworks.md`

**Depends on**: Phase 1 Review APPROVED + Scout findings in scratchpad
**Gate**: Phase 2 Review does not start until deliverable written and validated
**Status**: ⬜ Not started

### Phase 2 Review — Review Gate
**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad, verdict APPROVED
**Depends on**: Phase 2 synthesis doc written and passing validate_synthesis
**Gate**: Phase 3 does not start until APPROVED
**Status**: ⬜ Not started

---

### Phase 3 — Archivist: Commit & Close
**Agent**: GitHub (Orchestrator acts directly — commit, push, PR)
**Deliverables**:
- `docs/research/competitor-landscape-agentic-frameworks.md` committed with `docs: competitor landscape research — closes #301`
- Branch pushed to origin
- PR opened targeting main
- Issue #301 acceptance criteria checkboxes updated

**Depends on**: Phase 2 Review APPROVED
**Gate**: Session closes when PR URL confirmed
**Status**: ⬜ Not started
