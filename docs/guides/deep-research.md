# Deep Dive Research Workflow

This guide defines the **Endogenic Deep Dive Research Workflow** — a recursive, programmatic-first research methodology for conducting exhaustive, hypothesis-driven investigations that culminate in academically rigorous synthesis documents and papers.

The workflow is self-referential: the methodology described here was itself discovered and refined through a deep dive into endogenic methodology foundations. See [`docs/research/methodology-review.md`](../research/methodology-review.md) as the seed document.

---

## When to Use This Workflow

Use this workflow when:

- A research question has been partially answered and requires exhaustive depth (≥3 hypothesis clusters to validate)
- The output is intended to be academically publishable or cited
- Multiple sprint cycles of source scouting and synthesis are required
- Cross-referencing across existing corpus is needed to discover interconnects
- You are building a cumulative, fully-cited knowledge artifact (not just a synthesis summary)

For single-topic research sprints (one hypothesis, one source cluster), use the standard research workflow in [`docs/guides/workflows.md`](workflows.md).

---

## Core Principles

This workflow encodes four endogenic axioms:

1. **Endogenous-First** — before any web scouting, run `scan_research_links.py` to extract what the existing corpus already knows. The local cache and committed docs are consulted first.
2. **Algorithms Before Tokens** — every repeated step (source fetching, scan, citation formatting) is scripted. No agent re-fetches or re-formats interactively what scripts already handle.
3. **Programmatic-First** — every manifest, bibliography, and scan result is a committed artifact. Research state is durable across sessions and agents.
4. **Local Compute-First** — sources are cached locally in `.cache/sources/` before any synthesis begins. Scouts read `.cache/`, not the web.

The SECI cycle governs each sprint: tacit Scout findings (Socialization) → externalized in scratchpad (Externalization) → combined in synthesis document (Combination) → internalized as updated AGENTS.md or guides (Internalization).

---

## Workflow Phases

### Phase 0 — Infrastructure

**Run once per research topic. Skip if infrastructure already exists.**

```bash
# 1. Scaffold a new manifest for this research topic
uv run python scripts/scaffold_manifest.py \
  --name <topic-slug> \
  --description "<research scope>" \
  --sprints '{"A": "H1 description", "B": "H2 description", ...}'

# 2. Pre-warm the standard source cache
uv run python scripts/fetch_all_sources.py

# 3. Run the corpus scan to discover existing links
uv run python scripts/scan_research_links.py \
  --scope all \
  --output docs/research/manifests/<topic-slug>-scan.json

# 4. Review scan output and triage URLs into the main manifest
# For each relevant URL:
uv run python scripts/add_source_to_manifest.py \
  --manifest docs/research/manifests/<topic-slug>.json \
  --url "<url>" \
  --title "<title>" \
  --sprint <A|B|C|D|E> \
  --priority <high|medium|low> \
  --reason "<why relevant>"
```

After Phase 0 is complete: commit all scaffolding artifacts before proceeding to scouting.

---

### Phase 1 — Corpus Scan (Endogenous-First)

Before any web scouting, extract what the existing corpus already knows:

```bash
# Scan all three tiers
uv run python scripts/scan_research_links.py --scope all --output /tmp/corpus-scan.json

# Review: how many URLs in each tier?
python3 -c "import json; d=json.load(open('/tmp/corpus-scan.json')); \
  print('Total unique:', d['unique_urls']); \
  from collections import Counter; \
  tiers = Counter(e['tier'] for e in d['urls']); \
  [print(f'  {k}: {v}') for k,v in tiers.items()]"
```

Key outputs to look for:
- **Cross-references** — URLs that appear in both `docs/research/` and `.cache/sources/` already have cached content available
- **Orphaned stubs** — URLs in `docs/research/sources/` that are not referenced from committed research docs
- **New candidates** — URLs in `.cache/sources/` that were fetched during previous sessions but not yet cited in committed docs

---

### Phase 2 — Web Scouting (per Sprint) [MANDATORY — DO NOT SKIP]

**Every research sprint must include aggressive web sourcing.** Skipping Phase 2 is an anti-pattern equivalent to conducting research without primary sources. This phase cannot be compressed or deferred.

