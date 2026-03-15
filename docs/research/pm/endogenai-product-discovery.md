---
title: EndogenAI Ecosystem Product Discovery
status: Final
---

## 1. Executive Summary

EndogenAI is evolving from a single-repository foundational knowledge system (`/workflows` → `@endogenai/dogma`) into a multi-repository open-source ecosystem designed to enable enterprises and practitioners to build, deploy, and scale agentic workflows following three core axioms: Endogenous-First (self-justifying knowledge), Algorithms Before Tokens (encoded solutions over interactive work), and Local Compute-First (no cloud lock-in). The ecosystem comprises seven planned repositories addressing different stages of adoption: dogma (foundational knowledge), init (greenfield setup), adopt (integration into existing projects), web (public-facing education and commercial engagement), scratchpad (session-management tooling), library (curated resources), and long-term specialized libraries (skills, workflows, characters). Revenue flows through consulting services and training/certification programs, with Conor and Sheela as founders, supported by specialist business agents (Business Lead, Comms Strategist, Public Engagement Officer) who bridge product discovery with market realities. Timeline: product discovery and roadmap planning (months 1–3), repo setup and wizard launch (months 1–3 concurrent), mid-term extraction and training development (months 4–6), long-term library build and revenue scaling (months 7+).

---

## 2. Hypothesis Validation — Vision & Alignment with MANIFESTO.md

### Endogenous-First Implementation
The multi-repository structure embodies the Endogenous-First axiom by ensuring each repository contains its own foundational knowledge, decision records, and self-justifying principles. Rather than centralizing all knowledge in a single repo and forcing downstream projects to reach back into a monolith, each ecosystem repository (`init`, `adopt`, `web`, `library`, `scratchpad`) carries enough context-scaffolding that practitioners can understand *why* decisions were made and *how* to extend or modify them locally. The `dogma` repo serves as the root axiom source, but `init` and `adopt` explicitly reference and instantiate dogma principles in their own scaffolds rather than treating them as remote dependencies. This design prevents knowledge loss and enables practitioners to fork and customize without forfeiting clarity.

### Algorithms Before Tokens Implementation
The ecosystem prioritizes encoded solutions (scripts, templates, agent definitions, decision trees) over interactive setup and coaching. The `init` wizard generates boilerplate projects via deterministic templates. The `adopt` wizard automates integration into existing codebases using code analysis and transformation rules. The `library` curates patterns and benchmarks that inform algorithm selection rather than requiring users to interview vendors or hire consultants. Specialist agents (Business Lead, Comms, Public Engagement Officer) encode their decision logic as scripts and checklists, avoiding the token burn of real-time Q&A for routine business decisions. This posture reduces the total cost of adoption (literal and token-based) and makes the system teachable to new teams.

### Local Compute-First Implementation
Every ecosystem repository is designed to run entirely on local infrastructure. The `dogma` repo contains no cloud dependencies; its CI/CD pipeline uses standard open-source tools (ruff, pytest, pre-commit, GitHub Actions). The `init` and `adopt` wizards generate projects that depend only on standard package managers (npm, pip, uv) and local tooling. The `web` SPA (private repo) is a static site deployment with no backend reliance on cloud APIs for core functionality. The `scratchpad` tool, once extracted, operates as a local session-management library with no telemetry or cloud sync. The `library` is a static resource repository (Markdown, YAML, data files) requiring no runtime dependencies. This constraint ensures that adopters can build sophisticated agentic systems in air-gapped environments and retain full ownership of their inference compute and data.

---

## 3. Pattern Catalog — Org Structure & Ecosystem Design

### @endogenai/dogma
The foundational knowledge repository containing MANIFESTO.md, core axioms, workflow guides, agent definitions, decision records (ADR suite), CI/CD templates, and the scripts that enforce these principles across the ecosystem. This repo serves as the root-of-trust for EndogenAI values and is the primary home for research, standards, and meta-processes (e.g., how agents themselves are authored). Currently equivalent to the `/workflows` repository; renaming preserves history while signaling the repo's role as the organization-level dogma container.

### @endogenai/init
A greenfield setup wizard that helps new users create an EndogenAI-conformant project from scratch. Contains scaffolding templates for Python, TypeScript, and other language stacks; a CLI tool that asks qualifying questions and generates boilerplate; and a curated set of best-practice defaults drawn from `dogma` (CI templates, agent skeleton files, folder structure, documentation stubs). Reduces time-to-first-working-project from days to hours.

