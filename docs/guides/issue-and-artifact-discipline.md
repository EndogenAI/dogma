# Issue & Artifact Discipline

## Overview

The Endogenic Development Methodology requires that **every knowledge artifact (agent, skill, script) is traceable to a decision point** — typically a GitHub issue that defines scope, acceptance criteria, and effort.

This guide documents the discipline that enables agents and skills to remain aligned with project governance (issues, milestones, labels) across sessions and team members.

---

## The Encoding Chain

```
GitHub Issue (source of truth)
  ↓ defines
Milestone assignment (issue labels: priority:, type:, area:, effort:)
  ↓ gates
Agent file / SKILL.md / Script (re-encodes the issue in knowledge artifact form)
  ↓ references
Agent Endogenous Sources section (declares defining issue, axiom, acceptance criteria)
  ↓ executes
Agent workflow steps (implement the issue's acceptance checklist)
  ↓ produces
Deliverable (committed files, closed issue, updated docs)
  ↓ closes
Issue (status updated, artifact committed, knowledge preserved)
```

**Key principle**: Knowledge artifacts are *not independent*. They are always traceable back to the project decision (GitHub issue) and forward to execution (agent workflow and completion criteria).

---

## Applied to Agent Files

### 1. GitHub Issue Definition

Every agent should correspond to a GitHub issue (or set of related issues) that defines:
- **Scope**: What the agent does and doesn't do
- **Acceptance criteria**: Numbered checklist of completed deliverables
- **Labels**: `type:`, `priority:`, `area:`, `effort:` (all required); `status:` if blocked
- **Milestone**: Which project phase (`Foundation`, `Wave 1` etc)

**Example issue body**:
```markdown
## Objective
Implement the Executive PM agent to maintain issues, milestones, and community health.

## Acceptance Criteria
- [ ] `executive-pm.agent.md` created with full Endogenous Sources section
- [ ] Agent reads GitHub issue definitions before acting (fetch-before-act)
- [ ] Handoff graph includes Review and GitHub agents
- [ ] Completion Criteria in agent match this issue's checklist
- [ ] Integrated into `.github/agents/README.md` fleet catalog
- [ ] CI passes: `validate_agent_files.py --all`

## Governi axiom
Endogenous-First — the agent reads project governance (issues, milestones, labels) before proposing any changes.
```

### 2. Agent Frontmatter (Governance Metadata)

Every `.agent.md` file should include optional governance fields:

```yaml
---
name: Executive PM
description: Maintain issues, labels, milestones, and community health...

# Governance metadata — map agent to project phase and effort
tier: Wave 1                    # Milestone this agent targets
effort: M                       # Effort estimate: small/medium/large/xlarge
status: active                  # active | beta | deprecated | blocked
area: agents                    # One of: agents | scripts | docs | ci | tests | deps | research
depends-on:                     # Other agents this must follow from
  - Review
  - GitHub
---
```

**Where to fill these in:**
- `tier`: The milestone the issue is assigned to
- `effort`: The issue's `effort:` label (s/m/l/xl)
- `status`: `active` unless the issue is blocked (then `blocked`)
- `area`: The issue's `area:` label
- `depends-on`: Which agents must run before this one (from Handoff graph and issue dependencies)

### 3. Agent Endogenous Sources Section (Required Issue Link)

The `## Endogenous Sources` section MUST reference:

```markdown
## Endogenous Sources

This agent is defined by:
- **Issue**: [#62 Implement Remaining Agent Skills](https://github.com/EndogenAI/Workflows/issues/62)
- **Milestone**: Wave 1: Agent Fleet Tier A+B
- **Labels**: type:feature, priority:high, area:agents
- **Governing axiom**: *Endogenous-First* (see [`MANIFESTO.md`](../../MANIFESTO.md))
- **Acceptance criteria**: See the linked issue checklist

[Read `AGENTS.md` before modifying this agent](../../AGENTS.md)
```

**What this encodes**:
1. **Traceability**: Anyone can find the defining issue immediately
2. **Governance alignment**: The agent's status is directly tied to issue progress
3. **Axiom grounding**: The agent's behavior is governed by a named foundational principle
4. **Completion definition**: The agent is "done" when the issue checklist is complete

### 4. Agent Completion Criteria (Mirror Issue Checklist)

The `## Completion Criteria` section should mirror the issue's acceptance checklist:

