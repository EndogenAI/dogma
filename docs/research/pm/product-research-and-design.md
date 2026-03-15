---
title: "Product Research and Design Methodologies"
research_issue: "#20"
status: Final
date: 2026-03-07
closes_issue: 20
sources:
  - .cache/sources/nngroup-com-articles-design-thinking.md
  - .cache/sources/ideou-com-blogs-inspiration-what-is-design-thinking.md
---

# Product Research and Design Methodologies

> **Status**: Final (seed pass)
> **Research Question**: How do product research and design methodologies — JTBD, design thinking, user research, and rapid prototyping — apply to an AI-agent-augmented OSS tooling project?
> **Date**: 2026-03-07

---

## 1. Executive Summary

This is a seed pass across five domains of product research and design methodology — Jobs-to-be-Done (JTBD), design thinking, user research, LLM-era prototyping, and OSS product sense — surveying applicability to an AI-agent-augmented open-source tooling project. The scope is deliberately wide over deep: the goal is landscape orientation and identification of the most applicable concepts, not exhaustive treatment of any single domain.

Two primary sources were cached (NNGroup's "Design Thinking 101" and IDEO's "What is Design Thinking?"), supplemented by domain knowledge of JTBD theory, OSS product patterns, and LLM prototyping practice. The three highest-leverage insights are: (1) JTBD's progress-based framing applies to agents as consumers of tools, not just humans; (2) design thinking's prototyping phases now compress dramatically with LLMs, eliminating the traditional fidelity gradient; and (3) GitHub Issues and Discussions are the de facto user research infrastructure for OSS projects and should be treated as a structured, agent-parseable feedback corpus.

For a project at this stage — documentation-only, no released artifact, agent fleet in progress — the highest-value interventions are: clarifying the "job" each agent and script is hired to do, adopting a README-driven development posture for new tools, and treating GitHub Discussions as the primary user feedback channel rather than an informal side-channel.

---

## 2. Hypothesis Validation

Six seed-pass hypotheses were submitted for validation against primary sources and domain reasoning. All six are confirmed with varying degrees of nuance.

### H1 — JTBD reframes the unit of design from "user" to "progress"

**Hypothesis**: The JTBD framework is applicable to tool design for AI agents, not just human product users.

**Verdict**: CONFIRMED

Jobs-to-be-Done theory (Christensen, Moesta) defines a "job" as the progress a system or person is trying to make in a specific circumstance. The unit of design is not a user persona — it is the desired state transition: *from struggling with X, toward achieving Y, in context Z*. Applied to this repo, the primary human job is: "help me run a research or coding session with AI agents without losing context or repeating myself." Secondary jobs are discrete and tool-scoped: "validate my synthesis before committing," "scaffold a new agent without making structural errors," "archive a session without manual cleanup."

The key insight: **agents themselves have JTBD jobs**. `fetch_source.py` is hired to do: "get me a distilled readable article without opening a browser." `validate_synthesis.py` is hired to do: "catch quality failures before they reach the repo." JTBD applied to agent-tool design produces cleaner, more focused script interfaces than persona-based user stories — it eliminates scope ambiguity by forcing a single primary progress unit per tool.

### H2 — Design thinking adapts to agentic products by extending "empathy" to agent constraints

**Hypothesis**: Design thinking's human-centred core requires meaningful adaptation when the product's consumers include AI agents.

**Verdict**: CONFIRMED WITH EXTENSION

Design thinking's canonical Empathize → Define → Ideate → Prototype → Test → Implement cycle (NNGroup) applies cleanly to product decisions in this repo. The required adaptation: the Empathize phase must account for two distinct consumer types — the human operator and the agent using the tool. Agents have different constraints than humans: they cannot interact with a browser UI, they consume text tokens, they are sensitive to ambiguous instructions, and they fail silently in ways humans do not.

IDEO's desirability/feasibility/viability/responsibility lens extends correctly with two agent-specific additions: **legibility** (can the agent parse the tool's output without additional transformation?) and **idempotency** (can the agent call the tool twice without side effects?). These two constraints should become default checklist items in any design review for scripts — they are the agent-native equivalent of "is this UI discoverable?"

### H3 — Lightweight user research is feasible and partially automatable for small OSS teams

**Hypothesis**: A 2–5 person OSS team without a CS function can conduct meaningful user research using GitHub-native methods.

**Verdict**: CONFIRMED

