---
title: "AIGNE AFS Context Governance Layer Evaluation"
research_issue: "#14"
status: Final
date: 2026-03-09
closes_issue: 14
sources_read: 7
---

# AIGNE AFS Context Governance Layer Evaluation

> **Status**: Final
> **Research Question**: Can the AIGNE Agent File System (AFS) context governance pipeline serve as the substrate for EndogenAI's token offloading strategy — replacing or augmenting the current scratchpad approach?
> **Date**: 2026-03-09

---

## 1. Executive Summary

The AIGNE AFS (Agentic File System) is a context governance layer backed by SQLite + a local vector store, exposing an MCP tool interface for agent integration. It implements a formal context engineering pipeline (Context Constructor → Context Updater → Context Evaluator) layered on top of the LangChain-attributed write→select→compress→isolate four-stage pattern (`docs/research/agentic-research-flows.md` §Attribution Correction).

**Governing axioms**: `MANIFESTO.md §2 — Algorithms Before Tokens` (a deterministic context manager reduces token burn per session) and `MANIFESTO.md §3 — Local Compute-First` (SQLite + local vector store, no cloud dependency).

**Recommendation: MONITOR — do not adopt yet.**

AIGNE AFS is architecturally the strongest candidate for a context governance layer among options surveyed. Its design directly addresses EndogenAI's primary context management gap: no semantic retrieval layer over episodic/experiential memory between sessions. However, it shares the same prerequisite as the episodic memory libraries evaluated in `docs/research/episodic-memory-agents.md`: the local compute baseline (`OPEN_RESEARCH.md` item 1) must be resolved before a local AFS deployment is viable. Premature adoption before that baseline is stable adds infrastructure complexity against an uncertain inference backend.

The current scratchpad-based approach remains the correct architecture for now. The evaluation below provides a concrete integration design that should be executed once the prerequisite is met.

---

## 2. Hypothesis Validation

### H1 — The AIGNE AFS pipeline directly addresses the EndogenAI context management gap

**Validated.** The AIGNE paper enumerates seven memory types. The current EndogenAI architecture satisfies two of them:

| AIGNE Memory Type | Persistence Scope | EndogenAI Coverage |
|---|---|---|
| **Scratchpad** | Ephemeral — single reasoning step | ✅ `.tmp/<branch>/<date>.md` |
| **Historical Record** | Immutable — append-only audit trail | ✅ Git commit history |
| **Episodic** | Session-scoped — task or conversation | ⚠️ Partial — scratchpad is session-scoped but not queryable |
| **Experiential** | Long-term — heuristics from outcomes | ❌ Not implemented — re-discovered each session |
| **Fact** | Long-term — explicit factual claims | ❌ Not implemented — research docs serve this role but are not retrievable by query |
| **Procedural** | Long-term — how-to knowledge | ⚠️ Partial — encoded in AGENTS.md and workflow guides but not indexed |
| **User** | Long-term — user-specific preferences | ❌ Not implemented |

The AFS layer would close the three ❌ gaps (Experiential, Fact, User) and upgrade the two ⚠️ partials (Episodic, Procedural) to queryable. This is a genuine capability gap that the current scratchpad cannot address.

### H2 — AIGNE AFS is local-first compatible

**Validated (conditional).** AIGNE's architecture uses:
- SQLite for structured persistence (zero-infrastructure, file-based)
- A local vector store (supports qdrant-in-memory or SQLite-vec extension — no cloud required)
- MCP tool interface for agent integration

No cloud dependency is required for the core AFS pipeline. The prerequisite is a local embedding model (Ollama `nomic-embed-text` or equivalent) to generate vector embeddings for the vector store. This is the same dependency as `docs/research/episodic-memory-agents.md` — the local compute baseline (`OPEN_RESEARCH.md` item 1) must be in place.

**Anti-pattern**: Deploying AIGNE AFS with an OpenAI or Anthropic embedding endpoint as "easier to get running" — this violates `MANIFESTO.md §3 — Local Compute-First`. The double-violation (cloud inference for embeddings + potential cloud AFS deployment) is the canonical anti-pattern (`MANIFESTO.md §3, lines 140–142`).

### H3 — The AFS can wrap the existing `.tmp/<branch>/<date>.md` convention

