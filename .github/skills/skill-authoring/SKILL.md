---
name: skill-authoring
description: |
  Encodes conventions for authoring SKILL.md files in .github/skills/<name>/: YAML frontmatter, required headings, issue linkage, governance metadata, and CI validation. USE FOR: creating or modifying reusable domain-specific skills; understanding skill vs agent distinction; packaging procedural knowledge for cross-agent use. DO NOT USE FOR: agent file authoring (use agent-file-authoring skill); creating new agents (use that skill first); general VS Code settings questions.
argument-hint: "skill name slug (e.g. deep-research-sprint)"
---

# SKILL.md Authoring

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): skills are re-encodings of documented procedures and patterns from [`AGENTS.md`](../../../AGENTS.md), not independent inventions.

Skills are tactical-layer knowledge artifacts that encode *how a task is done*. They sit beneath agents (who encode *who does a task*) and above session behavior.

---

## 1. File Naming and Location

- **Location**: `.github/skills/<skill-name>/SKILL.md`
- **Slug format**: kebab-case, lowercase, e.g. `deep-research-sprint`, `pr-review-reply`, `session-management`
- **One skill per domain** — do not combine multiple domain procedures into a single skill file

To create a new skill, create the directory `.github/skills/<skill-name>/` and add a `SKILL.md` file.
You can copy an existing `SKILL.md` as a starting point — for example:

```bash
cp .github/skills/source-caching/SKILL.md .github/skills/<skill-name>/SKILL.md
```

Then update the frontmatter and sections according to the conventions in this document.

---

## 2. YAML Frontmatter

Every skill file must open with YAML frontmatter:

```yaml
---
name: <skill name in kebab-case>
description: |
  <Clear description of what this skill encodes — ≥25 characters>
  USE FOR: [bullet list of appropriate use cases]
  DO NOT USE FOR: [bullet list of what this skill explicitly excludes]
argument-hint: "usage hint shown in chat input box"
---
```

**Field requirements**:

| Field | Required | Constraint |
|-------|---------|------------|
| `name` | Yes | Kebab-case, lowercase |
| `description` | Yes | ≥ 25 characters, includes USE FOR / DO NOT USE FOR |
| `argument-hint` | Optional | Brief input suggestion for the user |

**Discipline fields** (encode project governance):

```yaml
---
name: deep-research-sprint
description: "Orchestrates ..."

# Optional — encode milestone/effort/applicability
tier: Foundation                          # Which milestone this skill applies to
type: research                            # Type: research | feature | scripting | automation | tooling | validation
effort: L                                 # Effort for practitioner to execute: s/m/l/xl
applies-to:                               # Which agent roles use this skill
  - Executive Researcher
  - Research Scout
status: active                            # Status: active | beta | deprecated | blocked
requires:                                 # Dependencies on other skills or tools
  - name: source-caching
    description: "Must cache sources before scouting"
---
```

---

## 3. Required Sections

Every skill file must contain at least one of each:

| Category | Accepted heading variants | Purpose |
|----------|--------------------------|---------|
| Endogenous Sources | `Endogenous Sources`, `Sources`, `Reference`, `Context` | Declare governing axioms, link to issues/patterns, citation chain |
| Core Procedure/Workflow | `Workflow`, `Steps`, `Procedure`, `How To` | Define the task sequence |
| Quality-gate/Completion | `Completion Criteria`, `Done When`, `Acceptance Criteria`, `Validation` | State what "executed correctly" looks like |

**Discipline rule for Endogenous Sources section**: Always encode:

1. The governing axiom this skill enacts (from [`MANIFESTO.md`](../../../MANIFESTO.md))
2. The pattern or GitHub issue this skill implements (e.g., `#45 Research: Product Definition`)
3. Which agents and tools depend on this skill
4. Citation chain to foundational documents

**Example Beliefs & Context**:

```markdown
## Beliefs & Context

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md) by encoding the complete research sprint workflow as a reusable procedure.

**Implements**: The research orchestration pattern from issue [#45 (Research: Product Definition)](https://github.com/EndogenAI/dogma/issues/45)

**Used by**:
- Executive Researcher (orchestrates fleet)
- Research Scout (gathers sources)
- Research Synthesizer (transforms findings)
- Research Reviewer (validates output)
- Research Archivist (commits deliverables)

**Foundation documents**:
- [`AGENTS.md`](../../../AGENTS.md) — governance constraints
- [`docs/guides/deep-research.md`](../../../docs/guides/deep-research.md) — full investigation methodology
- [`docs/research/methodology-review.md`](../../../docs/research/methodology/methodology-review.md) — prior art survey
```

---

## 4. Skill vs Agent — Composition Rule

**When to create a skill** (not an agent):

| Signal | Decision |
|--------|----------|
| Procedure needed by 1 agent only; unique posture | Create as agent *body* — embed procedure |
| Procedure needed by 2+ different agents/tools; no posture dependency | Extract to skill — reference from agents |
| Tactical workflow; could benefit multiple roles; tool-agnostic | Skill is appropriate |
| Authorization/oversight required; must gate execution | Agent with Review handoff is appropriate |

**Extraction test**: If a procedure in an agent body would benefit a *different* agent or tool without requiring that agent's posture or handoff logic, move it to a skill and reference it from both agents.

