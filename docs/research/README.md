# Research Hub

This directory contains research synthesis documents, gap analyses, and exploratory findings for the EndogenAI Workflows project. Documents follow the **D4 Diátaxis-Agentic Hybrid** standard.

## Agent Navigation Guide

**Before running `list_dir` recursively:** read this file first. It maps each sub-folder to its scope and key entry points so you can descend directly to relevant content.

| Sub-folder | Domain | Key entry point |
|------------|--------|-----------------|
| [agents/](agents/) | Fleet design, agent taxonomy, skills integration | `agents/agent-taxonomy.md` |
| [methodology/](methodology/) | Values encoding, endogenic theory, axioms | `methodology/values-encoding.md` |
| [infrastructure/](infrastructure/) | Security, scripting, substrate mechanics | `infrastructure/security-threat-model.md` |
| [models/](models/) | LLM strategies, local inference, behavioral testing | `models/llm-tier-strategy.md` |
| [pm/](pm/) | Project management, GitHub workflows, product discovery | `pm/github-project-management.md` |
| [neuroscience/](neuroscience/) | Bubble clusters, neuroplasticity, holographic encoding | `neuroscience/values-encoding-neuroscience.md` |
| [sources/](sources/) | Raw per-source synthesis notes (D4 Pass 1) | — |

## Root-level Key Docs

- [OPEN_RESEARCH.md](OPEN_RESEARCH.md) — Active research queue and open questions
- [oss-documentation-best-practices.md](oss-documentation-best-practices.md) — OSS documentation patterns and Diátaxis benchmark
- [docs-ux-restructuring-strategy.md](docs-ux-restructuring-strategy.md) — This restructuring strategy document

## Search Tips (for agents)

Use these patterns to narrow scope before reading:
- `grep_search "values.*encoding" --includePattern "docs/research/methodology/**"` — endogenic theory docs
- `grep_search "security|SSRF|injection" --includePattern "docs/research/infrastructure/**"` — security docs
- `grep_search "fleet|agent.*taxonomy|skills" --includePattern "docs/research/agents/**"` — fleet design docs