Delegate to Research Scout. Provide:

1. The hypothesis being validated (H1–H4 or cross-cutting)
2. The depth level (exhaustive / broad / targeted)
3. The manifest path (Scout appends URLs directly via `add_source_to_manifest.py`)
4. Any seed URLs from the corpus scan
5. **Explicit emphatic instruction**: Conduct exhaustive web searches across academic (arXiv, ACM, IEEE, Google Scholar), industry (official docs, standards, vendor reports), and practitioner (blogs, conference talks, discussions) sources. This is the primary mandate, not an optional addition.

**Scouting tiers** (use all three for deep dives; narrower sprints use at least two):
- **Academic** — arXiv (`arxiv.org`), ACM Digital Library (`dl.acm.org`), IEEE Xplore (`ieeexplore.ieee.org`), Google Scholar
- **Industry & Standards** — RFC standards, W3C specs, ISO standards, official vendor documentation, whitepapers
- **Practitioner** — Conference talks (YouTube, conference proceedings), flagship blogs (ACM Queue, IEEE Spectrum, InfoQ, the morning paper), Hacker News substantive discussions
- **Grey literature** — Theses (ProQuest, DART-Europe), preprints (SSRN, PhilPapers), working papers from research labs

**Minimum source count**: At least 7 primary sources per sprint. If fewer are found, the Scout must re-search — low hit count indicates either a narrow topic (split into sub-hypotheses) or inadequate search strategy.

**Scout output format** (written to scratchpad `## Sprint X Scout Output`):
```markdown
## Sprint X Scout Output

**Hypothesis**: H1 — [description]
**Depth**: exhaustive
**Sources examined**: N

### [Source Title](URL)
**Why relevant**: ...
**Key claims**: ...
**Added to manifest**: yes/no, sprint X, priority high/medium/low
```

---

### Phase 3 — Source Fetching

After scouting, fetch all newly added manifest sources:

```bash
# Fetch all pending sources in the manifest
uv run python scripts/fetch_all_sources.py \
  --manifest docs/research/manifests/<topic-slug>.json

# Remove 404s: set status to "skip" manually in the manifest JSON,
# or re-run with --dry-run first to see which fail
uv run python scripts/fetch_all_sources.py \
  --manifest docs/research/manifests/<topic-slug>.json \
  --dry-run

# Update manifest source status for fetched sources (edit the JSON directly)
```

**404 triage rule**: if a URL returns 404 or garbled content after two fetch attempts, set `"status": "skip"` in the manifest. Document the failure in the sprint synthesis under `## Source Notes`.

---

### Phase 4 — Sprint Synthesis (per Sprint)

For each sprint, delegate to Research Synthesizer. Provide:

1. Cached source paths (`.cache/sources/<slug>.md`)
2. The hypothesis being synthesized (with seed claims from methodology-review.md)
3. The target output path (`docs/research/<topic>-<sprint>.md`)
4. Any existing adopt/gap items from the seed review
5. Required D4 headings (Hypothesis Validation, Pattern Catalog)

**Sprint synthesis document structure**:

```markdown
---
title: "Sprint <X> Synthesis: <Hypothesis Name>"
status: "Draft"  # → "In Review" → "Final"
---

# Sprint X: [Hypothesis Full Name]

## 1. Executive Summary
## 2. Hypothesis Validation
### H[N].1 — [Sub-claim]
### H[N].2 — [Sub-claim]
## 3. Pattern Catalog
### [Pattern Name]
**Prior art**: ...
**Endogenic alignment**: ...
**Adopt**: ...
**Gap**: ...
## 4. Bibliography Notes
## 5. Source Index
```

After synthesis: delegate to Research Reviewer, then Research Archivist to commit.

---

### Phase 5 — Bibliography Enrichment

As each sprint is synthesized, enrich `bibliography.yaml` with any new sources:

