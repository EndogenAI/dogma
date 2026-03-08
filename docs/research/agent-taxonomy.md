---
title: "Agent Taxonomy: Roles, Skills, and Fleet Constraints"
status: Final
---

# Agent Taxonomy: Roles, Skills, and Fleet Constraints

> **Status**: Final
> **Research Question**: What is the principled taxonomy of VS Code customization primitives — Roles (`.agent.md`; VS Code: Custom Agents), Agent Skills (`SKILL.md`), and fleet constraints (`AGENTS.md`) — and what decision rules govern what belongs where?
> **Date**: 2026-03-07
> **Branch**: `feature/skills-research-and-adaption`
> **Related**: [`AGENTS.md`](../../AGENTS.md) (guiding constraints), [`MANIFESTO.md`](../../MANIFESTO.md) (foundational axioms), [`ADR-006`](../decisions/ADR-006-agent-skills-adoption.md) (skills adoption), [`docs/research/agent-skills-integration.md`](./agent-skills-integration.md) (prior Phase 1 synthesis)

---

## Executive Summary

The VS Code customization stack has three first-class primitives with non-overlapping roles: **Roles** (`.agent.md`; VS Code: Custom Agents) encode *who does a task* — role-specific persona, posture, tool restrictions, and handoff graph; **Agent Skills** (`SKILL.md`) encode *how a task is done* — reusable workflow procedures and resources loadable on demand across any skills-compatible AI tool; and **fleet constraints** (`AGENTS.md`) encode *what all agents must do* — universal behaviours enforced across the entire fleet. The VS Code upstream term for `.agent.md` files is **"Custom Agents"** (since VS Code 1.106; previously "custom chat modes"); the EndogenAI project term is **"Roles"**, reflecting the conceptual purpose of these files as defined roles in the fleet. The boundary between these three layers has a precise formulation: role bodies retain only what is role-exclusive, while anything a second agent or non-VS-Code tool could use becomes a skill, and anything every agent must do goes into `AGENTS.md`. The central risk is **boundary erosion** — role bodies that accumulate skill-level procedures (too thick) or that delegate so much they lose distinct persona identity (too thin) — and this synthesis provides decision rules to prevent both failure modes. The prior Phase 1 synthesis ([`agent-skills-integration.md`](./agent-skills-integration.md)) established the composition rule; this document formalises the full three-way taxonomy with pattern catalogs and actionable decision trees.

---

## Hypothesis Validation

This section addresses the six research questions from the linked sprint.

---

### Q1 — Naming: "Roles" as the Endogenous Term

**Question**: Should we use "custom agents" (VS Code canonical) or an endogenous project term for `.agent.md` files?

**Evidence**:

- VS Code documentation (v1.106+) uses "custom agents" throughout: *"Custom agents enable you to configure the AI to adopt different personas tailored to specific development roles and tasks."* (`.cache/sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md`)
- Prior to VS Code 1.106, these were called "custom chat modes" — that term is now deprecated.
- The `.github/agents/AGENTS.md` now uses "Roles (`.agent.md` files — VS Code: Custom Agents)" as its governing description.
- `docs/guides/agents.md` opens with "Roles (`.agent.md` files — VS Code: Custom Agents)" — updated to align.
- Root `AGENTS.md` uses "agent" colloquially throughout but does not formally define the VS Code term; this is the only documentation gap.

**Verdict: DECIDED** — The project endogenous term is **Roles**. While VS Code uses "Custom Agents" as the upstream label for `.agent.md` files (since v1.106), EndogenAI uses "Roles" to emphasise the conceptual purpose — these files define *who does a task* and *what role they play* in the fleet. "Custom Agents" remains appropriate when referring specifically to the VS Code tooling mechanism. "Roles" is the canonical term in all EndogenAI project documentation.

**Mapping table** (VS Code canonical → EndogenAI endogenic usage):

