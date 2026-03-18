---
name: agent-file-authoring
description: |
  Encodes the conventions for authoring .agent.md files in .github/agents/: YAML frontmatter requirements, required section headings, relative path rules, cross-reference density, and CI validation. USE FOR: creating or modifying .agent.md role files (VS Code: Custom Agents); diagnosing validate_agent_files.py CI failures; verifying a draft role file before committing; scaffolding a new role from template. DO NOT USE FOR: skill authoring (SKILL.md files use a different format — see the agent-customization skill); general VS Code settings questions; MCP server configuration.
argument-hint: "role slug for the agent (e.g. executive-docs)"
---

# Agent File Authoring

This skill enacts the *Endogenous-First* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md): agent files are re-encodings of [`AGENTS.md`](../../../AGENTS.md), not independent inventions. Every `.agent.md` file derives its structure, posture, and governing constraints from `AGENTS.md` and `MANIFESTO.md`. Agents re-encode; they do not re-derive. Full authoring guidance is in [`docs/guides/agents.md`](../../../docs/guides/agents.md) and the fleet catalog in [`.github/agents/README.md`](../../../agents/README.md).

---

## 1. File Naming and Location

- **Location**: `.github/agents/<role-slug>.agent.md`
- **Slug format**: kebab-case, lowercase, e.g. `executive-docs`, `research-scout`
- **One file per agent role** — do not combine multiple personas into a single file

Use the scaffold helper to generate a compliant template:

```bash
uv run python scripts/scaffold_agent.py <role-slug>
# Creates: .github/agents/<role-slug>.agent.md
```

---

## 2. YAML Frontmatter

Every agent file must open with YAML frontmatter:

```yaml
---
name: <role name in title case>
description: |
  <≥25 character description — CI enforces minimum length>
---
```

**Field requirements** (enforced by `validate_agent_files.py`):

| Field | Required | Constraint |
|-------|---------|------------|
| `name` | Yes | Non-empty string |
| `description` | Yes | ≥ 25 characters |

The `description` field should be a `|` block for multi-line content. It is consumed by VS Code and GitHub Copilot as the agent's self-description in selection menus.

---

## 2b. Optional Discipline Fields for Project Governance

Every agent file **should** include optional frontmatter fields to track project governance and effort:

```yaml
---
name: Executive PM
description: Maintain issues, labels, milestones, and project hygiene...

# Optional — encode project governance, milestone tracking, and effort
tier: Wave 1                    # Milestone this agent targets/belongs to (Foundation|Wave 1|Wave 2|Adoption|Hardening)
effort: M                       # Effort to implement: s/m/l/xl (small/medium/large/xlarge)
status: active                  # Current status: active | beta | deprecated | blocked
area: agents                    # Codebase domain: agents | scripts | docs | ci | tests | deps | research
depends-on:                     # Other agents this agent requires/follows from
  - Review
  - GitHub
---
```

**Why encode these fields?**

| Field | Purpose | Example |
|-------|---------|---------|
| `tier` | Maps to project milestone; enables planning queries | `Wave 1: Agent Fleet Tier A+B` |
| `effort` | Effort estimate for implementation | `xl` (large initiative), `s` (small script) |
| `status` | Tracks lifecycle (active → beta → deprecated) | If issue #45 is blocked, agent status: `blocked` |
| `area` | Enables filtering by codebase domain | `area: agents` vs `area: scripts` |
| `depends-on` | Records agent dependency graph | Which agents must execute before this one |

These fields are optional in syntax but **semantically required** for mature agent governance. Every agent should encode these values in its Endogenous Sources section (body), whether or not frontmatter is populated.

**Discipline rule**: When an agent is created for a GitHub issue, encode:
- The issue number and title in the Endogenous Sources section
- The milestone (tier) in frontmatter or body
- The effort estimate from the issue label (effort:s/m/l/xl)
- The guiding axiom and acceptance criteria

See [`.github/agents/README.md`](../../../agents/README.md) for the milestone structure and [docs/guides/agents.md](../../../docs/guides/agents.md) for issue linkage patterns.