---

## 5. Link Path Rule

**All links in skill files that exit `.github/skills/<name>/` must use workspace-root-relative `/` paths.** This is consistent with the agent file convention and ensures VS Code's `prompts-diagnostics-provider` can resolve them.

```
.github/skills/my-skill/SKILL.md
  │
  ├─ ../              → .github/skills/   ← WRONG (wrong target)
  ├─ ../../           → .github/          ← WRONG (wrong target)
  ├─ ../../../        → (repo root)       ← resolves on disk but fails VS Code diagnostics
  └─ /                → (workspace root)  ← CORRECT (consistent with agent file rule)
```

**Correct usage for skills**:

```markdown
[`MANIFESTO.md`](/MANIFESTO.md)
[`AGENTS.md`](/AGENTS.md)
[`docs/guides/agents.md`](/docs/guides/agents.md)
[`.github/agents/README.md`](/.github/agents/README.md)
```

**Within-directory links** (to sibling files in `.github/skills/<name>/`) remain relative:
```markdown
[`./other-file.md`](./other-file.md)   ← same directory: OK
```

**Do not use `../../../`** — consistent with agent file rule; `/` is the preferred form across all `.github/` files.

---

## 6. Cross-Reference Density

Every skill file must contain at least one back-reference to the foundational document that governs it:

- Pure procedural skills → reference `/AGENTS.md`
- Research-oriented skills → reference `/MANIFESTO.md` (Endogenous-First axiom)
- Automation/scripting skills → reference `/AGENTS.md` § Programmatic-First

**Minimum pattern** (place in Endogenous Sources):

```markdown
This skill enacts the *<Axiom Name>* axiom from [`MANIFESTO.md`](/MANIFESTO.md).
It is governed by [`AGENTS.md`](/AGENTS.md) and associated procedural guidelines.
```

---

## 7. Encoding Inheritance Declaration

The skill's first substantive section must ground it in the encoding chain:

```markdown
## Beliefs & Context

This skill enacts the *<Axiom>* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md).

**Implements**: [Pattern or issue reference]

**Governed by**: [`AGENTS.md`](../../../AGENTS.md) § [relevant section]

Read [`docs/guides/agents.md`](../../../docs/guides/agents.md) before modifying this skill.
```

Governing axioms by skill type:

| Skill type | Governing axiom(s) |
|----------|-------------------|
| Research procedures | *Endogenous-First* |
| Scripting / automation | *Algorithms Before Tokens* |
| Documentation / synthesis | *Endogenous-First* |
| Validation / testing | *Algorithms Before Tokens* |
| Multi-phase orchestration | *Endogenous-First* + *Algorithms Before Tokens* |

---

## 8. Completeness Template

Use this template structure for new skills:

```yaml
---
name: <skill-name>
description: |
  <Clear description>
  
  USE FOR: [bullet list]
  DO NOT USE FOR: [bullet list]
argument-hint: "<usage hint>"

# Governance metadata
tier: <Foundation|Wave 1|Wave 2|...>
type: <research|feature|scripting|automation|tooling|validation>
effort: <s|m|l|xl>
applies-to:
  - <Agent Name>
status: active
---

# <Skill Title>

## Beliefs & Context

[Declare axioms, pattern, dependent agents, foundational docs]

---

## <Core Workflow/Procedure>

[Step-by-step instructions, code examples, decision trees]

---

## <Quality Gate/Completion Criteria>

[What constitutes successful execution]

---

## Guardrails

- [Never do X]
- [Always do Y]
```

---

## 9. No Heredocs in Skill Bodies

Like agents, skill files must not contain `cat >> file << 'EOF'` patterns or inline Python heredoc writes in example steps.

**Instead**: Instruct practitioners to use `create_file` (new files) or `replace_string_in_file` (edits) — both are safe for Markdown content.

---

## 10. Validate Before Committing

Before committing a new or modified skill:

```bash
uv run python scripts/validate_agent_files.py --skills
# To validate a single skill:
uv run python scripts/validate_agent_files.py .github/skills/<skill-name>/SKILL.md
```

**Pre-commit checklist**:

- ✅ Frontmatter has all required fields (name, description with USE FOR / DO NOT USE FOR)
- ✅ Optional governance fields present (tier, type, effort, applies-to, status)
- ✅ All repo-root paths use `../../../` prefix (not `../../`)
- ✅ Endogenous Sources declares governing axiom
- ✅ Endogenous Sources references defining issue or pattern
- ✅ Completion Criteria section defines success
- ✅ No heredoc patterns in workflow steps
- ✅ All cross-references to foundational docs are correct links
- ✅ No orphaned or broken internal links

---

## Guardrails

- **Never use `../../` for repo-root references in skills** — always `../../../` (one extra level up from agents)
- **Never omit the Endogenous Sources section** — encoding fidelity depends on it
- **Never combine multiple domains in one skill** — one skill per bounded domain
- **Never create a skill without understanding the agent(s) that will use it** — ask yourself: which agents will benefit from this?
- Do not add a skill without running the CI linter and passing all checks
- Do not introduce a procedure that is not grounded in an existing `AGENTS.md` principle or a prior-art pattern
