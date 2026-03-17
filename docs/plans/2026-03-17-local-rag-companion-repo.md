---
title: "Local RAG Companion Repo — LanceDB + BGE-Small-EN-v1.5"
status: "Active"
closes_issue: 294
date: 2026-03-17
sprint: 15
related_research:
  - docs/research/local-inference-rag.md
  - docs/research/greenfield-repo-candidates.md
  - docs/research/intelligence-architecture-synthesis.md
---

## Objective

Scaffold a standalone companion repository providing local vector search for the dogma knowledge base. Built on LanceDB (no server process) + BGE-Small-EN-v1.5 (≤100MB model) + H2-chunk indexing of `docs/research/` and `docs/guides/`. Exposed via MCP stdio server (`rag_query`, `rag_reindex` tools) with `@mcp.tool()` FastMCP pattern.

## Prerequisites

1. Phase 1: B' SQLite scratchpad index (#129) — not required for RAG, but in same sprint
2. Phase 1: #297 MCP server shipped (validates FastMCP stdio pattern before RAG server)

## Phases

### Phase 1 — Environment + Dependencies

**Agent**: Executive Scripter
**Description**: Bootstrap the companion repository with all runtime and dev dependencies.

**Tasks**:
- Create companion repo: `dogma-rag/` (separate git repo, not monorepo)
- `pyproject.toml`: `lancedb>=0.5`, `sentence-transformers>=2.7`, `mcp>=1.0` (FastMCP)
- Model download script: `scripts/download_model.py` with `huggingface_hub` pull
- Test: `pytest tests/test_model_load.py`

**Deliverables**:
- D1: `dogma-rag/pyproject.toml` committed with locked dependencies
- D2: `dogma-rag/scripts/download_model.py` present and executable
- D3: `tests/test_model_load.py` passes (`uv run pytest tests/test_model_load.py`)

**Depends on**: nothing
**Gate**: Phase 2 does not start until all three deliverables confirmed present and tests green.

---

### Phase 2 — Indexer

**Agent**: Executive Scripter
**Description**: Implement the H2-chunked LanceDB indexer over `docs/research/` and `docs/guides/`.

**Tasks**:
- `indexer.py`: walk `docs/research/`, `docs/guides/`, chunk by `## ` heading (H2), write LanceDB table
- Schema: `{id: str, source: str, heading: str, content: str, embedding: vector[384]}`
- CLI: `uv run python indexer.py --root /path/to/dogma [--force]`
- Idempotent: detect existing embeddings by content hash; skip unchanged chunks
- Test: `pytest tests/test_indexer.py` covering happy path + incremental update + force-rebuild

**Deliverables**:
- D1: `dogma-rag/indexer.py` implemented with `--root` and `--force` flags
- D2: `tests/test_indexer.py` green with ≥ 80% coverage

**Depends on**: Phase 1 (model download script required)
**Gate**: Phase 3 does not start until `tests/test_indexer.py` passes and coverage reported ≥ 80%.

---

### Phase 3 — MCP Server

**Agent**: Executive Scripter
**Description**: Implement the FastMCP stdio server exposing `rag_query` and `rag_reindex`.

**Tasks**:
- `server.py`: `FastMCP("dogma-rag")`
- `@mcp.tool() rag_query(query: str, top_k: int = 5)` — returns top-k chunks with `audience: ["user"]`
- `@mcp.tool() rag_reindex(force: bool = False)` — triggers indexer
- stdio transport; no network exposure
- Security: validate `root_path` against allowlist; no arbitrary file access
- Test: `pytest tests/test_server.py` using FastMCP test client

**Deliverables**:
- D1: `dogma-rag/server.py` implemented and running over stdio
- D2: `tests/test_server.py` green; path-traversal security test included

**Depends on**: Phase 2 (indexer must exist before server can call it)
**Gate**: Phase 4 does not start until `tests/test_server.py` passes.

---

### Phase 4 — Integration with dogma

**Agent**: Executive Docs
**Description**: Wire the companion server into the dogma repo and document setup.

**Tasks**:
- `.mcp.json` at dogma repo root: add `dogma-rag` server entry pointing to companion repo
- End-to-end test: `claude -p "what does mcp-state-architecture.md recommend for transport?" --mcp-config .mcp.json`
- Create `docs/guides/local-rag-setup.md` with install + index + query walkthrough

**Deliverables**:
- D1: `dogma/.mcp.json` updated and committed
- D2: `docs/guides/local-rag-setup.md` committed

**Depends on**: Phase 3
**Gate**: End-to-end query returns a relevant chunk; guide committed before closing issue.

---

### Phase 5 — Review & Commit

**Agent**: Review → GitHub
**Description**: Validate all changed files; commit and push.

**Deliverables**: All phases committed; PR updated; CI green.
**Depends on**: All prior phases.

## Acceptance Criteria

- [ ] `indexer.py` indexes all `docs/research/` and `docs/guides/` Markdown files by H2 section
- [ ] `rag_query` returns relevant chunks with source citation and `audience: ["user"]` annotation
- [ ] `rag_reindex` is idempotent (no duplicates on re-run)
- [ ] Test coverage ≥ 80% across all scripts
- [ ] `.mcp.json` integration documented in `docs/guides/local-rag-setup.md`
- [ ] All LanceDB data stored under `.cache/rag/` (gitignored except `.cache/rag/README.md`)

## Risks

- `sentence-transformers` first-run model download (~90 MB) may fail in CI; mitigate with `--skip-download` flag + pre-download in CI workflow.
- LanceDB v0.5 API may differ from later versions; pin version in lockfile.