---

## 3. Required Sections — BDI Framing

CI fuzzy-matches for three required section types using Beliefs-Desires-Intentions (BDI) agent framing. Every agent file must contain at least one of each:

| BDI Category | Canonical Heading | Accepted variants | Purpose |
|----------|-------------------|------------------|----------|
| Beliefs & Context | `## Beliefs & Context` | `Endogenous Sources`, `Sources`, `Reference`, `Context` | Agent's knowledge base and foundational context — guiding axioms, GitHub issue definition, acceptance criteria |
| Workflow & Intentions | `## Workflow & Intentions` | `Action`, `Workflow`, `Checklist`, `Conventions`, `Instructions`, `Steps`, `Scope`, `Methodology` | Agent's desired goals and planned steps — how the agent acts to achieve those goals |
| Desired Outcomes & Acceptance | `## Desired Outcomes & Acceptance` | `Quality-gate`, `Completion Criteria`, `Guardrails`, `Done When`, `Acceptance` | Success definition — what "completed" looks like per the defining issue, measurable outcomes |

Use `## Beliefs & Context`, `## Workflow & Intentions`, and `## Desired Outcomes & Acceptance` as the canonical heading names. Accept the listed variants for backward compatibility during migration.

**Discipline rule for Beliefs & Context section**: Always encode:
1. The governing axiom from [`MANIFESTO.md`](../../../MANIFESTO.md) this agent enacts
2. Link to the GitHub issue number that defines this agent (e.g., `#62 Implement Remaining Agent Skills`)
3. The milestone this agent targets (from Optional Discipline Fields above)
4. A reference to the issue's acceptance criteria (see docs/guides/agents.md for example)

**Example Beliefs & Context**:
```markdown
## Beliefs & Context

This agent is defined by:
- **Issue**: [#62 Implement Remaining Agent Skills](https://github.com/EndogenAI/dogma/issues/62)
- **Milestone**: Wave 1: Agent Fleet Tier A+B
- **Governing axiom**: *Endogenous-First* (from [`MANIFESTO.md`](../../../MANIFESTO.md))
- **Acceptance criteria**: All deliverables in the linked issue checklist

Read [`AGENTS.md`](../../../AGENTS.md) and [`docs/guides/agents.md`](../../../docs/guides/agents.md) before modifying this agent.
```

---

## 4. Link Path Rule

**All links in `.github/agents/` files that point outside `.github/agents/` must use relative `../../` paths** — never `/`-rooted paths like `/AGENTS.md`.

VS Code's `prompts-diagnostics-provider` resolves `/`-rooted paths against the OS filesystem root (`/`), not the workspace root. On macOS, `/AGENTS.md` resolves to `/AGENTS.md` on disk — a path that does not exist — producing VS Code Problems panel errors. Relative `../../` traversal resolves correctly from `.github/agents/` because `.github/agents/` is at depth 2 from the repo root.

```
.github/agents/<file>.agent.md
           │
           ├─ ../   → .github/            ← WRONG (single-level, wrong target)
           ├─ /AGENTS.md → OS filesystem root ← WRONG (resolves to /AGENTS.md on macOS)
           └─ ../../ → (repo root)        ← CORRECT
```

**Correct** (depth 2 from repo root, so 2 `../` levels needed):
```markdown
[`AGENTS.md`](../../AGENTS.md)
[`MANIFESTO.md`](../../MANIFESTO.md)
[`docs/guides/agents.md`](../../docs/guides/agents.md)
[`.github/skills/session-management/SKILL.md`](./../skills/session-management/SKILL.md)
```

**Incorrect** (will produce VS Code Problems panel errors):
```
# Note: paths below use X as placeholder for / to avoid triggering the pre-commit hook
[`AGENTS.md`](X/AGENTS.md)    ← /-rooted: resolves to /AGENTS.md on macOS — OS filesystem root
[`AGENTS.md`](../AGENTS.md)   ← resolves to .github/AGENTS.md — does not exist
```

