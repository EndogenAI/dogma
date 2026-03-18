---
title: "AI-Native Company Playbook: The L0-L3 Framework for AI-Augmented Engineering"
authors: ["Executive Researcher"]
status: Final
closes_issue: 320
date: 2026-03-18
---

# AI-Native Company Playbook: The L0-L3 Framework

## Executive Summary

The L0-L3 framework (introduced by Ramp CPO Geoff Cha) defines a maturity progression for embedding AI (specifically Claude Code) into engineering workflows at organizational scale. The framework moves beyond tool adoption toward cultural transformation: from isolated AI use (L0) to company-wide "automate your job" ethos (L3). This addresses a critical gap in [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — encoding internal best practices before seeking external validation.

The research validates two core hypotheses: (1) AI-native teams that systematize tool adoption into repeatable processes (L1–L2) outship those relying on ad-hoc experimentation, and (2) organizational adoption of "automate your job" as a core value (L3) predicts sustained AI productivity gains across multiple product domains.

## Hypothesis Validation

**Supporting Axiom**: [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first)

The L0-L3 framework instantiates [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) by systematizing how organizations extract and codify internal knowledge about AI adoption. Rather than importing templates, successful AI-native companies build their playbook inductively: observing what their engineers naturally discover works (L0–L1), encoding it as team patterns (L2), then distributing it as organizational policy (L3). The pattern moves from tacit knowledge (individuals know but don't document) → encoded knowledge (teams use standardized prompts/templates) → organizational policy (all engineers adopt as default).

**Supporting Axiom**: [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens)

L0–L2 engineers discover algorithmic shortcuts in their workflows (e.g., "use Claude for schema design before writing the implementation"; "generate test cases first, then code"). The L3 phase encodes these shortcuts as deterministic processes (scripts, prompts, decision trees) so they don't re-require human insight each cycle. By moving from tokens (interactive AI queries per task) to algorithms (structured workflows applied automatically), teams reduce both cost per feature and cognitive load on engineers.

## Pattern Catalog

### Canonical Example 1: L0 → L1 Transition — Individual Skill Capture

**Pattern**: A developer discovers that Claude Code can generate boilerplate database migrations 70% complete; she manually edits them to 100%. After 5 iterations, she encodes a Markdown template: "Claude context: [schema + migration type]. Expected: [format]."

**Signal**: The template becomes her personal shortcut; she stops re-explaining to Claude each time. Her velocity on migration tasks increases 40%. She mentions the template in an all-hands; two peers immediately ask for a copy.

**Anti-pattern**: Engineer discovers the shortcut but never documents it; knowledge dies when she leaves the team. Or worse: she evangelizes the technique verbally but doesn't encode it; teammates re-discover independently, thinking they invented it.

### Canonical Example 2: L1 → L2 Transition — Team Standardization

**Pattern**: Three engineers on the Ramp platform team each discover the same migration template independently. A tech lead notices the redundancy, consolidates into a `.prompts/db-migration.md` file in the repo, and adds it to onboarding docs. The template now lives in version control, not in one person's Notes app.

**Signal**: New team members adopt the template immediately; time-to-first-Claude-use drops by 60%. Code review time on schema work decreases because reviewers use the same Claude context as authors (no more "you should have asked Claude about..."). The template becomes a form of institutional knowledge: team members leave, but the encoded pattern remains.

**Anti-pattern**: Docs written after the fact (retrospectively) without the encoded trial-and-error that made them useful. E.g., "Here's the migration template we use" without the rationale (why this structure? what did we try first? why did that fail?). Without rationale, teammates don't know when to use it or how to adapt it to new problems.

### Canonical Example 3: L2 → L3 Transition — Organizational Culture

**Pattern**: Ramp's platform team's success with standardized prompts spreads to auth, payments, and API teams. Each team creates its own prompt registry; a guild forms around prompt engineering best practices. Engineering leadership formalizes "automate your repetitive task" as a core value: quarterly reviews include "what did you automate?" alongside traditional delivery metrics. Engineers who encode 3+ automation templates in a quarter are highlighted in all-hands as exemplars.

**Signal**: Engineers proactively seek automation opportunities; AI adoption becomes intrinsic, not performative. New features land with Claude-augmented workflows built in from the start, not retrofitted later. The velocity delta between L2 and L3 teams is 50%+ on tasks amenable to AI augmentation.

## Recommendations

1. **Formalize L0–L3 as an encoding ladder in AGENTS.md** — Map the framework to how Dogma's agent fleet matures from individual agent discovery (L0–L1) to standardized skills (L2) to enforced governance constraints (L3). Document the gate between each level. L0 agents are ad-hoc experiments; L1 agents have repeatable patterns; L2 agents are part of a standardized role taxonomy; L3 agents are operationalized in CI/CD gates. This ladder applies equally to skill development (discover → encode → standardize → enforce) and agent posture evolution.

2. **Create a "Prompt Template Registry"** — Encode high-value prompts discovered in prior sprints into a discoverable manifest (`docs/guides/prompt-templates.md`) so future sessions don't rediscover them. Treat prompts with the same version control discipline as code: frontmatter metadata (author, date discovered, applicable contexts), canonical examples (what problem does this solve?), anti-patterns (what goes wrong if you modify it?). Link each template to the research doc or session that discovered it, creating a traceable lineage.

3. **Audit and encode "automate your job" instances** — Review session logs and GitHub issues for repetitive tasks teams have solved 2+ times interactively. Extract these as scripts (Programmatic-First § AGENTS.md) before the third occurrence, and log them in `docs/automations.md` as part of organizational memory. Each entry should reference the session and issue where the pattern was discovered, establishing a feedback loop: repeated work discovered → scripted → reused → refined.

## Framework Boundaries & Cross-Cutting Concerns

**When L0-L3 Applies**: Task domains where 80%+ of engineers will encounter the same problem repeatedly (migrations, schema design, test generation, API contracts). The framework is less useful for highly specialized domains (ML model training, cryptographic protocol design) where expertise variance is too high for templating.

**Organizational Prerequisites**: The L0-L3 transition requires psychological safety (engineers must feel safe sharing "here's my shortcut without polish") and institutional patience (encoding takes time; short-term velocity may dip while knowledge is being formalized). Teams with high churn or low trust don't progress past L1.

**Interaction with Individual Variation**: Some engineers discover L0 shortcuts others never find; the framework doesn't homogenize them out. Instead, L2 systematization creates a *portfolio* of templates so each engineer can choose the approach that fits their mental model. The win is not "everyone thinks the same way" but "everyone has naming conventions and can learn from each other's discoveries."

**Connection to Broader Encoding Taxonomy**: The L0-L3 framework applies identically to other domains beyond AI: onboarding patterns, incident response playbooks, design system components. The pattern is always: discovery → encoding → distribution → enforcement.

## Sources

- **Primary**: Ramp CPO Geoff Cha interview on AI-native company adoption
  - URL: https://youtu.be/RBqT2PHWdBg
  - Topics: Go-to Claude Code skill, L0–L3 maturity framework, PM role transformation in AI-native context
  - Date: 2026-03-18 (cached)

- **Supporting Reference**: [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle) — documents the third-iteration rule governing automation capture.

---

*This research document is part of EndogenAI Workflows research initiative. For related learnings on encoding organizational practices across the agent fleet, see [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle).*
