---
title: "Project Management and Dev Team Structures"
research_issue: "#19"
status: Final
date: 2026-03-07
closes_issue: 19
sources:
  - docs/research/sources/docs-github-com-en-issues-planning-and-tracking-with-project.md
  - docs/research/sources/docs-github-com-en-communities-setting-up-your-project-for-h.md
  - docs/research/sources/opensource-guide-building-community.md
  - docs/research/sources/opensource-guide-leadership-and-governance.md
  - docs/research/sources/atlassian-com-agile-kanban-kanban-vs-scrum.md
  - docs/research/sources/teamtopologies-com-key-concepts.md
  - docs/research/sources/adr-github-io.md
---

# Project Management and Dev Team Structures

> **Status**: Final
> **Research Question**: What PM methodologies and team structures best fit a small OSS project augmented by an AI agent fleet? Covering issue-first workflows, planning cadence, governance, decision records, and async communication.
> **Date**: 2026-03-07

---

## 1. Executive Summary

Seven research questions were submitted for validation against six primary sources spanning GitHub's own project tooling documentation, OSS governance guides, agile methodology analysis, and team topology research. All seven questions converge on a coherent and mutually reinforcing picture.

**The central finding**: for a 2–5 person OSS team with an agent fleet, the correct system is Kanban-flow planning (not Scrum sprints), liberal contribution governance (not BDFL or meritocracy), GitHub-native tooling (not external PM tools), and Team Topologies' four-team-type model applied to both human contributors and agents. No external tooling is warranted at this scale.

The highest-leverage gaps in the current repo are: (1) no structured labels taxonomy, making triage require human judgment on every issue; (2) no GitHub Projects board, making work state invisible; (3) no Architecture Decision Records practice, creating re-litigation risk as the agent fleet grows; and (4) no `GOVERNANCE.md`, meaning agent and human roles are implicit rather than explicit.

The agent fleet maps directly onto Team Topologies' framework: agent executives are Enabling teams (temporary skill augmentation), specialist agents are Complicated Subsystem teams (deep expertise, on-demand), and the GitHub/Review agents are Platform teams (consumed X-as-a-Service). This mapping has practical PM implications: agents should be treated as **tools with defined SLAs**, not as standing team members with velocity or burndown.

---

## 2. Hypothesis Validation

### RQ1 — Issue-First Workflow Maturity

**Hypothesis**: A mature GitHub issue-driven workflow requires a structured label taxonomy, issue templates, PR-to-issue linking, and a Project board for visual triage.

**Verdict**: CONFIRMED

**Evidence**: GitHub Projects (official docs) provides table, board, and roadmap views with direct bi-directional sync to issues and PRs, custom fields (priority, complexity, type, iteration), built-in automations, and status updates. The system is explicitly non-prescriptive: "Rather than enforcing a specific methodology, a project provides flexible features you can customize to your team's needs." Custom iteration fields with break support allow lightweight sprint-like planning without committing to Scrum ceremony overhead.

The GitHub contributing guidelines docs confirm that `CONTRIBUTING.md` and issue templates are the trust infrastructure of a project — they reduce issue quality variance before code is written, they are surfaced in the Contributing tab and sidebar, and they reduce friction for both new and returning contributors.

**Minimum viable label taxonomy for this repo**:
- `type:` — `type:bug`, `type:feature`, `type:research`, `type:docs`, `type:chore`, `type:agent`
- `area:` — `area:agents`, `area:scripts`, `area:docs`, `area:ci`, `area:infra`
- `priority:` — `priority:high`, `priority:medium`, `priority:low`
- `status:` — `status:blocked`, `status:needs-review`, `status:good-first-issue`

---

### RQ2 — Small Team Topologies

**Hypothesis**: The Team Topologies four-type model applies to a 2–5 person + agent fleet; the human team is Stream-aligned and agents map onto Platform and Enabling types.

**Verdict**: CONFIRMED — with a precise mapping

**Evidence**: Team Topologies identifies four fundamental team types: Stream-aligned (delivers customer value directly), Platform (accelerates stream-aligned teams via internal services), Enabling (temporarily boosts capability, then moves on), and Complicated Subsystem (deep specialist knowledge, on-demand). Three interaction modes govern boundaries: Collaboration (high bandwidth, time-limited discovery), X-as-a-Service (clear API, minimal interaction), and Facilitation (temporary mentoring).

The nine principles reinforce what the agent fleet research already established: "Eliminate Team Dependencies — fix the handoffs, not just the teams." This maps directly to the Compression-on-Ascent / Focus-on-Descent handoff pattern. Handoff quality IS the team topology.

