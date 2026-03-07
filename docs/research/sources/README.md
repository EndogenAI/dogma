# docs/research/sources/

Per-source synthesis documents — one file per research source surveyed by the research fleet.

Each file is a research-quality analysis of a single external source: its argument, evidence,
limitations, key claims with direct quotes, and editorial opinion on what EndogenAI should
adopt, adapt, or reject. These documents are the **atomic unit** that issue synthesis files
(`docs/research/*.md`) reference and build upon.

---

## Why This Exists

When the same source is relevant to multiple research questions — which happens as the project
matures — having a dedicated synthesis document prevents duplication and keeps issue syntheses
lean. Instead of re-analysing `arXiv:2512.05470` in every synthesis that cites it, you write
the analysis once here and link to it.

This also produces a **cumulative source knowledge base**: every source ever surveyed by the
research fleet is catalogued here. Over time this becomes the project's annotated bibliography
with depth — not just a list of sources, but a record of what each source argues and why it
matters to this specific project.

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

Each file is a **full synthesis report** for one source, produced by a single Synthesizer
invocation that reads the complete `.cache/sources/<slug>.md` distillation. It is not a
note or an index card — it is a stand-alone analytical document.

```markdown
---
title: "<source title>"
url: "<source url>"
slug: "<slug>"
authors: "<Author Name(s) or Organisation>"
year: "<YYYY>"
type: paper | documentation | blog | cookbook | repo
evidence_quality: strong | moderate | weak | opinion | documentation
cached_at: "<YYYY-MM-DD>"
cache_path: ".cache/sources/<slug>.md"
topics: [<tag1>, <tag2>]
---

# <Source Title>

**URL**: <url>
**Type**: paper | documentation | blog | cookbook | repo
**Cached**: `uv run python scripts/fetch_source.py <url> --slug <slug>`

## Citation

<!--  Full bibliographic citation (APA or equivalent).
      Authors, year, title, venue/publisher, DOI or URL.
      One line. -->

## Research Question Addressed

<!--  What question does this source answer or speak to?
      Frame it in terms of EndogenAI's own research questions where possible.
      1–2 sentences. -->

## Theoretical / Conceptual Framework

<!--  What theoretical lens, design paradigm, or conceptual model does the source use?
      E.g. "ReAct: interleaved reasoning and acting"; "memory-augmented LLM agent loop".
      If none (blog post, announcement), write N/A and one line of context. -->

## Methodology and Evidence

<!--  How the source is organised and what evidence it presents.
      For papers: methodology, datasets, metrics, experimental design.
      For docs/cookbooks: sections and their purpose, code examples, version specificity.
      For repos: architecture, key modules, licence, maintenance status.
      Anchored in direct quotes. 4–8 sentences or short bullet breakdown. -->

## Key Claims

<!--  10–20 bullets. Each bullet:
      - States a specific, grounded claim
      - Includes a direct quote in > blockquote format where source text supports it
      - Notes the location (section/heading/abstract)
      - Adds 1-sentence analytical commentary when context is needed
      Err toward more bullets. Dense sources warrant 20. -->

## Critical Assessment

<!--  2–3 paragraphs of editorial analysis:
      1. Evidence quality and rigour: is this peer-reviewed, independently replicated, practitioner
         opinion, or product documentation? Assign one of: Strong | Moderate | Weak | Opinion | Documentation
         and justify the rating in one sentence.
      2. Limitations and gaps: what does the source not cover? Where is it incomplete, outdated,
         contested, or narrowly scoped?
      3. Risks or caveats for EndogenAI adoption: vendor lock-in, version sensitivity,
         conceptual mismatch with endogenic principles. -->

## Connection to Other Sources

<!--  Other files in docs/research/sources/ that this source relates to.
      Use relative links with a one-line note on the relationship (supports / contradicts / extends). -->

## Relevance to EndogenAI

<!--  One or more analytical paragraphs (5–10 sentences total).
      Name specific agent files, scripts, or guides this bears on.
      State what should be ADOPTED, ADAPTED, or REJECTED — and why.
      Take a position. "This is relevant" is not sufficient. -->

## Referenced By

<!-- Populated automatically by scripts/link_source_stubs.py — do not edit manually -->
```

---

## Section Reference

| # | Section | Purpose |
|---|---------|---------|
| 1 | Citation | Full bibliographic reference |
| 2 | Research Question Addressed | Maps source to EndogenAI's questions |
| 3 | Theoretical / Conceptual Framework | Paradigm or model the source uses |
| 4 | Methodology and Evidence | How evidence is structured and presented |
| 5 | Key Claims | 10–20 grounded bullets with direct quotes |
| 6 | Critical Assessment | Evidence quality rating + limitations + adoption risks |
| 7 | Connection to Other Sources | Cross-links with relationship notes |
| 8 | Relevance to EndogenAI | Adopt / Adapt / Reject recommendation |
| 9 | Referenced By | Auto-populated by `link_source_stubs.py` |

---

### Depth requirements

A source synthesis document is considered complete when:
- All eight body sections are present and non-empty (Section 3 may be `N/A` for non-academic sources)
- `## Key Claims` has ≥ 10 bullets with direct quotes where the source text supports them
- `## Critical Assessment` includes an explicit **evidence quality rating** (`strong | moderate | weak | opinion | documentation`) matching the `evidence_quality` frontmatter field
- `## Relevance to EndogenAI` names at least one specific EndogenAI file or script
- Total length ≥ 100 lines

Documents below these thresholds are treated as **incomplete** and must be regenerated
before any issue synthesis that cites them. The Synthesizer is invoked with one source
per invocation — it has full context window capacity to produce this depth.

---

## Git Tracking

| Artifact | Git status |
|----------|-----------|
| `docs/research/sources/*.md` (synthesis reports) | **tracked** — committed to the repo |
| `.cache/sources/<slug>.md` (raw distillations) | **gitignored** — regenerable via `fetch_source.py` |
| `.cache/sources/manifest.json` (fetch index) | **tracked** — committed to the repo |

The raw distillations are excluded because they are large, regenerable, and contain noise.
The synthesis reports are the curated, committed record of what each source argues and why it matters.

---

## Self-Referential Session Syntheses

Not all files in this directory are analyses of external sources. Some are **self-referential session synthesis documents** — structured retrospectives written by the research fleet about a session in which the workflow itself was the subject of investigation.

These files have a distinct naming convention:

```
session-synthesis-<YYYY-MM-DD>-<letter>.md
```

Examples: `session-synthesis-2026-03-06-a.md`

They do not follow the 8-section external-source format. Their content is first-person operational: what was attempted, what actually happened, and what was learned — with particular attention to lessons that update assumptions previously encoded in agent files or guides.

**Why they belong here**: self-referential sessions are a class of primary source in the endogenic methodology. The session itself is the object of study; the synthesis is the analysis of that object. Placing these alongside external source syntheses maintains a single, queryable knowledge base of what the fleet has learned — regardless of whether the origin was external or internal. Over time this record enables a Synthesizer or Executive to query across sessions for recurring patterns without re-reading raw scratchpad archives.

**Traceability purpose**: these files are the primary traceability artefact for decisions that were reached through live practice rather than literature review. When an agent convention changes mid-session (e.g., the scratchpad write-back requirement added to `executive-researcher.agent.md` during the 2026-03-06 session), the session synthesis is the record of *why* the change was made and what failure mode it addressed.

**Do not truncate or gitignore these files.** They are committed history, not scratchpad noise.

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