**Validated (design only — not implemented).** The integration design in Section 3 (Pattern A1) shows how the scratchpad convention can be preserved as the human-facing write layer while AFS provides the machine-queryable retrieval layer. The two layers are complementary, not competing.

### H4 — AIGNE's Context Engineering Pipeline supersedes the four-stage loop

**Partially validated — with attribution correction.** Prior synthesis attributed the write→select→compress→isolate pattern to AIGNE. This was incorrect. The four-stage pattern is LangChain's industrial practice, cited by the AIGNE paper as `[LangChainContextEngineering2024]`. AIGNE's unique contribution is the **Context Engineering Pipeline** (Constructor + Updater + Evaluator) that operationalises the four stages with lineage metadata, confidence scoring, and human-review triggers.

The attribution matters for evaluation: the four-stage pattern is available independently of AIGNE (it can be implemented as a script without the full AFS framework). AIGNE adds the formal pipeline with auditable provenance — valuable for a project that already tracks provenance via `scripts/audit_provenance.py`.

---

## 3. Pattern Catalog

### Pattern A1 — Scratchpad-Preserving AFS Integration

**Context**: The local compute baseline is confirmed. The scratchpad convention is working well for single-session continuity but cross-session retrieval is becoming a bottleneck: the session start step requires reading multiple prior scratchpad files to reconstruct context.

**How it works**: The AFS wraps the scratchpad, not replaces it. At session close, a script indexes the scratchpad into the AFS repository. At session start, the AFS provides a retrieved context digest instead of requiring linear reads of prior scratchpad files.

**Integration design**:

```
Session                 Scratchpad (.tmp/)              AFS (SQLite + vector)
  |                           |                               |
  | write ------------------→ |                               |
  |                           |                               |
  | [close session]           |                               |
  |                           | index_to_afs(date, branch) →  |
  |                           |                               | write(episodic)
  |                           |                               | write(fact)
  |                           |                               |
  | [next session start]      |                               |
  |                           |         ← retrieve(query) --- |
  |  read scratchpad summary ←|                               |
  |  read afs digest          |                               |
```

**Canonical example**:

```python
# scripts/index_session_to_afs.py — run at session close
import sqlite3
import json
from pathlib import Path
from datetime import date

def index_session(scratchpad_path: Path, db_path: Path = Path(".afs/context.db")):
    """Index today's scratchpad entries into the AFS SQLite store."""
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY,
            branch TEXT,
            date TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    content = scratchpad_path.read_text()
    conn.execute(
        "INSERT INTO episodes (branch, date, content, created_at) VALUES (?, ?, ?, ?)",
        (scratchpad_path.parent.name, str(date.today()), content, date.today().isoformat())
    )
    conn.commit()
    conn.close()
```

```python
# scripts/retrieve_afs_context.py — run at session start before Session Start write
import sqlite3
from pathlib import Path

def retrieve_recent(db_path: Path, branch: str, n: int = 3) -> list[dict]:
    """Retrieve the n most recent session records for this branch."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT date, content FROM episodes WHERE branch = ? ORDER BY date DESC LIMIT ?",
        (branch, n)
    ).fetchall()
    conn.close()
    return [{"date": r[0], "content": r[1]} for r in rows]
```

**Anti-pattern**: Replacing the scratchpad with AFS, removing the `.tmp/<branch>/<date>.md` human-readable file. The scratchpad's value is its human-readability, git manageability, and use as a recovery artifact after context compaction. AFS augments retrieval — it does not replace the audit trail.

**Applicability**: Deferred. Requires `OPEN_RESEARCH.md` item 1 resolved and a local embedding model available.

---

### Pattern A2 — Context Constructor as Pre-Session Digest

**Context**: Multiple research branches have accumulated scratchpad histories. The session start step is spending significant tokens re-reading prior files. The AFS Context Constructor pipeline can pre-compute a compressed, relevance-ranked digest.

**How it works**: At session start, instead of `cat .tmp/<branch>/YYYY-MM-DD.md`, a script queries the AFS and returns a compressed digest: top-N most relevant episodic records + extracted fact claims for the current research theme.

**Canonical example**:

