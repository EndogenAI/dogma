---
slug: towardsdatascience-com-claude-skills-and-subagents
title: "Claude Skills and Subagents: Escaping the Prompt Engineering Hamster Wheel"
url: https://towardsdatascience.com/claude-skills-and-subagents
cached: true
type: article
topics: [Claude-Skills, lazy-loading, token-economics, subagents, progressive-disclosure]
date_synthesized: 2026-03-06
---

## Summary

Ruben Broekx (Towards Data Science, February 2026) explains Claude Skills — Anthropic's reusable, lazy-loaded instruction sets that solve context bloat through three-level progressive disclosure: metadata stub (~100 tokens, loaded at startup), skill body (~5,000 tokens, loaded on invocation), and referenced files (loaded on demand). Compares the economics of skills vs. MCP tools vs. subagents. States that the full instruction set is never dumped into context upfront, solving the "prompt engineering hamster wheel" of repetitive prompting.

## Key Claims

- "Skills are reusable, lazy-loaded, and auto-invoked instruction sets that use progressive disclosure across three levels: metadata, body, and referenced files. This minimizes the upfront cost by preventing to dump everything into the context window."
- Metadata (max 64 chars name, max 1,024 chars description): ~100 tokens per skill — "negligible overhead even with hundreds of skills registered."
- Skill body: up to ~5,000 tokens, enters context window only when agent determines the skill is relevant.
- Referenced files: "practically no limit" — agent reads on demand when instructions reference them and the task requires it.
- Article reflects state of Claude Skills as of February 2026; notes "AI moves fast, so some details may be outdated."

## Relevance to EndogenAI

Canonical source for the skills manifest generator pattern. The three-level progressive disclosure model validates the EndogenAI approach of separating agent metadata (frontmatter) from full agent bodies — a `generate_agent_manifest.py` output implementing level-1 stubs would allow orchestrators to load only relevant agent instructions rather than the full fleet at session start. See also `tds-claude-skills-subagents` (cached duplicate of this article).

## Referenced By

- [agentic-research-flows](../agentic-research-flows.md)
