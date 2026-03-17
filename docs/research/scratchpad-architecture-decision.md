---
title: "Scratchpad Architecture Decision — Structured Store vs Flat Markdown"
status: "Final"
research_issue: 304
closes_issue: 304
date: 2026-03-17
sources:
  - docs/research/mcp-state-architecture.md
  - docs/research/agent-to-agent-communication-protocol.md
  - docs/research/intelligence-architecture-synthesis.md
  - https://modelcontextprotocol.io/specification/2025-03-26/basic/transports
  - https://www.sqlite.org/fts5.html
  - AGENTS.md
  - MANIFESTO.md
---

# Scratchpad Architecture Decision — Structured Store vs Flat Markdown

> **Status**: Final
> **Research Question**: What storage architecture best serves dogma's cross-agent scratchpad coordination needs — flat Markdown, SQLite, a hybrid, or MCP-mediated access?
> **Date**: 2026-03-17
> **Closes**: issue #304

---

## Executive Summary

The current flat Markdown scratchpad (`.tmp/<branch>/<YYYY-MM-DD>.md`) is adequate for today's session sizes (200–500 lines) but becomes structurally inadequate as agent delegation depth and session count grow. Four of five agent query patterns — phase status lookup, section content retrieval, cross-day lookup, and issue status tracking — require O(n) full-file scans or brittle heading-grep heuristics. The `validate_session_state.py` parser currently depends on consistent heading conventions that agents do not reliably produce, making phase-status queries fragile. This is a concrete manifestation of the gap identified in [mcp-state-architecture.md](mcp-state-architecture.md) as the "programmatic queryability" and "state shape enforcement" deficiency — a Redux-analogue that is only partially present in the current substrate.

**Candidate B' (SQLite-as-index + Markdown source of truth, the hybrid architecture)** is the recommended adoption path. This pattern is production-validated by Obsidian and Logseq, both of which maintain Markdown files as the canonical write target while using a SQLite read-accelerator index for query performance. The write path for dogma agents is unchanged: `replace_string_in_file` via VS Code tools continues to write Markdown. The SQLite index is rebuilt from Markdown on `prune_scratchpad.py --init` and updated incrementally on each write event. Queries from `validate_session_state.py` and the Executive Orchestrator route to SQLite rather than heading-grep, eliminating the brittleness without changing any agent behaviour. This directly implements the **Local Compute-First** axiom ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)): structured query capability lives entirely on-device with no external service dependency.

**Candidate D (MCP-mediated scratchpad server)** is valid as an access-layer addition on top of B', not a standalone alternative. The MCP specification recommends stdio transport for local subprocess servers, keeping the implementation surface minimal. Critically, Candidate D requires a structured backend query store — it cannot retrieve phase status or section content from flat Markdown any faster than the current heading-grep approach. The dependency relationship is therefore: B' is a prerequisite for a performant Candidate D. Issue #297 (MCP-mediated scratchpad query) should be scoped accordingly. As an immediate incremental improvement, Candidate C (YAML-fronted Markdown) can be adopted now — adding structured frontmatter to `prune_scratchpad.py --init` costs nothing and addresses session-level metadata queries while B' is being implemented, consistent with the **Algorithms Before Tokens** axiom ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)): encode deterministic metadata at write time rather than re-deriving it via LLM parsing at read time.

---

## Hypothesis Validation

### H1: The current flat Markdown scratchpad is adequate for dogma's cross-agent coordination needs

**VERDICT: PARTIALLY SUPPORTED**

The flat Markdown format is adequate today for sessions under 500 lines with one or two active agents. Human readability and git-diffability are genuine strengths — they enable session retrospectives without tooling and provide a durable audit trail. However, four of the five query patterns agents need require O(n) full-file scans: phase status (heading grep), section content by phase label (regex scan), cross-day lookup (multi-file reads), and issue status (full-text search across files). Only single-session read, where an agent reads the whole file sequentially, is naturally suited to the flat format. As [agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md) identified, the missing piece for reliable cross-agent handoffs is atomic write coordination and indexed lookup — neither is provided by flat Markdown. The hypothesis is partially supported in the short term and will fail increasingly as delegation depth grows.

### H2: SQLite FTS5 as a standalone replacement for the Markdown scratchpad would improve query performance

