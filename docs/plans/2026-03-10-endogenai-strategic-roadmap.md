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
- ✅ Init repo live with MVP CLI wizard (Python projects in Month 1; expand to other languages in Month 2)
- ✅ Adopt repo live with playbook documentation and migration guidance
- ✅ Web SPA basic structure operational (may be private until Month 3 launch)
- ✅ All 3 specialist agents drafted, committed to dogma, syntax-validated
- ✅ First consulting or training inquiry pipeline identified via web/email outreach

### Team & Effort

- **Conor**: 100+ hours (dogma rename, init wizard, business development, specialist agent authoring)
- **Sheela**: 80+ hours (documentation, adoption playbook, content strategy, comms agent)
- **Optional**: 1 contractor (40–60 hrs) for web SPA design/build (defer to Month 2 if budget unavailable)

Team capacity: ~180–220 person-hours for Month 1 across full workload

### Key Dependencies

1. **Dogma rename must succeed first** — blocks all downstream repos from referencing dogma
2. **Init/Adopt scaffold CI/CD** — must be stable before wizard implementation
3. **Specialist agents scoped on discovery doc** — agents need endogenous sources to function
4. **Web SPA design** — can proceed in parallel with wizards but output depends on positioning clarity from init/adopt

### Risk Management

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Dogma rename breaks CI or links | High | Low | Pre-rename: run lychee link checker; dry-run rename on feature branch; verify git history post-rename |
| Init wizard scope creep | Medium | Medium | MVP scope: Python only, single project template. Expand to TypeScript, Node, other languages in Month 2 |
| Web SPA budget unavailable | High | Medium | **Plan A**: Conor builds SPA in Month 2; focus Month 1 on selling (positioning deck suffices). **Plan B**: Use free template (e.g., Astro) + Vercel for fast launch |
| Specialist agent scope unclear | Medium | Medium | Keep agents narrow in Month 1: Business Lead tracks deals only; Comms handles messaging only; Public Engagement runs GitHub + events only. Expand scope in Month 2 after month 1 validation |
| First customer deal slips past Month 3 | Medium | High | **Mitigation**: Begin outreach in Month 2 (Week 6 at latest). Accept LOI or signed engagement letter counts as "contract." |

---

## Mid-Term Phase (Months 4–6) — Content Extraction & Scaling

### Primary Deliverables

1. **Scratchpad Standalone** (`@endogenai/scratchpad`) — Extracted from dogma into reusable package
2. **Library Resources** (`@endogenai/library`) — Curated research, patterns, benchmarks
3. **Training Program Pilot** — 1 cohort-based course or self-paced module launched
4. **First Consulting Engagement** — 1 customer, 4-week project, proof-of-concept

### Success Criteria

- ✅ Scratchpad repo live with documentation and package installation test
- ✅ Library repo live with searchable resource index (README + folder structure)
- ✅ Training curriculum defined; first cohort enrolled or module published
- ✅ First consulting contract fully executed (even if still in progress)
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

## Specialist Agent Definitions (Month 1 Scope)

Three specialist agents are scoped and drafted in Week 3 of Month 1. See `.github/agents/business-lead.agent.md`, `.github/agents/comms-strategist.agent.md`, `.github/agents/public-engagement-officer.agent.md` for full definitions. 

**Month 1 Scope**: Each agent assists with discovery and team alignment; decision authority with Conor; escalation protocols defined.

**Month 2+**: Agency and autonomy expand per Conor's confidence and revenue justification.

---

## Next Steps — Execution & Review

1. **Phase 3 Review Gate**: This roadmap is validated against MANIFESTO.md alignment, feasibility, and sequencing by the Review agent.
2. **Upon APPROVAL**: 90-Day Execution Workplan (detailed month-by-month) becomes the tactical daily reference.
3. **GitHub Project #3 Integration**: All issues linked to roadmap milestones via labels + project board.
4. **Monthly Status Updates**: Scratchpad and project board updated in real-time; monthly retrospective with Conor + Sheela.