```yaml
# docs/research/bibliography.yaml entry format
- id: <authorYYYY>
  type: article|book|inproceedings|techreport|web|misc
  title: "<Full title>"
  authors:
    - "Full Name"
  year: YYYY
  venue: "<journal/conference/publisher>"
  doi: "10.XXXX/..."   # if available
  url: "https://..."
  retrieved: "YYYY-MM-DD"  # for web resources only
```

Verify rendering:
```bash
uv run python scripts/format_citations.py --list
uv run python scripts/format_citations.py --key <id>
```

---

### Phase 6 — Main Synthesis Document

After all sprint syntheses are committed (Status: Final), delegate to Research Synthesizer to produce the main synthesis. Provide:

1. All sprint synthesis doc paths
2. The `bibliography.yaml` path
3. The target output path (`docs/research/<topic>-synthesis.md`)
4. Cross-reference map from corpus scan (Phase 1 output)

**Main synthesis is the integration layer** — it does not repeat content from sprint docs, but cites them and synthesizes across their findings.

---

### Phase 7 — Academic Paper

The academic paper follows ACM SIG Proceedings structure. Delegate to Research Synthesizer (academic mode). All citations come from `bibliography.yaml` rendered via `format_citations.py`.

**Required sections**:

```markdown
# [Title]: [Subtitle]

## Abstract

## 1. Introduction
### 1.1 Problem Statement
### 1.2 Contributions
### 1.3 Paper Organization

## 2. Background and Related Work

## 3. [Methodology Name]
### 3.1 Core Axioms
### 3.2 Operational Components
### 3.3 Design Constraints

## 4. Evaluation
### 4.1 [Method / Case Study]
### 4.2 Results
### 4.3 Limitations

## 5. Discussion
### 5.1 Implications
### 5.2 Future Work

## 6. Conclusion

## References
```

Generate reference list:
```bash
uv run python scripts/format_citations.py --bibliography docs/research/bibliography.yaml
```

---

## The Recursive Loop

This workflow is itself a product of endogenic research. It encodes a meta-pattern: the methodology used to conduct research is the same methodology being researched. At each application of the workflow:

1. The corpus grows (new `.cache/` entries, new committed synthesis docs)
2. The bibliography grows (`bibliography.yaml` enriched with new entries)
3. The workflow itself may be updated if new patterns are discovered in Sprint E (cross-cutting)
4. The agent fleet may be updated if new agent types are needed (spawn via `scaffold_agent.py`)

This recursive property — the research substrate growing through its own use — is the operational instantiation of autopoiesis applied to AI-assisted research.

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scaffold_manifest.py` | Create a new blank sprint manifest | `uv run python scripts/scaffold_manifest.py --name <slug>` |
| `add_source_to_manifest.py` | Add a source to a manifest | `uv run python scripts/add_source_to_manifest.py --manifest <path> --url <url> ...` |
| `fetch_all_sources.py` | Fetch all manifest URLs | `uv run python scripts/fetch_all_sources.py --manifest <path>` |
| `scan_research_links.py` | Scan corpus for URLs | `uv run python scripts/scan_research_links.py --scope all` |
| `format_citations.py` | Render ACM citations | `uv run python scripts/format_citations.py` |
| `prune_scratchpad.py` | Archive session scratchpad | `uv run python scripts/prune_scratchpad.py --init` |

---

## Checklist: Starting a Deep Dive Session

```markdown
- [ ] Read today's scratchpad: `cat .tmp/<branch>/$(date +%Y-%m-%d).md`
- [ ] Pre-warm cache: `uv run python scripts/fetch_all_sources.py`
- [ ] Check manifest for pending sources: `cat docs/research/manifests/<slug>.json | python3 -m json.tool`
- [ ] Check .cache/ before fetching any individual URL
- [ ] Write ## Session Start with governing axiom and endogenous source
- [ ] Run scan before any web scouting: `uv run python scripts/scan_research_links.py --scope all`
```

## Checklist: After Each Sprint

```markdown
- [ ] Synthesis document committed (Status: Final)
- [ ] bibliography.yaml updated with new sources
- [ ] Manifest source statuses updated (pending → skip for 404s)
- [ ] Scratchpad pruned: `uv run python scripts/prune_scratchpad.py`
- [ ] Pre-compact checkpoint committed
```
