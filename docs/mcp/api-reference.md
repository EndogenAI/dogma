---
title: MCP Server API Reference — Deep Docs
status: Active
---

# MCP Server API Reference

The dogma governance MCP server exposes 8 tools for substrate validation, scaffolding, research, and session management.

**Setup**: See [`mcp_server/README.md`](../../mcp_server/README.md) for installation and configuration.

---

## MCP Tool Inventory

### validate_agent_file

Validate a `.agent.md` or `SKILL.md` file against AGENTS.md encoding constraints.

**Parameters**:
- `file_path` (string, required): Absolute or repo-relative path to the file

**Returns** (JSON):
```json
{
  "ok": true|false,
  "errors": ["error message 1", "error message 2"],
  "file_path": "path/to/file.md"
}
```

**Error codes**:
- Missing required frontmatter field (name, description, tools)
- Invalid tool posture (must match readonly/creator/full)
- Broken internal links or missing headings

**Example**:
```
validate_agent_file(".github/agents/executive-orchestrator.agent.md")
```

---

### validate_synthesis

Validate a D4 research synthesis document before archiving.

**Parameters**:
- `file_path` (string, required): Path to the synthesis Markdown file
- `min_lines` (integer, optional): Minimum non-blank line count (default: 80)

**Returns** (JSON):
```json
{
  "ok": true|false,
  "errors": ["error message 1"],
  "file_path": "docs/research/example.md"
}
```

**Error codes**:
- Missing required headings (`## 1. Executive Summary`, `## 2. Hypothesis Validation`, `## 3. Pattern Catalog`)
- Insufficient H2 heading count (minimum 4 required)
- Insufficient non-blank line count (<min_lines)
- Bare axiom names without `MANIFESTO.md §` reference on the same line

---

### check_substrate

Run a full CRD substrate health check (MANIFESTO.md, AGENTS.md, key scripts).

**Parameters**: None

**Returns** (JSON):
```json
{
  "ok": true|false,
  "errors": ["error message 1"],
  "report": "Full health check report as text"
}
```

**Checks**:
- MANIFESTO.md present and non-empty
- AGENTS.md present and valid YAML
- Key scripts (prune_scratchpad.py, validate_synthesis.py) exist and are executable
- Pre-commit hooks configured

**Example**:
```
check_substrate()
# Returns health status before starting a new phase
```

---

### scaffold_agent

Scaffold a new `.agent.md` stub in `.github/agents/` using the project template.

**Parameters**:
- `name` (string, required): Display name for the agent (e.g. 'Research Scout')
- `description` (string, required): One-line summary ≤ 200 characters
- `area` (string, optional): Area prefix in filename (e.g. 'research'); default: 'scripts'
- `posture` (string, optional): Tool posture — 'readonly', 'creator', or 'full'; default: 'creator'

**Returns** (JSON):
```json
{
  "ok": true|false,
  "output_path": "path/to/generated/file.agent.md",
  "errors": ["error message 1"]
}
```

**Example**:
```
scaffold_agent(
  name="Data Validator",
  description="Validates dataset quality and schema compliance",
  area="data",
  posture="creator"
)
```

---

### scaffold_workplan

Scaffold a new `docs/plans/<date>-<slug>.md` workplan from template.

**Parameters**:
- `slug` (string, required): Dash-separated slug (e.g. 'my-feature-sprint')
- `issues` (string, optional): Comma-separated issue numbers (e.g. '42,43')

**Returns** (JSON):
```json
{
  "ok": true|false,
  "output_path": "docs/plans/2026-03-18-my-feature-sprint.md",
  "errors": ["error message 1"]
}
```

**Example**:
```
scaffold_workplan(slug="sprint-19-docs", issues="340,363,366")
```

---

### run_research_scout

Fetch and cache an external URL via the dogma source cache. SSRF-validated before any network request.

**Parameters**:
- `url` (string, required): The https:// URL to fetch and cache
- `force` (boolean, optional): If true, re-fetch even if cached; default: false

**Returns** (JSON):
```json
{
  "ok": true|false,
  "url": "https://example.com/page",
  "cache_path": ".cache/sources/example-com-page.md",
  "errors": ["error message 1"]
}
```

**Error codes**:
- Invalid URL scheme (must be https://)
- SSRF rejection (internal IP ranges, localhost)
- Network timeout
- HTTP error (404, 503, etc.)

**Example**:
```
run_research_scout("https://example.com/research-paper")
```

---

### query_docs

BM25 query over the dogma documentation corpus.

**Parameters**:
- `query` (string, required): Search query string
- `scope` (string, optional): Corpus scope — 'manifesto', 'agents', 'guides', 'research', 'toolchain', 'skills', or 'all'; default: 'all'
- `top_n` (integer, optional): Number of top results; default: 5

**Returns** (JSON):
```json
{
  "ok": true|false,
  "results": [
    {"document": "docs/guides/session-management.md", "score": 0.95, "excerpt": "..."},
    {"document": "AGENTS.md", "score": 0.88, "excerpt": "..."}
  ],
  "errors": ["error message 1"]
}
```

**Example**:
```
query_docs("phase gating workflow", scope="guides", top_n=3)
```

---

### prune_scratchpad

Initialise or inspect the session scratchpad for the current branch.

**Parameters**:
- `branch` (string, optional): Branch slug (auto-detected from git if empty)
- `dry_run` (boolean, optional): If true, only checks status without writing; default: false

**Returns** (JSON):
```json
{
  "ok": true|false,
  "file_path": ".tmp/main/2026-03-18.md",
  "exists": true|false,
  "lines": 42,
  "errors": ["error message 1"]
}
```

**Example**:
```
# Initialize scratchpad for today
prune_scratchpad(dry_run=false)

# Check status without creating
prune_scratchpad(dry_run=true)
```

---

## Governance Package API

The `packages/dogma-governance/` package exports core validation and scaffolding modules. See the package README for module structure and imports.

**Usage**:
```python
from dogma_governance.validation import validate_agent_file
from dogma_governance.scaffolding import scaffold_agent
```

---

## Common Error Responses

All tools return error messages in an `errors` list. Common patterns:

| Error | Cause | Resolution |
|-------|-------|-----------|
| "File not found: ..." | Path does not exist or is outside repo | Verify path is absolute or repo-relative |
| "Invalid YAML frontmatter" | Malformed YAML in file headers | Check YAML syntax, quote strings if needed |
| "SSRF rejection: ..." | URL is to an internal IP / localhost | Use public https:// URLs only |
| "Missing heading: ..." | Required section not found in doc | Add the missing section |

---

## Usage Examples

### Example 1: Validate a newly scaffolded agent

```
scaffold_agent(name="Tech Lead", description="Architectural decisions", area="ai", posture="full")
# Output: output_path: .github/agents/ai-tech-lead.agent.md

validate_agent_file(".github/agents/ai-tech-lead.agent.md")
# Output: ok: true (file is valid)
```

### Example 2: Prepare a research workplan

```
scaffold_workplan(slug="research-sprint-19", issues="315,317,319")
# Output: output_path: docs/plans/2026-03-18-research-sprint-19.md

query_docs("research methodology", scope="research", top_n=3)
# Find prior research to inform new sprint
```

### Example 3: Run substrate health check before session start

```
check_substrate()
# Returns ok: true + full health report
# If failures: fix & retry before proceeding with new phase
```
