---
name: corpus-sweep
description: |
  Orchestrates a large-corpus scouting pass (≥20 docs) using batched reads and compressed return. USE FOR: scanning research/, docs/, agent fleet for cross-cutting patterns before a synthesis phase; producing a compressed ≤2000-token findings summary. DO NOT USE FOR: single-doc reads; live web fetches (use source-caching skill instead).
argument-hint: "index path and keyword to sweep for"
---

# Corpus Sweep

## Governing Axiom

This skill enacts the **Endogenous-First** axiom from [`MANIFESTO.md`](../../../MANIFESTO.md#1-endogenous-first) and is governed by [`AGENTS.md`](../../../AGENTS.md) § Programmatic-First Principle. Before sweeping any corpus, check whether a prior sweep result is already cached in `.cache/sources/` or recorded in the active session scratchpad — re-sweeping a cached corpus wastes tokens and violates *Local Compute-First*.

> *"Scaffold from existing system knowledge and external best practices."*
> — MANIFESTO.md § 1 Endogenous-First

---

## When to Use

- A synthesis or implementation phase requires patterns found across ≥20 source documents.
- The Orchestrator needs a cross-cutting summary before delegating to a Synthesizer.
- A research epic requires an initial landscape report before forming hypotheses.
- You are auditing agent files, research docs, or session scratchpads for a recurring pattern.

Do **not** use this skill for:
- Single-document reads (use `read_file` directly).
- Live web fetches (use the `source-caching` skill instead).
- Tasks where the required context fits within a single `grep_search` or `semantic_search` call.

---

## Workflow

1. **Pre-warm cache** — before reading any source file, run:
   ```
   uv run python scripts/fetch_all_sources.py
   ```
   Skip if `.cache/sources/manifest.json` was updated within the current session.

2. **Read source index** — identify the target corpus:
   - For research sources: read `.cache/sources/manifest.json` to list all cached URLs.
   - For internal docs: list `docs/research/`, `docs/guides/`, or `.github/agents/` as appropriate.
   - Record the total document count before batching.

3. **Batch-read docs** — divide the corpus into batches of 5–10 files. For each batch:
   - Use `read_file` (for long docs) or `grep_search` (for keyword scanning).
   - Record findings per document: filename, key claim, relevant quote (≤50 words), and cross-references noted.
   - Stop scanning a document once sufficient signal is found — avoid reading full content when a heading scan suffices.

4. **Record findings** — append findings to the active session scratchpad under `## Corpus Sweep Output`:
   ```
   ## Corpus Sweep Output
   - <filename>: <key claim> — "<quote>"
   ```
   Write incrementally after each batch; do not accumulate all findings in memory before writing.

5. **Compress and return** — after all batches complete, produce a ≤2000-token compressed summary and return it to the Orchestrator. Follow the compression rules in [`AGENTS.md`](../../../AGENTS.md) § Focus-on-Descent / Compression-on-Ascent.

---

## Output Format

Return **only** the compressed summary — no preamble, no prose framing. Use this structure:

```
Corpus: <name> — <N> docs scanned
Keywords: <keyword list>

Findings:
- <doc-name>: <one-line finding>
- …

Patterns:
- <cross-cutting pattern 1>
- <cross-cutting pattern 2>

Gaps:
- <topic with no coverage>

Token count: ~<estimate>
```

Maximum return: **≤2000 tokens**. If findings exceed this, compress by:
1. Dropping per-document lines with no cross-cutting signal.
2. Merging duplicate findings into a single pattern entry.
3. Omitting gaps that are not actionable for the current phase.

If compression is truly unavoidable, note `[truncated — N docs omitted]` at the end.

---

## Example Invocation

```
@corpus-sweep Sweep docs/research/ for "values encoding" patterns across all synthesis docs.
Return: compressed summary, ≤2000 tokens, bullets only.
```

Expected output shape:

```
Corpus: docs/research/ — 23 docs scanned
Keywords: values encoding, encoding fidelity, signal loss

Findings:
- values-encoding.md: cross-reference density proxy for encoding fidelity
- agent-taxonomy.md: POSTURE-mapped toolsets reduce drift at T3 static layer
- bubble-substrate-model.md: membrane permeability spec governs Scout→Synthesizer handoff

Patterns:
- Encoding loss is highest at session-prompt layer (T4)
- Cross-reference density (back-links per 1000 words) is the primary fidelity metric

Gaps:
- No synthesis covering T4 runtime governor effectiveness data

Token count: ~320
```