Viable methods in order of effort: (1) **issue analysis** — mine closed issues for recurring complaints and failed use cases; (2) **fork archaeology** — examine how forkers modify the repo to infer unmet needs; (3) **async Discussion threads** — structured Q&A with contributors as interview substitutes; (4) **reference-count tracking** — which guides and agent files are cited most often reveals revealed importance.

Key multiplier: an agent can perform the issue synthesis step. A User Research Agent reading all closed `type:feedback` issues and outputting a structured JTBD summary compresses weeks of manual analysis into a single session — the endogenous answer to the absence of a CS team. This is worth prototyping once the label taxonomy from `pm-and-team-structures.md` R1 is in place.

### H4 — LLM-era prototyping collapses the fidelity gradient

**Hypothesis**: LLMs eliminate the traditional sketch-to-working-prototype fidelity sequence.

**Verdict**: CONFIRMED

Traditional prototyping follows a fidelity sequence: sketch → wireframe → mockup → working prototype. LLMs collapse this gradient entirely. A system prompt is a prototype. A working agent file is simultaneously the lowest-fidelity concept (a paragraph of instructions) and the highest-fidelity executable artifact. The Ideate → Prototype → Test cycle now runs in minutes, not days.

For this repo, *vibe-coding* — iterating on agent behaviour by prompting and observing output — is already the de facto practice. The gap is capture: when effective prompt patterns are discovered, the learning rarely makes it back into the agent file. A "prompt archaeology" practice — periodically reviewing session histories and encoding working patterns into `.agent.md` `<examples>` blocks — would close this feedback loop.

### H5 — "Product" for an OSS tooling project means developer experience, not features

**Hypothesis**: Success metrics should be DX-oriented, not feature-count or vanity-metric oriented.

**Verdict**: CONFIRMED WITH REFRAME

For this repo, "product" is the experience of a developer or agent picking up the repo and making measurable progress within 10 minutes. Two user types have overlapping needs: (1) **developers** adopting or adapting the workflow system; (2) **agents** (Copilot and similar) that parse documentation and agent files as context. Both need clear, self-contained, discoverable documentation with accurate current examples.

Actionable DX signals requiring no external tooling: Can a new contributor run `scaffold_agent.py` successfully without reading more than one document? Can Copilot correctly invoke `validate_synthesis.py` without human correction? These are measurable quality signals derivable from issue triage and session retrospectives.

### H6 — OSS feedback loops must be deliberately architected

**Hypothesis**: Without designed feedback channels, OSS feedback is sparse and biased toward high-opinion contributors.

**Verdict**: CONFIRMED

OSS projects that do not deliberately design feedback channels collect signal only from contributors with strong enough opinions to open issues unprompted. Viable infrastructure for this repo: (1) a pinned GitHub Discussion with JTBD-style problem framing ("I was trying to… I expected… Instead…"); (2) issue templates that surface intent, not just symptoms; (3) periodic agent-assisted synthesis of closed `type:feedback` issues into a "user insights" summary.

Telemetry is inappropriate at this stage (privacy overhead, no established user base) but should be re-evaluated when the repo gains external contributors. Any future telemetry must be opt-in, script-local, and produce structured logs parseable by a research agent.

---

## 3. Pattern Catalog

Reusable patterns derived from this seed pass, applicable directly to this repo. Each pattern is named, described with a trigger condition, and annotations showing when to apply it. These patterns are not aspirational — they are ready to implement now.

For agent authors and script contributors, patterns H2-derived (legibility/idempotency) should be treated as non-negotiable gates rather than suggestions.

**JTBD Job Statement per Script** — Each script in `scripts/README.md` carries a one-line job statement: "Hired to do: [progress verb] [object] [in context]." Forces single-purpose scope and makes design review language concrete. Applied at authoring time.

**Agent Design Checklist — Legibility and Idempotency** — Any script destined for agent invocation is evaluated against: (1) output legibility without transformation; (2) side-effect safety on repeated calls. Documented in `CONTRIBUTING.md`; applied at PR review time.

**README-Driven Script Development** — Write the `scripts/README.md` entry before writing the code. Forces upfront job clarity, prevents goldplating, aligns with the Documentation-First constraint in `AGENTS.md`. Applied at task-start time.

**Prompt Archaeology Session** — Periodic review of session histories that extracts effective prompt patterns and encodes them into the relevant `.agent.md` `<examples>` block. Prevents capability regression. Cadence: monthly or post-sprint.

**Quarterly Issue Synthesis Run** — A Research Scout pass at the start of each quarter over all closed issues and discussions, committing a structured JTBD summary to `docs/research/`. Replaces a CS team for OSS purposes with zero user-facing overhead.