**Direct mapping for this repo**:

| Team Topologies type | Agent role |
|---|---|
| Stream-aligned | Human maintainers (own the product, drive direction) |
| Enabling | Executive agents (Researcher, Docs, Scripter) — task-scoped augmentation |
| Complicated Subsystem | Research Scout, Synthesizer, domain specialist agents |
| Platform | GitHub agent, Review agent — consumed X-as-a-Service |

Interaction mode guide: default to X-as-a-Service for any agent with a defined handoff contract. Switch to Collaboration only when discovering new capabilities or patterns (i.e., first run of a new workflow).

---

### RQ3 — Sprint vs. Kanban vs. Flow

**Hypothesis**: For an OSS project with irregular contributor cadence, Kanban continuous flow is a better fit than Scrum fixed sprints.

**Verdict**: CONFIRMED

**Evidence**: Atlassian's comparative analysis identifies the key structural difference: Scrum commits to a fixed increment within a sprint boundary and requires a Product Owner, Scrum Master, and development team with defined velocity. Kanban uses continuous flow, WIP limits, and visualised work states with no required roles. "Kanban is great for teams that have lots of incoming requests that vary in priority and size. Whereas scrum processes require high control over what is in scope, kanban lets you go with the flow."

Three structural reasons Scrum fails for this project: (1) agents are on-demand instances, not standing sprint team members with velocity; (2) work items span from 15-minute agent tasks to multi-day implementation arcs — sprint sizing is artificial; (3) research questions surface ad-hoc from issues, conflicting with sprint planning's assumption of a scoped, stable backlog.

Kanban WIP limits are directly applicable: no more than two active research tracks simultaneously prevents context switching and partial-completion waste. The existing scratchpad system (`.tmp/<branch>/`) is already a proto-Kanban work-in-progress externalisation — the missing piece is a board view in GitHub Projects.

**Scrumban consideration**: if the project acquires a regular release cadence, a Scrumban hybrid (Kanban day-to-day, retrospective per release milestone) is appropriate. Not warranted yet.

---

### RQ4 — Agent Fleet as PM Entity

**Hypothesis**: Agent fleet roles can be mapped to traditional PM contributor roles, enabling structured accountability.

**Verdict**: PARTIALLY CONFIRMED — mapping works; "RACI" over-bureaucratizes it

**Evidence**: The opensource.guide leadership-and-governance source identifies three OSS governance models: BDFL (one decision-maker), Meritocracy (voting by active contributors), and Liberal Contribution (most current work = most influence; consensus-seeking over voting). Liberal Contribution is the optimal model for an agent-augmented team: agents contribute in proportion to assigned work, human maintainers retain BDFL-level authority on direction, and no voting overhead is introduced.

**Practical PM role mapping**:

| PM role | Human/agent |
|---|---|
| Product owner / BDFL | Human maintainer(s) — final say on direction |
| Senior contributor | Executive agents — delegated authority within defined scope |
| Contributor | Specialist task agents — execute defined work units |
| Gatekeeper | Review agent — quality gate, not creative contributor |

Critical nuance: agents are not "team members" with persistent roles. They are **runtime instances of function contracts**. PM frameworks should define agent SLAs (e.g., "Research Scout returns ≤ 2,000 tokens within one session"), not assign agents to sprint teams.

---

### RQ5 — Roadmap and Milestone Patterns

**Hypothesis**: GitHub Milestones + `OPEN_RESEARCH.md` + `docs/plans/` is sufficient for long-horizon tracking at this scale; no external PM tools are warranted.

**Verdict**: CONFIRMED

**Evidence**: GitHub Projects (official docs) provides status updates (On Track / At Risk / Off Track), timeline/roadmap views, and iteration fields, all natively inside GitHub. "Share high-level overviews which people can use to determine the status of your project." This covers everything a standalone roadmap tool would provide.

The existing tracking infrastructure in this repo already implements a three-tier planning hierarchy that merely needs to be made explicit:

| Horizon | Tool | Scope |
|---|---|---|
| H3 (quarter+) | `OPEN_RESEARCH.md` + GitHub Milestones | Long-range goals, open research |
| H2 (weekly) | `docs/plans/YYYY-MM-DD-<slug>.md` | Multi-session workplans |
| H1 (session) | `.tmp/<branch>/<date>.md` | In-progress scratchpad |

The gap: GitHub Milestones are not currently being used. Creating one milestone per research sprint or per OPEN_RESEARCH domain would immediately surface completion progress without adding process overhead.

---

### RQ6 — Architecture Decision Records

