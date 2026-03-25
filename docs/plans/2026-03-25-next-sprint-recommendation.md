---
title: "Sprint Recommendation: March 25, 2026"
date: 2026-03-25
author: "Executive Orchestrator"
status: "Recommended"
milestone: "Q2 Governance"
closes_issues: []
---

# Next Sprint Recommendation

**Current Context**: Issue #435 (branch-sync gate) is in active flight. User is asking for a sprint recommendation for parallel and follow-on work.

**Backlog Health**: 67 open issues. Primary themes cluster into 6–7 distinct streams.

---

## Key Findings: Backlog Clustering

### Stream 1: Branch & Session Infrastructure (ACTIVE)
**Status**: In flight (issue #435)  
**Issues**: #435 (branch-sync gate), #434 (feat: pre-branch...)  
**Lock**: #435 gates #434 — they are sequentially dependent  
**Recommendation**: Let #435 complete; #434 is follow-on  

### Stream 2: Security Hardening (HIGH PRIORITY, PARALLEL)
**Issues**:
- #424 (high) — Extend SSRF protections
- #423 (high) — Implement runtime action behaviors
- #360 (high) — OWASP LLM threat model
- #361 (medium) — Subscribe to CVE feeds
- #357 (medium) — Schedule dependency audits

**Lock**: None — these are independent  
**Recommend**: Cluster as Sprint Phase 2A (security hardening sprint)  
**Owner** (if assigned): Security Researcher (likely)  
**Effort**: Medium–High (requires threat modeling + external research)

### Stream 3: Research Infrastructure (HIGH PRIORITY)
**Issues**:
- #422 (high) — Define Primary Research Procedure
- #410 (high) — Apply approved changes to docs
- #411 (medium) — Identify and cleanup inconsistencies
- #402 (high) — Retrospective: readiness for Foundation release

**Lock**: #422 gates #410 (cannot apply changes if the procedure isn't defined)  
**Recommend**: Cluster as Sprint Phase 2B (research governance finalization)  
**Owner**: Executive Docs + Executive Researcher  
**Effort**: Medium (documentation + synthesis)

### Stream 4: Agent Fleet Standardization (HIGH PRIORITY, SCAFFOLDING)
**Issues**:
- #333 (high) — feat(agents): implement multi-turn
- #335 (high) — feat(agents): enforce return compression
- #334 (high) — feat(observability): adopt L3 instrumentation
- #332 (high) — feat(governance): enforce consensus YAML syntax
- #331 (high) — feat(decision-logic): encode axiom priority ordering
- #336 (high) — refactor(mcp): standardize tool naming

**Lock**: #332 gates most others (YAML syntax standardization must be uniform first)  
**Recommend**: Sequence as Sprint Phase 2C (agent fleet scaffolding)  
**Owner**: Executive Fleet + Executive Scripter  
**Effort**: High (affects 40+ .agent.md files)  
**Note**: This is a refactor pass; coordinate timing to avoid merge conflicts with other PR work

### Stream 5: Observability & Metrics Infrastructure (MEDIUM PRIORITY)
**Issues**:
- #369, #376, #342, #343 (medium) — observability foundation
- #346, #345 (medium) — metrics & velocity tracking
- #344 (medium) — script encoding

**Lock**: None on others; builds on #333–#336  
**Recommend**: Defer to Sprint 2 Phase 3 (post-agent-fleet stabilization)  
**Owner**: Executive Scripter  
**Effort**: Medium–High

### Stream 6: Skills & Automation (MEDIUM PRIORITY)
**Issues**:
- #432 (medium) — Skill: Automate PR review triage
- Other automation/skill items

**Lock**: Depends on #422 (research procedure definition)  
**Recommend**: Sprint 2 Phase 4 (post-research infrastructure)

### Stream 7: Research Topics (LOW–MEDIUM PRIORITY)
**Issues**:
- #396 (high) — research: LLM performance benchmarking
- #422 (high primary research procedure) — GATE for all secondary research
- #414, #413, #421 (medium) — secondary research sprints
- #426, #415, #419 (low) — bare-bones research issues

**Lock**: Nothing; independent research work  
**Recommend**: Parallel track (can run in isolation or distributed to Research Scout fleet)

### Stream 8: CI/Infrastructure (MEDIUM–HIGH PRIORITY)
**Issues**:
- #408 (medium) — add weekly GitHub API snapshot
- #388 (high, blocking) — lychee v0.23.0 SendErr issue
- #336 (high) — MCP tool naming standardization

**Lock**: #388 blocks CI; should be prioritized  
**Recommend**: Phase 0 pre-sprint (fix #388 before sprint begins)

---

## Recommended Sprint Phases

### Phase 0: Pre-Sprint Blocking Issues (This Week)
**Gate**: Clear before Phase 1 begins  
**Issues**:
- #388 (high) — lychee SendErr [Depends on lychee release or workaround]
- #435 (active) — branch-sync gate [In flight, expected complete]

**Owner**: CI Monitor + Executive Orchestrator  
**Effort**: Low–Medium

---

### Phase 1: Security Hardening Foundation
**Issues**:
- #424 (extend SSRF)
- #423 (runtime action behaviors)
- #360 (OWASP LLM threat model)
- #361, #357 (supporting security chores)

**Gate**: All 5 issues pass Review + CI before Phase 2 begins

**Owner**: Security Researcher (primary), Executive Scripter (script support)  
**Effort**: 5–8 days  
**Maturity Target**: L2 → L3 (threats encoded, no longer ad-hoc)

---

### Phase 2: Research Infrastructure Finalization
**Issues**:
- #422 (define primary research procedure) — GATE  
- #410 (apply approved changes to docs)  
- #411 (identify inconsistencies)  
- #402 (retrospective: readiness for Foundation release)

**Gate**: #422 complete before #410 starts; all 4 issues pass Review + CI before Phase 3

**Owner**: Executive Researcher + Executive Docs  
**Effort**: 5–7 days  
**Maturity Target**: Research procedures L2 → L3 (standardized, taught, enforced)

---

### Phase 3: Agent Fleet Standardization
**Issues**:
- #332 (feat: enforce YAML syntax consensus) — GATE  
- #333 (implement multi-turn)  
- #335 (enforce return compression)  
- #334 (adopt L3 observability)  
- #331 (encode decision logic / axiom priority)  
- #336 (standardize MCP tool naming)

**Gate**: #332 complete and all agent files migrated before remaining issues start

**Owner**: Executive Fleet + Executive Scripter  
**Effort**: 8–12 days (scope for each updated .agent.md file)  
**Note**: High-scope; recommend smaller team to avoid merge conflicts. Coordinate with any other PRs in flight.  
**Maturity Target**: Agent fleet L1 → L2 (standardized syntax, consistent tooling)

---

### Phase 4: Observability & Metrics Infrastructure (Post-Phase 3)
**Issues**:
- #369, #376, #342, #343 (observability foundation)  
- #346, #345 (velocity metrics)  
- #344 (script refactor)

**Gate**: Phase 3 complete; all metrics issues pass Review + CI before Phase 5

**Owner**: Executive Scripter  
**Effort**: 5–7 days

---

### Phase 5: Skills & Automation (Post-Phase 2)
**Issues**:
- #432 (Skill: Automate PR review triage)  
- Supporting automation

**Gate**: Phase 2 complete; all issues pass Review + CI

**Owner**: Executive Automator + Executive Planner  
**Effort**: 3–4 days

---

## Sprint Structure: Proposed Timeline

```
Week 1 (Mar 25–Apr 1)
├─ Phase 0: Pre-sprint blocking issues (#388, #435) [concurrent]
├─ Phase 1: Security Hardening (#424, #423, #360, #361, #357) [start after Phase 0]
└─ Phase 2: Research Infrastructure (#422→#410→#411→#402) [start end of Week 1 OR Week 2]

Week 2 (Apr 1–8)
├─ Phase 3: Agent Fleet Standardization (#332→#333→#335→#334→#331→#336) [start after Phase 2]
└─ Phase 4: Observability & Metrics (#369, #376, #342, #343, #346, #345, #344)

Parallel Track (Research & Secondary Work)
├─ Phase 5: Skills & Automation (#432 + supporting)
└─ Research Fleet: Secondary research sprints (#414, #413, #421, #426, #415, #419)
```

---

## Dependencies & Sequencing Rules

| Dependency | Gate | Why |
|---|---|---|
| Phase 0 must complete | Phase 1 starts | CI blocker (#388) must not interfere with sprint execution |
| Phase 1 independent | Can run with Phase 2 | Security work is orthogonal to research infrastructure |
| Phase 2 gates Phase 5 | #422 (research proc) must exist before #432 (PR review automation) | Automation assumes research procedure is defined |
| Phase 3 gates Phase 4 | Agent fleet standardization must be stable before metrics instrumentation | Observability depends on consistent agent YAML |
| Phase 0 completes | Milestone created | Create or update sprint milestone after Phase 0 clear |

---

## Effort & Team Recommendations

| Phase | Issues | Effort | Owner(s) | Parallel Work |
|-------|--------|--------|-----------|---|
| Phase 0 | 2 | S–M | CI Monitor + Orchestrator | Can start now |
| Phase 1 (Security) | 5 | M–L | Security Researcher | Can run with Phase 2 |
| Phase 2 (Research) | 4 | M | Executive Docs + Researcher | Blocked by #422 gate |
| Phase 3 (Agent Fleet) | 6 | L | Executive Fleet + Scripter | Blocked by Phase 2 |
| Phase 4 (Observability) | 7 | M–L | Executive Scripter | Blocked by Phase 3 |
| Phase 5 (Skills) | TBD but ~3–4 | S–M | Executive Automator | Can run after Phase 2 |
| **Research Track** | ~5 | M per item | Research Scout + Synthesizer | Independent parallel stream |

**Total Sprint Capacity**: ~50–70 story points (rough 8–12 day equivalent)  
**Recommended Parallelization**: 
- Phase 1 (Security) and Phase 2 (Research) can run concurrently if 2+ agents available
- Phase 5 (Skills) can start as soon as Phase 2 is complete (no Phase 3 gate)
- Research fleet can always run in parallel

---

## Proposed Milestone: "Q2 Governance Wave 1"

**Name**: `Q2 Governance Wave 1`  
**Target**: April 8, 2026 (2 weeks from sprint start)  
**Issues** (recommended set):
- Phase 0: #388, #435
- Phase 1: #424, #423, #360, #361, #357
- Phase 2: #422, #410, #411, #402

**Success Criteria for Milestone**:
- All Phase 0–2 issues closed or moved to follow-up sprint
- Branch sync gate encoded in AGENTS.md and implemented in scripts
- Security threat model document published
- Research procedure standardized and documented
- CI stable with zero SendErr blocks on lychee

---

## Not Recommended for This Sprint (Deferred)

These are solid future work but not critical for the next 2 weeks:

- RAG/Knowledge Systems (#358, #352–#355, #359) — defer to Q2 Wave 2
- Testing & Release Harnesss (#428, #350, #113) — defer pending Wave 1 stabilization
- Long-tail research topics (#283, #131, #128) — standing backlog, not urgent
- DevRel / Adoption (#427, #430, #429, #428) — [DEFER] items, intentionally deferred

---

## Previous Sprint Context

**Completed (PR #431, Sprint Close 2026-03-24)**:
- Recommendation provenance sprint
- Session retrospective encoding

**Issues Fixed**:
- Identified in retro that branch sync should be automated (source for #435)
- Encoding gaps in session checkpoint flow (source for #422 gate emphasis)

**Open Concerns**:
- Lychee SendErr regression (#388) is actively blocking CI
- Agent fleet YAML syntax drift detected during #333–#336 scoping (source for #332 gate)

---

## Questions for Human Review

1. **Do we want to start Phase 3 (Agent Fleet) in Week 2, or defer to Week 3?** (Risk: large refactor + PR conflicts if other work is concurrent.)
2. **Should Security Hardening (Phase 1) include #425 (RL drift monitoring)** or keep it focused on the 5 items listed?
3. **Research Fleet**: Should we run a parallel secondary-research sprint during Phase 1–2, or keep the main sprint focused on infrastructure?

---

## Recommendation Summary

**Start this sprint with**: Phase 0 (clear blocking #388 + complete #435), then Phase 1 (Security) in parallel with Phase 2 (Research Infrastructure).

**Sequence**: Phase 0 → Phase 1 + Phase 2 → Phase 3 → Phase 4 (+ Phase 5 can run after Phase 2).

**Expected Delivery**: All Phase 0–2 issues resolved by April 1; Phase 3–4 by April 8.

**Milestone**: Create `Q2 Governance Wave 1` milestone and assign all Phase 0–2 issues.

---
