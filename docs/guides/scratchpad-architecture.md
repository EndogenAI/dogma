---
title: "Scratchpad Architecture — Cross-Session Working Memory"
status: Draft
owner_issue: 552
phase: 5
x-governs: [session-management, scratchpad, cross-session-retrieval]
---

# Scratchpad Architecture — Cross-Session Working Memory

**Status**: Draft (Phase 5) — Export section implemented. Import (Phase 5 deferred to #553), Cross-Session Retrieval (Phase 6), Provenance (Phase 7), and Standards Compliance (Phase 8) sections to be added in subsequent phases.

**Purpose**: This guide documents the architecture, conventions, and tooling for the `.tmp/` scratchpad substrate — the project's file-based cross-session working memory system for agent coordination and session-state persistence.

**Governing constraints**: [`AGENTS.md § Agent Communication`](../../AGENTS.md#agent-communication), [`session-management` SKILL.md](../../.github/skills/session-management/SKILL.md)

---

## Overview

The scratchpad substrate is a **file-based working memory system** that allows agents to persist session state, coordinate across multiple agents in a single session, and preserve context across sessions spanning multiple days or weeks.

### Why File-Based?

- **Durable**: Survives compaction events in VS Code Copilot Chat and Claude Code
- **Inspectable**: Human-readable Markdown; agents and humans can both read/write
- **Versionable**: Lives in `.tmp/` (gitignored), but can be archived to `docs/sessions/` for long-term review
- **Portable**: Structured export enables migration to future substrates or external tools

### MCP Integration

The DogmaMCP server exposes scratchpad operations via the `prune_scratchpad` tool:
- **Init**: Create a new session file with structured YAML state block
- **Check**: Read current scratchpad state without writing
- **Archive**: Copy session file to `docs/sessions/` (deprecated in favor of export)

---

## Structure

### Directory Layout

```
.tmp/
  <branch-slug>/               # One folder per git branch
    _index.md                  # One-line stubs of all closed sessions
    <YYYY-MM-DD>.md            # One file per session day
```

**Branch naming convention**: Branch slug = branch name with `/` replaced by `-`. Example: `feat/research-550` → `feat-research-550`.

### File Naming

Each session file is named `<YYYY-MM-DD>.md` where the date matches the session start date in ISO 8601 format.

**Example**: `.tmp/feat-open-harness-sprint/2026-04-13.md`

### Required Sections

Every scratchpad file must include these sections (enforced by `scripts/validate_scratchpad.py`):

1. **Session State** (YAML block)
2. **Audit Trail** (table)
3. **Telemetry** (table)

Optional sections (strongly encouraged):
- **Session Start** (encoding checkpoint: governing axiom + primary endogenous source)
- **Phase N Output** (results from each phase)
- **Session Summary** (orientation point for next session)
- **Executive Handoff** (end-of-session handoff notes)

See [`data/scratchpad-schema.yml`](../../data/scratchpad-schema.yml) for the full schema specification.

### Session State YAML

The Session State section contains a YAML block with these required fields:

```yaml
branch: feat-my-branch          # Git branch name
date: '2026-04-13'              # Session date (ISO 8601)
active_phase: "Phase 2"         # Current phase (nullable)
active_issues: [123, 456]       # GitHub issue numbers in scope
blockers: []                    # Blocking issues or dependencies
last_agent: "Executive Orchestrator"  # Last agent to write to scratchpad
phases:                         # Phase history
  - name: "Phase 1"
    status: "Closed"
  - name: "Phase 2"
    status: "In Progress"
```

**Date consistency**: The `date:` field must match the filename date. Validator enforces this.

---

## Export

### Overview

The `scripts/export_scratchpad.py` tool exports scratchpad files to structured formats for:
- **Archival**: Long-term storage in `docs/sessions/` or external systems
- **Migration**: Moving session state to future substrates (e.g., SQLite, vector DB)
- **External tool integration**: Feeding session data to analysis tools, dashboards, or LLM context systems

### Export Formats

Three formats supported:
1. **JSON**: Machine-readable structured export
2. **YAML**: Human-editable structured export
3. **Markdown**: Pass-through copy (archival)

All formats preserve the full structure of the scratchpad.

### Usage

#### Single File Export

```bash
# Export to JSON (stdout)
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md

# Export to YAML file
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md --format yaml -o /tmp/session.yml

# Export to Markdown (archival copy)
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md --format markdown -o docs/sessions/2026-04-13-my-branch.md
```

#### Batch Export (All Scratchpads)

```bash
# Export all files in .tmp/*/*.md to .cache/scratchpad-exports/<timestamp>/
uv run python scripts/export_scratchpad.py --all --format json
```

Output directory structure:
```
.cache/scratchpad-exports/
  20260413-143052/              # Timestamped batch export
    feat-branch-1_2026-04-13.json
    feat-branch-2_2026-04-14.json
```

### JSON Export Structure

Example JSON export:

```json
{
  "metadata": {
    "branch": "feat-my-branch",
    "date": "2026-04-13",
    "source_file": ".tmp/feat-my-branch/2026-04-13.md",
    "exported_at": "2026-04-13T14:30:00.123456"
  },
  "session_state": {
    "branch": "feat-my-branch",
    "date": "2026-04-13",
    "active_phase": "Phase 2",
    "active_issues": [123, 456],
    "blockers": [],
    "last_agent": "Executive Orchestrator",
    "phases": [
      {"name": "Phase 1", "status": "Committed"},
      {"name": "Phase 2", "status": "In Progress"}
    ]
  },
  "audit_trail": [
    {
      "agent": "Executive Orchestrator",
      "decision": "Start Phase 1",
      "justification": "Workplan approved",
      "time": "10:00"
    }
  ],
  "telemetry": {
    "Phases finished": "1",
    "Delegations made": "2",
    "Rate-limit events": "0",
    "Estimated tokens used": "15000"
  },
  "phases": [
    {
      "phase_num": 1,
      "title": "Phase 1 Output",
      "content": "**Date**: 2026-04-13\n**Agent**: Research Scout\n..."
    },
    {
      "phase_num": 2,
      "title": "Phase 2 Output",
      "content": "**Date**: 2026-04-13\n**Agent**: Executive Scripter\n..."
    }
  ]
}
```

### Round-Trip Validation

The export tool guarantees round-trip preservation of structure:

```bash
# Export to JSON
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md --format json -o /tmp/export.json

# Validate round-trip (all sections preserved)
python3 -c "import json; d=json.load(open('/tmp/export.json')); assert 'session_state' in d; assert 'phases' in d; print('Round-trip valid')"
```

**Guarantee**: Parsing the exported JSON/YAML will produce a dict with all keys (`metadata`, `session_state`, `audit_trail`, `telemetry`, `phases`) intact, preserving section content verbatim.

### When to Export

**Use cases**:
- **Sprint close**: Archive completed session state to `docs/sessions/` for future review
- **Migration**: Moving to a new scratchpad substrate (e.g., SQLite, vector DB)
- **Analysis**: Feed session data to external tools (token counting, phase duration analysis)
- **Backup**: Periodic snapshots before risky operations (compaction, rebase)

**Not needed for**:
- **Cross-session retrieval** (Phase 6 will add BM25/vector search directly on Markdown files)
- **Provenance tracking** (Phase 7 will add direct session-to-commit linkage)

### Exit Codes

- **0**: Success
- **1**: Validation failure (scratchpad does not meet schema)
- **2**: Invalid usage or file not found

### Validation Before Export

The export tool automatically runs `scripts/validate_scratchpad.py` before exporting. If validation fails, export is aborted:

```bash
uv run python scripts/export_scratchpad.py .tmp/invalid/2026-04-13.md --format json
# ERROR: Scratchpad validation failed: .tmp/invalid/2026-04-13.md
# Run: uv run python scripts/validate_scratchpad.py <file>
# Exit code: 1
```

---

## Import

**Status**: Deferred to issue #553 (user decision Q3).

This section will document the import tool (`scripts/import_scratchpad.py`) for restoring session state from exported JSON/YAML files.

---

## Cross-Session Retrieval

**Status**: Implemented (Phase 6) — BM25-based query tool for searching across all scratchpad files.

### Overview

The `scripts/query_sessions.py` tool enables fast keyword-based retrieval across all session files in `.tmp/*/`, allowing agents to discover prior decisions, findings, and context without re-reading every scratchpad manually.

**Technology choice**: BM25 (not vector embeddings) for:
- **Fast execution**: In-process, no model loading
- **Exact keyword matching**: Good for finding specific issue numbers, agent names, phase results
- **Zero dependencies**: Uses existing `rank_bm25` package already in the dependency tree
- **Local-first**: No external API calls or model downloads

### Usage

#### Basic Query

```bash
# Search all branches
uv run python scripts/query_sessions.py "memory governance"

# Output (text format):
# .tmp/main/2026-04-01.md:42-48
# ## Session Start Governing axiom: Endogenous-First — primary endogenous source: MANIFESTO.md...
```

#### Branch-Specific Search

```bash
# Search only one branch
uv run python scripts/query_sessions.py "issue #552" --branch feat-open-harness-sprint
```

#### JSON Output

```bash
# Get structured results
uv run python scripts/query_sessions.py "Research Scout" --output json

# Output:
# [
#   {
#     "text": "## Phase 1 Output\n\n**Agent**: Research Scout\n...",
#     "file": ".tmp/feat-research-550/2026-03-15.md",
#     "branch": "feat-research-550",
#     "start_line": 42,
#     "end_line": 58
#   }
# ]
```

#### Increase Result Count

```bash
# Return top 10 results instead of default 5
uv run python scripts/query_sessions.py "Phase 1 completed" --top-n 10
```

### When to Use

**Use cross-session retrieval when**:
- Starting a sprint and need to check if similar work was done before
- Looking for prior decisions on a specific topic (e.g., "rate limiting", "BM25 vs vector")
- Finding which branches/sessions dealt with a specific issue number
- Recovering context after a compaction event

**Do NOT use for**:
- Querying documentation corpus (use `scripts/query_docs.py` instead)
- Searching committed code (use `grep_search` or `semantic_search` tools)
- Real-time session state (read the active scratchpad directly)

### Indexing Scope

The tool indexes:
- All `.tmp/*/*.md` files (scratchpad session files)
- Excludes: `_index.md` files (summary stubs only)

Each chunk preserves:
- Parent `## Heading` context
- Branch name (derived from directory)
- Line range (1-indexed)
- Full text content

### Performance

Typical query performance on a corpus of ~50 session files (~500KB total):
- **Index build**: <1 second
- **Query execution**: <100ms
- **Memory usage**: <10MB

BM25 is fast enough for interactive use — no pre-indexing or caching required.

**Status**: Phase 6 (issue #552) — not yet implemented.

This section will document the retrieval tool for searching across all scratchpad files in `.tmp/*/` to find relevant prior session context.

**Planned approach** (user decision Q2): Research BOTH BM25 and vector retrieval; implement based on findings.

---

## Provenance

**Status**: Phase 7 (issue #552) — not yet implemented.

This section will document the provenance tracking system linking session scratchpad entries to committed changes (via `.cache/session-events.jsonl`).

**Deferred dependency**: OpenTelemetry integration deferred to issue #554 (user decision Q4). Phase 7 uses `.cache/session-events.jsonl` only.

---

## Standards Compliance

**Status**: Phase 8 (issue #552) — not yet implemented.

This section will consolidate all Phase 5–7 sections into a finalized guide and add compliance gates (CI validation, pre-commit hooks).

---

## References

- [`AGENTS.md § Agent Communication`](../../AGENTS.md#agent-communication)
- [`session-management` SKILL.md](../../.github/skills/session-management/SKILL.md)
- [`data/scratchpad-schema.yml`](../../data/scratchpad-schema.yml)
- [`scripts/validate_scratchpad.py`](../../scripts/validate_scratchpad.py)
- [`scripts/export_scratchpad.py`](../../scripts/export_scratchpad.py)
- Issue #552: Scratchpad Maturity Epic
- Issue #553: Import Tooling (deferred)
- Issue #554: OpenTelemetry Integration (deferred)
