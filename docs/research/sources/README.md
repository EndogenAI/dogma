# docs/research/sources/

Per-source synthesis stubs — one file per research source surveyed by the research fleet.

Each file is a structured distillation of a single external source: its key claims, methodology
notes, and relevance to the EndogenAI project. These stubs are the **atomic unit** that issue
synthesis documents (`docs/research/*.md`) reference and build upon.

---

## Why This Exists

When the same source is relevant to multiple research questions — which happens as the project
matures — having a dedicated stub prevents duplication and keeps issue syntheses lean. Instead
of re-summarising `arXiv:2512.05470` in every synthesis that cites it, you write the summary
once here and link to it.

This also produces a **cumulative source knowledge base**: every source ever surveyed by the
research fleet is catalogued here. Over time this becomes the project's annotated bibliography.

---

## File Naming

Files are named by **slug** — the same slug used in `.cache/sources/manifest.json`:

```
docs/research/sources/<slug>.md
```

The slug is derived from the URL by `fetch_source.py`. To find a source's slug:

```bash
uv run python scripts/fetch_source.py --list
```

---

## File Structure

Each stub follows this frontmatter + body format:

```markdown
---
title: "<source title>"
url: "<source url>"
slug: "<slug>"
cached_at: "<YYYY-MM-DD>"
cache_path: ".cache/sources/<slug>.md"
issue_syntheses:
  - docs/research/<topic>.md
---

# <Source Title>

**URL**: <url>
**Type**: paper | documentation | blog | cookbook
**Cached**: `uv run python scripts/fetch_source.py <url> --slug <slug>`

## Summary

<!-- 2–4 sentences describing what the source is and its primary contribution. -->

## Key Claims

<!-- Bullet list of the most important claims relevant to EndogenAI research. -->

## Relevance to EndogenAI

<!-- How this source specifically bears on the EndogenAI project. -->

## Referenced By

- [docs/research/<topic>.md](../<topic>.md)
```

---

## Git Tracking

| Artifact | Git status |
|----------|-----------|
| `docs/research/sources/*.md` (these stubs) | **tracked** — committed to the repo |
| `.cache/sources/<slug>.md` (raw distillations) | **gitignored** — regenerable via `fetch_source.py` |
| `.cache/sources/manifest.json` (fetch index) | **tracked** — committed to the repo |

The raw distillations are excluded because they are large, regenerable, and contain noise.
The stubs are the curated, committed record of what each source says and why it matters.

---

## Relationship to Issue Syntheses

```
docs/research/
  sources/
    arxiv-org-abs-2512-05470.md    ← per-source stub
    anthropic-building-effective-agents.md
    ...
  agentic-research-flows.md        ← issue synthesis (references stubs above)
  OPEN_RESEARCH.md
```

Issue syntheses own the cross-source conclusions. Per-source stubs own the source summaries.
Never duplicate a source summary inside an issue synthesis — link to the stub instead.
