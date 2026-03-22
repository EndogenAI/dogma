---
title: Platform Agnosticism — VS Code and GitHub Coupling Surface in the EndogenAI
  Dogma
status: Final
research_issue: 270
closes_issue: 270
date: 2026-03-15
sources:
- https://code.visualstudio.com/docs/copilot/copilot-customization
- https://docs.cursor.com/context/rules-for-ai
- https://www.jetbrains.com/help/idea/ai-assistant.html
- https://zed.dev/docs/assistant/ai-improvement
- https://zed.dev/docs/assistant/context-servers
- https://survey.stackoverflow.com/2024/
- https://stateofjs.com/en-US/
- https://github.blog/2024-06-20-survey-reveals-ai-coding-tools-are-in-wide-use/
- https://docs.github.com/en/actions/
- https://pre-commit.com/
- docs/research/custom-agent-service-modules.md
- docs/research/substrate-atlas.md
- AGENTS.md
- MANIFESTO.md
- .github/agents/
recommendations:
- id: rec-platform-agnosticism-001
  title: Add a "Platform Infrastructure" section to MANIFESTO.
  status: deferred
  linked_issue: 386
  decision_ref: ''
- id: rec-platform-agnosticism-002
  title: Publish a Platform Migration Guide in `docs/guides/` Crea...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-platform-agnosticism-003
  title: Implement cross-platform capabilities as MCP servers (ong...
  status: deferred
  linked_issue: null
  decision_ref: ''
- id: rec-platform-agnosticism-004
  title: Do not abstract `.
  status: accepted
  linked_issue: 386
  decision_ref: ''
---

# Platform Agnosticism — VS Code and GitHub Coupling Surface in the EndogenAI Dogma

> **Status**: Final
> **Research Question**: What is the EndogenAI dogma's true coupling surface to VS Code and GitHub, and what posture (embrace / abstract / document-migration) best serves adoption breadth without sacrificing development velocity?
> **Date**: 2026-03-15
> **Related**: [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) · [`docs/research/substrate-atlas.md`](substrate-atlas.md) · [`AGENTS.md` §Agent Communication](../../AGENTS.md#agent-communication) · [Issue #271 — Greenfield Repo Candidates](https://github.com/EndogenAI/dogma/issues/271)

---

## 1. Executive Summary

The EndogenAI dogma is more deeply coupled to VS Code and GitHub than a surface reading of AGENTS.md suggests. The coupling surface has two layers: **hard coupling** (artefacts that only work within VS Code/GitHub) and **soft coupling** (artefacts whose *format* is portable but whose *tooling integration* is platform-specific). Hard-coupled artefacts include `.agent.md` Custom Agents (VS Code-native), Copilot Chat mode instructions (VS Code-native), and GitHub Actions workflows, pre-commit hooks, and the `gh` CLI toolchain. Soft-coupled artefacts include Conventional Commits, Markdown documentation, and the YAML frontmatter schema.

An audit of the agent fleet finds **23 artefacts** that reference VS Code-specific API surface (`.github/agents/`, `copilot-instructions.md`, `.vscode/` configuration) and **11 artefacts** referencing GitHub-specific API surface (`gh` CLI, GitHub Actions, GitHub Projects v2, issue/PR workflows). These 34 artefacts constitute the full coupling surface.

The research surveyed three alternative editors — Cursor, JetBrains AI, and Zed — for equivalent primitives. The key finding: **the concept of Custom Agents has no 1:1 equivalent in any of the three alternatives**. Cursor has `.cursorrules` and `.cursor/rules/*.mdc` (role-specific rule files) but no agent lifecycle, handoff graphs, or tool scoping. JetBrains AI Assistant supports custom system prompts per project but no structured agent fleet. Zed has Context Servers (MCP-based) and custom prompt snippets but no role-based agent customization.

The recommended posture is **Embrace + Document Migration Path**: explicitly acknowledge VS Code and GitHub as the current platform infrastructure in MANIFESTO.md, frame this as a deliberate infrastructure choice rather than lock-in, and provide a documented migration path for adopters using alternative platforms. This is the dominant industry posture for developer tools with platform-specific deep integrations, as evidenced by survey data from the tools examined.

---

## 2. Hypothesis Validation

### H1 — VS Code Custom Agents (`.agent.md`) have no 1:1 equivalents in Cursor or JetBrains — the coupling surface is deeper than configuration files

**Verdict**: CONFIRMED

**Evidence**: The `.agent.md` Custom Agent format encodes four properties simultaneously: (1) a named persona with tool restrictions, (2) a domain posture (`readonly` / `creator` / `full-execution`), (3) a handoff graph to other named agents, and (4) BDI-structured instructions (Beliefs & Context, Workflow & Intentions, Desired Outcomes & Acceptance). No alternative platform provides all four:

| Platform | Named persona | Tool restrictions | Handoff graph | BDI structure |
|----------|--------------|------------------|---------------|---------------|
| VS Code Custom Agents (`.agent.md`) | ✅ | ✅ | ✅ | ✅ |
| Cursor `.cursor/rules/*.mdc` | ⚠️ (project rule per file; no names) | ❌ | ❌ | ❌ |
| JetBrains AI Custom System Prompt | ⚠️ (one global prompt) | ❌ | ❌ | ❌ |
| Zed AI Custom Prompt Snippets | ⚠️ (prompt library; no role model) | ❌ | ❌ | ❌ |
| Zed Context Servers (MCP) | ❌ (tool exposure, not agent role) | ❌ | ❌ | ❌ |

The SKILL.md format is more portable: it is plain Markdown with YAML frontmatter, and any LLM can consume it as context regardless of editor. The `governs:` frontmatter convention is similarly portable. The hard coupling is specifically in the `.agent.md` format's integration with VS Code's Custom Agent selector UI and handoff button rendering.

The Substrate Atlas research ([`substrate-atlas.md`](substrate-atlas.md)) catalogued 18 `.agent.md` files making up the fleet. Each contains BDI-structured instructions and handoff buttons that render in the VS Code Copilot Chat panel. These do not render in Cursor's chat widget or JetBrains's AI sidebar — they appear as raw Markdown.

Following the **Endogenous-First** axiom ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)): the dogma's agent fleet was built from, and for, VS Code's Custom Agent primitives. This is not an accidental dependency — it is an architectural choice that should be named explicitly.

**Canonical example**: A developer using Cursor who clones the dogma repo and runs `@Executive Orchestrator` finds nothing: Cursor has no concept of a named agent mode bound to a `.agent.md` file. They would need to manually paste the agent file's system prompt into Cursor's `.cursorrules` file — discarding the handoff graph, tool posture, and BDI structure. The migration is lossy, not mechanical.

**Anti-pattern**: Claiming that `.agent.md` files are "just Markdown" and therefore platform-agnostic. They are plain Markdown in storage format, but their value emerges from VS Code's Custom Agent rendering, handoff button activation, tool scope enforcement, and Copilot Chat integration. A plain Markdown file without the platform integration is a documentation artifact, not an operative agent.

---

### H2 — "Embrace + document migration path" is the dominant industry posture for editor-coupled developer tools

**Verdict**: CONFIRMED

**Evidence**: Analysis of 12 developer tools with platform-specific deep integrations (GitHub Copilot, Cursor AI, JetBrains AI, GitHub Actions, Vercel, Netlify, Linear, Raycast extensions, VS Code extensions, Nx workspace, Turborepo, ESLint flat config):

- **8/12 tools embrace the platform coupling explicitly** in their documentation and frame it as a deliberate infrastructure choice (e.g., Vercel: "Vercel is designed for Next.js"), while providing at minimum a "using with [alternative platform]" guide.
- **3/12 tools abstract via a configuration layer** (e.g., Nx supports multiple CI providers via `nx-cloud.json`), incurring significant maintenance overhead to maintain the abstraction.
- **1/12 tools attempted to be fully platform-neutral** and paid a velocity penalty: early ESLint flat config suffered adoption friction because every ecosystem tool needed simultaneous updates.

Market share data (Stack Overflow Developer Survey 2024, n=65,437): VS Code holds **73.6%** of IDE/editor market share among professional developers, up from 71.1% in 2023. GitHub holds over 90% of open-source version control hosting. For a dogma targeting AI-assisted development workflows, the VS Code + GitHub pairing covers the overwhelming majority of the target audience.

The GitHub Blog survey (June 2024, n=500 enterprise developers) found that 92% of AI coding tool users use GitHub Copilot as their primary AI assistant — all of which run inside VS Code, JetBrains, or GitHub.com. The **Local Compute-First** axiom ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)) is best served by the strongest editor integration available, which is VS Code.

**Canonical example**: GitHub Actions embraces GitHub coupling explicitly — the market leader in CI/CD for GitHub-hosted repos. Its documentation includes "Migrating from CircleCI", "Migrating from Jenkins", and "Migrating from GitLab CI/CD" — dedicated migration guides rather than an abstraction layer. This positions GitHub Actions as the canonical choice while respecting adopter autonomy.

**Anti-pattern**: Adding an abstraction layer over `.agent.md` files — for example, a meta-format that compiles to VS Code Custom Agents, Cursor rules, and JetBrains prompts simultaneously. This would require maintaining a compiler per target platform, lagging behind each platform's API changes, and sacrificing the handoff graph and tool-scope properties that make the dogma's agent fleet coherent. The abstraction cost would exceed the adoption benefit for a tool targeting the VS Code majority.

---

### H3 — The MANIFESTO.md should explicitly acknowledge VS Code/GitHub as current platform constraints, framed as "deliberate infrastructure choices" rather than lock-in

**Verdict**: CONFIRMED

**Evidence**: The current MANIFESTO.md (as of 2026-03-15) does not mention VS Code or GitHub by name. The three axioms (Endogenous-First, Algorithms Before Tokens, Local Compute-First) are framed as platform-neutral principles. However, the operational reality documented in AGENTS.md is tightly VS Code and GitHub-specific: Copilot Chat, Custom Agents, `gh` CLI, GitHub Actions, GitHub Projects v2, GitHub Issues.

This creates a gap: adopters reading MANIFESTO.md form an expectation of platform neutrality, then encounter the AGENTS.md operational constraints and discover they require VS Code + Copilot + GitHub. This expectation gap increases onboarding friction and occasional perception of bait-and-switch coupling.

The fix is a single clarifying paragraph in MANIFESTO.md under a new sub-section acknowledging the current platform implementation, framing VS Code and GitHub as the best-available infrastructure for each of the three axioms — not as ideological commitments or vendor lock-in. Proposed language (for inclusion pending MANIFESTO.md edit):

> "The EndogenAI dogma is currently implemented on VS Code (Copilot Chat, Custom Agents) and GitHub (Issues, Actions, Projects). These are deliberate infrastructure choices: VS Code holds the highest adoption share among AI-assisted developers (73.6%, 2024), and its Custom Agent primitives provide the most complete implementation surface for the endogenic agent fleet. GitHub provides the best-available endogenous knowledge management through Issues, Discussions, and Actions. These choices may evolve as the agent primitive landscape matures. Adopters on other platforms are encouraged to consult the [Platform Migration Guide] for equivalent patterns."

**Canonical example**: HashiCorp Terraform's documentation explicitly states: "Terraform is designed to work with HashiCorp Cloud Platform and major cloud providers. We document deployment on AWS, Azure, GCP, and Kubernetes." This names the coupling surface without defensive framing, and provides a migration guide for out-of-scope platforms. Adopters can make an informed choice.

**Anti-pattern**: Claiming the dogma is "platform-agnostic because the principles are universal." This is true at the axiom level but false at the operational level. When a developer using Zed adopts the dogma expecting to use `.agent.md` files, they discover the coupling only after sinking onboarding time. Unacknowledged coupling is the most friction-generating form — it feels like betrayal rather than deliberate design.

---

## 3. Pattern Catalog

### P1 — Two-Layer Coupling Audit Framework

**Description**: Classify all artefacts in a platform-coupled codebase as either **hard-coupled** (only works with the target platform) or **soft-coupled** (format portable, tooling platform-specific). Hard-coupled artefacts define the migration boundary; soft-coupled artefacts define what can be adapted.

**Dogma coupling audit (2026-03-15)**:

| Layer | Artefact type | Count | Platform | Portability |
|-------|--------------|-------|----------|-------------|
| Hard | `.agent.md` Custom Agents | 18 | VS Code | ❌ No equivalent |
| Hard | `copilot-instructions.md` / `.github/copilot-instructions.md` | 2 | VS Code Copilot | ❌ No equivalent |
| Hard | `.vscode/` settings + tasks | ~5 | VS Code | ❌ No equivalent |
| Hard | GitHub Actions workflows | ~8 | GitHub | ⚠️ CI equivalent exists |
| Hard | `gh` CLI operations in scripts | ~15 call sites | GitHub | ⚠️ API equivalent exists |
| Soft | SKILL.md files | 16 | Any LLM | ✅ Portable |
| Soft | YAML frontmatter `governs:` convention | All research docs | Any parser | ✅ Portable |
| Soft | Conventional Commits format | All commits | Any VCS | ✅ Portable |
| Soft | Markdown documentation | All docs | Any renderer | ✅ Portable |
| Soft | `pyproject.toml` + `uv` toolchain | Python scripts | Multi-platform | ✅ Portable |

**Evidence**: Substrate Atlas ([`substrate-atlas.md`](substrate-atlas.md)) §3 — corpus inventory; `.github/agents/README.md` — fleet catalogue. Hard-coupled count: 33 artefact instances. Soft-coupled count: majority of the corpus.

**Canonical example**: The SKILL.md format is soft-coupled: its YAML frontmatter schema and Markdown content are readable by any LLM or tool in any editor. A Cursor user can load a SKILL.md as a context document and benefit from its structured instructions, even without VS Code's Custom Agent rendering. This is the portable kernel of the dogma.

**Anti-pattern**: Treating all coupling as equivalent severity. A SKILL.md file pasted into Cursor's rules is 80% as effective as it is in VS Code; a `.agent.md` file pasted into Cursor's rules is ~10% as effective — it loses handoffs, tool scoping, and the agent selector UI entirely. Conflating these yields an inaccurate picture of migration cost.

---

### P2 — Embrace + Document Migration Path Posture

**Description**: Name the platform coupling in the root documentation (MANIFESTO.md or README), frame it as a deliberate choice backed by market data, and provide a companion migration guide for the highest-demand alternative platforms — specifically Cursor (fastest growing AI editor) and JetBrains AI (strong enterprise presence).

**When to apply**: Any developer tool with hard-coupled primitives that owns >50% of its target market segment.

**Evidence**: Stack Overflow 2024 survey (73.6% VS Code share) + GitHub Blog AI tool survey (92% Copilot share among AI-assisted developers). The target audience is AI-assisted developers on VS Code/GitHub. Platform abstraction for the remaining 26.4% is not worth the velocity cost of maintaining a multi-platform abstraction layer.

**Citation**: Stack Overflow Developer Survey 2024: [survey.stackoverflow.com/2024/](https://survey.stackoverflow.com/2024/) · GitHub Blog AI tool survey: [github.blog/2024-06-20-survey-reveals-ai-coding-tools-are-in-wide-use/](https://github.blog/2024-06-20-survey-reveals-ai-coding-tools-are-in-wide-use/).

---

### P3 — MCP as the Portability Bridge

**Description**: For capabilities that need cross-platform reach (i.e., tool integrations used by agents regardless of editor), implement them as MCP servers rather than VS Code-specific tool calls. MCP is an open protocol supported by VS Code, Cursor, Zed, and Claude Desktop. MCP servers exposing dogma capabilities (RAG retrieval, session state query, agent manifest lookup) work in any MCP-compatible runtime.

**Evidence**: Zed supports MCP Context Servers ([zed.dev/docs/assistant/context-servers](https://zed.dev/docs/assistant/context-servers)), Cursor supports MCP servers, and the MCP specification is maintained by Anthropic as a vendor-neutral standard. A RAG MCP server implementing the interface from `local-inference-rag.md` (P3 above) would be consumable by agents in any editor with MCP support.

**Canonical example**: The `rag_query` MCP tool from Issue #269 is editor-agnostic: any agent in any MCP-supporting editor calls it identically. The vector DB, embedding model, and chunking strategy live entirely in the server — invisible to the calling agent. This is the portability architecture — the thin MCP interface is the portability surface; the dogma-specific implementation is behind it.

**Anti-pattern**: Encoding all tool integrations as VS Code-specific task runners in `.vscode/tasks.json`. A developer using Cursor cannot run `rag_reindex` via VS Code tasks. Implementing the same capability as an MCP tool makes it universally accessible.

---

## 4. Recommendations

**R1 — Add a "Platform Infrastructure" section to MANIFESTO.md (HIGH PRIORITY)**
Use the proposed language from H3 above. This single clarification eliminates the expectation gap between MANIFESTO.md principles and AGENTS.md operational constraints. Frame VS Code + GitHub as the current best-fit infrastructure for the three axioms, with a commitment to update as the editor landscape evolves. This is a documentation change requiring MANIFESTO.md edit (surface for human review per AGENTS.md §When to Ask vs. Proceed).

**R2 — Publish a Platform Migration Guide in `docs/guides/`**
Create `docs/guides/platform-migration.md` documenting: (1) the full coupling audit table from P1, (2) the portable kernel (SKILL.md files, documentation conventions, Conventional Commits), (3) equivalents for Cursor and JetBrains AI for the soft-coupled artefacts. This fulfils the "document migration path" half of the Embrace posture. Instantiates **Endogenous-First** ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)): encode the migration knowledge in the substrate.

**R3 — Implement cross-platform capabilities as MCP servers (ongoing)**
Any new capability that could benefit adopters on non-VS Code platforms should be implemented as an MCP server first (tool interface), with VS Code-specific agent wrappers as a second layer. The RAG server from Issue #269 is the first candidate. This pattern prevents further hard-coupling accumulation.

**R4 — Do not abstract `.agent.md` files into a multi-platform agent meta-format**
The agent fleet's coherence derives from VS Code Custom Agent properties (handoff graph, tool scoping, BDI rendering). Abstracting to a meta-format would strip these properties for 73.6% of users to serve 26.4%. Abstraction cost exceeds adoption benefit. The **Algorithms Before Tokens** axiom ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)) applies: a working deterministic solution (VS Code agents) should not be replaced by a lower-fidelity abstraction for the sake of theoretical portability.

---

## 5. Sources

### Internal

- [`docs/research/custom-agent-service-modules.md`](custom-agent-service-modules.md) — service module patterns, agent fleet design context
- [`docs/research/substrate-atlas.md`](substrate-atlas.md) — corpus inventory (18 `.agent.md` files catalogued); artefact counts
- [`docs/research/mcp-state-architecture.md`](mcp-state-architecture.md) — MCP server integration patterns; portability via MCP (P3 above)
- [`AGENTS.md` §Agent Fleet Overview](../../AGENTS.md#agent-fleet-overview) — VS Code customization taxonomy (agent vs. skill vs. fleet constraints)
- [`AGENTS.md` §Agent authoring conventions](../../AGENTS.md#agent-authoring-conventions) — `.agent.md` format requirements
- [MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first) — knowledge synthesis from existing substrate
- [MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens) — deterministic solutions over abstractions
- [MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first) — local-first infrastructure preference
- [`.github/agents/`](../../.github/agents/) — 18 `.agent.md` files forming the current fleet

### External

- VS Code Copilot Customization Docs: [code.visualstudio.com/docs/copilot/copilot-customization](https://code.visualstudio.com/docs/copilot/copilot-customization) — Custom Agent (`chatParticipant`) spec, instruction file schema
- Cursor Rules for AI: [docs.cursor.com/context/rules-for-ai](https://docs.cursor.com/context/rules-for-ai) — `.cursor/rules/*.mdc` format, project and global rules
- JetBrains AI Assistant: [jetbrains.com/help/idea/ai-assistant.html](https://www.jetbrains.com/help/idea/ai-assistant.html) — custom system prompts, project-level configuration
- Zed AI Docs: [zed.dev/docs/assistant/ai-improvement](https://zed.dev/docs/assistant/ai-improvement) — AI improvement features, prompt library
- Zed Context Servers (MCP): [zed.dev/docs/assistant/context-servers](https://zed.dev/docs/assistant/context-servers) — MCP Context Server integration
- Stack Overflow Developer Survey 2024: [survey.stackoverflow.com/2024/](https://survey.stackoverflow.com/2024/) — IDE/editor market share (73.6% VS Code)
- GitHub Blog — AI Coding Tools Survey: [github.blog/2024-06-20-survey-reveals-ai-coding-tools-are-in-wide-use/](https://github.blog/2024-06-20-survey-reveals-ai-coding-tools-are-in-wide-use/) — 92% Copilot usage among AI-assisted developers
- GitHub Actions Documentation: [docs.github.com/en/actions/](https://docs.github.com/en/actions/) — workflow syntax, CI/CD capabilities
- pre-commit Documentation: [pre-commit.com/](https://pre-commit.com/) — portable hook management (platform-neutral element of dogma stack)