**VERDICT: SUPPORTED (with qualification)**

SQLite FTS5 (`CREATE VIRTUAL TABLE sessions USING fts5(...)`) addresses all five query patterns at O(log n) using stdlib `sqlite3` with zero new dependencies. FTS5 automerge handles background compaction — eliminating the lossy compression problem in `prune_scratchpad.py`. Performance at the 200–2000 row scale dogma operates at is excellent. The qualification is decisive: a binary `.db` file as the canonical scratchpad breaks git-diff entirely, eliminating the session audit trail, manual review, and session-retrospective workflows that depend on human-readable history. Standalone replacement (Candidate B) is therefore not recommended. The FTS5 approach is the right query engine — but it must serve as a read-accelerator index, not the source of truth. H2 is supported for the query-performance claim; the architectural recommendation is the hybrid (B').

### H3: The SQLite-as-index + Markdown source-of-truth hybrid (Candidate B') is the optimal architecture for dogma's scratchpad

**VERDICT: CONFIRMED**

Candidate B' preserves every strength of the current flat Markdown system (human readability, git-diffability, agent write path unchanged) while eliminating the O(n) query brittleness. The pattern is production-validated: both Obsidian and Logseq use this exact architecture — Markdown files are canonical, SQLite is a read-accelerator rebuilt from source. The schema `(id, file_path, modified_at, phase, heading, section_content, metadata_json)` maps cleanly onto dogma's existing scratchpad structure. The index is rebuilt at `prune_scratchpad.py --init` and can be updated incrementally via a file-watcher (the same mechanism as `watch_scratchpad.py`). The `validate_session_state.py` heading-grep is replaced by a parameterised SQLite query. The finding from [intelligence-architecture-synthesis.md](intelligence-architecture-synthesis.md) that LangGraph uses a SQLite checkpointer for cross-phase state persistence confirms this is the established pattern for agentic workflows requiring durable, queryable session state.

### H4: The MCP-mediated scratchpad server (Candidate D) is an alternative to, not dependent on, a structured local store

**VERDICT: NOT SUPPORTED**

Candidate D exposes phase status and section content via MCP tool calls (`rag_query`, `session_status`). The MCP specification's recommendation for stdio transport (local subprocess, no HTTP infrastructure) makes the access layer lightweight. However, the server must query *something* — and if that something is still raw Markdown files, it still performs O(n) heading-grep, providing no improvement over the current approach. Streamable HTTP transport adds Origin validation, DNS rebinding prevention, and `Mcp-Session-Id` header management, materially increasing the implementation surface for no benefit in a local subprocess context. The correct architecture is B' (structured SQLite index) as backend, with Candidate D as an MCP tool access layer on top. This is consistent with the pattern in [agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md) which identified MCP as the "minimal viable A2A surface" — but that surface must sit on top of a queryable store, not replace the need for one.

---

## Pattern Catalog

### P1: SQLite-as-Index (Append-Indexed Markdown Journal)

Markdown files serve as the canonical, append-only source of truth for session content. A SQLite database (FTS5 virtual table) is maintained as a derived read-accelerator, rebuilt deterministically from Markdown source on init and updated incrementally on write. Query paths route to SQLite; write paths route to Markdown. The index is never the source of truth — if it is deleted or corrupted, a full rebuild from Markdown restores it exactly.

**Canonical example**: Obsidian and Logseq both maintain `.md` files as the user-facing canonical format. On vault open, an internal SQLite index is built from all Markdown files. Search, backlink resolution, and graph view all query SQLite. Users write `.md` files directly; the index is transparent. Applying this to dogma: `prune_scratchpad.py --init` creates `.tmp/<branch>/.scratchpad_index.db`; `validate_session_state.py` queries `SELECT phase, status FROM sessions WHERE status = 'active'` instead of grepping headings; `watch_scratchpad.py` triggers an incremental index update on each file-change event.

**Anti-pattern**: Treating the SQLite `.db` file as the primary artifact committed to git or shared between agents. Binary SQLite files do not git-diff, cannot be manually inspected during a session review, and introduce merge conflicts with no resolution path. Any architecture that places SQLite as the write target rather than the index target inherits all of these problems. Candidate B (standalone SQLite) is this anti-pattern — it trades readability for query performance without the hybrid's ability to preserve both.

---

### P2: Incremental YAML-Frontmatter Enrichment

Session-level metadata (active phase, current branch, active issue numbers, blocker flags) is encoded as YAML frontmatter at the top of each scratchpad file at init time. This addresses the fastest-path query patterns (Q1: active phase, Q5: open blockers) without requiring any infrastructure beyond the `python-frontmatter` library. It is not a final architecture — it does not address cross-session queries or section-content lookup — but it is a zero-friction incremental improvement that can ship immediately while B' is being implemented.

**Canonical example**:
```yaml
---
branch: feature/scratchpad-sqlite
date: 2026-03-17
active_phase: "Phase 2"
active_issues: [304, 297, 128]
blockers: []
last_agent: "Executive Orchestrator"
---
```
With this frontmatter, `validate_session_state.py` can answer Q1 and Q5 via `frontmatter.load(path).metadata['active_phase']` — a single dict lookup, not a heading scan. Agents write their active phase label to frontmatter on phase transition via `replace_string_in_file`, preserving the existing write tool contract.

**Anti-pattern**: Using YAML frontmatter as a substitute for a structured query layer — attempting to encode the full section-content index and cross-session history in frontmatter keys. YAML frontmatter is bounded by the fact that `python-frontmatter` loads the entire file into memory and returns a string for `.content` — it does not provide indexed access into body sections. Queries Q2 (section content) and Q3 (cross-day lookup) still require full-file reads even with frontmatter present. Candidate C treated as a final architecture produces a system that answers two of five queries well and the remaining three no better than the status quo.

---

## Gap & Differentiation Matrix

| Dimension | A (Flat Markdown) | B' (SQLite-as-index + Markdown) | C (YAML-fronted Markdown) | D (MCP-mediated server) |
|---|---|---|---|---|
| **Query power** (all 5 patterns?) | ❌ 1/5 native; 4/5 require O(n) scan | ✅ 5/5 at O(log n) via FTS5 index | ⚠️ 2/5 native (Q1, Q5); 3/5 still O(n) | ⚠️ Depends on backend — inherits B' score if backed by B' |
| **Git compatibility** (human-readable, diffable?) | ✅ Full git-diff; session history readable | ✅ Markdown source diffs cleanly; `.db` file is gitignored | ✅ Full git-diff | ✅ Markdown source unchanged |
| **Write path change required?** | — (no change) | ❌ No write-path change; index updated by watcher/init | ❌ No write-path change; frontmatter added at init | ❌ No write-path change (access layer only) |
| **Migration complexity** | — (status quo) | Low — `prune_scratchpad.py --init` builds index from existing files | Very low — add frontmatter block to `--init` template | Medium — requires B' as prerequisite; MCP server scaffolding |
| **Local Compute-First compliance** | ✅ Zero infrastructure | ✅ stdlib `sqlite3`; no network; no external deps | ✅ stdlib + `python-frontmatter`; no network | ✅ stdio subprocess; no network (stdio transport) |

---

## Recommendations

### 1. Adopt Candidate B' (SQLite-as-index + Markdown source of truth)

**Decision**: ADOPT

**Implementation path**:
- `prune_scratchpad.py --init` creates `.tmp/<branch>/.scratchpad_index.db` with schema `(id INTEGER PK, file_path TEXT, modified_at INTEGER, phase TEXT, heading TEXT, section_content TEXT, metadata_json TEXT)`.
- `validate_session_state.py` phase-status queries replace heading-grep with `SELECT phase, status FROM sessions WHERE phase MATCH ?`.
- `watch_scratchpad.py` triggers incremental index update on each `.md` file-change event (reuse existing watcher loop).
- The `.db` file is gitignored; Markdown `.md` scratchpad files continue to be committed as session records.
- No agent behaviour changes — all agents continue to write via `replace_string_in_file`.

This closes the "programmatic queryability" gap identified in [mcp-state-architecture.md](mcp-state-architecture.md) using only stdlib dependencies, consistent with the **Local Compute-First** axiom ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)).

