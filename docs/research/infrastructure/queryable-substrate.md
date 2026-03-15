---
title: "Queryable Documentation Substrate"
status: Final
---

# Queryable Documentation Substrate

How can the endogenic documentation corpus be made queryable via BM25 retrieval-on-demand,
so agents retrieve precisely the section they need rather than bulk-loading entire documents?

Related issue: #80

---

## 1. Executive Summary

The endogenic substrate — 124 Markdown docs plus 33 `.agent.md` role files — is currently
consumed by agents in bulk: entire files are loaded at session start, consuming context window
before any task-specific reasoning begins. `docs/research/values-encoding.md` Pattern 7
("Retrieval-Augmented Governance") identifies this as a structural loss point: the
compress-and-include architecture displaces the foundational constraint as context fills.

This synthesis validates three design decisions for a `scripts/query_docs.py` tool
that implements on-demand BM25 retrieval over scoped corpus slices. All three hypotheses
are confirmed by endogenous evidence. The corpus size (≈157 text files) places this
comfortably within BM25's efficient range without requiring embedding infrastructure.
The work directly enacts `../../AGENTS.md` Axioms 2 and 3: **Algorithms Before Tokens**
(prefer deterministic, encoded solutions over interactive token burn) and
**Local Compute-First** (minimize token usage; run locally whenever possible).

---

## 2. Hypothesis Validation

### Q1 — Is BM25 (via `rank_bm25`) sufficient for this corpus without embeddings?

**Corpus facts**:
- `docs/` contains **124** `.md` files; `.github/agents/` contains **33** `.agent.md` files.
- Total corpus: ≈157 text files, predominantly governance prose and structured reference material.
- `rank_bm25>=0.2` is listed in `pyproject.toml` [project.dependencies] and included in `uv.lock`.
- No embedding server, vector database, or GPU is assumed available in the dev environment.

**Endogenous evidence**:
- `../../AGENTS.md` Axiom 2 ("Algorithms Before Tokens") mandates deterministic encoded solutions
  over interactive token burn. BM25 is a deterministic scoring function; embedding similarity search
  introduces non-determinism via model version and temperature.
- `../../AGENTS.md` Axiom 3 ("Local Compute-First") mandates local execution without external
  services. `rank_bm25` is pure Python, zero-dependency beyond itself, installs from PyPI, and
  runs entirely in-process.
- `docs/research/values-encoding.md` §Pattern 7 explicitly recommends a "lightweight RAG system"
  that "injects the relevant MANIFESTO section at each task boundary." BM25 is the canonical
  lightweight retrieval function for keyword-rich governance text.
- BM25 excels at exact-term recall — critical for governance queries like "Algorithms Before Tokens"
  or "programmatic-first" where the exact phrase appears in the target section. Semantic similarity
  adds no benefit over verbatim axiom names.
- Corpus size of ≈157 files (each ≤ a few thousand tokens) means full in-memory index construction
  takes < 100 ms, well within interactive tool latency budget.

> **Verdict Q1: CONFIRMED.** BM25 via `rank_bm25` is sufficient and preferred.
> Embeddings would violate Axioms 2 and 3 without providing meaningful precision gains
> for this keyword-rich governance corpus. Add `rank_bm25>=0.2` to `pyproject.toml`.

---

### Q2 — Is blank-line paragraph chunking the correct strategy?

**Candidate strategies**:
1. **Blank-line paragraph** — split on `\n\n`; natural Markdown semantic unit.
2. **Heading-boundary** — split on `^##*`, returning entire sections.
3. **Fixed token window** — fixed-size sliding windows (e.g., 256 tokens).

**Endogenous evidence**:
- Markdown governance docs in this repo are authored in short, self-contained paragraphs.
  Blank-line splitting preserves authorial intent — paragraphs were composed as units.