```markdown
## Completion Criteria

Deliverables match the acceptance criteria in [issue #62](https://github.com/EndogenAI/Workflows/issues/62):

- ✅ `executive-pm.agent.md` created with full Endogenous Sources section
- ✅ Agent reads GitHub issue definitions before acting
- ✅ Handoff graph complete (Review → GitHub)
- ✅ Completion Criteria in agent match issue checklist
- ✅ Integrated into `.github/agents/README.md` fleet catalog
- ✅ CI passes: `validate_agent_files.py --all`
```

**Why**: This creates a dual-audit: the issue checklist tracks progress for the team; the agent's Completion Criteria ensure the agent doesn't exceed its scope.

---

## Applied to SKILL.md Files

### 1. Skill Frontmatter (Governance Metadata)

Every `.github/skills/<name>/SKILL.md` should include:

```yaml
---
name: deep-research-sprint
description: Orchestrates research fleet...

# Governance metadata
tier: Foundation                    # Which milestone this skill applies to
type: research                      # Type: research | feature | scripting | automation | tooling | validation
effort: L                           # Effort for practitioner to execute: s/m/l/xl
applies-to:                         # Which agent roles use this skill
  - Executive Researcher
  - Research Scout
status: active                      # active | beta | deprecated | blocked
requires:                           # Other skills this depends on
  - name: source-caching
    description: "Must cache sources before scouting"
---
```

### 2. Skill Endogenous Sources (Pattern/Issue Reference)

```markdown
## Endogenous Sources

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md).

**Implements**: The research orchestration pattern from [issue #45 (Research: Product Definition)](https://github.com/EndogenAI/Workflows/issues/45)

**Used by**: Executive Researcher, Research Scout, Research Synthesizer, Research Reviewer, Research Archivist

**Foundation documents**:
- [`AGENTS.md`](../../../AGENTS.md) § Programmatic-First Principle
- [`docs/guides/deep-research.md`](../../../docs/guides/deep-research.md)
- [`docs/research/methodology-review.md`](../../../docs/research/methodology-review.md)
```

---

## Applied to Scripts

### Script Metadata (Docstring)

Every script in `scripts/` should open with a docstring that encodes:

```python
#!/usr/bin/env python3
"""scripts/my_script.py

Purpose:
    [What this script does — usually corresponding to a Programmatic-First need]

Inputs:
    --arg1     [Description]
    --arg2     [Description]

Outputs:
    [What the script produces or modifies]

Usage examples:
    uv run python scripts/my_script.py --arg1 value

Exit codes:
    0  Success
    1  [Failure condition]

Related issues:
    Issue #XX — [Why this script was created]
"""
```

**Where to reference**:
- The issue that motivated the script (Usually a Programmatic-First issue where a task was performed >2 times interactively)
- The milestone the script contributes to
- Dependencies on other scripts

---

## Milestone Structure

The five project milestones define when artifacts are created and their lifecycle:

| Milestone | Purpose | Artifacts Created |
|-----------|---------|-------------------|
| **Foundation: Endogenic Methodology** | Codify framework, research deliverables | Research syntheses, MANIFESTO updates, methodology docs |
| **Wave 1: Agent Fleet Tier A+B** | Specialist research + engineering agents | 11 agent files (Tier A+B), associated skills, scripts |
| **Wave 2: Agent Fleet Tier C+D** | Community + knowledge/governance agents | 8 agent files (Tier C+D), associated skills |
| **Adoption: Scripts & Tooling** | Onboarding, developer experience | Wizard scripts, adoption templates, contributor guides |
| **Hardening: Production Readiness** | Security, performance, CI gates | Security patches, new validation scripts, CI improvements |

**When authoring a new artifact**:
1. Create/reference the GitHub issue
2. Assign the issue to the relevant milestone
3. Apply `type:`, `priority:`, `area:` labels to the issue
4. Reference the milestone in the artifact's frontmatter (`tier:` field)
5. Link to the issue in the artifact's Endogenous Sources section

---

## Validation Checklist

Before committing any agent, skill, or script:

### For Agent Files