**Within-directory links** (to sibling files in `.github/agents/`) remain relative:
```markdown
[`README.md`](./README.md)        ← same directory: OK
```

This convention is enforced by the `no-absolute-path-links-in-agent-files` pre-commit hook which blocks `](` followed by `/` patterns in `.github/agents/` and `.github/skills/` files.

---

## 5. Cross-Reference Density

Every agent file must contain at least one back-reference to `/MANIFESTO.md` **or** `/AGENTS.md` in the body. CI checks this as a proxy for encoding fidelity.

**Minimum pattern** (place in the first substantive section; agent files are at depth 2 — use `../../`):

```markdown
This agent is governed by [`AGENTS.md`](../../AGENTS.md) and the foundational axioms
in [`MANIFESTO.md`](../../MANIFESTO.md).
```

Low cross-reference density is a signal of encoding drift — the agent has been authored without grounding in the inheritance chain.

---

## 6. Encoding Inheritance Declaration

The first substantive section (Beliefs & Context) of every agent file must name the governing axiom and cite the primary endogenous source. This mirrors the session-start encoding checkpoint pattern:

```markdown
## Beliefs & Context

This agent enacts the *<Axiom Name>* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md).
Read [`AGENTS.md`](../../../AGENTS.md) before modifying any procedure in this file.
```

Governing axioms by agent type:

| Agent type | Governing axiom |
|------------|----------------|
| Research agents | *Endogenous-First* |
| Scripting / automation agents | *Algorithms Before Tokens* |
| Docs / archival agents | *Endogenous-First* |
| Validation / CI agents | *Algorithms Before Tokens* |
| Executive / orchestration | *Endogenous-First* + *Algorithms Before Tokens* |

---

## 7. No Heredoc Writes

Agent files must not contain `cat >> file << 'EOF'` patterns or inline Python heredoc writes in their workflow steps. CI flags these as failures.

**Why**: Heredocs silently corrupt Markdown content containing backticks or triple-backtick fences when executed through the VS Code terminal tool.

**Instead**: instruct the agent to use `create_file` (new files) or `replace_string_in_file` (edits) — both are safe for Markdown content.

---

## 8. Validate Before Committing

Run the compliance check before every `git commit` that touches agent files:

```bash
# Check a single file
uv run python scripts/validate_agent_files.py .github/agents/<file>.agent.md

# Check all agent files
uv run python scripts/validate_agent_files.py --all
```

The validator enforces:
1. Valid YAML frontmatter (`name`, `description` ≥ 25 chars)
2. Required sections present (fuzzy-matched)
3. At least one cross-reference to `/MANIFESTO.md` or `/AGENTS.md`
4. No heredoc patterns

**Manual pre-commit checklist** (in addition to automated validation):

- ✅ Agent frontmatter includes optional discipline fields (`tier`, `effort`, `status`, `area`, `depends-on`) where applicable
- ✅ Endogenous Sources section references the defining GitHub issue number (e.g., `#62`)
- ✅ Endogenous Sources section declares the governing axiom (one of the three core axioms from `MANIFESTO.md`)
- ✅ Completion Criteria section mirrors the defining issue's acceptance checklist
- ✅ All links exiting `.github/agents/` use `../../`-relative paths (e.g. `../../AGENTS.md`), not `/`-rooted paths
- ✅ No heredoc write patterns in workflow steps
- ✅ No orphaned URLs or dead links to internal docs
- ✅ Every agent has at least one handoff to a downstream agent

A file that fails validation or the manual checklist will also fail CI. Fix all violations before committing.

---

## Guardrails

- **Never use `/`-rooted paths for cross-directory references** in agent files — always use `../../`-relative paths (e.g. `../../AGENTS.md`). See [Section 4: Link Path Rule](#4-link-path-rule).
- **Never omit the cross-reference density check** — at least one `/MANIFESTO.md` or `/AGENTS.md` link is required.
- **Never embed heredoc write patterns** in workflow steps.
- Do not add an agent without running `validate_agent_files.py --all` and passing.
- Do not introduce a new governing axiom that is not grounded in an existing `MANIFESTO.md` principle.