- Heading-boundary chunks are too coarse for a corpus where a single section like
  `## Programmatic-First Principle` spans 30+ lines and multiple distinct sub-points.
  Returning the entire section when one sentence is relevant inflates context unnecessarily,
  partially defeating the purpose of BM25 retrieval.
- Fixed token windows fracture Markdown structures mid-sentence, break list items, and
  destroy co-references that span sentence boundaries. They require a tokenizer dependency.
- Blank-line chunks should be augmented with **heading ancestry** (the nearest parent `##`
  heading prepended to the chunk text). This preserves navigability without adding overhead:
  the ancestry is extracted with a simple scan backward from the chunk position.
- `scripts/audit_provenance.py` demonstrates the canonical corpus-read pattern for this repo:
  `Path.read_text(encoding="utf-8")` for each file discovered via `Path.glob()`. BM25
  chunking should reuse this pattern verbatim.

> **Verdict Q2: CONFIRMED with one required augmentation.**
> Blank-line paragraph chunking is the correct strategy, but each chunk must be prefixed
> with its immediate parent heading text to make retrieval results directly navigable.
> Implement as: split on `\n\n`, scan backward for the nearest `^#{1,6}\s` line, prepend.

---

### Q3 — Is the proposed `SCOPE_PATHS` mapping correct?

