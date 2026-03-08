# ADR-006: Agent Skills Adoption

**Date**: 2026-03-07
**Status**: Accepted
**Deciders**: EndogenAI core team

---

## Context

The VS Code customization stack has three first-class primitives: always-on instructions (`.instructions.md`), Roles (`.agent.md`; VS Code: Custom Agents), and skills (`SKILL.md`). This repository has deployed agents and always-on instructions but has not adopted skills, leaving the fleet with a three-primitive gap. Workflow procedures — session management, research sprint orchestration, conventional commit conventions — are currently embedded in agent bodies or distributed across `docs/guides/`. This creates two problems:

1. **Duplication and drift**: A procedure embedded in an agent body cannot be reused by another agent or by a non-VS-Code tool (Copilot CLI, Claude Code) without copying. When the procedure changes, every copy must be updated.
2. **Token inefficiency**: Procedures carried in always-on instructions or large agent bodies are loaded on every request, regardless of relevance. This violates the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../MANIFESTO.md): interactive token burn for knowledge that could be encoded once and loaded on demand.

**Agent Skills** (agentskills.io open standard, developed by Anthropic) address both problems. Skills are `SKILL.md` files stored in `.github/skills/` and discovered automatically by GitHub Copilot. Only the `name` and `description` frontmatter (~100 tokens per skill) are loaded at startup; the full skill body loads only when relevant. The spec is cross-ecosystem and agent-agnostic — the same `SKILL.md` works in GitHub Copilot, Copilot CLI, and Claude Code (via `.claude/skills/`).

Skills extend the encoding inheritance chain from four layers to six (adding both the subdirectory AGENTS.md tier and the SKILL.md tier):

| Layer | Format | Role |
|-------|--------|------|
| `MANIFESTO.md` | Constitution | Foundational axioms |
| `AGENTS.md` (root) | Operational constraints | Behavioural translation |
| **`AGENTS.md` (subdirectory)** | **Narrowing constraints** | **Scope-specific rules for `docs/`, `.github/agents/`, etc.** |
| `.agent.md` files | Roles (VS Code: Custom Agents) | Role-specific persona and capabilities |
| **`SKILL.md` files** | **Skill procedures** | **Reusable tactical knowledge** |
| Session behaviour | Enactment | Observable output |

This is the endogenic alignment: skills are a stronger instantiation of *Algorithms Before Tokens* than any single script, because they cover the entire instruction class of repeated tasks, are agent-agnostic, and add capability without proportional context cost.

---

## Decision

### 1. Agents vs Skills — Composition Rule

**Agents encode *who does a task***; **skills encode *how a task is done***.

| Primitive | Encodes | Keep as agent when | Becomes a skill when |
|-----------|---------|-------------------|---------------------|
| `.agent.md` | Persona, posture, tool restrictions, handoff graph | Unique posture, handoff logic, or tool restriction is required | — |
| `SKILL.md` | Workflow procedures, conventions, templates | — | The procedure is needed by more than one agent or tool |

**Extraction rule**: any procedure in an agent body that a *different* agent or AI tool could also benefit from — without needing that agent's posture or tool restrictions — is a skill candidate. Do not extract a procedure until the agent body has been updated to reference the new skill.

### 2. Location and Naming

Skills live at `.github/skills/<skill-name>/SKILL.md`. The directory name must exactly match the `name` field in the frontmatter (lowercase, hyphens only, no leading/trailing/consecutive hyphens, 1–64 chars). Do not store skills in `.github/agents/` or `docs/`.

### 3. Encoding Inheritance Extension

Every `SKILL.md` body must cite `AGENTS.md` as its governing constraint document. This anchors skills to the encoding inheritance chain and makes encoding-fidelity auditable via CI. The governing axiom citation must appear in the first substantive section of the body (e.g., *"This skill enacts the Algorithms Before Tokens axiom from [`MANIFESTO.md`](../../MANIFESTO.md)."*).

### 4. Tier 1 Skills — Immediate Implementation

Three skills are approved for immediate implementation:

| Skill name | Encodes | Source material |
|------------|---------|-----------------|
| `session-management` | Scratchpad protocol, encoding checkpoints, session-start/end procedure | `docs/guides/session-management.md`, `AGENTS.md § Agent Communication` |
| `deep-research-sprint` | Scout → Synthesizer → Reviewer → Archivist orchestration | `docs/guides/deep-research.md` |
| `conventional-commit` | Conventional Commits + endogenic commit discipline | `CONTRIBUTING.md § Commit Discipline`, `AGENTS.md § Commit Discipline` |

