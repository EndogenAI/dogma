# docs/AGENTS.md

> This file narrows the constraints in the root [`AGENTS.md`](../AGENTS.md) for documentation work.
> It does not contradict any root constraint — it only adds documentation-specific rules.

---

## Purpose

This file governs the creation, review, and maintenance of documentation in `docs/`.

---

## Documentation-First Requirement

Every agent action that changes a workflow, script, or agent file must produce a corresponding
documentation update. The sequence is:

1. Change made → commit
2. Documentation updated → commit
3. PR opened linking both commits

**Never merge a script or agent change without updating the relevant `docs/` files.**

---

## What Lives in `docs/`

| Path | Purpose |
|------|---------|
| `docs/guides/` | Step-by-step guides for working with agents, scripts, and workflows |
| `docs/research/` | Issue-specific synthesis documents; each closes a GitHub research issue |
| `docs/research/sources/` | Per-source synthesis stubs — one per surveyed source; committed to git |
| `docs/research/OPEN_RESEARCH.md` | Open research queue, seed references, and gate deliverables |

---

## Writing Standards

- Use clear, concise Markdown
- Every guide should have a "Why" section explaining the motivation
- Code blocks must include the language identifier (` ```bash `, ` ```python `, etc.)
- Link to related docs, agents, and scripts by relative path
- Research docs should distinguish between "established fact", "working hypothesis", and "open question"

---

## Research Output Structure

The research workflow produces two complementary layers of documentation:

### 1. Per-Source Stubs — `docs/research/sources/<slug>.md`

One file per surveyed source, written by the **Research Synthesizer** during the first pass.
Each stub is a structured distillation: source metadata, key claims, methodology notes,
and relevance to the EndogenAI project. These stubs are the **atomic unit** that issue
synthesis documents reference. Writing them once prevents re-summarising the same source
across multiple syntheses.

```markdown
---
slug: "<slug>"
title: "<source title>"
url: "<source url>"
cached: true
type: paper | blog | docs | repo | article
topics: [<tag1>, <tag2>]
date_synthesized: "<YYYY-MM-DD>"
---

## Summary

<2-4 sentences on what this source covers>

## Key Claims

- <claim 1 — exact quote preferred>
- <claim 2>
- <claim 3>

## Relevance to EndogenAI

<1-3 sentences on how this source applies to the EndogenAI Workflows project>

## Referenced By

<!-- Populated by issue synthesis pass; use relative links -->
- [docs/research/<topic>.md](../<topic>.md)
```

### 2. Issue Synthesis — `docs/research/<slug>.md`

One file per research issue, written by the **Research Synthesizer** during the second pass.
Draws conclusions across all per-source stubs for this question. **Must reference the
per-source stubs** using relative links rather than re-summarising source content inline.

```markdown
# <Research Topic>

> **Status**: Draft — pending review  
> **Research Question**: <question>  
> **Date**: <YYYY-MM-DD>  
> **Sources**: see [docs/research/sources/](sources/)

## Summary
## Key Findings
## Recommendations
## Open Questions
## Sources
```

Research is the bridge between external knowledge and endogenous encoding. Every issue
synthesis should end with actionable recommendations — what should be adopted, scripted,
or documented as a result of the research.

### Git Tracking

| Artifact | Location | Git status |
|----------|---------|------------|
| Raw HTML→Markdown distillations | `.cache/sources/<slug>.md` | **gitignored** (regenerable) |
| Source manifest (what has been fetched) | `.cache/sources/manifest.json` | **tracked** |
| Per-source synthesis stubs | `docs/research/sources/<slug>.md` | **tracked** |
| Issue synthesis documents | `docs/research/<slug>.md` | **tracked** |
