---
title: "EndogenAI 90-Day Execution Workplan — Months 1–3 (March–May 2026)"
status: active
---

# EndogenAI 90-Day Execution Workplan — Months 1–3 (March–May 2026)

## Overview

This workplan details week-by-week execution for Month 1 (critical path), month-level planning for Months 2–3, per-task assignments, effort estimates, risk mitigation, and success metrics.

**Timeline Update (Mar 10, 2026)**: Web SPA launch moved to **Week 1 parallel track** (was deferred to Month 2). This accelerates market presence from Month 2 to Week 1, requiring ~31 person-hours in Week 1 but freeing Month 2 capacity for init/adopt feature expansion and customer outreach.

**Month 1 Flexibility**: Weeks 2–4 can flex based on Web SPA completion status and first customer feedback from Week 1 launch.

---

## Month 1 — Foundation & Launch (Mar 10–Apr 10)

### Week 1 (Mar 10–16): Dogma Rename + Web SPA MVP Launch

**Objective**: (1) Safely rename `/workflows` → `@endogenai/dogma` with zero git history loss; (2) Launch simple React SPA with public landing page at endogenai.accessi.tech. Execute in parallel to maximize Week 1 impact.

#### Task List — Dogma Rename Track

- [ ] **Conor: Test dogma rename procedure on feature branch** (4 hrs)
  - Clone workflows repo locally
  - `git mv` rename at filesystem level
  - Update `pyproject.toml`, `README.md`, `mkdocs.yml`, any hardcoded references
  - Run `lychee docs/` to check for broken markdown links
  - Commit to feature branch `feat/workflows-rename-dogma`
  - Verify CI passes (GitHub Actions workflow, pre-commit hooks)

- [ ] **Conor: Execute dogma rename on main** (2 hrs)
  - Merge feature branch to main (or PR for review)
  - Tag new version: `git tag -a v0.1.0-dogma -m "Official rename: /workflows -> @endogenai/dogma"`
  - Update CONTRIBUTING.md, CODE_OF_CONDUCT.md with new repo name
  - Push to origin; verify CI green

- [ ] **Sheela: QA dogma rename — comprehensive link & content check** (6 hrs)
  - Clone renamed repo; verify folder structure intact
  - Run `lychee` locally; document any dead links found
  - Check GitHub Actions workflows (all relative paths still correct)
  - Verify pre-commit hooks still function
  - Test `uv sync` environment setup
  - Document findings; create GitHub issue for any dead links found

- [ ] **Both: Release notes & communications** (2 hrs)
  - Draft release announcement for GitHub issue #93 (epic update)
  - Update README.md front matter (rename reference)
  - Prepare dogma announcement for communities

#### Task List — Web SPA Launch Track (Parallel)

- [ ] **Conor: Scaffold React SPA project** (6 hrs)
  - Initialize React app (Vite or Create React App, current best practices)
  - Set up folder structure: `src/pages/`, `src/components/`, `public/`
  - Configure GitHub Pages deployment (build → `docs/` folder, CNAME file for endogenai.accessi.tech)
  - Install dependencies: React Router, Tailwind CSS or similar (minimal, high-performance setup)
  - Verify build passes local tests

- [ ] **Conor: Build landing pages** (8 hrs)
  - Homepage: "What is EndogenAI — Vision & Positioning"
  - Getting Started page: "Quick links to dogma, init, adopt; call-to-action for consulting"
  - Use Case / case studies page: "How EndogenAI works for open-source + enterprise"
  - About page: "Team, mission, links to GitHub/discussions"
  - Deploy to GitHub Pages; test at endogenai.accessi.tech

- [ ] **Sheela: Content & messaging for SPA** (4 hrs)
  - Write homepage headline + value prop
  - Draft getting started copy (motivate dogma, init, adopt repos)
  - Prepare images/diagrams (what is agent-first development?)
  - Proofread + accessibility check (alt text, color contrast)

- [ ] **Conor: Domain setup & DNS** (1 hr)
  - Point endogenai.accessi.tech CNAME to GitHub Pages
  - Verify domain resolves + HTTPS is active
  - Test mobile responsiveness

