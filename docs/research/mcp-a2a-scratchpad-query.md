---
title: "MCP-Mediated Scratchpad Query — A2A Minimal Viable Surface"
status: "Final"
research_issue: 297
closes_issue: 297
date: 2026-03-17
sources:
  - docs/research/agent-to-agent-communication-protocol.md
  - docs/research/mcp-state-architecture.md
  - docs/research/scratchpad-architecture-decision.md
  - docs/research/mcp-production-pain-points.md
  - https://modelcontextprotocol.io/docs/concepts/tools
  - https://github.com/modelcontextprotocol/python-sdk
  - AGENTS.md
  - MANIFESTO.md
---

# MCP-Mediated Scratchpad Query — A2A Minimal Viable Surface

## Executive Summary

This document synthesises research across MCP production pain points (#285), scratchpad
architecture decisions (#304), prior A2A interface recommendations, and MCP tool schema
specifications to deliver a **PROCEED** verdict for a prototype `scratchpad-query` MCP server.
The server is scoped to three tools — `get_phase_status`, `get_section`, and `get_blockers` —
and exposes the scratchpad's SQLite FTS5 index (architecture B') as a controlled query surface
for agent-to-agent coordination. This prototype is gated: architecture B' (SQLite index in
`prune_scratchpad.py`, issue #129) must ship first. Without B', the server degrades to
heading-grep and provides no improvement over the current `validate_session_state.py` approach.

The dominant justification is **token efficiency**, not fleet size. FTS5 returns approximately
50 lines against a 500-line scratchpad for a targeted section query, reaching break-even at a
200-line scratchpad queried for a 20-line section. This threshold is crossed in every multi-phase
dogma session, making the per-session query-frequency threshold the correct adoption criterion —
not fleet scale. This aligns with the Algorithms-Before-Tokens axiom (MANIFESTO.md §2): encoding
the retrieval problem deterministically at the FTS5 layer produces a more efficient, auditable
outcome than prompting agents to navigate raw Markdown.

Security is addressed through three complementary controls sufficient for the local stdio threat
model: path allowlisting to `.tmp/` to prevent traversal, parameterized FTS5 queries to prevent
SQL injection, and `audience: ["user"]` annotations on all content-returning tools to prevent
the LLM from interpreting scratchpad content as agent directives. The stdio transport means VS
Code sandbox approval is the trust boundary; no network exposure is introduced. Tasks API
integration is explicitly deferred pending MCP lifecycle specification stabilisation, consistent
with the stateless-first design pattern documented in [mcp-production-pain-points.md](mcp-production-pain-points.md).

---

## Hypothesis Validation

### H1: MCP-mediated scratchpad query provides material security improvement vs. direct `read_file` access

**VERDICT: PARTIALLY SUPPORTED**

The server does not improve transport-level security — `read_file` and an MCP stdio call both
access the same local `.tmp/` files with the same OS-level permissions. The real security gain is
**controlled content routing**: by annotating all content-returning tools with `audience: ["user"]`
(MCP spec 2025-06-18 §5.1), the server signals to the VS Code host that scraped scratchpad text
should not be passed back to the LLM as directive-level input. This is prompt injection isolation,
not data access control.

Direct `read_file` calls have identical data exposure; the MCP layer adds no secrecy. The
meaningful improvement is that the structured envelope `{"section": ..., "content": ...}` plus
the `audience` annotation makes the trust boundary explicit and machine-checkable — whereas a
raw `read_file` return provides no such signal. For the local stdio use case, this distinction
is sufficient. The Endogenous-First axiom (MANIFESTO.md §1) supports encoding this trust signal
in the tool schema rather than relying on agent-level prompt instructions.

### H2: The MCP server can provide useful phase status queries without a structured backend (Candidate D as standalone)

**VERDICT: NOT SUPPORTED**

Architecture Candidate D (MCP-mediated access layer) is not standalone. Without the B' SQLite
FTS5 index, every tool call must fall back to heading-grep over raw Markdown, which: (a) provides
no token savings over reading the file directly, (b) is brittle to heading text changes, and
(c) does not support fuzzy or cross-section queries. Per [scratchpad-architecture-decision.md](scratchpad-architecture-decision.md),
B' defines Markdown as source of truth with SQLite as index — Candidate D is explicitly "access
layer on top of B'". Implementing the MCP server before #129 ships would produce a thin wrapper
over a tool (`validate_session_state.py`) that already exists. B' is a hard prerequisite.

### H3: Token cost savings from MCP FTS5 queries justify the implementation overhead

**VERDICT: CONFIRMED**

FTS5 returns ~50 lines versus 500 for a full file read when querying a specific 20-line section
in a 200-line scratchpad. Across a typical 8-phase multi-phase session with ≥2 section queries
per phase, the gross saving is on the order of 3,600 lines avoided (16 queries × 450 lines saved
each). At typical LLM context costs this is material. The IPC overhead of stdio JSON-RPC adds
5–15ms and approximately 200 bytes of framing per call — negligible against the token budget.
Break-even is reached at 200-line scratchpad queried for a 20-line section, which is the default
dogma session format. The Algorithms-Before-Tokens axiom (MANIFESTO.md §2) is directly
instantiated here: a deterministic FTS5 query encodes more value per token than prompting an
agent to scan the file interactively.

### H4: Fleet size is the relevant threshold for MCP server adoption

**VERDICT: NOT SUPPORTED**

Fleet size was proposed as a threshold because the value of shared state grows with concurrent
readers. However, per-session query frequency is the correct independent variable for token
efficiency. The current fleet (single Orchestrator + up to 4 delegated subagents, no concurrent
writers) crosses the per-session threshold in every multi-phase sprint because the Orchestrator
alone queries scratchpad state multiple times per phase. Adoption is justified now, independent
of whether the fleet expands. Prior A2A research ([agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md))
correctly identified the recommended interface shape (`get_phase_status`, `get_active_agents`,
`get_unresolved_blockers`) without assuming fleet scale — this synthesis confirms that read
frequency, not fleet size, is the driver.

---

## Pattern Catalog

### P1 — Structured-Envelope Return (Prompt Injection Isolation)

**Problem**: An MCP tool that returns raw scratchpad section text risks the LLM treating
that text as agent directives. A `## Handoff` section containing imperative language ("Do X
before Y") could be interpreted as a new instruction rather than historical state.

**Canonical example**:

```python
@mcp.tool(annotations={"audience": ["user"]})
async def get_section(scratchpad_path: str, heading: str) -> dict:
    content = _fts5_query(scratchpad_path, heading)
    return {
        "section": heading,
        "content": content,        # audience:user — not passed as LLM directive
        "line_start": content.line_start,
        "line_end": content.line_end,
    }
```

The `audience: ["user"]` annotation (MCP spec 2025-06-18 §5.1) signals to the VS Code host that
the returned content should be displayed to the user or written to a structured artifact, not
injected back into the model's instruction stream. For a local stdio server, VS Code sandbox
approval constitutes the trust boundary — trusting this annotation is appropriate.

**Anti-pattern**:

```python
# BAD: returns raw scratchpad text without audience annotation
@mcp.tool()
async def get_section(scratchpad_path: str, heading: str) -> str:
    return open(scratchpad_path).read()   # Full file, no envelope, no annotation
```

This approach: (1) returns the full file rather than a targeted section (token waste), (2)
provides no trust boundary signal for LLM hosts, and (3) exposes multi-section content that
could contain directive-format text from earlier agents.

---

### P2 — SQLite-Backed stdio MCP Server (FTS5 query layer over Markdown source of truth)

**Problem**: Agent scratchpad access via `read_file` reads entire files and has no structured
query capability. Phase status and blocker lookups require scanning hundreds of lines per call.

**Canonical example**:

```python
from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("scratchpad-query")

def _fts5_query(db_path: str, query: str, limit: int = 5):
    conn = sqlite3.connect(db_path)
    # Parameterized query — no SQL injection surface
    rows = conn.execute(
        "SELECT date, branch, phase, status, content FROM sessions WHERE sessions MATCH ?",
        (query,)
    ).fetchmany(limit)
    conn.close()
    return rows
```

This pattern is grounded in the winning architecture from [scratchpad-architecture-decision.md](scratchpad-architecture-decision.md):
B' (SQLite FTS5 as index, Markdown as source of truth). The MCP server is a thin query adapter
over B' — it does not own the data, does not write to the index, and does not replace the
Markdown scratchpad. The FTS5 schema is:

```sql
CREATE VIRTUAL TABLE sessions USING fts5(date, branch, phase, status, content);
```

Parameterized queries are non-negotiable: FTS5 `MATCH` clauses are still vulnerable to
injection if values are interpolated via f-strings. Always pass user-supplied query strings
as bound parameters.

**Anti-pattern**:

```python
# BAD: f-string SQL injection surface
query_str = f"SELECT * FROM sessions WHERE sessions MATCH '{user_input}'"
conn.execute(query_str)
```

This is a SQL injection vulnerability even in FTS5 — a malicious `user_input` can close the
MATCH clause and inject arbitrary SQL. Always use `cursor.execute("... MATCH ?", (value,))`.

---

## Gap & Differentiation Matrix

| Dimension | Current approach (`read_file` / `validate_session_state.py`) | MCP-mediated (`scratchpad-query` server + B') |
|---|---|---|
| **Prompt injection isolation** | None — raw file content returned as LLM context | Structured envelope + `audience: ["user"]` annotation isolates content from directive stream |
| **Query performance (tokens)** | Full file read (~500 lines) per status check | FTS5 targeted query (~50 lines); break-even at 200-line file |
| **Write path impact** | None | None — server is read-only; B' index written by `prune_scratchpad.py` |
| **Implementation complexity** | Zero — read_file is built-in | Medium — requires B' (#129) shipped first; then ~150-line FastMCP server |
| **Fleet scalability** | Degrades with file size; no cross-section query | Constant-time per FTS5 query regardless of file size; supports cross-section and fuzzy queries |
| **Structured blocker tracking** | Manual grep (fragile) | `get_blockers` returns `{text, phase, resolved}` envelope from FTS5 index |
| **Dependency** | None | Hard dependency on B' (issue #129) |

The matrix confirms: the MCP approach is strictly better on query performance and prompt injection
isolation, neutral on write path, and introduces a one-time implementation cost plus a hard
prerequisite. There is no dimension on which the current approach is superior for scratchpads
exceeding 200 lines queried more than twice per session.

---

## Recommendations

### 1. PROCEED with prototype — gated on B' (#129)

Implement `scripts/mcp_scratchpad_query.py` as a FastMCP stdio server exposing three tools:
`get_phase_status`, `get_section`, and `get_blockers`. Do not begin this work until
`prune_scratchpad.py` ships the B' SQLite FTS5 index (issue #129). The server is a thin adapter
over B' queries; any implementation before #129 ships produces heading-grep, not FTS5 — no
improvement over the status quo.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("scratchpad-query")

@mcp.tool()
async def get_phase_status(scratchpad_path: str, phase: int | None = None) -> dict:
    """Query active phase status from SQLite scratchpad index."""
    ...

@mcp.tool()
async def get_section(scratchpad_path: str, heading: str, fuzzy: bool = False) -> dict:
    """Retrieve a specific section from the scratchpad. Content is audience:user."""
    ...

@mcp.tool()
async def get_blockers(scratchpad_path: str, branch: str | None = None) -> dict:
    """List unresolved blockers from the scratchpad."""
    ...

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The interface names are drawn directly from prior A2A research ([agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md)):
`get_phase_status` and `get_unresolved_blockers` were recommended there; `get_section` is the
generalised retrieval primitive enabling those higher-level queries. STDOUT must not be written
in the stdio server body — all logging must go to stderr (MCP spec stdio constraint confirmed
in #285 findings).

### 2. IMPLEMENT security controls before first use

Three controls are required and non-negotiable for the prototype:

- **Path allowlist**: validate `scratchpad_path` against `.tmp/` prefix using `os.path.realpath`
  and assert it starts with the workspace root. Reject any path containing `..`, symlink targets
  outside `.tmp/`, or absolute paths not under the workspace.
- **Parameterized FTS5 queries**: all `MATCH` clauses must use bound parameters
  (`cursor.execute("... MATCH ?", (query,))`). Never interpolate user-supplied strings.
- **`audience: ["user"]` annotations**: apply to all three tools via FastMCP `annotations`
  kwarg. This is the primary prompt injection mitigation and must not be omitted in the
  prototype — it is not a polish item.

These controls are sufficient for the local stdio threat model. The Endogenous-First axiom
(MANIFESTO.md §1) supports encoding these as enforced schema constraints (MCP annotations +
Python assertions) rather than relying on agent-level prompt reminders.

### 3. DEFER Tasks API integration

The MCP Tasks API (async long-running lifecycle) is deferred pending specification
stabilisation. Pain point P2 from #285 confirms that lifecycle transitions in the current
Tasks spec are underspecified and cause production errors in complex multi-step workflows.
The `scratchpad-query` MVP uses synchronous request/response only — all three tools return
immediately from FTS5 queries. If long-running analysis tasks are needed in future (e.g.,
cross-session trend queries), revisit after the MCP spec publishes stable lifecycle
semantics. Do not add Tasks API dependency to the prototype.

---

## Sources

1. **[docs/research/agent-to-agent-communication-protocol.md](agent-to-agent-communication-protocol.md)** — Prior dogma A2A interface recommendations; source of `get_phase_status`, `get_active_agents`, `get_unresolved_blockers` interface naming; prompt injection security guidance.

2. **[docs/research/mcp-state-architecture.md](mcp-state-architecture.md)** — MCP server architecture patterns; stateless vs. stateful tool design; production deployment considerations.

3. **[docs/research/scratchpad-architecture-decision.md](scratchpad-architecture-decision.md)** — Winning architecture B' (SQLite FTS5 as index + Markdown as source of truth); Candidate D dependency on B'; FTS5 schema definition.

4. **[docs/research/mcp-production-pain-points.md](mcp-production-pain-points.md)** — Phase 1A findings: stdio transport constraints (STDOUT corruption, logging to stderr); Tasks API deferral rationale; stateless tool call design pattern.

5. **MCP Specification 2025-06-18 §5.1** — Tool schema: `name`, `description`, `inputSchema`, `annotations` (`audience`, `priority`) fields. URL: https://modelcontextprotocol.io/docs/concepts/tools

6. **MCP Python SDK** — `FastMCP` class, `@mcp.tool()` decorator, `mcp.run(transport="stdio")` pattern. URL: https://github.com/modelcontextprotocol/python-sdk

7. **[AGENTS.md](../../AGENTS.md)** — Governing operational constraints; security guardrails; `Algorithms-Before-Tokens` and `Endogenous-First` axiom references.

8. **[MANIFESTO.md](../../MANIFESTO.md)** — Foundational axioms: §1 Endogenous-First, §2 Algorithms-Before-Tokens, §3 Local-Compute-First.