### 2. Scope Candidate D (#297) as an access layer on top of B' — not a standalone architecture

**Decision**: SCOPE (deferred, depends on B')

Issue #297 (MCP-mediated scratchpad query) remains valid and its access-layer architecture is sound. The implementation should:
- Use stdio transport exclusively (no HTTP server); the MCP spec recommends stdio for local subprocesses.
- Expose three tool calls: `session_status` (active phase, blockers), `section_query` (section content by phase label), `issue_lookup` (cross-session issue status).
- Back all three tool calls against the B' SQLite index, not against Markdown file reads.
- Treat atomic write coordination (the gap identified in [agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md)) as a separate concern — SQLite WAL mode provides the write serialisation primitive.

**#297 depends on B'**. Do not implement the MCP server before the SQLite index exists — this would produce a server with O(n) query performance, defeating the purpose.

### 3. Adopt Candidate C (YAML-fronted Markdown) as an immediate incremental step

**Decision**: ADOPT NOW (fast win while B' is in progress)

Add structured YAML frontmatter to `prune_scratchpad.py --init`. Fields: `branch`, `date`, `active_phase`, `active_issues`, `blockers`, `last_agent`. This costs one `replace_string_in_file` call at init time and enables `validate_session_state.py` to answer Q1 (active phase) and Q5 (open blockers) without heading-grep. The `python-frontmatter` library parses it with a single dict lookup. Agents that transition phases write their new phase label to the frontmatter block — a one-line `replace_string_in_file` call. This delivers immediate brittleness reduction for the two highest-frequency queries before B' ships, consistent with the **Algorithms Before Tokens** axiom ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)).

---

### Impact Analysis

| Issue | Impact | Action |
|---|---|---|
| **#128** (Phase 1 AFS Integration) | **SCOPED** — depends on B' SQLite index for cross-phase state retrieval. Unblock #128 once B' index is implemented and `validate_session_state.py` is updated. | Add `blocked-by: B'` dependency note; reopen after B' ships. |
| **#129** (SQLite Pattern A1) | **CONVERGED** — #129's SQLite FTS5 approach is the correct pattern and directly overlaps with B' index implementation. Refocus #129 as the B' implementation issue to avoid duplicated effort. | Update #129 body to reflect B' hybrid schema; close original FTS5-standalone framing. |
| **#297** (MCP-mediated scratchpad) | **SCOPED** — implement as MCP tool access layer on top of B'; use stdio transport; valid but depends on B' first. | Add `blocked-by: #129-B'` label; keep open. |

---

## Open Questions

- **Incremental index update fidelity**: `watch_scratchpad.py` currently triggers on file-change events. The incremental index update strategy for partial section rewrites (when `replace_string_in_file` changes one section but not others) requires a diff-aware indexing pass or full-file re-index on each write. Full re-index is simpler and correct at dogma's file sizes (< 500 lines); diff-aware is an optimisation for later.
- **Multi-agent write serialisation**: SQLite WAL mode serialises concurrent writes at the database level. The Markdown source-of-truth files do not have equivalent lock semantics. For now, dogma's single-agent-per-file-per-session convention avoids this; explicit file locking should be evaluated if parallel agents write to the same session file.
- **Retention and archive policy**: The current `prune_scratchpad.py` compression/archive model is deprecated (per-day files replace weekly compression). The B' index should mirror this: one `.db` file per branch, rebuilt on `--init`, not retained long-term in session archives.

---

## Sources

- [docs/research/mcp-state-architecture.md](mcp-state-architecture.md) — gap analysis: "programmatic queryability" and "state shape enforcement" deficiencies in current scratchpad substrate
- [docs/research/agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md) — MCP as minimal viable A2A surface; atomic write coordination gap
- [docs/research/intelligence-architecture-synthesis.md](intelligence-architecture-synthesis.md) — LangGraph SQLite checkpointer as production-validated cross-phase state persistence pattern
- [MCP Specification — Transports (2025-03-26)]( https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) — stdio transport recommendation for local subprocesses; HTTP transport complexity
- [SQLite FTS5 Extension](https://www.sqlite.org/fts5.html) — FTS5 virtual table schema, automerge, query syntax
- [AGENTS.md](../../AGENTS.md) — Local Compute-First, Algorithms Before Tokens, Programmatic-First constraints
- [MANIFESTO.md](../../MANIFESTO.md) — §2 Algorithms Before Tokens, §3 Local Compute-First (foundational axioms)