**How-Might-We Framing for Agent Capability Design** — Before designing or extending an agent's capability, frame the question as: "How might we help [user type] [make progress] when [context]?" Borrowed from IDEO design thinking; prevents capability creep and reduces scope drift in agent files.

---

## 4. Recommendations for this Repo

Six actionable recommendations ordered by implementation complexity, from lowest-effort convention changes (R1–R2) to recurring process changes (R5–R6). All six are feasible without new tooling.

**R1 — Add a JTBD job statement to each script entry in `scripts/README.md`**
One line per script: "Hired to do: [progress verb] [object] [in context]." Grounds each tool in user intent; creates a shared vocabulary for scope discussions and design reviews.

**R2 — Add legibility and idempotency checklist items to `CONTRIBUTING.md`**
Two additional questions in the script PR review checklist. Takes one edit; prevents a class of agent-incompatibility defects before they reach production.

**R3 — Create a pinned GitHub Discussion: "Friction & Feature Requests"**
With explicit JTBD problem framing in the opening post. Link from `README.md` and `CONTRIBUTING.md`. Minimum viable user research infrastructure for the current stage.

**R4 — Adopt README-driven development for new tools**
Write the `scripts/README.md` section for a new script before writing the code. Zero-overhead convention change that forces upfront clarity on scope. Aligns with the Documentation-First constraint in `AGENTS.md`.

**R5 — Implement prompt archaeology as a post-sprint ritual**
After each agent development sprint, review session scratchpads for effective prompt patterns and encode them into `.agent.md` `<examples>` blocks. Prevents regression; accumulates capability over time.

**R6 — Schedule a quarterly "voice of the user" synthesis run**
Run a Research Scout pass over all closed issues and discussions at the start of each quarter; commit the JTBD summary to `docs/research/`. Delivers comparable product insight to telemetry with zero privacy implications.

The six recommendations above together constitute a lightweight product practice for an OSS tooling project — achievable within a single sprint, no external tooling required.

---

## 5. Open Questions

Four areas identified as warranting a full research sprint, not resolvable within this seed pass. Each maps to a potential research issue.

**OQ1 — How do JTBD switch interview techniques translate to async OSS interaction?**
Bob Moesta's "Switch Interviews" are synchronous and conversational. Async OSS equivalents haven't been formalized. A sprint could produce an issue template that elicits job-narrative responses at contribution time.

**OQ2 — Can an agent reliably perform JTBD analysis on a corpus of GitHub issues?**
A User Research Agent reading closed issues and outputting structured JTBD analysis is plausible. Accuracy and reliability are unknown. Warrants a prototype sprint once the label taxonomy is in place.

**OQ3 — What does "agent UX" look like as a formal design discipline?**
When the primary consumer of a tool is another agent, traditional UX heuristics (discoverability, learnability, error recovery) require restatement in agent-native terms. No consensus framework exists — this repo is positioned to contribute a working definition.

**OQ4 — How does design thinking's Test phase adapt to non-deterministic LLM output?**
Testing a prompt-based system involves token cost, temperature, and run-to-run variance absent from traditional usability testing. A systematic evaluation methodology for agent output quality warrants a full sprint.

**OQ5 — What is the right product feedback cadence for an OSS agent-fleet project?**
Quarterly synthesis may be too infrequent during early adoption; too frequent invites noise. Optimal cadence is unknown and likely depends on issue volume and contributor activity. Warrants data once the label taxonomy and Discussion channel are in place.

---

## 6. Sources

Two primary sources cached locally; three domain-knowledge references; one cross-reference to an adjacent synthesis in this repo.

- NNGroup, "Design Thinking 101" (Sarah Gibbons, July 2016): `.cache/sources/nngroup-com-articles-design-thinking.md`
- IDEO, "What is Design Thinking & Why Is It Beneficial?" (updated March 2025): `.cache/sources/ideou-com-blogs-inspiration-what-is-design-thinking.md`
- Christensen, Clayton M. et al. *Competing Against Luck* (2016) — JTBD core theory (domain knowledge)
- Moesta, Bob. *Demand-Side Sales 101* (2020) — Switch Interviews and JTBD application (domain knowledge)
- Cross-reference: `docs/research/pm-and-team-structures.md` — issue taxonomy and GitHub Projects recommendations
- Cross-reference: `docs/research/agentic-research-flows.md` — agent delegation and orchestration patterns
