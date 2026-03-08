---
title: "Agent Skills Integration — Research Synthesis"
status: Final
---

# Agent Skills Integration — Research Synthesis

> **Status**: Final
> **Research Question**: How do VS Code Agent Skills (agentskills.io open standard) complement the existing `.agent.md` fleet, what is the canonical composition rule, and what is the optimal integration path for the EndogenAI Workflows repository?
> **Date**: 2026-03-07
> **Related**: [`AGENTS.md`](../../AGENTS.md) (guiding constraints), [`MANIFESTO.md`](../../MANIFESTO.md) (Algorithms Before Tokens axiom), [`docs/guides/agents.md`](../guides/agents.md), [`docs/plans/2026-03-07-issue-60-agent-skills.md`](../plans/2026-03-07-issue-60-agent-skills.md)

---

## 1. Executive Summary

Agent Skills are an open standard (agentskills.io, developed by Anthropic) for packaging workflow expertise as portable `SKILL.md` files that AI agents load on demand. In VS Code, skills are stored in `.github/skills/` and discovered automatically by GitHub Copilot — only metadata (~100 tokens per skill) is loaded at startup, with full instructions loaded only when relevant. Skills sit at the tactical layer of the VS Code customization stack: they encode *how to do a task* (procedures, conventions, templates), while `.agent.md` Roles encode *who does it* (persona, posture, tool restrictions, handoff logic). This separation is the canonical composition rule.

For this repository, skills are the precise implementation of the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../MANIFESTO.md): workflow knowledge that currently lives in `docs/guides/`, `CONTRIBUTING.md`, and agent bodies can be extracted into skills, encoded once, and inherited across all sessions, tools, and platforms without repeated prompting overhead. The three highest-priority candidates — `session-management`, `deep-research-sprint`, and `conventional-commit` — are available for immediate implementation.

---

## 2. Hypothesis Validation

This section validates the seven research questions (Q1–Q7) from Issue #60.

### Q1 — Skills vs Agents: The Composition Rule

**Hypothesis**: A precise, non-overlapping composition rule exists between skills and agents that the fleet can apply to every candidate pattern.

**Verdict**: CONFIRMED — the boundary is strategic/tactical, not size or frequency.

| Layer | Format | Encodes | Loaded When |
|-------|--------|---------|-------------|
| **Agent** | `.agent.md` | Persona, posture, tool restrictions, handoff graph | Selected explicitly or via delegation |
| **Skill** | `SKILL.md` | Workflow procedures, conventions, templates, scripts | Automatically when task matches description, or via `/slash-command` |