**Effort**: Conor 21 hrs, Sheela 10 hrs | **Total**: 31 hrs | **Effort per person**: Conor ~3 days full-time, Sheela ~1.25 days

**Risk**:
- SPA build takes longer than 6 hrs → Mitigation: use template/starter (Vite React minimal template, not full-featured)
- DNS propagation delays → Mitigation: start DNS change immediately; test GitHub Pages URL first, then point domain
- Domain not responding by Friday → Mitigation: accept GitHub Pages default URL (github.com/..) as backup; DNS can finish over weekend

**Success Criteria**:
- Dogma rename successfully executed; CI green; git history intact
- Web SPA live at endogenai.accessi.tech with 4+ pages
- HTTPS active; mobile responsive
- No broken links on SPA
- All content proofread + on-brand

**Blocker for**: Week 2 (init/adopt repos depend on stable dogma reference + web presence completed)

---

### Week 2 (Mar 17–23): Init & Adopt Repo Scaffolding

**Objective**: Create GitHub repos for init and adopt wizards. Establish foundational CI/CD, folder structure, and documentation stubs. Both repos should mirror dogma's engineering standards (ruff, pytest, pre-commit).

#### Task List

- [ ] **Conor: Create @endogenai/init GitHub repo from dogma template** (3 hrs)
  - Create new repo on GitHub (public, open-source license per existing)
  - Mirror dogma's CI/CD pipeline (GitHub Actions, ruff linting, pytest, pre-commit)
  - Copy dogma's `.github/workflows/`, `pyproject.toml`, `ruff.toml`, `.pre-commit-config.yaml`
  - Create basic folder structure: `src/endogenai_init/`, `tests/`, `docs/`
  - Create README stub: "EndogenAI init — Greenfield project setup wizard"
  - Create CONTRIBUTING.md (reference dogma's MANIFESTO)

- [ ] **Conor: Create @endogenai/adopt GitHub repo from dogma template** (3 hrs)
  - Same process as init (create repo, mirror CI/CD, folder structure)
  - Create README stub: "EndogenAI adopt — Integration wizard for existing projects"

- [ ] **Sheela: Document init wizard UX & requirements** (4 hrs)
  - Interview Conor on init wizard scope (what questions? what templates? what outputs?)
  - Sketch user flow diagram (CLI questions → project structure → generated files)
  - Document adoption path (what new users experience; minutes to first working demo)
  - Create GitHub issue #96 subtasks: wizard scope, template design, MVP acceptance criteria

- [ ] **Sheela: Document adopt playbook structure** (4 hrs)
  - Outline adoption lifecycle (assessment → design → implementation → validation)
  - Document typical adoption engagement scope (hours/weeks, what's included, what's not)
  - Create GitHub issue #97 subtasks: playbook sections, case study template, customer success criteria

- [ ] **Both: CI/CD validation for both repos** (2 hrs)
  - Verify ruff, pytest, pre-commit all functional on both init and adopt repos
  - Trigger first GitHub Actions runs (empty test suite, but workflow should execute)
  - Validate `.gitignore`, `poetry.lock` / `uv.lock` are correct

**Effort**: Conor 6 hrs, Sheela 8 hrs | **Total**: 14 hrs

**Risk**:
- CI setup takes longer than 2 hrs → Mitigation: use dogma's exact config (copy-paste, not reinvent)
- Repo template creation is slower than expected → Mitigation: create both repos in parallel using GitHub web UI

**Success Criteria**:
- Both repos live on GitHub, properly configured, with read-me and contributing stubs
- All CI/CD workflows green (even with minimal/empty content)
- Clear folder structure present (mirrors dogma standards)
- Issues #96 and #97 have detailed task breakdowns for Week 3–4

**Blocker for**: Week 3 (specialist agents draft) and Week 4 (wizard implementation)

---

### Week 3 (Mar 24–30): Specialist Agents Draft

**Objective**: Define three specialized agent roles as `.agent.md` files (Business Lead, Comms Strategist, Public Engagement Officer) with Month 1 scope (discovery/team alignment, not autonomous decision-making yet).

#### Task List

- [ ] **Conor: Draft Business Lead `.agent.md`** (4 hrs)
  - Role scope (Month 1): Synthesize customer insights, track consulting pipeline, inform pricing strategy
  - Endogenous sources: `docs/research/endogenai-product-discovery.md`, `MANIFESTO.md`, GitHub issue #93 (epic), consulting inquiry log
  - Action section: Responsibilities — weekly pipeline review, customer feedback synthesis, deal mechanics research
  - Quality gate: All recommendations logged in GitHub issues; weekly sync with Conor reviews all decisions
  - Constraints: No autonomous contracts; all deals require Conor approval

- [ ] **Sheela + Conor: Co-author Comms Strategist `.agent.md`** (5 hrs)
  - Role scope (Month 1): Define messaging framework, propose content calendar, establish brand voice
  - Endogenous sources: `docs/research/endogenai-product-discovery.md`, competitor analysis, GitHub issue #93, dogma repo README
  - Action section: Responsibilities — content brainstorm, messaging testing (via GitHub discussions), social media calendar, PR/blog outline
  - Quality gate: All messaging proposals reviewed by Conor + Sheela; calendar locked weekly
  - Constraints: No autonomous posts; all public-facing content requires approval

- [ ] **Sheela: Draft Public Engagement Officer `.agent.md`** (4 hrs)
  - Role scope (Month 1): GitHub PR review presence, community discussions monitoring, event outreach
  - Endogenous sources: `docs/research/endogenai-product-discovery.md`, `CONTRIBUTING.md`, community guidelines, GitHub issues
  - Action section: Responsibilities — monitor dogma + init/adopt PRs & discussions, surface community questions, identify speaker opportunities
  - Quality gate: All community summaries posted as GitHub issue comments; monthly report to Conor
  - Constraints: No autonomous PR merges; facilitator role only

- [ ] **Both: Review agents against agent authoring standards** (2 hrs)
  - Check each agent file against `.github/agents/AGENTS.md` requirements (YAML frontmatter, required sections, cross-reference density)
  - Run `validate_agent_files.py` (if available) to syntax-check all three
  - Verify endogenous sources use correct relative paths (`../../` from `.github/agents/` to repo root)

- [ ] **Conor: Commit agents to dogma + link to epic** (1 hr)
  - Add all three `.agent.md` files to `dogma/.github/agents/`
  - Commit: `feat: add specialist agents — business-lead, comms-strategist, public-engagement-officer`
  - Create comment on GitHub issue #103 linking to committed agent files
  - Update epic #93 body to reference Week 3 completion

**Effort**: Conor 5 hrs, Sheela 9 hrs | **Total**: 14 hrs

**Risk**:
- Agent scope creep (too many responsibilities assigned) → Mitigation: keep scope explicitly narrow; Month 1 agents are discovery-assistants, not decision-makers
- Endogenous sources unclear / broken links → Mitigation: Sheela QA all links; validate_agent_files.py catches bad paths

**Success Criteria**:
- All 3 agents drafted, committed, syntactically valid
- Endogenous sources properly linked and readable
- Month 1 scope explicitly narrow (discovery/facilitation, not autonomous decision authority)
- GitHub issue #103 updated with agent file links

**Blocker for**: Week 4 (agents provide context for init wizard scope refinements)

---

### Week 4 (Mar 31–Apr 6): Init Wizard MVP Implementation

**Objective**: Implement MVP version of init wizard CLI. Should generate a working Python project scaffold in <5 minutes. Expand to other languages in Month 2.

#### Task List

- [ ] **Conor: Implement init wizard MVP CLI** (12 hrs)
  - CLI framework: Python Click or Typer (chosen based on dogma's existing tooling preferences)
  - Wizard flow (questions):
    - Project name?
    - Python version preference (3.10, 3.11, 3.12)?
    - Use [dogma/init] scripts or [dogma] docs?
  - Output: Generated project folder with:
    - `pyproject.toml` (minimal, uv-ready)
    - `.venv/` scaffolding or poetry/uv instructions
    - `README.md` (reference to dogma + onboarding links)
    - `.github/workflows/` CI template (ruff, pytest)
    - `src/myproject/`, `tests/`, `docs/` folders
  - Testing: Test wizard locally; generate 2–3 sample projects; verify they run (empty hello world is sufficient)

- [ ] **Sheela: Document adopt playbook first draft** (6 hrs)
  - Write adoption assessment questionnaire (analyze existing codebase, identify pain points, propose integration points)
  - Outline playbook sections: Discovery → Design → Migration → Validation
  - Create GitHub issue #97 with detailed task breakdown for Month 2 implementation

- [ ] **Both: Set up Month 2 sprint planning** (2 hrs)
  - Schedule Conor + Sheela sync for Mar 31 (end of Week 4, before April)
  - Outline Month 2 priorities: init wizard expansion, adopt playbook implementation, web SPA kickoff
  - Update GitHub project #3 board with Month 2 issues

**Effort**: Conor 12 hrs, Sheela 8 hrs | **Total**: 20 hrs

**Risk**:
- Wizard complexity exceeds time budget → Mitigation: MVP scope is Python only; TypeScript/Node added in Month 2
- Generated projects don't run → Mitigation: Test locally 3+ times before committing; all generated files match dogma templates exactly

**Success Criteria**:
- Init wizard CLI live in `@endogenai/init` repo
- MVP scope achieved: generates Python project scaffold in <5 min
- All generated projects pass `uv sync` + basic hello-world test
- Commit: `feat: init wizard MVP — Python projects`
- GitHub issue #96 updated with MVP completion; Month 2 expansion tasks added

---

## Month 2 — Wizards, Web, Consulting Pipeline (Apr 10–May 10)

### Parallel Workstreams

**Workstream 1: Init/Adopt Expansion**
- Expand init wizard to TypeScript/Node (if time permits; otherwise Month 3)
- Complete adopt playbook (assessment questionnaire, case study template, migration guide)
- Success: Adopt repo has playbook + 1 case study; init supports 2+ languages

**Workstream 2: Web SPA Launch Preparation**
- Finalize web SPA design (Figma or equivalent)
- Implement basic SPA (Astro / Next.js / React)
- Deploy to staging environment
- Success: Staging URL accessible; public launch in Month 3

**Workstream 3: First Customer Outreach**
- Begin consulting pipeline conversations (target: 3-5 warm leads by end of Month 2)
- Qualify first customer (scope, timeline, budget)
- Success: 1 customer in advanced discussion; LOI drafted

**Workstream 4: Training Curriculum Outline**
- Define training modules/topics (based on first customer needs + market validation)
- Outline 1 pilot cohort or self-paced module
- Success: Training scope defined; enrollment path designed

**Effort Distribution**:
- Conor: 60 hrs (consulting outreach, web design input, specialist agent feedback)
- Sheela: 80 hrs (adopt playbook, training curriculum, content + comms)
- Specialist agents: 20 hrs (business lead pipeline tracking, comms messaging reviews, public engagement event scouting)

---

## Month 3 — Product Launch & Revenue (May 10–Jun 10)

### Parallel Workstreams

**Workstream 1: Web SPA Launch**
- Deploy public website (private repo for code; public-facing URL)
- All positioning, messaging, CTAs live
- Announce via GitHub releases, social media
- Success: 50+ GitHub stars; 10+ consulting inquiries in first week

**Workstream 2: First Consulting Engagement**
- Kick off first customer consulting engagement (4-week project start)
- Establish delivery team (Conor lead; Sheela for content/documentation)
- Success: Customer feedback positive; proposal for follow-on engagement initiated

**Workstream 3: Training Pilot Launch**
- Launch 1 training course (1 cohort if group; or 1 self-paced module)
- Recruit 5-10 participants (target: dogma users, GitHub stars, warm intros)
- Success: All participants pass; feedback collected for Month 4 iteration

**Workstream 4: Specialist Agents Operational**
- Business Lead agent actively tracking pipeline, making recommendations
- Comms agent managing content calendar, social presence
- Public Engagement Officer facilitating GitHub discussions, monitoring community
- Success: All 3 agents providing measurable value; Conor confidence in agent autonomy increases

**Effort Distribution**:
- Conor: 80 hrs (consulting delivery, business development, agent feedback)
- Sheela: 100 hrs (training delivery, content, comms operations)
- Specialist agents: 40 hrs (autonomous decision support, community presence)

---

## Critical Path & Dependency Map

```
┌─ Week 1: Dogma Rename ✓ (CRITICAL)
│
├─ Week 2: Init/Adopt Scaffold ✓
│  ├─ Blocks: Week 3 (specialists agents need stable repos to reference)
│  └─ Blocks: Week 4 (wizard implementation)
│
├─ Week 3: Specialist Agents Draft ✓
│  └─ Blocks: Month 2 (agents inform business decisions)
│
├─ Week 4: Init Wizard MVP ✓
│  └─ Blocks: Month 2 (expansion to other languages)
│
├─ Month 2: Web SPA + Consulting Outreach (PARALLEL)
│  ├─ Web SPA gates: Public announcement in Month 3
│  └─ Consulting outreach gates: First contract in Month 3
│
└─ Month 3: Product Launch + Revenue
   ├─ Gates: Web SPA live + first customer go-live
   ├─ Gates: Training pilot launched
   └─ Gates: Clear product-market fit signal
```

---

## Risk Register

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|-----------|-------------|
| **Dogma rename breaks CI/links** | High | Low | Pre-rename dry-run; lychee check; feature branch test | Revert to feature branch; fix + retry next week |
| **Init wizard scope creep** | Medium | High | MVP = Python, 1 template only; TypeScript deferred to Month 2 | Deploy MVP; extend in Month 2 with full resources |
| **Web SPA budget/contractor unavailable** | High | Medium | **Plan A**: Conor builds SPA in Month 2 (defer Month 1). **Plan B**: Use free Astro template + Vercel (minimal complexity) | Use positioning deck + GitHub README until SPA ready |
| **First customer deal slips past Month 3** | Medium | High | Start outreach in Month 2 Week 1; aim for LOI by Month 2 Week 8 | Accept verbal commitment + LOI; formal contract in Month 4 |
| **Specialist agent scope unclear / conflicts** | Medium | Medium | Keep Month 1 scope narrow (discovery only); Weekly Conor+Sheela sync on agent decisions | Rollback to manual processes; agents retry in Month 2 with refined scope |
| **Training curriculum too ambitious** | Medium | Medium | Pilot = 1 module or small cohort (5-10 people), not full program | Scale down to 1 topic; defer advanced modules to Month 4 |

---

## Success Metrics @ End of Month 3

**Infrastructure**:
- ✅ Dogma repo renamed; all CI passing; git history preserved
- ✅ Init & Adopt repos live with MVP features
- ✅ Web SPA accessible (live public URL)
- ✅ All 3 specialist agents `.agent.md` files committed + operational

**Market & Revenue**:
- ✅ 1+ consulting engagement letter signed (even if kickoff in Month 4)
- ✅ 1 training pilot cohort launched or self-paced module published
- ✅ 20+ GitHub stars on dogma repo
- ✅ 10+ consulting/training inquiries received

**Community & Operations**:
- ✅ GitHub project #3 tracking all work; "Product Discussion" milestone 80%+ completed
- ✅ Specialist agents actively supporting Conor+Sheela decision-making
- ✅ Issue #93 (epic) substantially advanced; most sub-issues (95–104) in "In Progress" or "Done"

**Data-Driven Decision**:
- ✅ Conor + Sheela monthly retrospective (Mar -> Apr, Apr -> May, May -> Jun); feedback loop documented
- ✅ Roadmap refinements for Months 4–6 driven by actual market feedback, not assumptions

---

## Appendix: Specialist Agent Files

Three agent definitions are committed in Week 3, Month 1. See:
- `.github/agents/business-lead.agent.md`
- `.github/agents/comms-strategist.agent.md`
- `.github/agents/public-engagement-officer.agent.md`

Each agent's scope is explicitly narrow in Month 1 (discovery/facilitation). Authority to make decisions is escalated to Conor until Month 2–3 feedback validates autonomous decision-making.