**Hypothesis**: ADRs are worth implementing at this scale; a `docs/decisions/` directory with Markdown files is the minimal implementation.

**Verdict**: CONFIRMED — lightweight ADR practice is justified even at 2-person scale

**Evidence**: The ADR pattern (adr.github.io; Nygard format) captures decision, context, and consequences in ≤ 30 lines. Key value at small scale: preventing re-litigation of settled architectural choices as the team and agent fleet grows. Every new agent or contributor can absorb architectural intent without bespoke orientation. The cost of not maintaining ADRs is proportional to fleet size — it grows quadratically as agents multiply and forget prior context.

**Trigger threshold for this repo**: an ADR is warranted when a decision (a) has non-obvious tradeoffs, (b) is difficult to reverse, or (c) would be confusing to a future agent or contributor who encounters it without context.

**First three ADRs for this repo**:
1. Why `uv run` over `python` directly
2. Why scratchpad-per-session (`.tmp/`) over a persistent context store
3. Why `AGENTS.md` files over a single `copilot-instructions.md` system prompt

---

### RQ7 — Async Communication Patterns

**Hypothesis**: GitHub Issues + PRs is sufficient async communication infrastructure; no supplementary tools are required.

**Verdict**: MOSTLY CONFIRMED — one gap: GitHub Discussions for community Q&A

**Evidence**: The opensource.guide building-community source identifies the contributor funnel (Potential User → User → Contributor → Maintainer) and notes that friction at any funnel stage drives attrition. A Mozilla study cited confirms that code reviews within 48 hours have a significantly higher contributor return rate. Public communication infrastructure is not optional: "If you don't give people a public place to talk about your project, they will likely contact you directly — over time this exhausts maintainers."

Audit of current infrastructure:

| Communication type | Current state |
|---|---|
| Task tracking | GitHub Issues ✅ |
| Code/doc review | GitHub PRs ✅ |
| Contributor expectations | `CONTRIBUTING.md` ✅ |
| Community Q&A / discussion | Not yet enabled ❌ |
| Architecture/philosophy debates | No dedicated space ❌ |

GitHub Discussions covers both gaps at zero tooling cost. It is the correct low-complexity answer before the community grows to a scale where a forum or Discord would add more value.

---

## 3. Pattern Catalog

Six patterns extracted from the validation above, ranked by leverage for this project:

**P1 — Three-Tier Planning Hierarchy**
Horizon 1 (`.tmp/` scratchpad, session scope) → Horizon 2 (`docs/plans/`, workplan scope) → Horizon 3 (`OPEN_RESEARCH.md` + GitHub Milestones, quarter scope). Codify this stack explicitly in `AGENTS.md` under the "Agent Communication" section so all agents use the correct tier for each planning artifact.

**P2 — Labels Taxonomy as Machine-Parseable Triage**
`type:`, `area:`, `priority:`, `status:` prefixes create script-accessible issue metadata. Accessible via `gh issue list --label "area:agents"` in any agent session pre-warm. Encode in a `scripts/create_labels.py` script so the taxonomy is reproducible and self-documenting.

**P3 — Agent Fleet as Platform + Enabling Teams**
Model agents as Team Topologies Platform/Enabling team types, not as team members. Default interaction mode: X-as-a-Service (consume agent output via defined handoff contracts). Switch to Collaboration mode only when discovering new capabilities or patterns. This framing prevents the failure mode of "assigning" agents to sprints.

**P4 — Liberal Contribution + BDFL-Direction Hybrid**
Human maintainers hold BDFL authority on project direction; agents and contributors operate under liberal contribution (most current work = most influence). Document in `GOVERNANCE.md`. This resolves all ambiguity about who can override an agent's output without over-specifying the contribution model.

**P5 — ADRs as Forward Context for the Agent Fleet**
Document reversibility-significant architecture decisions in `docs/decisions/`. Target ≤ 30 lines per ADR using the Nygard format (Title, Status, Context, Decision, Consequences). Optimise for future agent readability: assume a future agent has no session context and must understand the decision from the ADR alone.

**P6 — Continuous Kanban with Milestone Retrospectives**
Visualise work in a GitHub Projects Kanban board. Enforce WIP limits (≤ 2 active research tracks, ≤ 3 open implementation PRs). Hold a retrospective at each milestone boundary rather than each sprint. Defer Scrumban hybrid until the project has a versioned release cadence.

---

## 4. Recommendations for This Repo

In priority order:

**R1 — Create GitHub Projects Kanban board** (30 min)
Add table + board views. Create custom fields: `Priority` (High / Medium / Low), `Area` (agents / scripts / docs / ci), `Type` (research / feature / bug / chore / agent). The board column structure: `Backlog → In Progress → Blocked → In Review → Done`.