- ✅ GitHub issue exists and is assigned to a milestone
- ✅ Issue body includes acceptance criteria checklist
- ✅ Agent frontmatter includes `tier`, `effort`, `status`, `area` fields (or commented as TODO)
- ✅ Endogenous Sources section references the issue number and title
- ✅ Endogenous Sources declares the governing axiom
- ✅ Completion Criteria mirror the issue's acceptance checklist
- ✅ All paths to repo-root files use `../../` prefix
- ✅ No orphaned handoff routes
- ✅ `validate_agent_files.py .github/agents/<file>.agent.md` passes

### For SKILL.md Files

- ✅ Endogenous Sources references the pattern or issue this skill implements
- ✅ Frontmatter includes `tier`, `type`, `effort`, `applies-to`, `status` fields
- ✅ All paths to repo-root files use `../../../` prefix (not `../../`)
- ✅ Completion Criteria/Quality-Gate section is present
- ✅ No heredoc patterns in workflow steps

### For Scripts

- ✅ Docstring opens with Purpose, Inputs, Outputs, Usage, Exit codes
- ✅ Related GitHub issue referenced in docstring
- ✅ Tests exist and pass: `uv run pytest tests/test_<script_name>.py`
- ✅ Linted: `uv run ruff check scripts/<script_name>.py`

### For All Artifacts

- ✅ Cross-references to `MANIFESTO.md` or `AGENTS.md` present (encoding fidelity)
- ✅ No broken internal links
- ✅ No secrets or credentials embedded
- ✅ If issue is closed, artifact status field is `deprecated` or `archived`

---

## Discipline in Action: Example Workflow

**Scenario**: "We need a new agent to audit research documents."

### Step 1: Create GitHub Issue
```
Title: "Implement Docs Linter Agent"
Body: 
  - Objective: Audit docs/research/ for D4 compliance
  - Acceptance criteria: [checkbox list]
  - Issue labels: type:feature, priority:high, area:agents, effort:m
  - Milestone: Wave 1: Agent Fleet Tier A+B
```

### Step 2: Create Agent File

**Run scaffold**:
```bash
uv run python scripts/scaffold_agent.py --name "Docs Linter" ...
```

**Update frontmatter**:
```yaml
---
name: Docs Linter
description: Audit docs/research/ for D4 compliance...
tier: Wave 1                              # From milestone
effort: m                                 # From effort: label
status: active                            # New agent
area: agents
depends-on:
  - Review
  - GitHub
---
```

**Update Endogenous Sources**:
```markdown
## Endogenous Sources

This agent is defined by:
- **Issue**: [#XX Implement Docs Linter Agent](...)
- **Milestone**: Wave 1: Agent Fleet Tier A+B
- **Governing axiom**: *Algorithms Before Tokens* (automated compliance checks)
- **Acceptance criteria**: See issue #XX
```

### Step 3: Commit & Close Issue

When the agent is ready:
```bash
git add .github/agents/docs-linter.agent.md
git commit -m "feat(agents): implement Docs Linter agent for d4 synthesis audits

Closes #XX

- Agent audits docs/research/*.md against validation standards
- Referencing issue #XX acceptance criteria
- Integrated into fleet catalog README"

git push
```

Issue is closed; artifact remains in the codebase with complete traceability to the decision that created it.

---

## Benefits

This discipline provides:

1. **Traceability**: Every artifact can be traced back to the decision that created it
2. **Governance alignment**: Artifacts stay synchronized with project milestones and effort estimates
3. **Reusability**: Future teams can understand why an artifact exists and what it was intended to accomplish
4. **Audit trail**: Git history + issue history = complete record of decisions
5. **Reduced re-discovery**: New contributors can read the issue to understand context without asking
6. **Completion clarity**: Artifacts have explicit "done" definitions that match issue checklists

---

## References

- [`AGENTS.md`](../../AGENTS.md) — Agent fleet constraints and discipline
- [`.github/agents/AGENTS.md`](../../.github/agents/AGENTS.md) — Agent-specific governance
- [`.github/agents/README.md`](../../.github/agents/README.md) — Fleet catalog with milestone mapping
- [`docs/guides/agents.md`](./agents.md) — Agent authoring guide with issue linkage
- [`.github/skills/agent-file-authoring/SKILL.md`](../../.github/skills/agent-file-authoring/SKILL.md) — Skill authoring discipline
- [`.github/skills/skill-authoring/SKILL.md`](../../.github/skills/skill-authoring/SKILL.md) — SKILL.md-specific discipline
- [`docs/guides/github-workflow.md`](./github-workflow.md) — GitHub label and issue conventions