### 5. CI Validation

Extend `validate_agent_files.py` with a `--skills` flag, or create a parallel `validate_skill_files.py`, that enforces:

1. Valid YAML frontmatter with required fields: `name`, `description`
2. `name` format: `^[a-z][a-z0-9-]*[a-z0-9]$`, max 64 chars, no consecutive hyphens
3. `name` matches parent directory name
4. At least one cross-reference to `AGENTS.md` or `MANIFESTO.md` in the body (encoding inheritance check)
5. Minimum body length: ≥ 100 chars (after frontmatter)

The CI `lint` job must run this check on every PR that touches `.github/skills/`.

### 6. Invocability Defaults

Use VS Code-specific frontmatter fields where appropriate; they degrade gracefully on other agents:

| Skill | `user-invocable` | `disable-model-invocation` | Rationale |
|-------|-----------------|--------------------------|-----------|
| `session-management` | `false` | `false` | Auto-load silently; no slash-menu pollution |
| `deep-research-sprint` | `true` | `false` | Explicit invocation preferred; auto-load also useful |
| `conventional-commit` | `true` | `false` | Commit work needs explicit invocation in most contexts |

---

## Consequences

### Positive

- **Portable encoding**: Skill procedures work in GitHub Copilot, Copilot CLI, and Claude Code without modification. A `.claude/skills/` symlink or duplicate is the only addition needed for Claude Code support.
- **Token efficiency**: At 20 registered skills, baseline overhead is ~2,000 tokens (metadata only). Compare to the same knowledge in always-on instructions: ~20,000+ tokens always loaded. Per the *Algorithms Before Tokens* axiom, this is a meaningful reduction in session-time token burn.
- **Composability**: Agent bodies become leaner. The composition rule (agent = frame, skill = procedure) is explicit and testable. Future agents can reference existing skills rather than re-embedding their procedures.
- **Cross-agent reuse**: Any skill can be triggered by any agent or tool in the fleet without re-authoring the procedure. Updates to a skill propagate automatically to all consumers.
- **Five-layer encoding chain**: Skills extend the inheritance chain, increasing the system's capacity to encode institutional knowledge in durable, programmatic form rather than in interactive session prompts.

### Negative

- **New file type to maintain**: `SKILL.md` files must be kept current as procedures evolve. A skill that drifts from the guide it encodes is worse than no skill (agents may follow the skill over the guide).
- **CI extension required**: `validate_agent_files.py` must be extended (or `validate_skill_files.py` created) before skills can be reliably shipped. Merging skills without CI validation removes the encoding-fidelity gate.
- **Boundary discipline required**: The agents-vs-skills boundary is precise but not self-enforcing. Teams must apply the extraction rule consistently. A procedure incorrectly left in an agent body that is also in a skill creates a divergence risk. The rule: the skill is canonical; the agent references it.
- **Plugin path is deferred**: The agentskills.io plugin packaging mechanism (VS Code extension with `chatSkills`) is Preview and adds distribution overhead not yet warranted for a single-repo skill set. This decision does not include plugin publishing.

### Migration Path

1. Implement `validate_skill_files.py` (or extend `validate_agent_files.py --skills`) with CI integration.
2. Implement the three Tier 1 skills (`session-management`, `deep-research-sprint`, `conventional-commit`) in `.github/skills/`.
3. For each Tier 1 skill, identify agent bodies that embed the same procedure and replace the embedded text with a reference to the skill. Do not remove the embedded procedure from an agent body until the skill is merged and CI passes.
4. After Tier 1 ships, audit remaining agent bodies for further extraction candidates. Apply the extraction rule: if another agent or tool could use it, extract it.

---

## References

- [`docs/research/agent-skills-integration.md`](../research/agent-skills-integration.md) — Phase 1 research synthesis; all findings in this ADR are derived from it
- [`MANIFESTO.md`](../../MANIFESTO.md) — *Algorithms Before Tokens* axiom
- [`AGENTS.md`](../../AGENTS.md) — guiding constraints; governs all skill bodies
- [`docs/guides/agents.md`](../guides/agents.md) — agent fleet guide
- [`docs/guides/session-management.md`](../guides/session-management.md) — source material for `session-management` skill
- [`docs/guides/deep-research.md`](../guides/deep-research.md) — source material for `deep-research-sprint` skill
- [`scripts/validate_agent_files.py`](../../scripts/validate_agent_files.py) — existing CI gate; extension target
- Issue [#60](https://github.com/EndogenAI/Workflows/issues/60) — decision trigger