| VS Code Term | EndogenAI Endogenic Usage | File Format |
|---|---|---|
| Custom Agent | **Role** / "agent" (informal shorthand) | `.agent.md` |
| Agent Skills | Agent Skills / "skill" (shorthand) | `SKILL.md` in `.github/skills/<name>/` |
| Custom instructions (always-on) | Fleet constraints / "AGENTS.md layer" | `AGENTS.md`, `.instructions.md`, `copilot-instructions.md` |
| Prompt files | Prompt files (not yet in active use) | `.prompt.md` |

---

### Q2 — Boundary: Role Body vs SKILL.md

**Question**: What is the principled line between what belongs in an `.agent.md` body vs a `SKILL.md`?

**Evidence**:

The VS Code customization overview provides the canonical distinction:

> *"Custom agents: Different tasks require different capabilities… Custom agents let you specify exactly which tools are available for each task."*
> *"Agent Skills: Teach specialized capabilities and workflows… Task-specific, loaded on-demand."*

ADR-006 formalised this for the EndogenAI fleet:

> *"Agents encode who does a task; skills encode how a task is done."*

The `session-management` SKILL.md itself demonstrates the pattern: it encodes a full lifecycle procedure (scratchpad init, encoding checkpoint, phase gate, session close) that every agent in the fleet benefits from — not just the Executive Orchestrator where the procedure was originally embedded.

The composition rule from ADR-006 is directional: *agents call skills; skills never call agents*. A skill that contains handoff logic, posture constraints, or tool invocation instructions has leaked agent-level concerns into skill-level content — a structural anti-pattern.

**Verdict: CONFIRMED** — The boundary is strategic vs tactical, not large vs small. The test is reusability across role boundaries, not content volume.

**Decision Rule**:

> Content belongs in the `.agent.md` body when it is *exclusively* about this agent's role: its persona statement, posture (what it can and cannot do), tool list, list of endogenous sources to read before acting, and the handoff graph. Content belongs in a `SKILL.md` when it describes how a task is performed and at least one other agent or AI tool (Copilot CLI, Claude Code) could benefit from that knowledge without needing this agent's posture or tool restrictions. If a procedure appears more than once across agent bodies, it must be extracted to a skill before the third copy is written — the Programmatic-First constraint from [`AGENTS.md`](../../AGENTS.md) applies to instruction prose, not only to shell scripts.

**Decision tree**:

```
Is this content exclusively about WHO does the task?
  │
  ├─ YES → Agent body
  │         (persona, posture, tool list, handoff graph,
  │          role-specific endogenous sources)
  │
  └─ NO → Is this about HOW a task is performed?
            │
            ├─ Could a different agent or tool use this? → SKILL.md
            │
            └─ Must every agent in the fleet do this? → AGENTS.md
```

---

### Q3 — Boundary: AGENTS.md vs Individual Agent File

**Question**: What belongs in fleet-level `AGENTS.md` vs an individual agent file? When should a constraint be universal vs per-role?

**Evidence**:

Root `AGENTS.md` currently contains:
- Programmatic-First principle (all agents)
- Commit discipline (all agents)
- Security guardrails (all agents)
- Async process handling (all agents)
- Agent communication protocol — `.tmp/` scratchpad (all agents)
- `When to Ask vs Proceed` policy (all agents)

Individual `.agent.md` files contain:
- YAML frontmatter (name, description, tools, handoffs) — role-specific
- Endogenous sources section — role-specific reading list
- Workflow steps — role-specific action sequence
- Role-specific guardrails — per-agent constraints beyond fleet defaults

The `.github/agents/AGENTS.md` sub-file narrows constraints further for the agent-authoring subdirectory: frontmatter schema, tool posture table, validation script usage. This is the correct pattern — subdirectory `AGENTS.md` files only *add* constraints, never override root.

**Verdict: CONFIRMED** — the AGENTS.md / agent file boundary maps cleanly to fleet-universal vs role-exclusive.

**Decision Rule**:

> A constraint belongs in root `AGENTS.md` when it must be honoured by every agent in every session regardless of role — including security guardrails, commit discipline, scratchpad protocol, and tool cost principles. It belongs in an individual `.agent.md` file when it applies only to that agent's specific role, posture, or workflow context. Subdirectory `AGENTS.md` files (e.g., `.github/agents/AGENTS.md`) occupy an intermediate tier: they encode constraints shared across all agents in that directory without being fleet-wide. The test: *if removing this constraint from a single agent file would create a policy gap, it belongs higher in the hierarchy.*