**The composition rule**: Agents call skills (directly or through the model's automatic loading); skills never call agents. An agent may reference a skill description; a skill body never contains handoff logic. If a proposed skill requires posture constraints or a handoff graph, it must remain an agent.

**Fleet application**:
- **Stays as agent**: Any `.agent.md` with unique posture (e.g., `executive-researcher` needs full posture + handoff to 4 sub-agents), distinct tool requirements, or error-isolation needs.
- **Becomes skill**: Any procedure currently embedded in an agent body that a *different* agent or tool also needs — specifically session management, commit conventions, research sprint protocol, and validation checklists.
- **Decision test**: Can a different AI tool (Copilot CLI, coding agent) benefit from this knowledge without any of the agent's tool restrictions? If yes, skills > agent body.

### Q2 — Reference Implementations

**Hypothesis**: Public skill libraries contain directly adoptable skills for this repo.

**Verdict**: PARTIALLY CONFIRMED — reference patterns are adoptable; specific skills are not directly portable.

**`anthropics/skills`** (Anthropic reference library): Focuses on document manipulation primitives (PDF processing, Excel/PowerPoint/Word manipulation). These assume a Claude VM filesystem environment and are not applicable to the Workflows repo's use cases. However, the structural patterns — SKILL.md with a `scripts/` subdirectory, `references/` for detailed sub-documents, and `assets/` for templates — are canonical and should be followed.

**`github/awesome-copilot`** (community collection): Contains testing skills (Playwright), GitHub Actions debugging, and code review skills. These demonstrate production-quality SKILL.md format and the `argument-hint` field in practice. No skills in this collection cover session management, endogenic methodology, or conventional commit conventions — confirming this repo's contributions would be novel additions to the community.

**Key gap**: No public skill currently encodes:
- Multi-session scratchpad management with encoding checkpoints
- Research sprint orchestration (Scout → Synthesizer → Reviewer → Archivist)
- Conventional Commits + endogenic commit discipline

These three are the highest-value original contributions this repo can make to the open standard.

### Q3 — Cross-Agent Claude Portability

**Hypothesis**: Skills authored for VS Code Copilot work without modification when Claude is the model.

**Verdict**: CONFIRMED — the agentskills.io spec is agent-agnostic by design.

The `SKILL.md` format is identical across all three supported platforms:
1. **GitHub Copilot in VS Code** — skills discovered from `.github/skills/`, `.claude/skills/`, or `.agents/skills/`
2. **GitHub Copilot CLI** — reads same skill directories
3. **Claude Code** — reads `.claude/skills/`; uses bash to access SKILL.md from its VM filesystem

**Loading mechanism across agents**:
- Level 1 (always): `name` + `description` frontmatter read at startup (~100 tokens)
- Level 2 (on trigger): Full SKILL.md body loaded when request matches description
- Level 3 (on demand): Files in `scripts/`, `references/`, `assets/` loaded only when explicitly referenced in body

The standard is explicitly cross-model. Supporting `.github/skills/` (VS Code Copilot) and `.claude/skills/` (Claude Code) simultaneously requires only a directory symlink or duplicated SKILL.md — both directories can share the same skill contents.

**VS Code-specific frontmatter** (`argument-hint`, `user-invocable`, `disable-model-invocation`) is supported only by VS Code Copilot and degrades gracefully (is ignored) on other agents.

### Q4 — Skills + Hooks + Prompt Files Composition

**Hypothesis**: A canonical layer-stack pattern exists for complex multi-tool workflows.

**Verdict**: CONFIRMED — VS Code documentation defines an explicit priority and trigger hierarchy.

| Layer | Format | Trigger | Primary Purpose |
|-------|--------|---------|-----------------|
| Hooks | Shell commands | Agent lifecycle events | Deterministic gates (ruff, validate-synthesis) |
| Always-on instructions | `.instructions.md` | Every request | Coding standards, project conventions |
| Agents | `.agent.md` | Explicit selection or delegation | Persona, posture, tool restrictions |
| **Skills** | `SKILL.md` | Task-match auto-load or `/slash` | Workflow expertise, procedures |
| Prompt files | `.prompt.md` | `/slash-command` | Single-task templates |
| MCP | Server config | Tool-match auto-load | External API capabilities |
| Plugins (Preview) | Extension package | Install-once | Bundled marketplace packages |

**Canonical pattern for this fleet**: `Agent` (persona + posture + handoffs) + `Skill` (procedure + conventions + templates) + `MCP` (external capabilities) + `Hook` (lifecycle gates). The agent provides the strategic frame; the skill injects tactical expertise; MCP tools are the actuators; hooks enforce quality gates deterministically.

This directly implements the *Algorithms Before Tokens* axiom: hooks and skills replace interactive prompting for well-understood procedures. The agent layer provides judgment; the lower layers provide determinism.

### Q5 — Agent Plugin Opportunity

**Hypothesis**: This repo should publish an agent plugin bundling its skills.

**Verdict**: DEFERRED — plugins are Preview; the standard path first.

**Plugin structure** (when adopted): A VS Code extension with `chatSkills` in `package.json` pointing to skill directories. The `name` in `SKILL.md` frontmatter must exactly match the parent directory name (enforced by VS Code loader).

**Assessment for this repo**:
- Skills work without plugins — `.github/skills/` is discovered automatically by any user who opens the repo
- Plugin authoring requires VS Code extension packaging; documentation is sparse (Preview)
- The value proposition (easier distribution) doesn't apply for a single-repo skill set
- **Recommended decision**: Implement skills in `.github/skills/` first; evaluate plugin packaging after VS Code Agent Plugins reaches GA and the skill library stabilizes

### Q6 — `validate_agent_files.py` Extension for SKILL.md

**Hypothesis**: The existing CI validation script can be extended to validate SKILL.md files with equivalent rigor to `.agent.md` files.

**Verdict**: CONFIRMED — SKILL.md has a well-specified validation surface; CI extension is straightforward.

**Required frontmatter fields** (per agentskills.io spec):

| Field | Required | Constraints |
|-------|---------|-------------|
| `name` | Yes | Lowercase, hyphens only, 1–64 chars, no leading/trailing/consecutive hyphens, must match parent directory name |
| `description` | Yes | 1–1024 chars, non-empty, should describe both what and *when to use* |
| `license` | No | Free text or license file reference |
| `compatibility` | No | 1–500 chars; only include if platform/env requirements exist |
| `metadata` | No | Arbitrary key-value map |
| `allowed-tools` | No | Space-delimited tool list (experimental) |

**VS Code-specific optional fields** (gracefully ignored by other agents):

| Field | Default | Purpose |
|-------|---------|---------|
| `argument-hint` | — | Hint text for slash-command invocation |
| `user-invocable` | `true` | Whether skill appears in `/` slash menu |
| `disable-model-invocation` | `false` | Whether to block auto-load by agent |

**CI gate design**: Extend `validate_agent_files.py` with a `--skills` flag (or create `validate_skill_files.py`) that checks:
1. Valid YAML frontmatter with required fields: `name`, `description`
2. `name` format: `^[a-z][a-z0-9-]*[a-z0-9]$` + max 64 chars + no consecutive hyphens
3. `name` matches parent directory name
4. At least one cross-reference to `AGENTS.md` or `MANIFESTO.md` in the body (extends encoding inheritance to skill layer)
5. Minimum body length (≥20 non-blank lines)

**Endogenous inheritance note**: Checks 1–3 mirror the agentskills.io spec; check 4 is this repo's addition — it enforces that skill bodies are anchored to the encoding inheritance chain (`MANIFESTO.md` → `AGENTS.md` → agent files → skills → session).

### Q7 — Endogenic Fit

**Hypothesis**: Agent Skills map precisely to the *Endogenous-First* and *Algorithms Before Tokens* axioms and can extend the encoding inheritance chain.

**Verdict**: CONFIRMED — skills are the strongest available primitive for enacting ABT in the VS Code customization stack.

**Algorithms Before Tokens alignment** (from [`MANIFESTO.md`](../../MANIFESTO.md)):
> *"Every token spent in interactive sessions comes at a cost — computational, financial, and environmental. The core strategy is to move work upstream: encode algorithms, scripts, and decision trees that prevent re-discovery at session time."*

Skills implement this directly: a session management skill encodes the scratchpad protocol once; every subsequent session loads it in ~100 tokens of metadata + ~2000 tokens on trigger, instead of re-prompting an agent to recall the procedure. At 50 sessions/month, the token deficit from re-prompting vs. skill-loading compounds rapidly into a measurable ABT violation.

**Endogenous-First alignment**: Skills extend the encoding inheritance chain from four layers to five:

| Layer | Format | Role in chain |
|-------|--------|--------------|
| MANIFESTO.md | Constitution | Foundational axioms |
| AGENTS.md | Operational constraints | Behavioral translation |
| `.agent.md` files | Agent implementations | Specific functional implementations |
| **`SKILL.md` files** | **Skill procedures** | **Reusable tactical knowledge** |
| Session behavior | Enactment | Observable output |

Each SKILL.md body should cite `AGENTS.md` as its governing constraint document. This makes the skill encoding-fidelity-auditable in the same way that agent files are — a future `validate_skill_files.py` cross-reference check would catch drift at CI time.

**Cross-reference density note**: `MANIFESTO.md` [`§Algorithms Before Tokens`](../../MANIFESTO.md#2-algorithms-before-tokens) names the `scripts/watch_scratchpad.py` watcher as the canonical ABT example. Skills are an equal-or-higher-tier canonical example: they cover the entire *instruction class* of repeated tasks (not just one script), are agent-agnostic, and require zero runtime token cost below the description threshold.

---

## 3. Pattern Catalog

### Pattern A — Agent-Skill Separation (Composition Rule)

**Context**: Fleet has 20+ `.agent.md` files; several embed reusable workflow procedures in their bodies that other agents or tools also need.

**Forces**: Procedure knowledge duplicated in multiple agent bodies → update one, miss others. `.agent.md` files carry persona + posture + tool restrictions that are VS Code-specific; other tools cannot use them.

**Solution**: Extract standalone workflow procedures into `SKILL.md` files in `.github/skills/`. Agent bodies reference the skill by name/description (or the model auto-loads it). The agent remains the strategic frame; the skill provides the tactical detail.

**Consequences**: Skill updates propagate to all agents that trigger them. Skill portability (Copilot CLI, Claude Code) is automatic. Agent bodies become leaner. Encoding inheritance chain is extended by one layer.

### Pattern B — Progressive Disclosure for Token Economy

**Context**: MCP tools load ALL tool metadata upfront (~32,000 tokens for a typical dev stack); skills load only metadata (~100 tokens each) until triggered.

**Forces**: Context window pressure increases with fleet size. Always-loaded instructions accumulate. Skills add capability without proportional context cost.

**Solution**: Use skills for domain expertise that is relevant *conditionally*. Keep always-on instructions for universal project standards. Use `user-invocable: false` for skills that should be invisibly available (background knowledge) without slash-command pollution.

**Token budget** (estimated at 20 registered skills): ~2,000 tokens baseline metadata × 1–2 skills triggered per session ≈ 4,000–12,000 tokens. Compare to: same knowledge in always-on instructions ≈ 20,000+ tokens always loaded.

### Pattern C — Endogenic Skill Body Structure

**Context**: Skill bodies need to be useful standalone (for Copilot CLI, coding agent) while also fitting into the repo's endogenic conventions.

**Forces**: External tools don't read `AGENTS.md`. Sessions may not have loaded any agent file. The skill must carry enough context to be self-contained.

**Solution**: Structure SKILL.md bodies with:
1. Governing axiom citation (one sentence, e.g., "This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../MANIFESTO.md).")
2. When to use this skill (3–5 lines)
3. Step-by-step procedure
4. References to supporting scripts or guide files (relative paths)
5. Common failure modes

### Pattern D — Slash-Command vs Auto-Load Routing

| `user-invocable` | `disable-model-invocation` | Use case |
|-----------------|--------------------------|---------|
| `true` (default) | `false` (default) | General skills: appears in `/` menu AND auto-loads |
| `false` | `false` | Background knowledge: auto-loaded but not in `/` menu |
| `true` | `true` | Explicit-only: must be invoked via `/`; never auto-loads |

For this fleet: `session-management` skill should be `user-invocable: false, disable-model-invocation: false` — it should auto-load silently when the model detects session context, but not pollute the slash menu.

---

## 4. Recommendations

### Immediate (Tier 1 Skills — 3 files)

**R1 — Implement `session-management` skill** in `.github/skills/session-management/SKILL.md`
- Encodes: scratchpad location convention, session-start encoding checkpoint, session-end Summary + Reflection pattern, prune threshold
- Replaces: multiple paragraphs currently duplicated across `AGENTS.md`, `docs/guides/session-management.md`, and 5+ agent bodies
- ABT impact: Every session that auto-loads this skill saves ~500 tokens of re-prompt overhead

**R2 — Implement `deep-research-sprint` skill** in `.github/skills/deep-research-sprint/SKILL.md`
- Encodes: Scout → Synthesizer → Reviewer → Archivist delegation sequence, D4 doc requirements, validate_synthesis.py gate
- Replaces: currently lives in `docs/guides/deep-research.md` + `executive-researcher.agent.md` body
- Cross-tool benefit: Copilot CLI and coding agent can execute research sprints without loading the executive-researcher agent

**R3 — Implement `conventional-commit` skill** in `.github/skills/conventional-commit/SKILL.md`
- Encodes: Conventional Commits type/scope table, this repo's body line-limit and co-author conventions from `CONTRIBUTING.md`, guardrail against `--no-verify`
- Cross-tool benefit: Available to coding agent during automated PRs; no agent context needed

### High Priority (Tier 2 Skills — 3 files)

**R4 — Implement `workplan-scaffold` skill** — `.github/skills/workplan-scaffold/SKILL.md`
- Delegates to `scripts/scaffold_workplan.py`; encodes naming convention, template path, commit instruction

**R5 — Implement `validate-before-commit` skill** — `.github/skills/validate-before-commit/SKILL.md`
- Encodes the 4-step pre-commit gate from `AGENTS.md`: ruff check + format, pytest fast subset, validate_agent_files, validate_synthesis (if applicable)

**R6 — Implement `source-cache` skill** — `.github/skills/source-cache/SKILL.md`
- Encodes the fetch-before-act posture: `uv run python scripts/fetch_source.py --check` before fetching, `scripts/fetch_all_sources.py` for pre-warm

### CI and Tooling

**R7 — Extend `validate_agent_files.py`** with a `--skills` mode (or create `validate_skill_files.py`) covering: frontmatter schema, name format, directory-name match, cross-reference density, minimum body length. Add to CI lint job alongside existing agent file validation.

**R8 — Skills cite MANIFESTO.md/AGENTS.md** — Enforce at CI time that every SKILL.md body contains at least one reference to `MANIFESTO.md` or `AGENTS.md`. This extends the encoding inheritance chain check to the skill layer.

### Deferral

**R9 — Agent plugin**: Defer until VS Code Agent Plugins GA. `.github/skills/` path works without packaging.

---

## 5. Implementation Path

### Phase 1 — Foundations (1 session)
1. Extend `validate_agent_files.py` with `--skills` mode (or new `validate_skill_files.py`)
2. Add tests to `tests/test_validate_agent_files.py` (or new test file)
3. Add CI lint step: `for f in .github/skills/**/SKILL.md; do validate_skill_files.py "$f"; done`
4. Implement 3 Tier 1 skills: `session-management`, `deep-research-sprint`, `conventional-commit`
5. Run validate_skill_files.py against all 3 before committing

### Phase 2 — Skill Coverage Expansion (1–2 sessions)
1. Implement Tier 2 skills: `workplan-scaffold`, `validate-before-commit`, `source-cache`
2. Add skills section to `docs/guides/agents.md` (composition rule, pattern catalog summary)
3. Add skills conventions to `AGENTS.md` (path convention, cross-reference requirement, validation command)
4. Run lychee pass on all new `.github/skills/` files to verify internal links

### Phase 3 — Evaluation and Plugin Consideration (future session, post-GA)
1. Audit agent bodies for additional skill extraction opportunities (Orchestrator, Planner, Review agents)
2. Evaluate VS Code Agent Skills Plugin packaging when feature reaches GA
3. Consider publishing `session-management` and `conventional-commit` skills to `github/awesome-copilot` community collection

---

## Sources

### Primary (External)

1. **VS Code Agent Skills documentation** (2026-03-04)
   - URL: https://code.visualstudio.com/docs/copilot/customization/agent-skills
   - Cache: `.cache/sources/code-visualstudio-com-docs-copilot-customization-agent-skill.md`
   - Relevance: Complete SKILL.md format reference, composition stack, plugin contribution point, three-level loading architecture

2. **agentskills.io homepage**
   - URL: https://agentskills.io
   - Cache: `.cache/sources/agentskills-io.md`
   - Relevance: Standard overview, adoption by VS Code/Copilot/Claude Code, Anthropic origin

3. **agentskills.io specification**
   - URL: https://agentskills.io/specification
   - Cache: `.cache/sources/agentskills-io-specification.md`
   - Relevance: Complete frontmatter field spec, `name` constraints, directory structure, progressive disclosure definition, validation via skills-ref

4. **VS Code Customization Overview**
   - URL: https://code.visualstudio.com/docs/copilot/customization/overview
   - Cache: `.cache/sources/code-visualstudio-com-docs-copilot-customization-overview.md`
   - Relevance: Full customization stack (skills, agents, hooks, prompts, MCP, plugins); canonical composition table

5. **Anthropic Claude Platform — Agent Skills Overview**
   - URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
   - Cache: `.cache/sources/platform-claude-com-docs-en-agents-and-tools-agent-skills-ov.md`
   - Relevance: Claude-side loading mechanism (bash filesystem reads), progressive disclosure table, three content types

6. **"Claude Skills and Subagents: Escaping the Prompt Engineering Hamster Wheel"** (Towards Data Science, Feb 2026)
   - URL: https://towardsdatascience.com/claude-skills-and-subagents
   - Cache: `.cache/sources/tds-claude-skills-subagents.md`
   - Relevance: Token economics of skills vs MCP; skills as lazy-loaded context; subagent context isolation; change-report skill worked example

### Endogenous

7. **[`MANIFESTO.md`](../../MANIFESTO.md)** — Foundational axioms: Endogenous-First, Algorithms Before Tokens, Local Compute-First; the encoding inheritance chain; biological substrate metaphors
8. **[`AGENTS.md`](../../AGENTS.md)** — Operational constraints: programmatic-first, encoding inheritance, session-start checkpoint, commit discipline, guardrails
9. **[`.github/agents/README.md`](../../.github/agents/README.md)** — Fleet catalog: 20+ agents, specialist-vs-extend decision tree, named patterns
10. **[`docs/guides/agents.md`](../guides/agents.md)** — Agent authoring guide, endogenous-sources requirement, handoff patterns
11. **[`scripts/validate_agent_files.py`](../../scripts/validate_agent_files.py)** — Existing CI validation logic; checks 1–4; MANIFESTO/AGENTS cross-reference check pattern
12. **[`docs/plans/2026-03-07-issue-60-agent-skills.md`](../plans/2026-03-07-issue-60-agent-skills.md)** — Workplan: 5-phase integration plan, Tier 1/Tier 2 candidate skills, acceptance criteria