**Proposed mapping** (from issue #80):
- `manifesto` → `MANIFESTO.md`
- `agents` → `AGENTS.md` + `.github/agents/*.agent.md`
- `guides` → `docs/guides/*.md`
- `research` → `docs/research/*.md`
- `all` → union of all above

**Observed corpus structure**:
- `docs/toolchain/` contains 6 curated CLI reference files (e.g., `gh.md`, `uv.md`, `ruff.md`).
  These are agent-readable references and are currently excluded from the proposed mapping.
- `docs/decisions/` contains 7 ADR files — rarely queried for operational guidance, but useful
  for architectural rationale queries.
- `.github/skills/*/SKILL.md` contains 10 skill files — same query class as agent files.

> **Verdict Q3: CONFIRMED with two additions.**
> Add `toolchain→docs/toolchain/*.md` as a first-class scope (frequently queried by agents
> for CLI patterns). Add `skills→.github/skills/**/*.md` to cover skill files. The core five
> proposed scopes are structurally correct. The `all` → union scope should include `toolchain`
> and `skills` in its union.

---

## 3. Pattern Catalog

### Pattern 1 — Corpus-Scoped BM25 Index

Build the BM25 index only over the files the agent needs, not the full repository. Accept a
`--scope` argument (one of the SCOPE_PATHS keys) and glob the corresponding paths. This keeps
index construction under 100 ms for any single scope. Index construction is run fresh per
query (no persistence needed at this corpus size); no stale-index invalidation logic required.

**Reuse anchor**: mirrors `build_report(agents_dir, manifesto_path)` in `audit_provenance.py`
where the file set is resolved by the caller, not hardcoded inside the function.

---

### Pattern 2 — Paragraph Chunk with Heading Ancestry Prefix

When building the list of BM25 documents, split each file on blank lines, then for each
paragraph scan backward to find the nearest Markdown heading. Store the chunk as:
`"[<heading>] <paragraph text>"`. The heading prefix costs a few tokens but makes returned
chunks immediately actionable — an agent receiving the chunk can cite its position.

**Implementation sketch**:
```python
import re
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")

def chunk_file(text: str) -> list[str]:
    lines = text.splitlines()
    last_heading = ""
    chunks, current = [], []
    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            last_heading = m.group(1)
        if line.strip() == "" and current:
            chunks.append(f"[{last_heading}] " + " ".join(current))
            current = []
        else:
            current.append(line)
    if current:
        chunks.append(f"[{last_heading}] " + " ".join(current))
    return [c for c in chunks if c.strip()]
```

---

### Pattern 3 — Retrieve-Then-Apply (Endogenous RAG)

Extend `docs/research/values-encoding.md` Pattern 7 into a concrete script. The workflow:

1. Agent calls `uv run python scripts/query_docs.py "<query>" --scope guides --top-n 3`
2. Script returns top-3 scored chunks as Markdown-fenced output including source path and score.
3. Agent reads only those chunks, not the full file.

This converts the current "bulk-load at session start" posture into a "retrieve-exactly-what-
is-needed" posture, directly addressing the context displacement problem identified in
`values-encoding.md` §Pattern 7. It is a deterministic, encoded solution — Axiom 2 in action.

---

### Pattern 4 — Score-Threshold Gating

After ranking with BM25, discard any chunk whose score falls below a configurable minimum
(default: 0.5 × top score). This prevents low-signal chunks from polluting the context window
when the query matches weakly across many documents. Expose as `--min-score-ratio FLOAT`.
The ratio-based threshold (relative to top score) is more robust than an absolute cutoff
because BM25 scores are corpus-dependent.

---

### Pattern 5 — Dry-Index Cache for CI

For CI validation (e.g., checking that every SCOPE_PATH glob resolves to at least one file),
build the index in `--dry-run` mode: resolve paths and count chunks without performing a query.
Exit non-zero if any scope resolves to 0 chunks. This catches accidental scope misconfiguration
at the CI gate rather than at agent runtime — consistent with the Testing-First requirement
in `../../AGENTS.md`.

---

## 4. Recommendations

### R1 — `rank_bm25` and `scripts/query_docs.py` delivered in Phase 5

**Rationale**: `../../AGENTS.md` Axiom 2 ("Algorithms Before Tokens") mandates deterministic,
encoded solutions. A BM25 retrieval tool encodes the query → section lookup once, eliminating
repeated manual bulk-loading across sessions. `rank_bm25>=0.2` is a pure-Python dependency
with no system requirements and a stable API.

**Acceptance criteria**: `uv run python scripts/query_docs.py "programmatic-first" --scope agents --top-n 3`
returns the three highest-scoring paragraphs from `AGENTS.md` and `.github/agents/*.agent.md`
within 500 ms on a cold start.

---

### R2 — Include `toolchain` and `skills` scopes in `SCOPE_PATHS`

**Rationale**: `docs/toolchain/` files (e.g., `gh.md`, `uv.md`) are consulted frequently by
agents before running CLI commands. Skills files (`.github/skills/**/*.md`) encode reusable
procedures. Excluding both from retrieval scopes means agents must still bulk-load these files
manually — defeating the purpose of the retrieval tool.

**Implementation**: Add to `SCOPE_PATHS` dict:
```python
"toolchain": ["docs/toolchain/*.md"],
"skills":    [".github/skills/**/*.md"],
```

---

### R3 — Tests must cover happy path, empty-scope error, and score-threshold logic

**Rationale**: `../../AGENTS.md` §Testing-First Requirement states every script must have
automated tests before it ships. For `query_docs.py`, critical regressions include:
(a) a scope glob that resolves to zero files silently returns no results rather than erroring,
and (b) score-threshold logic that filters all results when set too high. Mark I/O tests with
`@pytest.mark.io` per `pyproject.toml` marker conventions.

---

## 5. Sources

- `../../AGENTS.md` — Axiom 2 (Algorithms Before Tokens), Axiom 3 (Local Compute-First),
  §Testing-First Requirement
- `../../docs/research/values-encoding.md` — §Pattern 7 (Retrieval-Augmented Governance)
- `../../scripts/audit_provenance.py` — canonical corpus-read pattern (`Path.glob` + `read_text`)
- `../../pyproject.toml` — dependency list (`rank_bm25>=0.2` added in Phase 5)
- `rank_bm25` PyPI package — pure-Python BM25 implementation, no external dependencies
- BM25 (Okapi BM25): Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and
  Beyond", Foundations and Trends in Information Retrieval, 3(4), 2009
- Corpus size: 124 `docs/**/*.md` + 33 `.github/agents/*.agent.md` = ≈157 text files (verified
  via `find` on 2026-03-08)