### @endogenai/adopt
An integration/adoption wizard for existing projects. Analyzes incoming codebases, detects existing agent definitions, CI/CD patterns, and business logic; proposes minimal changes to incorporate EndogenAI workflows and decision records; and generates a migration guide that preserves existing code while adding new tooling and practices. Targets enterprises with mature but rigid systems who need agentic capability grafted on without full rewrite.

### @endogenai/web
Public-facing SPA (initially GitHub Pages at endogenai.accessi.tech; private ownership to separate product narratives from operational dogma). Explains the EndogenAI approach to non-technical audiences with deep dives for advanced users. Includes landing pages for consulting and training offerings, case studies, demo link to dogma, and FAQ. Targets prospective clients, partners, and advanced practitioners. Launch: March Week 1 (React MVP, 4+ pages). Future: analytics and conversion tracking to inform go-to-market adjustments.

### @endogenai/scratchpad
A standalone, installable session-management tool extracted from `dogma` into a reusable package. Implements the session lifecycle, context compaction, and scratchpad watcher functionality as a library that any project can integrate to enable Copilot-style multi-agent session orchestration. Reduces coupling between core dogma and projects that want session-level tooling without adopting the full ecosystem.

### @endogenai/library
A curated collection of resources (research documents, patterns, case studies, performance benchmarks, market analysis, competitive landscape) that inform agent decision-making and business strategy. Separates the "body of knowledge we've learned" from the "process we use to learn" (which lives in `dogma`). Browsable and searchable; can be integrated into agent decision logic as a knowledge base.

### @endogenai/skills, @endogenai/workflows, @endogenai/characters (Long-term)
Specialized domain libraries built after the core ecosystem is operational. **Skills**: reusable tactical procedures (e.g., "vendor evaluation," "network troubleshooting," "customer onboarding") encoded as SKILL.md files and scripts. **Workflows**: multi-phase templates for common business processes (quarterly planning, hiring, acquisition screening). **Characters**: pre-configured VS Code agent definitions with specialized personas and endogenous sources (e.g., "Sales Engineer Agent," "Security Architect," "Marketing Analyst"). These libraries are where the ecosystem's value accrues over time as the library grows richer and more specialized.

---

## Go-To-Market Strategy

### Commercial Engagement Models
**Consulting**: Pricing model established at ~$2.5K/day rate. Typical project scope: 1–4 weeks; estimated timeline per engagement: 2–6 weeks (including discovery + implementation). MinimumEngagement: signed engagement letter (binding commitment) with $10K–$15K value threshold to signal market fit (vs. non-binding LOI). Business Lead Character manages pipeline and tracks deal flow. Revenue model: project-based with recurring support options.

**Training & Certification**: Hybrid format decided. Sheela leads curriculum development in Month 4: self-paced foundational content (videos, labs, docs) paired with async community cohort (Discord/GitHub Discussions, 2x weekly syncs). First cohort: 20–30 learners, 6 weeks, 70%+ completion target with 2+ consulting leads generated as success signal. Revenue model: freemium (free OSS, paid enterprise tier with live lab support). Certification signals competency; future cohorts scale by moderation only (Algorithms Before Tokens axiom).

### Target Audience
- **Primary**: Enterprises (financial services, healthcare, manufacturing) and data-heavy teams looking to adopt agentic automation frameworks to reduce operational overhead and improve decision velocity.
- **Secondary**: Individual practitioners and startups building AI-native systems; open-source developers adopting EndogenAI patterns in their own projects.
- **Tertiary**: Consulting firms and system integrators who integrate EndogenAI into client engagements (partner distribution channel).

### First Customer Hypothesis
[TBD — who is the ideal first customer type? What problem will EndogenAI solve for them? Why will they sign before competitors do?]
Profile

Target for Month 3 closed deal: Mid-market enterprise (50–500 employees) in finance, healthcare, or manufacturing with a specific workflow automation use case (e.g., document processing, compliance automation, decision support). Budget authority for $10K–$15K engagement. Platform: Python-based or cloud-agnostic (aligns with Local Compute-First positioning).
Success will be measured across three dimensions:

1. **Market Adoption**: GitHub stars; active projects using `init` and `adopt` wizards; community size (discussions activity, event participation).
2. **Revenue Metrics**: Consulting pipeline value and contracted bookings; training program enrollment rate; average consulting contract value.
3. **Community Health**: GitHub discussions activity level and quality; events hosted (webinars, workshops); speaker appearances at conferences and community forums.

Specific numeric targets per dimension and timeline [TBD pending Conor + Sheela input during roadmap phase].

---

## Specialist Agents as Product Feature