```bash
# Session start: retrieve AFS digest for current branch
uv run python scripts/retrieve_afs_context.py \
  --branch "$(git branch --show-current)" \
  --query "bubble substrate model value encoding" \
  --top-n 5 \
  --output ".tmp/$(git branch --show-current)/afs-digest.md"

# Read the digest before writing Session Start
cat ".tmp/$(git branch --show-current)/afs-digest.md"
```

**Anti-pattern**: Using the AFS digest as a replacement for the scratchpad re-read. The digest is a compressed retrieval — the on-disk scratchpad remains the authoritative state record for the current session (per `docs/guides/session-management.md`).

---

## 4. Recommendations

### R1 — Adopt: MONITOR — do not implement yet

**Verdict: MONITOR.** AIGNE AFS is the right long-term architecture for EndogenAI's context governance layer. The recommendation is not "skip" — it is "not yet, with a clear adoption trigger."

**Rationale tied to Local Compute-First (`MANIFESTO.md §3`)**:
- AFS requires a local embedding model. Without `OPEN_RESEARCH.md` item 1 resolved, any AFS deployment would use a cloud embedding endpoint, violating the axiom.
- Adopting AFS before the local inference stack is confirmed creates a dependency on an uncertain backend — the opposite of the Algorithms-Before-Tokens principle.
- The current scratchpad architecture is deterministic and zero-dependency. Adding AFS before its prerequisite is met adds complexity without the compensating retrieval benefit.

**Adoption trigger**: `docs/guides/local-compute.md` published and a local Ollama stack confirmed → attempt the Phase 1 integration (Pattern A1, SQLite-only, no vector store) → evaluate cross-session retrieval quality.

### R2 — Phase 1 scope: SQLite-only, no vector store

When adoption begins, start with the SQLite-only pattern (Pattern A1) before adding vector embeddings. SQLite is zero-infrastructure. The retrieval can be keyword-based (FTS5) in Phase 1. Vector search (semantic retrieval) is Phase 2 once the embedding model is confirmed.

**This respects Algorithms Before Tokens**: a deterministic FTS5 index is an algorithm; a vector similarity search is a token-burning inference step. Use the algorithm first.

### R3 — Do not replace the scratchpad convention

The `.tmp/<branch>/<date>.md` scratchpad is the session recovery artifact. It is used after context compaction events to re-read authoritative state. AFS is a retrieval layer over prior sessions — it does not serve the in-session recovery function. The two concerns are architecturally distinct and must remain separate.

### R4 — Extend `prune_scratchpad.py` to optionally index to AFS on `--force`

When the adoption trigger fires, `prune_scratchpad.py --force` (session close) should accept an `--index-afs` flag that calls `scripts/index_session_to_afs.py`. This keeps the integration in the existing toolchain without modifying the session close protocol for sessions that have not adopted AFS.

### R5 — Confirm AIGNE SQLite schema DDL before implementation

The AIGNE paper describes the memory taxonomy and pipeline architecture but does not publish the SQLite schema DDL (tracked as OPEN in `docs/research/agentic-research-flows.md` §Open Items). Before implementing Pattern A1, fetch the AIGNE framework source at `https://github.com/AIGNE-io/aigne-framework` and extract the schema. Design the EndogenAI minimal schema to be forward-compatible with AIGNE's published schema.

---

## Sources

1. arXiv 2512.05470v1 — "Everything is Context: Agentic File System (AIGNE)" — AIGNE architecture, Context Engineering Pipeline, seven memory types: https://arxiv.org/abs/2512.05470
2. AIGNE framework GitHub repository: https://github.com/AIGNE-io/aigne-framework
3. `docs/research/agentic-research-flows.md` — prior AIGNE synthesis, attribution correction, memory taxonomy table: endogenous
4. `docs/research/OPEN_RESEARCH.md` — item 1 (local compute baseline), item 4 (AIGNE AFS evaluation): endogenous
5. `MANIFESTO.md §2 — Algorithms Before Tokens`, `§3 — Local Compute-First`: endogenous
6. `docs/research/episodic-memory-agents.md` — shared prerequisite (local compute baseline), library evaluation context: endogenous (this milestone)
7. `docs/guides/session-management.md` — scratchpad convention authority: endogenous
