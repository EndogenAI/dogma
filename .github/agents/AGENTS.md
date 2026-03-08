# .github/agents/AGENTS.md

> This file narrows the constraints in the root [`AGENTS.md`](../../AGENTS.md).
> It does not contradict any root constraint — it only adds agent-authoring-specific rules.
> Full authoring guide: [`docs/guides/agents.md`](../../docs/guides/agents.md)

---

## Programmatic-First

> The **programmatic-first** constraint from [root AGENTS.md](../../AGENTS.md#programmatic-first-principle) applies here without exception.

Before authoring, reviewing, or auditing agents interactively, check `scripts/` for existing scaffold, validation, or audit scripts.
Agent scaffolding, frontmatter validation, and fleet compliance checks should be encoded as scripts — extend them, don't repeat steps by hand.
Escalate scripting gaps to the `Executive Scripter`; automation design (watchers, hooks) to the `Executive Automator`.

**Research sessions**: before delegating to any Scout, pre-warm the source cache:

```bash
uv run python scripts/fetch_all_sources.py
```

This is the **fetch-before-act** posture. Scouts read cached `.md` files via `read_file` rather than re-fetching pages through the context window. See [`scripts/README.md`](../../scripts/README.md#scriptsfetch_all_sourcespy) for full usage.

**`gh` CLI in agent files**: any `.agent.md` that includes `gh` commands must use [`docs/toolchain/gh.md`](../../docs/toolchain/gh.md) as the source of command patterns — do not reconstruct syntax from memory. Known failure modes (body corruption, Projects v2 auth, silent API failures) are encoded there.

---

## Purpose

This file governs the authoring, review, and maintenance of Roles (`.agent.md` files — VS Code: Custom Agents) in this directory. Every agent in the fleet must comply with both the root `AGENTS.md` and the rules below.

---

## Frontmatter Schema

Agent files begin with a YAML front-matter block. The allowed fields are:

```yaml
---
name: <Display Name>            # Required. Shown in the Copilot agents dropdown. Must be unique.
description: <One-line summary> # Required. ≤ 200 characters.
argument-hint: <hint>           # Optional. Placeholder shown in the chat input box.
tools:                          # Required. Minimal subset — see posture table below.
  - <tool-id>
agents:                         # Optional. List of agent `name` values this agent may invoke.
  - <Agent Name>                # Must match the `name` field of the target agent exactly.
handoffs:                       # Required. At least one handoff per agent.
  - label: <Button text>
    agent: <Target agent name>  # Must match the `name` field of the target exactly.
    prompt: <Pre-filled prompt>
    send: false

# Optional discipline fields — encode project governance and tracking
tier: <Wave 1|Wave 2|Foundation|...>  # Milestone this agent targets/belongs to
effort: <s|m|l|xl>                     # Effort to implement: small/medium/large/xlarge
status: <active|beta|deprecated|blocked>  # Current status
area: <agents|scripts|docs|ci|tests|deps|research>  # Codebase domain
depends-on:                            # Other agents this agent requires/follows from
  - <Agent Name>
---
```

**Field requirements** (enforced by `validate_agent_files.py`):

| Field | Required | Constraint |
|-------|---------|----------|
| `name` | Yes | Non-empty string |
| `description` | Yes | ≤ 200 characters |
| `tools` | Yes | Minimal set per posture |
| `handoffs` | Yes | At least one route out |
| `tier` | No | Maps to project milestone (for tracking) |
| `effort` | No | Effort estimate: s/m/l/xl |
| `status` | No | active/beta/deprecated/blocked |
| `area` | No | One of: agents/scripts/docs/ci/tests/deps/research |
| `depends-on` | No | List of agent `name` values |

**Validation rules:**
- `name` must be unique across all `.agent.md` files in this directory.
- `description` must be one sentence, ≤ 200 characters.
- Every `handoffs[].agent` value must match an existing agent's `name` field exactly.
- Every `depends-on` agent must be defined in the fleet.
- `tools` must be the **minimum** set required for the agent's posture (see below).

**Discipline rule**: Every agent should encode a link to its defining GitHub issue (see "Endogenous Sources" section in agent body). The optional frontmatter fields (`tier`, `effort`, `status`, `area`) enable project management queries and milestone tracking without separate GitHub API calls.

---

## Tool Selection by Posture

Tools are specified as **toolsets** (named bundles provided by the VS Code Copilot API).

| Posture | Permitted toolsets |
|---------|-------------------|
| **Read-only** (review, plan, audit) | `search`, `read`, `changes`, `usages` |
| **Read + create** (scaffold) | adds `edit`, `web` |
| **Full execution** (implement, debug, executive) | adds `execute`, `terminal`, `agent` |

> **`web` toolset**: Never add `web` unless the agent body contains a step that explicitly fetches a remote URL. Omit it if the agent only reads local files or runs local commands.

**Toolset contents (reference):**

| Toolset | Individual tools bundled |
|---------|--------------------------|
| `search` | `codebase`, `findFiles`, `findTestFiles`, `grep` |
| `read` | `readFile`, `problems`, `terminalLastCommand`, `listDirectory` |
| `edit` | `editFiles`, `insertEdit` |
| `web` | `fetch` (+ web search) |
| `execute` | `runInTerminal`, `getTerminalOutput`, `runTests` |
| `terminal` | `runInTerminal`, `getTerminalOutput`, `terminalLastCommand` |
| `agent` | invoke other Copilot agents by name |

---

## Handoff Graph Patterns

Every agent must hand off to at least one downstream agent. Standard patterns:

```
Action agent  →  Review  →  GitHub
Scaffold agent  →  Review  →  GitHub
Executive (single phase)  →  sub-agents  →  [Back to Executive]  →  Review  →  GitHub
Executive (multi-phase)  →  [Phase 1] → Review → [Phase 2] → Review → ... → GitHub
```

- An executive agent orchestrates its fleet and must hand off to Review before committing.
- **Multi-phase executives invoke Review between every domain phase** — a Review gate APPROVED verdict, appended to the scratchpad under `## Review Output`, is required before the next domain phase begins.
- Sub-agents return control to their executive via takeback — they do not chain directly to the next sub-agent.
- Read-only agents (review, plan, audit) hand off to action agents or GitHub.
- The `send: false` default is strongly preferred — avoid auto-submitting prompts.

### Takeback Gates (Recommended Pattern)

The most reliable delegation pattern is the **takeback**: a sub-agent's final handoff returns control to the executive.

```
Executive → Sub-agent A → [Back to Executive] → Review (gate) → Sub-agent B → [Back to Executive] → Review (gate) → GitHub
```

**Anti-pattern — free-chaining** (`A → B → C → D → Review`): loses the executive's oversight role and skips inter-phase Review gates.

### Inter-Phase Review Gate (Required for Multi-Phase Sessions)

Any session with ≥ 2 domain phases must include a Review gate between each consecutive pair. The executive hands off to itself after each phase output, then to Review before the next phase begins:

```yaml
# Pattern: after Phase N output is logged, invoke Review before Phase N+1
- label: "✓ Phase N complete — Review gate"
  agent: Review
  prompt: |
    Phase N output is logged to the scratchpad under '## Phase N Output'.
    Changed files: [list]. Please validate against AGENTS.md constraints.
    Append verdict to scratchpad as '## Review Output'.
    Phase N+1 does not begin until APPROVED.
  send: false
```

**Gate enforcement rule**: the orchestrator may not delegate Phase N+1 unless the scratchpad contains a `## Review Output` section whose verdict is `APPROVED` (for example, via a `**Verdict**: APPROVED` line within that section).

### Evaluator-Optimizer Loop (Executive Pattern)

Executive agents should include handoff buttons that target **themselves** — one per phase boundary. These fire after a sub-agent returns and force a deliberate review step before the next delegation.

```yaml
- label: "✓ Scout done — review & decide"
  agent: Executive Researcher      # targets itself
  prompt: "Scout output is in the scratchpad. Review: ≥3–5 sources? No synthesis?
           If satisfied, delegate to Synthesizer. If not, re-delegate Scout."
  send: false
```

**Why evaluator-optimizer loop**: the executive absorbs the sub-agent's output, evaluates it against gates, and enriches the next prompt with that context before delegating again. The handoff button is the mechanism that enforces the review pause.

### Focus-on-Descent / Compression-on-Ascent

At each delegation boundary, outbound briefs narrow the problem to the minimum needed scope; inbound results compress extensive exploration into a dense ≤ 2,000 token handoff. This is not enrichment — it is contraction.

Each delegation level narrows the problem and scopes the task brief:

```
Human (sparse intent)
  → Executive (reads scratchpad + OPEN_RESEARCH.md + AGENTS.md → scoped, grounded task brief)
    → Sub-agent (receives narrow task brief → explores extensively → returns ≤ 2,000 token summary)
      → Specialist
```

This is the endogenous-first principle in practice: context already encoded in the repo shapes the delegation, so agents do not re-discover it interactively.

**Implication for prompt authoring**: handoff `prompt:` fields on executive agents should be narrow and task-scoped — dispatch the minimum necessary context. Sub-agents compress extensive exploration into dense results; they do not return raw search histories.

### Quasi-Encapsulated Sub-Fleets

Sub-agents **default to returning to their executive** (takeback), but may escalate directly to another agent in exceptional cases — when the executive's context is insufficient or the issue crosses fleet boundaries.

```
Normal:     Sub-agent → [Back to Executive]
Escalation: Sub-agent → Executive Docs  (cross-fleet, exceptional)
Escalation: Sub-agent → Review          (quality issue requiring immediate gate)
```

This hybrid model gives fleets quasi-autonomy while preserving executive oversight as the default. Full encapsulation (sub-agents can never escalate) and full openness (sub-agents chain freely) are both anti-patterns.

---

## Body Structure Requirements

Every agent body must follow this structure:

1. **Bold role statement**: `You are the **X agent** for the EndogenAI Workflows project.`
2. **Endogenous sources section**: list every file the agent must read before acting, with relative links.
3. **Workflow or checklist**: numbered steps or a role-specific checklist.
4. **Guardrails section**: explicit list of what the agent must NOT do.

### Hybrid Markdown + XML Schema

All agent files with more than one distinct behavioural subsystem must use the **hybrid schema**: `## Section` headings as the outer document skeleton (for human readability and IDE navigation), with each section's content wrapped in a semantic XML tag.

```markdown
## Workflow

<instructions>
Step-by-step process here.
</instructions>

## Guardrails

<constraints>
- Do not do X.
- Do not do Y.
</constraints>
```

**Canonical tag map** (see `docs/research/xml-agent-instruction-format.md` §4 for full inventory):

| Heading keyword | XML tag |
|---|---|
| Persona, Role | `<persona>` |
| Instructions, Behavior, Workflow | `<instructions>` |
| Context, Environment, Endogenous Sources | `<context>` |
| Examples | `<examples>` / `<example>` |
| Tools, Tool Guidance | `<tools>` |
| Constraints, Guardrails, Scope | `<constraints>` |
| Output Format, Deliverables, Completion Criteria | `<output>` |

**Rules**:
- XML tags apply **only to the body below the YAML `---` fence**. Never put XML in frontmatter values.
- Tag names are lowercase.
- Sections with fewer than 3 lines of body content may omit the XML wrapper.
- `scripts/scaffold_agent.py` emits XML-tagged stubs by default — new agents start correct.
- To migrate an existing agent: `uv run python scripts/migrate_agent_xml.py --file <path> --dry-run` (review diff), then without `--dry-run` to apply.

---

## Naming Conventions

**Canonical term**: Files in this directory are **Roles** — the EndogenAI endogenous term for VS Code Custom Agents (`.agent.md` files, the VS Code upstream term since v1.106, previously "custom chat modes"). Use **"Roles"** in project documentation. When referring specifically to the VS Code tooling mechanism, "Custom Agents" is also correct. Never use "chat modes" or "personas" as standalone terms. The full three-primitive taxonomy (fleet constraints / Roles / Agent Skills) is defined in the [root `AGENTS.md` → VS Code Customization Taxonomy](../../AGENTS.md#vs-code-customization-taxonomy) section.

### Convention Propagation Rule

When a new authoring convention is introduced for agent files, check whether it must also appear in the root `AGENTS.md` or `docs/AGENTS.md`:

- If it affects how **all agents communicate** (scratchpad, handoffs) → update root `AGENTS.md`
- If it affects **documentation structure** (how findings are written up) → update `docs/AGENTS.md`
- If it is **agent-file-authoring-only** (frontmatter, section order) → this file is sufficient

Run `find . -name 'AGENTS.md' | grep -v node_modules` to see all narrowing files before closing a PR that introduces a new convention.

| Agent type | File name pattern | `name` field |
|-----------|------------------|-------------|
| Fleet executive | `<area>-executive.agent.md` | `<Area> Executive` |
| Fleet sub-agent | `<area>-<role>.agent.md` | `<Area> <Role>` |
| Workflow agent | `<verb>.agent.md` or `<noun>.agent.md` | `<Verb>` or `<Noun>` |

Use lowercase kebab-case for filenames.

---

## Pre-Commit Gate for Agent Files

**Before committing any `.agent.md` file (new or edited), run:**

```bash
uv run python scripts/validate_agent_files.py --all
```

All 4 checks must pass:
- YAML frontmatter: `name` + `description` present
- Required sections: Endogenous Sources, Action section (heading containing `workflow`/`checklist`/`conventions`/`playbook`/`scope`/`methodology`), Quality-gate section (heading containing `completion criteria` or `guardrails`)
- Cross-reference density: ≥1 link to `MANIFESTO.md` or `AGENTS.md`
- No heredoc writes

This check also runs as a pre-commit hook (`validate-agent-files` in `.pre-commit-config.yaml`) so any unforced `git commit` on `.agent.md` files will catch failures automatically. **Never bypass with `--no-verify`.** CI enforces the same check as a blocking gate.

---

## File Writing Guardrail

**Never use heredocs to write agent or Markdown file content.**

Heredocs (`cat >> file << 'EOF'`, Python inline `<< 'PYEOF'`) silently corrupt or truncate content containing backticks, triple-backtick fences, or special characters when executed through the VS Code terminal tool.

> **This constraint is encoded as the first item in the `<constraints>` block of every `.agent.md` file in this directory.** Placing it first ensures it is read before role-specific constraints and is not skipped when context is compressed.
>
> **Observed failure pattern**: Agents attempt heredoc → observe silent corruption → retry with escaped heredoc → observe hang → eventually write a Python script. This wastes ~3–5 agent turns per occurrence. Correct action on the *first* attempt: use the file tool.

| Situation | Correct approach |
|-----------|------------------|
| Creating a new file | `create_file` tool |
| Editing an existing file | `replace_string_in_file` or `multi_replace_string_in_file` tool |
| Appending to any Markdown file | `replace_string_in_file` with anchor text |
| Writing large content blocks | Never heredoc — always use file tools |
| Writing multi-line `gh issue` body | Write to temp file; use `--body-file <path>` or Python `subprocess` list-args |

**`--body-file` pattern** (avoids shell-quoting hangs with `gh issue create/edit`):
```python
import subprocess, pathlib
body = pathlib.Path('/tmp/issue_body.md')
body.write_text('## Section\n\nContent here...')
subprocess.run(['gh','issue','create','--title','My Issue','--body-file',str(body)])
body.unlink()
```

---

## GitHub Issue Conventions for Agent-Created Issues

When an agent creates or edits a GitHub issue, the following rules apply:

- **Label every issue**: minimum one `type:` label and one `priority:` label.
  Full taxonomy: `type:`, `area:`, `priority:`, `status:` — see `docs/guides/github-workflow.md`.
- **Encode priority as a label**: Copilot reads labels; it does NOT read Projects v2 field values.
  Always set `priority:` label regardless of whether a project field is also set.
- **Self-contained body**: Put key facts in the issue body directly.
  Copilot does not traverse cross-reference links to other issues.
- **Verify after creating**: `gh issue list --state open --limit 3` immediately after `gh issue create`.
- **Projects v2 scope** (once per machine before any `gh project` commands):
  ```bash
  gh auth refresh -s project
  gh auth status  # verify "project" appears in scopes
  ```

See [`docs/guides/github-workflow.md`](../../docs/guides/github-workflow.md) for the full `gh` CLI quick-reference.
See [`docs/research/github-project-management.md`](../../docs/research/github-project-management.md) for the full synthesis.

---

## Verification Gate

Before committing a new or modified agent file:

```bash
# Check for name uniqueness
grep -h "^name:" .github/agents/*.agent.md | sort | uniq -d

# Verify all handoff targets resolve (manual: every `agent:` field must match a `name:`)
```

> Any session that creates or modifies `.agent.md` files should be reviewed before committing.
