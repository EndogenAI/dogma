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
| `docs/plans/` | Committed workplan files for multi-phase sessions — one per session, tracked in git history |
| `docs/research/` | Issue-specific synthesis documents; each closes a GitHub research issue |
| `docs/research/sources/` | Per-source synthesis reports — one per surveyed source; committed to git |
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

### 1. Per-Source Synthesis Reports — `docs/research/sources/<slug>.md`

One file per surveyed source, written by the **Research Synthesizer** (one agent invocation
per source). Each file is a full academic-style synthesis report — not a summary or index
card. The format follows standard synthesis note conventions used in systematic literature
reviews: citation, research question, theoretical framework, methodology, key claims with
quotes, critical assessment with an evidence quality rating, cross-source connections, and
project relevance. These reports are the **atomic unit** referenced by issue synthesis
documents.

```markdown
---
slug: "<slug>"
title: "<source title>"
url: "<source url>"
authors: "<Author(s) or publishing organisation>"
year: "<YYYY>"
type: paper | documentation | blog | cookbook | repo
topics: [<tag1>, <tag2>]
cached: true
evidence_quality: strong | moderatevidence | evidence_qualityntation
evidence_quality: strong | moderateviden Citaevidence_quality: uestioevidence_quality:eoevidence_quality: strong | moderateviden Citaevidence_quality: uestioeviden Crevidence_quality: strong | moderateviden Citaevidence_quality: uestioevidence_quality:ed By
```

Full section guidance lives in
[`.github/agents/research-synthesizer.agent.md`](../.github/agents/research-synthesizer.agent.md)
(Pass 1 format template). Minimum length: **100 lines**.

`## Referenced By` is populated automatically by `scripts/link_source_stubs.py` —
never edit it manually.

### 2. Issue Synthesis — `docs/research/<slug>.md`

One file per research issue, written by the **Research Synthesizer** during the third pass
(Pass 3). Draws conclusions across all per-source synthesis documents for this question.
**Must reference the per-source synthesis documents** using relative links rather than
re-summarising source content inline.

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
| Per-source synthesis reports | `docs/research/sources/<slug>.md` | **tracked** |
| Issue synthesis documents | `docs/research/<slug>.md` | **tracked** |
