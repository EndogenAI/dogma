---
slug: "docs-anthropic-com-en-docs-build-with-claude-prompt-caching"
title: "Prompt Caching"
url: "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching"
authors: "Anthropic"
year: "2025"
type: docs
topics: [prompt-caching, context-management, cost-optimisation, T1-instruction, cache-control]
cached: true
evidence_quality: authoritative
date_synthesized: "2026-03-08"
---

## Citation

Anthropic. (2025). *Prompt Caching*. Anthropic Documentation.
https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
(Accessed 2026-03-08.)

## Summary

Official Anthropic documentation for the prompt caching feature (`cache_control` breakpoints). Covers supported models, cache TTL (5 minutes; ephemeral), pricing (write: 1.25× base; read: 0.1× base), minimum cacheable token lengths (1024 for Claude 3.5+), and best practices for cache structure (static content first, dynamic content last).

## Relevance to context-budget-balance.md

Referenced for T1 instruction caching as a retrieval-cost mitigation strategy. Prompt caching allows the T1 layer (AGENTS.md + agent files + mode instructions) to be cached across turns, reducing the per-turn token cost of large instruction payloads. Relevant to the R1 recommendation in context-budget-balance.md regarding instruction compression and budget governance.
