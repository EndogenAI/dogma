---
title: EndogenAI Strategic Roadmap — Months 1–12
status: draft
---

# EndogenAI Strategic Roadmap — Months 1–12

## Vision & Success Criteria

EndogenAI is scaling from a single-repository foundational knowledge system into a multi-repository open-source product ecosystem. Success is measured across three dimensions: (1) **Market Adoption** — GitHub stars, active projects using init/adopt, community growth; (2) **Revenue Metrics** — consulting pipeline value, training enrollments, first contract value; (3) **Community Health** — GitHub discussions activity, contributor velocity, speaker engagements.

**Major Milestones**:
- **Month 3**: Dogma renamed; init/adopt repos operational; specialist agents scoped; first customer pipeline identified
- **Month 6**: Scratchpad + library standalone repos live; training pilot launched; 1 consulting contract closed
- **Month 12**: Skills/Workflows/Characters libraries operational; 3+ consulting engagements; 20+ training graduates; clear product-market fit signal

---

## Immediate Phase (Months 1–3) — Critical Path

### Primary Deliverables

1. **Dogma Repo Rename** — `/workflows` → `@endogenai/dogma` with preserved git history
2. **Init Wizard** (`@endogenai/init`) — Greenfield setup tool for new EndogenAI projects
3. **Adopt Playbook** (`@endogenai/adopt`) — Integration guide for existing projects
4. **Web Properties** (`@endogenai/web`, private) — Public-facing SPA explaining EndogenAI approach
5. **Specialist Agents** — Business Lead, Comms Strategist, Public Engagement Officer (drafted as `.agent.md` files)

### Success Criteria

- ✅ Dogma renamed successfully; all git history intact; CI/CD fully operational
- ✅ **Web SPA live at endogenai.accessi.tech** (React MVP, GitHub Pages hosting, 4+ landing pages) — launched Week 1
- ✅ Init repo live with MVP CLI wizard (Python projects in Month 1; expand to other languages in Month 2)
- ✅ Adopt repo live with playbook documentation and migration guidance
- ✅ All 3 specialist agents (Business Lead, Comms, Public Engagement) drafted as `.agent.md` files, committed to dogma, syntax-validated
- ✅ First consulting inquiry pipeline identified via web/email outreach
- ✅ Character terminology formalized in agent governance; Month 1 scope (discovery/facilitation) documented

### Team & Effort

- **Conor**: 120+ hours (dogma rename, Web SPA scaffold + build + deploy, init wizard design, business development)
- **Sheela**: 90+ hours (dogma QA, Web SPA content/messaging, documentation, adoption playbook)
- **Note**: Web SPA brought forward to Week 1 (was Month 2); no external contractor needed (in-house React MVP)

Team capacity: ~210 person-hours for Month 1 across full workload

### Key Dependencies

1. **Dogma rename must succeed first** — blocks all downstream repos from referencing dogma
2. **Init/Adopt scaffold CI/CD** — must be stable before wizard implementation
3. **Specialist agents scoped on discovery doc** — agents need endogenous sources to function
4. **Web SPA design** — can proceed in parallel with wizards but output depends on positioning clarity from init/adopt

### Risk Management

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Dogma rename breaks CI or links | High | Low | Pre-rename: run lychee link checker; dry-run rename on feature branch; verify git history post-rename |
| Web SPA deliverable slips past Friday Mar 16 | Medium | Low | Use Vite React starter template (minimal deps); GitHub Pages URL as backup if DNS delays; can point domain over weekend |
| Init wizard scope creep | Medium | Medium | MVP scope: Python only, single project template. Expand to TypeScript/Node in Month 2 per evolutionary-first principle |
| Specialist agent scope unclear | Medium | Low | Character terminology formalized in governance; Month 1 scope (discovery/facilitation) explicit; escalation paths defined |
| First customer deal closed before Month 3 | Medium | Medium | Start consulting outreach Week 2; target signed engagement letter ($10K–$15K minimum) for proof of market fit |
| Training pilot format undefined | Low | Very Low | Hybrid format decided: self-paced foundational + async cohort (20–30 learners); Sheela leads curriculum Month 4 |

---

## Mid-Term Phase (Months 4–6) — Content Extraction & Scaling

### Primary Deliverables