The following specialist agents are prerequisites for scaling business operations. They should also inform product decisions by surfacing market realities, customer needs, and operational constraints that affect roadmap prioritization. These three agents are scoped and defined as `.agent.md` files during Phase 1 (months 1–3) per the fleet authoring standards, with full operational implementation deferred to Phase 2 to avoid overload during initial product launch.

### Business Lead Agent
**Status**: [TBD] Responsibilities: revenue forecasting, pricing model refinement, partnership strategy, contract review, investor relations (as applicable), budget allocation, hiring/headcount planning. Endogenous sources: financial models, partner agreements, customer research, market analysis. **Product role**: Flags when engineering decisions conflict with revenue targets or customer acquisition strategy. Proposes tiered offerings (free tier for open-source projects, paid tier for enterprises) based on unit economics. Escalates risk (e.g., if cloud hosting costs would break the Local Compute-First promise). Identifies gaps in go-to-market execution before they harm adoption.

### Comms Strategist Agent
**Status**: [TBD] Responsibilities: content calendar, messaging framework, competitive positioning, market announcements, community engagement strategy, event planning. Endogenous sources: brand guidelines (TBD), competitor messaging patterns, community feedback, market trends. **Product role**: Proposes product positioning based on differentiation analysis (e.g., "endogenous-first is our defensible moat; emphasize it in all messaging"). Identifies gaps in the narrative that prevent user adoption (e.g., "practitioners don't understand the difference between `init` and `adopt`; let's refine positioning"). Recommends feature timing based on announcement cadence and market readiness.

### Public Engagement Officer Agent
**Status**: [TBD] Responsibilities: developer advocacy, GitHub discussions facilitation, community event planning, conference speaking, social media strategy, user onboarding for beta programs. Endogenous sources: community feedback, GitHub issues/discussions, event metrics, user surveys. **Product role**: Surfaces feature requests and friction points from users that the core team might miss. Prioritizes bugs and UX issues that affect community sentiment. Identifies training gaps: "Users are struggling to understand session compaction; let's add a walkthrough video." Recommends partner distribution channels based on community feedback.

---

## Tech Stack & Private/Public Boundary

### Web SPA Tech Stack
[TBD — framework choice (React, Vue, Astro, Next.js)? Hosting platform (Vercel, Netlify, self-hosted)? Analytics (Plausible, Segment, internal)? CDN? SSO for training cohorts?]

### Private Team Repository
A non-public repository will host business operations, financial models, partner contracts, market research, and team processes. Access: Conor + Sheela initially; expand to specialist agents and hires as the team grows. This prevents business data from leaking into public GitHub while maintaining audit trails and decision records.

### CI/CD Pipeline
Inherit the `dogma` repo's existing CI infrastructure: ruff (linting/formatting), pytest (testing), pre-commit hooks, GitHub Actions for validation and auto-deployment. Each new repo gets a copy of this pipeline configured for its language and testing requirements. Validation gates: `validate_agent_files.py` (for `.github/agents/*.agent.md`), `validate_synthesis.py` (for research docs), linting and formatting checks, test coverage thresholds.

### Content Hoarding Window
[TBD — how fast does content move from `dogma` to other repos? Immediate extraction (as soon as content is stable)? Quarterly extraction cycles (batch migration every 3 months)? Lazy extraction (only when an end-user needs it)?] This affects maintenance burden and keeps repos synchronized; decision impacts roadmap.

---

## Repo Migration Path

### Phase 1: Immediate (Months 1–3)
- **Week 1**: Rename `/workflows` → `@endogenai/dogma` (preserve git history); update all internal references.
- **Week 2–3**: Create `@endogenai/init` scaffold; begin implementation of greenfield wizard.
- **Week 2–3**: Create `@endogenai/adopt` scaffold; begin implementation of integration wizard.
- **Week 3**: Define specialist agents as `.agent.md` files in `dogma/` or create stub `.agent.md` files in `dogma` for Business Lead, Comms Strategist, Public Engagement Officer — clarify decision with Conor/Sheela.
- **Week 4+**: Launch `@endogenai/web` (private repo); begin content development and SPA scaffolding.
- **Parallel**: Conor/Sheela refine business model; Business Lead Agent gathers market data.

### Phase 2: Mid-term (Months 4–6)
- Extract `scratchpad` functionality from `dogma` into `@endogenai/scratchpad`; publish as installable package.
- Extract research and library resources into `@endogenai/library`.
- Begin development of training curriculum; identify cohort structure and pricing.
- First consulting engagement (ideal).
- Specialist agents operational and participating in weekly planning.

