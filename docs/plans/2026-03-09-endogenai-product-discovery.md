---
slug: endogenai-product-discovery
date: 2026-03-09
author: conor
status: in-progress
---

# EndogenAI Product Discovery Session — Multi-Repo Org & Product Strategy

## Objective

Establish product strategy, org structure, and sequenced roadmap for scaling EndogenAI from single-repo workflow system into a multi-repo open-source product with consulting/training revenue model. Define specialist agents needed to support business operations.

## Constraints & Givens

- **Current repo** (`/workflows`) → rename to `@endogenai/dogma`; preserve git history
- **Primary decision authority**: Conor (with Sheela as brilliant partner/collaborator)
- **Revenue model**: Consulting + training/certs (no hosted SaaS)
- **Web presence**: Public-facing SPA (code in private repo); product discovery issue is an epic
- **Specialist agents**: Business Lead, Comms Strategist, Public Engagement Officer — are in-scope prerequisites, should inform product discussion

## Phase Plan

### Phase 1 — Epic & Initial Issue Framing

**Agent**: Executive PM
**Deliverables**: 
- GitHub Epic issue created (with reference to #45)
- Sub-issues created for: dogma repo, init wizard, adopt wizard, web properties, mid-term (scratchpad, library), long-term (skills, workflows, characters), and specialist agents
- Discovery issue linked in epic; all issues labeled with `type:product`, `priority:high`, `area:product-strategy`

**Depends on**: Nothing
**Gate**: Epic created in GitHub, all sub-issues visible and linked
**Created by**: This workplan

---

### Phase 1 Review — Review Gate (Non-blocking)

**Agent**: Review
**Deliverables**: `## Phase 1 Review Output` appended to scratchpad; verdict: APPROVED or REQUEST CHANGES
**Depends on**: Phase 1 deliverables (issue creation)
**Purpose**: Validate issue structure, labeling, and clarity before discovery begins
**Status**: ⬜ Not started

---

### Phase 2 — Product Discovery Facilitation

**Agent**: Executive Researcher (or new Product Strategist specialist)
**Deliverables**: 
- Video/transcript interview with Conor + Sheela exploring product vision deeply
- Comprehensive discovery document (`docs/research/endogenai-product-discovery.md`) with sections:
  - **Vision & Axioms** (how multi-repo org aligns with MANIFESTO.md)
  - **Org Structure** (7-repo plan: dogma, init, adopt, web, scratchpad, library, skills/workflows/characters)
  - **Go-To-Market Strategy** (consulting, training, certifications, public engagement)
  - **Specialist Agents** (Business Lead, Comms, Public Engagement Officer — roles, responsibilities, success metrics)
  - **Technology Stack** (SPA framework, hosting, private repo access control)
  - **Repo Migration Path** (dogma rename first; content extraction timeline)
  - **Open Questions & Assumptions** (gaps needing clarification; decisions pending)
  - **Success Metrics** — how will we measure product-market fit?

**Depends on**: Phase 1 Review complete (non-blocking)
**Gate**: Discovery document drafted and reviewed by Conor + Sheela; approved for synthesis
**Status**: ⬜ Not started

---

### Phase 2 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 2 Review Output` appended to scratchpad; verdict: APPROVED or REQUEST CHANGES
**Depends on**: Phase 2 deliverables (discovery document)
**Purpose**: Validate discovery synthesis quality, evidence, and alignment with MANIFESTO
**Status**: ⬜ Not started

---

### Phase 3 — Roadmap & Workplan Synthesis

**Agent**: Executive Planner
**Deliverables**:
- **Strategic Roadmap** (`docs/plans/2026-03-09-endogenai-strategic-roadmap.md`):
  - Immediate phase (months 1–3): dogma rename, init wizard, adopt wizard, specialist agents, web properties begin
  - Mid-term phase (months 4–6): scratchpad standalone, library resources, content extraction from dogma
  - Long-term phase (months 7+): skills library, workflows library, characters library
  - Milestones, dependencies, estimated effort
  
- **Execution Workplan** (separate file for first 90 days):
  - Per-repo milestone and deliverable checklist
  - Agent assignments per phase
  - Weekly gate reviews
  - Success criteria

- **Specialist Agent Authoring Plan**:
  - Which custom agents are prerequisites (Business Lead, Comms, Public Engagement Officer)
  - What endogenous sources each agent needs
  - Skills each agent should invoke

**Depends on**: Phase 2 Review APPROVED
**Gate**: Roadmap committed; workplan reviewed by Conor
**Status**: ⬜ Not started

---

### Phase 3 Review — Review Gate

**Agent**: Review
**Deliverables**: `## Phase 3 Review Output` appended to scratchpad; verdict: APPROVED or REQUEST CHANGES
**Depends on**: Phase 3 deliverables
**Purpose**: Validate roadmap quality, feasibility, and sequencing before execution
**Status**: ⬜ Not started

---

### Phase 4 — Commit & Archive

**Agent**: GitHub
**Deliverables**:
- Discovery document committed to `docs/research/`
- Roadmaps committed to `docs/plans/`
- Epic + sub-issues visible in GitHub with proper linking
- Scratchpad archived via `prune_scratchpad.py --force`

**Depends on**: Phase 3 Review APPROVED
**Gate**: All files committed; scratchpad archived; user has linked issues and roadmap on local disk
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] Sub-issues cover all seven repos (dogma, init, adopt, web, scratchpad, library, skills/workflows/characters)
- [ ] Specialist agents (Business Lead, Comms, Public Engagement Officer) are scoped with clear responsibility areas
- [ ] Discovery document includes success metrics and assumptions
- [ ] Roadmap has clear milestones (month 1–3, 4–6, 7+)
- [ ] First 90-day workplan is executable (person + effort hours assigned per task)
- [ ] All phases passed Review gate with APPROVED verdict
- [ ] All commits follow Conventional Commits format

---

## Notes

- This workplan is not the product itself, but the container for the product strategy conversation. The real work begins after Phase 3 (individual repo creation, agent authoring, etc.) which will spawn separate workplans.
- Sheela should be invited as a collaborator on the epic discussion; her input should be captured in the discovery document.
- The specialist agent authoring (Business Lead, Comms, Public Engagement) should begin during Phase 2 so those agents can inform the product discussion itself.