**Hierarchy summary**:

| Layer | Scope | Format | Content |
|---|---|---|---|
| `MANIFESTO.md` | All agents, all tools, all contributors | Constitution | Foundational axioms |
| Root `AGENTS.md` | All agents in the fleet | Operational constraints | Fleet-wide behaviours |
| Subdirectory `AGENTS.md` | Agents in that directory | Narrowed constraints | Directory-level rules |
| `.agent.md` | Single agent | Agent file | Role, posture, workflow, handoffs |
| `SKILL.md` | Any agent or tool that loads the skill | Skill file | How-to procedures |
| Session behaviour | This session | Context | Enacted output |

This six-layer encoding inheritance chain extends the five-layer chain in ADR-006 by making explicit the subdirectory AGENTS.md as a distinct intermediate tier — a practical necessity given that `.github/agents/AGENTS.md` carries specialized frontmatter schema rules not applicable fleet-wide.

---

### Q4 — Persona Drift: Too Thin vs Too Thick

**Question**: Is there a risk of agent files becoming too thin (everything delegated to skills) or too thick (duplicating skill content)? What is the right balance?

**Evidence**:

The `executive-docs.agent.md` representative sample shows the correct balance:
- Frontmatter: name, description, tools, handoffs — role-exclusive
- Endogenous Sources: specific reading list for the Docs role
- Documentation Scope: docs-specific content table — role-exclusive
- OSS Documentation Standards: guidelines derived from research — this is a *skill candidate* (any agent writing docs would benefit)
- Guardrails: docs-specific (extra caution on MANIFESTO.md) — role-exclusive

This agent is at moderate thickness. The OSS documentation standards section is the one area where a future `oss-docs-standards` skill would better house that content, but it is not yet duplicated across agents so extraction is not urgent per Programmatic-First.

**Verdict: CONFIRMED RISK** — both failure modes are real.

**Too-thin failure mode**: An agent file reduced to only frontmatter and "read AGENTS.md" contains no persona-specific knowledge. The agent becomes indistinguishable from a base chat session. Loss of effective posture enforcement and role-specific context causes behavioural drift — the same failure that skills are designed to prevent, but now at the agent layer.

**Too-thick failure mode**: An agent body that embeds multi-step workflow procedures (e.g., session start protocol, commit conventions) duplicates skill content, causing two maintenance locations for the same logic. After ADR-006 adoption, this is a lint-detectable violation: `validate_agent_files.py` should warn when agent body length exceeds a threshold AND a skill covering the same topic exists.

**The balance heuristic**: An agent file should contain enough per-role content that removing it would make the agent behaviorally generic. It should contain nothing that a second agent or tool also needs. In practice, a well-balanced agent body is typically 80–200 lines: frontmatter (15–30 lines) plus three to five sections (role statement, endogenous sources, workflow sketch, guardrails, handoffs).

---

### Q5 — Boundary: Skill vs Custom Instruction (AGENTS.md)

**Question**: When does a reusable workflow belong in a `SKILL.md` vs simply in `AGENTS.md` as a shared constraint?

**Evidence**:

VS Code documentation distinguishes:
- **Custom instructions** (always-on): *"Define coding standards and guidelines… Instructions only… Always applied."*
- **Agent Skills**: *"Teach specialized capabilities and workflows… Instructions, scripts, examples, and resources… Task-specific, loaded on-demand."*

Root `AGENTS.md` already follows this pattern correctly:
- The scratchpad *protocol rule* (`.tmp/` structure, append-only convention) is in `AGENTS.md` — it is a standard agents must follow.
- The scratchpad *procedure* (how to init, write Session Start, run prune_scratchpad.py) is in the `session-management` SKILL.md — it is an active workflow.

**Verdict: CONFIRMED** — the boundary is **standards vs procedures**.

**Decision Rule**:

> Content belongs in `AGENTS.md` when it is a rule or constraint: an obligation, permission, or prohibition that agents must observe passively (e.g., "never use heredocs for Markdown content", "always verify after remote writes"). Content belongs in a `SKILL.md` when it is a procedure: a sequence of steps that an agent actively executes to accomplish a goal, especially when those steps include script invocations, templates, or examples that cannot be expressed as a single-sentence rule. The test: *can this be stated as a constraint ("always X", "never Y") without losing meaning?* If yes, AGENTS.md. If it requires step-by-step elaboration or resource files, SKILL.md.

---

### Q6 — Pattern Catalog

See the [Pattern Catalog](#pattern-catalog) section below.

---

## Pattern Catalog

### Role (`.agent.md`) — Canonical Patterns

**Pattern CA-1: Minimal Valid Agent**

```yaml
---
name: My Specialist Agent
description: One sentence ≤ 200 chars describing the role.
tools:
  - search
  - read
handoffs:
  - label: Hand off to Review
    agent: Review
    prompt: "Task complete. Please review."
    send: false
---

You are the **My Specialist** for this project. Your mandate is...

## Endogenous Sources — Read Before Acting

1. [`AGENTS.md`](../../AGENTS.md) — fleet constraints that govern this agent.
2. [<role-specific source>](...) — why this source is read first.

## Workflow

...

## Guardrails

**Never do these without explicit instruction**:
- ...
```

**Pattern CA-2: Executive Agent with Handoff Chain**

Executive agents use `tools: [search, read, edit, execute, terminal, agent]` and define a delegation chain via handoffs that use `send: false` (takeback pattern — returns control to executive after each step).

**Pattern CA-3: Subdirectory Scope Narrowing**

Agents operating within a specific directory (e.g., agents that only write docs) include a **Documentation Scope** or equivalent table listing their exclusive file territory. Files outside that table require explicit escalation.

---

### Role — Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Multi-step workflow procedure in agent body** | Duplicable; not reusable; maintenance-heavy | Extract to `SKILL.md`, reference by description in agent |
| **Tool listed without a specific use** | Violates minimal-posture constraint from [`AGENTS.md`](../../AGENTS.md) | Remove; add only when a concrete step requires it |
| **No handoffs defined** | Agent has no delegation path; creates a dead-end | Add at least one handoff (typically to Review or GitHub) |
| **Posture creep: read-only agent with `execute`** | Breaks role isolation | Audit tool list against posture table in `.github/agents/AGENTS.md` |
| **Endogenous sources list > 10 items** | Agent tries to read too broadly before acting | Trim to the 3–5 most role-relevant sources |
| **Agent body > 400 lines of prose** | Likely contains skill-level content | Audit for extractable procedure blocks |

---

### Agent Skills (`SKILL.md`) — Canonical Patterns

**Pattern SK-1: Minimal Valid Skill**

```yaml
---
name: my-skill-name
description: |
  One sentence describing the skill. USE FOR: ... DO NOT USE FOR: ...
---

# My Skill

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../MANIFESTO.md).
It is governed by [`AGENTS.md`](../../AGENTS.md) § <relevant section>.

## 1. Step One

...

## 2. Step Two

...
```

**Pattern SK-2: Skill with Scripts**

When a skill requires shell execution, place scripts in `<skill-name>/scripts/` and reference them by relative path. The SKILL.md body instructs the agent to run the script; the script is loaded only when that step is reached (progressive disclosure).

**Pattern SK-3: Skill Description Framing**

The `description` field is the routing mechanism — the model loads the skill only when the request matches the description. Use the `USE FOR: / DO NOT USE FOR:` pattern (seen in `session-management`) to improve precision and reduce false-positive loading. Keep description ≤ 400 characters for fast metadata scanning.

---

### Agent Skills — Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Handoff logic in SKILL.md body** | Skills must not call agents | Move handoff instructions to the calling agent's body |
| **Posture constraint in SKILL.md** | Posture is an agent concern, not a skill concern | Move to `.agent.md` |
| **No cross-reference to `AGENTS.md` or `MANIFESTO.md`** | Breaks encoding inheritance chain | Add governing axiom citation in first substantive section |
| **Skill duplicates procedure already in agent body** | Two maintenance points | Deprecate agent body version; agent body should reference skill description |
| **Skill `name` field does not match directory name** | CI validation failure | Rename to match; enforce via `validate_agent_files.py --skills` |
| **Skill description is not task-specific** | Over-broad loading; context noise | Narrow description with concrete trigger conditions |

---

### Fleet Constraints (`AGENTS.md`) — Canonical Patterns

**Pattern FL-1: Universal Constraint Syntax**

Fleet constraints are expressed as obligation statements ("always X", "never Y") rather than procedural steps. Multi-step procedures belong in skills.

```markdown
## Guardrails

**Run these checks before every `git commit` / `git push`:**
<commands>

**Never do these without explicit instruction:**
- Edit any lockfile by hand
- Commit secrets, API keys, or credentials
```

**Pattern FL-2: Intermediate Tier (Subdirectory AGENTS.md)**

Subdirectory `AGENTS.md` files carry directory-local rules that (a) narrow root constraints and (b) are too specific for root AGENTS.md. They must open with an explicit statement that they derive from root `AGENTS.md` and do not contradict it. Example: `.github/agents/AGENTS.md` carries the frontmatter schema for agent files — specific enough to be irrelevant to non-agent directories, but universal enough to apply to all agent files.

---

### Fleet Constraints — Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Role-specific constraint in root AGENTS.md** | Pollutes fleet-wide namespace | Move to individual `.agent.md` guardrails section |
| **Procedure in AGENTS.md (step-by-step instructions)** | Should be a skill instead | Extract to SKILL.md; leave a one-sentence rule in AGENTS.md |
| **Convention documented only in root AGENTS.md but applicable to subdirectories** | Missed by agents operating under subdirectory scope | Propagate to all relevant AGENTS.md files in same commit (see Convention Propagation Rule in root AGENTS.md) |
| **New constraint added without updating all AGENTS.md files** | Encoding inconsistency | Run `find . -name 'AGENTS.md'` before committing any new universal constraint |

---

## Recommendations

**R1 — Canonical Name: Use 'Roles' for `.agent.md` files**

Adopt **'Roles'** as the endogenous project term for `.agent.md` files, reflecting the conceptual purpose of these files — they define *who does a task* and encode a specific role in the fleet. Use 'agent' as informal shorthand in prose. The VS Code upstream term 'Custom Agents' is appropriate when referring specifically to the tooling mechanism, but 'Roles' is the preferred term in EndogenAI documentation. Retire any residual 'custom chat mode' references (none currently found). The root `AGENTS.md` VS Code Customization Taxonomy table has been updated to list 'Roles' as the primitive, with a note that this maps to VS Code Custom Agents.

**R2 — Role Body vs SKILL.md: The Two-Test Rule**

Apply these two tests in order:

1. *Reuse test*: Can a different agent or non-VS-Code tool (Copilot CLI, Claude Code) benefit from this content without needing this agent's posture or tool restrictions? If yes → extract to SKILL.md.
2. *Frequency test*: Does essentially the same procedure appear in two or more agent bodies? If yes → extract to SKILL.md before writing a third copy (Programmatic-First from [`AGENTS.md`](../../AGENTS.md)).

Agent bodies that pass both tests (content is role-exclusive AND not repeated) stay in the agent. Everything else is a skill candidate.

**R3 — AGENTS.md vs Agent File: The Scope Test**

Ask: *Would a constraint violation in one agent represent a policy gap, or a local deviation?* If it would represent a policy gap (security, commit discipline, scratchpad protocol), the constraint belongs in root `AGENTS.md`. If it represents a local deviation from role-appropriate behaviour, it belongs in the individual agent file. Subdirectory `AGENTS.md` files are the correct location for directory-scoped schema rules (e.g., frontmatter format for all agents) that are universal within the directory but not fleet-wide.

**R4 — Persona Balance: The 80–200 Line Heuristic**

Agent bodies should be 80–200 lines (excluding frontmatter). Below 80 lines: too thin — the agent likely lacks enough role-specific context to behave distinctively. Above 200 lines of prose: likely too thick — audit for extractable skill candidates. Extend `validate_agent_files.py` with a `--warn-thin` and `--warn-thick` flag to surface both risks at CI time. Threshold values should start conservative (warn-thin: < 60 lines; warn-thick: > 300 lines) and be calibrated by fleet experience.

**R5 — AGENTS.md vs Skill: The Rule/Procedure Test**

If the content can be stated as a single compliance rule ("always X", "never Y") without losing actionable meaning → AGENTS.md constraint. If it requires sequential steps, script invocations, templates, or examples to be actionable → SKILL.md procedure. Apply this test to existing AGENTS.md content as the skills layer matures: long procedural blocks in AGENTS.md (e.g., the scratchpad size guard and archive convention) are candidates for migration to the `session-management` skill, leaving only the one-sentence rule in AGENTS.md.

**R6 — Rename/Refactor Implications**

No file renames are required to implement these recommendations. The following documentation updates are recommended for the Executive Docs agent as Phase 2:

1. Root `AGENTS.md` § Fleet Overview: updated VS Code Customization Taxonomy table with 'Roles' as the primitive and the six-layer encoding chain (see Q3 above)
2. `docs/guides/agents.md`: updated to use 'Roles (VS Code: Custom Agents)' in first paragraph
3. `.github/agents/AGENTS.md`: Naming Conventions section updated to 'Roles' as canonical; VS Code Custom Agents noted
4. `docs/decisions/ADR-006-agent-skills-adoption.md`: updated to 'Roles'; six-layer chain confirmed consistent

---

## Sources

### Cached External Sources (read via `read_file`, not re-fetched)

1. **VS Code Custom Agents documentation** (v1.106+)
   Path: `.cache/sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md`
   Key data: "custom agents" canonical name, persona/role definition, handoff mechanism, comparison to built-in agents.

2. **VS Code Agent Skills documentation**
   Path: `.cache/sources/code-visualstudio-com-docs-copilot-customization-agent-skill.md`
   Key data: skills vs custom instructions comparison table, `SKILL.md` format, on-demand loading, portability.

3. **VS Code Customization Overview**
   Path: `.cache/sources/code-visualstudio-com-docs-copilot-customization-overview.md`
   Key data: Quick reference table mapping goal → customization type → activation trigger.

4. **agentskills.io specification**
   Path: `.cache/sources/agentskills-io-specification.md`
   Key data: Canonical SKILL.md directory structure, required frontmatter fields (name, description), optional sub-directories (scripts/, references/, assets/).

### Endogenous Sources

5. **[`AGENTS.md`](../../AGENTS.md)** (root) — fleet constraints; Programmatic-First, commit discipline, security guardrails, scratchpad protocol. Cited as governing constraint throughout.

6. **[`MANIFESTO.md`](../../MANIFESTO.md)** — foundational axioms; Endogenous-First, Algorithms Before Tokens, Local Compute-First. Referenced in skills encoding inheritance requirement.

7. **[`docs/research/agent-skills-integration.md`](./agent-skills-integration.md)** — prior Phase 1 synthesis establishing the composition rule (agents = *who*, skills = *how*) and confirming cross-agent portability. This document extends rather than repeats that synthesis.

8. **[`docs/decisions/ADR-006-agent-skills-adoption.md`](../decisions/ADR-006-agent-skills-adoption.md)** — decision record for skills adoption; encoding inheritance five-layer chain; Tier 1 skills; CI validation requirements.

9. **[`docs/guides/agents.md`](../guides/agents.md)** — current agent guide; posture table, handoff patterns, agent selection table. Confirmed "custom agents" terminology already in use.

10. **[`.github/agents/AGENTS.md`](../../.github/agents/AGENTS.md)** — agent-authoring conventions; frontmatter schema, posture-to-toolset table, validation script.

11. **[`.github/agents/executive-docs.agent.md`](../../.github/agents/executive-docs.agent.md)** — representative agent file; confirmed correct balance of role-exclusive content vs skill candidates.

12. **[`.github/skills/session-management/SKILL.md`](../../.github/skills/session-management/SKILL.md)** — representative skill file; confirmed correct skill structure, AGENTS.md cross-reference in first section, procedure-not-rule content type.