### Phase 3: Long-term (Months 7+)
- Build `@endogenai/skills` library (curated domain-specific procedures).
- Build `@endogenai/workflows` library (multi-phase process templates).
- Build `@endogenai/characters` library (pre-configured agent definitions).
- Establish recurring revenue from consulting + training; reinvest in product team expansion.
- Define product-market fit signal and begin scaling.

---

## Success Metrics

### Month 3 Milestones
[TBD — targets: dogma rename complete and verified; init + adopt wizards launched and tested; web properties live; specialist agents operational. Users/companies engaged: ____. GitHub stars: ____. Consulting inquiries: ____.]

### Month 6 Milestones
[TBD — targets: scratchpad extracted; library launched; first paid consulting contract signed; training program launching (with enrollment: ____). Revenue booked: ____. Active projects using `init`/`adopt`: ____. Specialist agents contributing to 2+ major decisions.]

### Month 12 Definition of Product-Market Fit
[TBD — concrete signal: what would indicate we've achieved PMF? (Revenue target? User growth rate? Market validation? Competitive moat established?)]

---

## Open Questions & Assumptions

### Key Assumptions
- **Consulting is primary revenue** (avoids SaaS/hosting overhead and lock-in; aligns with Local Compute-First constraint).
- **Sheela is a full collaborator/co-founder** ([TBD] — decision: partnership model, domain ownership, decision-making authority).
- **Open-source-first distribution** — all public repos are open-source; revenue comes from services, not licensing.
- **Specialist agents are VS Code agents** ([TBD] — clarify: custom `.agent.md` files in `dogma` or standalone tools?).

### Critical Questions Requiring Conor + Sheela Input

1. **Specialist Agent Implementation**: Should these three agents (Business Lead, Comms, Public Engagement Officer) be authored as `.agent.md` files and invoked within VS Code, or should they be standalone processes/scripts that live in the private team repo?

2. **Sheela's Role**: What is Sheela's primary domain/decision authority in product development? (Strategy? Engineering? Customer success? All of the above?) What is the partnership governance model?

3. **Content Hoarding Window**: How long can content live in `dogma` before it should be extracted to downstream repos? Immediate, quarterly, or lazy on-demand?

4. **Budget & Runway**: What is the financial runway and timeline pressure? Does EndogenAI need to hit revenue targets within a specific window? Are there investor expectations or team expansion constraints?

5. **First Customer Profile**: Who is the *ideal* first paying customer, and why are they more likely to engage EndogenAI than a general-purpose consulting firm or AI automation vendor?

6. **Training Cohort Model**: Is training delivered as instructor-led cohorts (high $, limited scale), self-paced modules (lower $, higher scale), or corporate packages (negotiated, key account model)?

---

## Critical Assessment

This research document completes the **discovery phase** of issue #45. The following limitations and gaps are explicitly acknowledged:

1. **TBD sections remain unresolved** — Go-to-Market pricing, first customer profile, training cohort model, tech stack choices, and all success metric numeric targets are marked `[TBD]`. These require Conor + Sheela facilitation sessions and are not resolvable via agent-led research alone.

2. **Competitor analysis not performed** — A comprehensive competitor landscape survey (gate deliverable in #45) is not included in this document. It requires a dedicated research sprint and is tracked as a follow-up implementation issue.

3. **No primary user research** — The target audience hypothesis and JTBD statements are inferred from the ecosystem design, not validated through direct user interviews or community feedback. This is a known gap in the discovery methodology.

4. **Specialist agent scope under-specified** — Business Lead, Comms Strategist, and Public Engagement Officer roles are described at a feature level only. Full `.agent.md` authoring, decision authority definitions, and escalation paths are Phase 1 implementation work (not research).

5. **Revenue model requires facilitation** — All revenue figures, contract structures, and pricing models are intentionally left as questions requiring Conor + Sheela input. This is a deliberate scope boundary, not a research gap.

**Scope of this document**: This synthesis covers ecosystem architecture, hypothesis validation against MANIFESTO.md axioms, repository structure, go-to-market strategy framework, and open questions. Implementation deliverables from issue #45 (pitch deck, technical requirements doc, Adopt/Init wizard specs) are scoped to separate execution-phase issues.

---

## Next Phase Handoff — Roadmap & Execution Planning

The roadmap and execution planning phase will:
- Refine all TBD sections with Conor + Sheela input.
- Detail monthly milestones and critical-path repo creation order.
- Define specialist agent authoring timeline and initial responsibilities.
- Assign Conor/Sheela ownership per phase and repo.
- Establish hiring and team expansion assumptions.
- Create detailed Phase 1 execution checklist and assign tasks.
- Produce a committed workplan (`docs/plans/`) with per-phase delivery gates.

This discovery document serves as the framing layer; roadmap will operationalize it.