**R2 — Apply structured labels taxonomy** (1 session)
Create label groups: `type:*`, `area:*`, `priority:*`, `status:*` as listed in RQ1 above. Write a `scripts/create_labels.py` script so the taxonomy is self-documenting and reproducible in any fork. Apply to all existing open issues.

**R3 — Add issue templates** (1 session)
Templates needed: Research (already exists), Feature Request, Bug Report, Agent Design. Each template should pre-populate a structured context block. Store in `.github/ISSUE_TEMPLATE/`. Link all templates from `CONTRIBUTING.md`.

**R4 — Create `docs/decisions/` with first three ADRs** (1 session per ADR)
Start with the three ADRs listed in RQ6. Use the Nygard format. Add a brief index to `README.md` or `docs/guides/` linking to the decision catalogue.

**R5 — Create `GOVERNANCE.md`** (1 session)
Cover: (a) decision authority (BDFL for direction, liberal contribution for execution), (b) agent fleet role classification using Team Topologies types, (c) path to maintainership, (d) tiebreaker process for contested decisions. Keep to ≤ 400 lines.

**R6 — Enable GitHub Discussions and activate GitHub Milestones** (30 min each)
Discussions: enable in repo settings, add a "Welcome" pinned post, link from README and CONTRIBUTING. Milestones: create one milestone per open research domain area (Horizons, Local Compute, etc.).

---

## 5. Open Questions

1. **GitHub Actions automation for Projects**: Can label-based GitHub Actions automate board column transitions (e.g., PR merged → close linked issue → move card to Done)? The GitHub Projects API supports this but the automation script does not exist yet. Scope for the automation sprint.

2. **Milestone cadence — time-boxed vs goal-boxed**: Goal-boxed milestones match OSS irregular contributor patterns better, but time-boxed milestones create useful forcing functions. Resolution: use goal-boxed milestones for research tracks (completed when deliverable ships) and time-boxed milestones for release-oriented work (if/when versioned releases begin).

3. **GOVERNANCE.md agent authority scope**: How explicitly should governance formalise agent authority boundaries? Over-specification risks the GOVERNANCE becoming stale as the fleet evolves. Recommended deferral: wait until the agent fleet has stabilised at ≥ 10 agents before codifying fine-grained authority boundaries.

4. **ADR tooling**: Plain Markdown in `docs/decisions/` is sufficient up to ~20 records. If the catalogue grows beyond that, `log4brains` or a GitHub-native ADR viewer script provides navigation. Not warranted yet.

5. **Agent "velocity" as a PM metric**: Is there value in tracking agent task completion rates across sessions (tasks per session, tokens per deliverable)? This could inform workplan scoping. The prerequisite is structured task logging — not yet implemented. Scope as a future `scripts/` addition.

---

## 6. Sources

- [GitHub: About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) — cached at `.cache/sources/docs-github-com-en-issues-planning-and-tracking-with-project.md`
- [GitHub: Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) — cached at `.cache/sources/docs-github-com-en-communities-setting-up-your-project-for-h.md`
- [Atlassian: Kanban vs. Scrum](https://www.atlassian.com/agile/kanban/kanban-vs-scrum) — cached at `.cache/sources/atlassian-com-agile-kanban-kanban-vs-scrum.md`
- [Team Topologies: Key Concepts](https://teamtopologies.com/key-concepts) — cached at `.cache/sources/teamtopologies-com-key-concepts.md`
- [Open Source Guide: Building Community](https://opensource.guide/building-community/) — cached at `.cache/sources/opensource-guide-building-community.md`
- [Open Source Guide: Leadership and Governance](https://opensource.guide/leadership-and-governance/) — cached at `.cache/sources/opensource-guide-leadership-and-governance.md`
- [ADR GitHub](https://adr.github.io/) — cached at `.cache/sources/adr-github-io.md` (empty; supplemented by domain expertise on Nygard ADR format)
- [Martinfowler: Architecture Decision Record](https://www.martinfowler.com/articles/adr.html) — HTTP 404; supplemented by domain expertise
- [Steve McConnell: Software Development Team Topologies](https://stevemcconnell.com/articles/software-development-team-topologies/) — HTTP 404; Team Topologies content sourced from teamtopologies.com directly
- Cross-reference: [`docs/research/agent-fleet-design-patterns.md`](agent-fleet-design-patterns.md) — Compression-on-Ascent / Focus-on-Descent findings apply directly to agent team topology mapping
