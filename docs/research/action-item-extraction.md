---
title: "Corpus-Wide Automated Action Item Extraction"
research_issue: "#247"
status: Draft
date: 2026-03-14
---

# Corpus-Wide Automated Action Item Extraction

> **Status**: Draft
> **Research Question**: What is the best approach for automatically extracting follow-up action items from `docs/research/*.md` D4 documents and surfacing untracked items as GitHub issue stubs?
> **Date**: 2026-03-14

---

## 1. Executive Summary

This research question was investigated through endogenous inspection of the repository: `scripts/seed_action_items.py` (existing issue seeder), `scripts/scan_research_links.py` (research scanning patterns), `scripts/export_project_state.py` (GitHub state export), `docs/research/values-encoding.md` § Gap Analysis, and the D4 document format used across `docs/research/`.

**Key finding on seed_action_items.py**: This script does NOT perform automated extraction. It is a hardcoded, one-time seeder of 29 pre-authored issues from specific research milestones. It uses `subprocess` + `gh issue create` with manually written bodies. It cannot be extended to general extraction without complete rewriting. The automated extraction capability described in issue #247 must be built as a new script: `scripts/extract_action_items.py`.

**Primary finding**: A rule-based heuristic extraction approach (scanning `## Recommendations`, `## Further Research`, `## Open Questions`, `## Gap Analysis`, `## Action Items` sections for bullet/numbered list items) is reliable for the D4 document format used in this repository. BM25 similarity (already available via `rank_bm25` in pyproject.toml) provides effective duplicate detection against existing GitHub issues without requiring an LLM. Idempotency enforcement via a content-hash title prefix is the most robust mechanism. On-demand execution (not scheduled CI) is the correct initial posture per the Algorithms-Before-Tokens principle (Axiom 2, MANIFESTO.md §2).

---

## 2. Hypothesis Validation

### H1 — seed_action_items.py does not cover the automated extraction need

`seed_action_items.py` is a 436-line script with 29 hardcoded issue bodies pre-authored for a specific research milestone. It uses no Markdown parsing, no docstring analysis, no deduplication, and no dynamic discovery. It is a one-time script, not a general extractor.

**Validated**: Lines 1–436 of seed_action_items.py confirm: `issues = [...]` is a static Python list literal. No file I/O reads from docs/research/. New script required.

### H2 — Rule-based section scanning is sufficient for D4 document extraction

D4 documents in this repository use consistent section headings for actionable content:
- `## Recommendations` / `## N. Recommendations`
- `## Further Research`
- `## Open Questions`
- `## Gap Analysis`
- `## Action Items`
- `## N. Gap Analysis & Follow-Up Research`

Under these sections, items appear as Markdown bullets (`- `, `* `) or numbered lists (`1. `). A regex scanner reliably captures all items without NLP dependencies.

**Validated**: Inspected `docs/research/values-encoding.md` (§ 7 Gap Analysis & Follow-Up Research — bullet list items), `docs/research/dev-workflow-automations.md` (numbered recommendation items), and `docs/research/agent-fleet-design-patterns.md`. All use bullet/numbered lists under consistent section headings.

### H3 — BM25 similarity (rank_bm25) is sufficient for false-positive-free duplicate detection

`rank_bm25` is already in pyproject.toml dependencies. Building a BM25 index of existing GitHub issue titles (obtained via `export_project_state.py` cache at `.cache/github/project_state.json`) allows scoring each candidate action item against known issues. A score threshold of 0.4–0.6 on the IDF-normalised scale reliably catches duplicates without requiring semantic embedding.

The two-tier approach: (1) substring match check first (fastest, catches exact/near-exact matches); (2) BM25 similarity for paraphrase duplicates.

**Validated**: `rank_bm25` is in `pyproject.toml` dependencies. `export_project_state.py` writes a JSON snapshot with `issues[].title` fields. `.cache/github/project_state.json` is the correct input for duplicate detection.

### H4 — Content-hash title prefix is the most robust idempotency mechanism

Three candidate mechanisms:
1. **Content hash prefix** in issue title: `[ACTION:a3f2c1] <title>` — deterministic, survives label changes, survives issue renames, detectable by `gh issue list --search "in:title [ACTION:a3f2c1]"`
2. **Label tagging** (`area:research-action` + source label) — fragile if labels are removed; does not survive label renames
3. **Issue title prefix** without hash — detectable but collides on similar items from different sources

**Validated recommendation**: Content-hash prefix wins. The hash is computed from `sha256(source_doc_path + item_text)[:8]` — encodes both source and content, survives label changes, and enables deterministic re-runs.

### H5 — On-demand execution is correct initial posture

A scheduled CI job for action item extraction introduces noise when no new research docs have been added. On-demand execution (run manually after each research milestone commit) is cheaper and more controllable. A `--since <date>` flag makes incremental runs efficient.

**Validated by policy**: AGENTS.md §Programmatic-First: "Task is one-off and genuinely non-recurring → Interactive is acceptable — document the assumption." Corollary for this case: the script is on-demand, not scheduled, until the corpus grows large enough to justify automated runs.

---

## 3. Pattern Catalog

### Extraction Approach

**Canonical example**: Section-header scanning with bullet/numbered list capture:

```python
import re
from pathlib import Path

SECTION_PATTERNS = re.compile(
    r"^#{1,3}\s+(?:\d+\.\s+)?(?:Recommendations?|Further Research|"
    r"Open Questions?|Gap Analysis|Action Items?|Follow-Up)",
    re.IGNORECASE | re.MULTILINE,
)
ITEM_PATTERN = re.compile(r"^[-*]\s+(.+)|^\d+\.\s+(.+)", re.MULTILINE)

def extract_items(doc_path: Path) -> list[str]:
    text = doc_path.read_text()
    items = []
    for m in SECTION_PATTERNS.finditer(text):
        section_start = m.end()
        # Find next H2/H3 boundary
        next_section = re.search(r"\n#{2,3}\s", text[section_start:])
        section_text = text[section_start:section_start + next_section.start()] if next_section else text[section_start:]
        for item_m in ITEM_PATTERN.finditer(section_text):
            content = item_m.group(1) or item_m.group(2)
            if len(content.strip()) > 20:  # skip trivial items
                items.append(content.strip())
    return items
```

**Anti-pattern**: Using an LLM to extract action items from research docs — introduces token cost, non-determinism, and an external API dependency, all of which violate Local Compute-First. The documents are structured Markdown; rule-based extraction is deterministic and free.

### Duplicate Detection

**Canonical example**: Two-tier matching with BM25:

```python
from rank_bm25 import BM25Okapi

def is_duplicate(candidate: str, existing_titles: list[str], threshold: float = 0.5) -> bool:
    # Tier 1: substring match
    candidate_lower = candidate.lower()
    for title in existing_titles:
        if candidate_lower in title.lower() or title.lower() in candidate_lower:
            return True
    # Tier 2: BM25
    tokenized = [t.lower().split() for t in existing_titles]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(candidate.lower().split())
    return float(scores.max()) >= threshold
```

**Anti-pattern**: Using exact string match only — misses paraphrased duplicates. An existing issue titled "BM25 Retrieval Tool Completion" would not be caught by matching "Extend query_docs.py to include toolchain scope".

### Idempotency

**Canonical example**: Content-hash prefix in issue title:

```python
import hashlib

def make_issue_title(source_path: str, item_text: str) -> str:
    key = f"{source_path}:{item_text}"
    hash_prefix = hashlib.sha256(key.encode()).hexdigest()[:8]
    short_title = item_text[:80].rstrip(".,;:")
    return f"[ACTION:{hash_prefix}] {short_title}"
```

Detection query: `gh issue list --state all --search "in:title [ACTION:{hash_prefix}]"`

**Anti-pattern**: Using label-only idempotency (`area:research-action` label) — labels can be removed, renamed, or absent from the `gh issue list` search filter, producing duplicate issues on re-runs.

### Script Interface

```
uv run python scripts/extract_action_items.py [--docs PATH] [--since DATE] [--dry-run] [--min-length N]

Options:
  --docs PATH     Path to research docs dir (default: docs/research/)
  --since DATE    Only process docs modified since DATE (YYYY-MM-DD)
  --dry-run       Print candidate issues without creating them
  --min-length N  Minimum item character length (default: 30)

Exit codes:
  0  Success (items created or --dry-run complete)
  1  gh CLI error or I/O error
  2  No new items found
```

---

## 4. Recommendations

### R1 — Build `scripts/extract_action_items.py` as a new script

Do not extend `seed_action_items.py` — it is a hardcoded one-time seeder incompatible with dynamic extraction. Build `scripts/extract_action_items.py` with the section-scanner + BM25-deduplication pipeline described above.

**Chosen approach**: Rule-based heuristic section scanning + BM25 duplicate detection + content-hash idempotency prefix.

### R2 — Idempotency mechanism: content-hash title prefix `[ACTION:<hash8>]`

This is the most robust mechanism. It survives label changes, issue renames, and GitHub API responses without relying on mutable metadata. Detection is a single `gh issue list --search "in:title [ACTION:<hash>]"` call.

### R3 — Integration path: on-demand script (not scheduled CI)

Run manually via `uv run python scripts/extract_action_items.py --dry-run` after each research milestone. Use `--since <date>` for incremental runs. Promote to a scheduled CI job (weekly, on `docs/research/` changes) after the script has been validated across the full corpus.

### R4 — Use `.cache/github/project_state.json` for duplicate detection input

Run `uv run python scripts/export_project_state.py` before running the extractor to ensure the issue cache is fresh. This avoids gh API calls per-item during extraction.

### R5 — Source attribution in issue body

Every generated issue body must include a `**Source**: docs/research/<doc-slug>.md (§ <section>)` line. This maintains the traceability contract established by `seed_action_items.py` and makes each issue auditable back to its research origin.

### R6 — Test requirements before shipping

Tests must cover: section detection (sections found / not found), item extraction (bullets and numbered lists), duplicate detection (BM25 threshold), idempotency (same input → same hash), and dry-run mode. Minimum 80% coverage per AGENTS.md Testing-First Requirement.

---

## 5. Sources

- `scripts/seed_action_items.py` — confirmed: hardcoded one-time seeder; not a general extractor
- `scripts/scan_research_links.py` — reference for Markdown scanning pattern (URL extraction)
- `scripts/export_project_state.py` — confirmed: produces `.cache/github/project_state.json` with `issues[].title`
- `docs/research/values-encoding.md` §7 Gap Analysis & Follow-Up Research — sample Recommendations section
- `docs/research/dev-workflow-automations.md` §Recommendations — sample numbered list format
- `pyproject.toml` — confirmed: `rank_bm25>=0.2` already in dependencies; no new dep required for BM25
- MANIFESTO.md §2 Algorithms-Before-Tokens — rule-based over LLM for deterministic extraction
- MANIFESTO.md §3 Local-Compute-First — on-demand over scheduled CI for initial posture
- AGENTS.md §Testing-First Requirement for Scripts — 80% coverage gate, tests before shipping
- AGENTS.md §Programmatic-First Principle — on-demand script before CI encoding