1. **Scratchpad Standalone** (`@endogenai/scratchpad`) — Extracted from dogma into reusable package
2. **Library Resources** (`@endoHybrid format (self-paced foundational content + async cohort, 20–30 learners, 70%+ completion target)
4. **First Consulting Engagement** — Signed engagement letter ($10K–$15K), 4-week proof-of-concept projeched
4. **First Consulting Engagement** — 1 customer, 4-week project, proof-of-concept

### Success Criteria

- ✅ Scratchpad repo live with documentation and package installation test
- ✅ Library repo live with sear (hybrid format with self-paced foundation); first cohort enrolled; 70%+ completion target
- ✅ First consulting contract signed and payment terms agreed ($10K–$15K minimum)
- ✅ Specialist Characters fully autonomous; integrated into dogma decision workflows with defined escalation paths
- ✅ Business Lead tracking pipeline value separately from booked revenue
- ✅ Specialist agents fully operational; integrated into dogma decision workflows

### Team & Effort

- **Conor**: 60+ hours (consulting delivery, partner outreach, dogma refinements)
- **Sheela**: 100+ hours (training content development, library curation, specialist agent automation)
- **Specialist agents**: 30+ hours (business lead pipeline tracking, comms community engagement, public engagement event planning)

### Key Dependencies

1. Dogma + init/adopt must reach stability (critical bugs resolved)
2. First consulting deal must close in Month 3 (scope/engagement defined by Month 4 kickoff)
3. Training curriculum outlined in Month 1, piloted in Month 4
4. Specialist agents fully operational with decision authority (or clear escalation paths to Conor)

---

## Long-Term Phase (Months 7+) — Library Build & Product Maturity

### Primary Deliverables

1. **Skills Library** (`@endogenai/skills`) — 3–5 domain-specific reusable skills (e.g., vendor evaluation, hiring process, security audit workflows)
2. **Workflows Library** (`@endogenai/workflows`) — 2–3 business process templates (quarterly planning, customer onboarding, incident response)
3. **Characters Library** (`@endogenai/characters`) — 2–3 specialized agent definitions (Sales Engineer, Security Architect, Marketing Analyst)
4. **Mature Revenue Streams** — Consulting + training repeatable and sustainable

### Success Criteria

- ✅ All three libraries live, documented, and included in monthly release cycle
- ✅ 3+ active consulting engagements delivering value
- ✅ 10+ training program graduates with feedback loop
- ✅ 100+ GitHub stars; 10+ contributing organizations or individuals
- ✅ Clear product-market fit signal (organic user growth, repeat customers, community momentum)

### Team & Effort

- **Conor**: Transition to business/strategy focus (40% technical, 60% customer/partnership)
- **Sheela**: Content/training lead (expand training to 2–3 concurrent cohorts, hire assistant)
- **Hires**: 1 full-time member (engineering or training) by Month 9–12, pending revenue availability
- **Community**: Open-source contributors beginning to propose skills/workflows

---

## Dependencies & Critical Path

```
Month 1:
  Week 1: Dogma rename ✓
  ├─ Gates: Week 2 (init/adopt scaffold)
  ├─ Gates: Week 3 (specialist agents draft)
  └─ Gates: Web SPA begin

Month 2:
  Init/Adopt completion ✓
  ├─ Gates: Specialist agents operational
  ├─ Gates: First customer outreach
  └─ Gates: Web SPA completion (or MVP defer)

Month 3:
  Web SPA launch + First customer deal ✓
  ├─ Gates: Mid-term roadmap (scratchpad extraction, training pilot)
  └─ Gates: Specialist agents autonomous operation

Month 4–6:
  Scratchpad/Library extraction + Training pilot + Consulting revenue ✓
  └─ Gates: Long-term libraries (skills/workflows/characters)

Month 7+:
  Sustained consulting + Training + Library maturity + Community growth
```

---
Character Definitions (Month 1 Scope)

Three specialist Characters are defined and drafted in Week 3 of Month 1. See `.github/agents/business-lead.agent.md`, `.github/agents/comms-strategist.agent.md`, `.github/agents/public-engagement-officer.agent.md` for full definitions. 

**Character Terminology**: Formalized in `.github/agents/AGENTS.md` and `docs/guides/agents.md` (commit ccf1f6e). Characters are narrow-scope specialist agents with explicit decision authority and escalation protocols.

**Month 1 Scope**: Each Character assists with discovery and team alignment; all decisions flagged to Conor for review; escalation protocols explicitly defined.

**Month 2+**: Character autonomy expands per Conor's confidence and business outcomes (consulting revenue, customer feedback, etc.)
**Month 2+**: Agency and autonomy expand per Conor's confidence and revenue justification.

---

## Next Steps — Execution & Review

1. **Phase 3 Review Gate**: This roadmap is validated against MANIFESTO.md alignment, feasibility, and sequencing by the Review agent.
2. **Upon APPROVAL**: 90-Day Execution Workplan (detailed month-by-month) becomes the tactical daily reference.
3. **GitHub Project #3 Integration**: All issues linked to roadmap milestones via labels + project board.
4. **Monthly Status Updates**: Scratchpad and project board updated in real-time; monthly retrospective with Conor + Sheela.

