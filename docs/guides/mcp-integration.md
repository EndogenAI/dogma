# MCP Integration Design

**Status**: Active implementation guide (updated after Sprint 17 delivery)
**Related issues**: #134, #123  
**Last updated**: 2026-03-11

---

## Overview

This document specifies the Model Context Protocol (MCP) integration for EndogenAI Workflows. MCP servers extend VS Code's Copilot Chat to access external tools, APIs, and local resources without token-intensive context loading.

The Endogenous-First principle (MANIFESTO.md § 1) prioritizes **local compute and endogenous knowledge** — MCP integration enables Copilot agents to invoke local tools and access repository knowledge through capability-gated interfaces, reducing token burn and increasing determinism.

---

## Enabled MCP Servers

### 1. GitHub MCP Server

**Purpose**: Enable Copilot agents to query and manipulate GitHub issues, PRs, labels, and milestones without breaking the context window.

**Capabilities**:
- Search issues by query
- Read issue/PR bodies and comments
- Create issues and PRs
- Update labels and milestones
- Query GitHub Actions run status

**Configuration** (`.vscode/mcp.json`):
```json
{
  "github": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_TOKEN}"
    }
  }
}
```

**Authentication**: Uses `GITHUB_TOKEN` environment variable (set via `gh auth` or shell exports).

**Usage in agents**:
- Lookup issue blocking status in milestone workflows
- Query PR state before review comments
- Seed new issues from research findings

---

### 2. Endogenic Filesystem Server

**Purpose**: Enable Copilot agents to read/query local repository files, scripts, and docs without embedding entire files in prompts.

**Capabilities**:
- Read file contents (with line-range queries)
- List directory contents with filtering
- Search for patterns within files
- Get file metadata (size, modification time)

**Configuration**: Sprint 17 implemented the governance MCP server at `mcp_server/dogma_server.py` with discovery config in `mcp_server/.well-known/mcp-servers.json` and runtime docs in `mcp_server/README.md`.

**Status**: Implemented in Sprint 17 (`feat(mcp)`) and tested in `tests/test_mcp_server.py`.

**Design notes**:
- Server is a Python subprocess (not Node.js)
- Must respect repository root boundary (no OWASP A01 — path traversal)
- Must support capability gating (e.g., only Research Scout can fetch external URLs via `fetch_source.py`)

---

## Configuration Schema

The `.vscode/mcp.json` file follows the MCP server registry format:

```json
{
  "mcpServers": {
    "<server-key>": {
      "command": "<executable>",
      "args": ["<arg1>", "<arg2>"],
      "env": {
        "<VAR_NAME>": "<value | ${env:SHELL_VAR}>"
      }
    }
  }
}
```

**Fields**:
- `command`: Executable to spawn (npx, node, python3, etc.)
- `args`: Array of command-line arguments; often includes package name
- `env`: Environment variables passed to the subprocess
  - Literal values: `"value"`
  - Shell variable substitution: `"${env:GITHUB_TOKEN}"`

**Location**: `.vscode/mcp.json` is in the repository root. VS Code Copilot reads this file on startup to initialize available servers.

---

## Usage Model

### For Agents

Agents can invoke MCP capabilities through Copilot Chat inline via special syntax:

```
@agent-name Can you check issue #25 status using the GitHub MCP?
```

In agent role files (`.agent.md`), MCP capabilities are referenced in the **Workflow & Intentions** section:

```markdown
## Workflow & Intentions

- Use GitHub MCP to query issue state before delegating phase gates
- Use Filesystem MCP to validate docs before publishing
```

### For Capability Gating

The **Capability Gate** (AGENTS.md § Executive Fleet Privileges) determines which agents can invoke which MCP capabilities. This is enforced by the capability_gate.py script and recorded in a JSONL audit log.

Early implementation focused on GitHub MCP; Sprint 17 now adds the local governance MCP server for validation/scaffolding/query workflows.

---

## Security Considerations

### Threat Model: OWASP A01 (Injection)

- **Risk**: Repository path traversal (e.g., `--file ../../../etc/passwd`)
- **Mitigation**: Filesystem MCP server MUST validate paths against repository root
- **Review**: Security audit of mcp_server.py implementation before merge

### Threat Model: OWASP A03 (Injection)

- **Risk**: GitHub API token leakage in logs or comments
- **Mitigation**:
  - Token sourced via `gh auth token` (secure credential store)
  - Token never echoed to stdout in debug output
  - GitHub MCP server handles credential refresh automatically
- **Review**: CI lint job must flag any line containing `GITHUB_TOKEN` literal string

---

## Follow-Up Work

The following aspects are tracked as follow-up sprint work:

| Item | Issue | Reason |
|------|-------|--------|
| Full generic Filesystem MCP server implementation | #134 | Governance MCP server is shipped; generic file-server hardening remains |
| Capability gating for MCP operations | #155 | Depends on capability_gate.py maturation |
| MCP server discovery and manifest | #158 | Align with fleet-wide agent capability registry continuity |
| Multi-server coordination (e.g., GitHub + Filesystem in same agent) | #297 | Depends on improved context window management |

---

## Next Steps

1. **Immediate**: Integrate `mcp_server/.well-known/mcp-servers.json` into editor-level MCP registry where needed
2. **Short-term**: Add capability gating + audit logging for governance MCP tool invocations
3. **Medium-term**: Publish and version MCP server discovery metadata alongside package docs
4. **Long-term**: Build agent capability registry + dynamic server discovery

---

## Sprint 17 Packaging Cross-Reference

- Standalone governance pre-commit package: `packages/dogma-governance/`
- Package hooks: `packages/dogma-governance/.pre-commit-hooks.yaml`
- Release workflow: `.github/workflows/release-governance-package.yml`
- CLI tools: `dogma-validate-agent`, `dogma-validate-synthesis`, `dogma-check-health`, `dogma-detect-drift`

---

## See Also

- [`AGENTS.md`](../../AGENTS.md) § Executive Fleet Privileges
- [`MANIFESTO.md`](../../MANIFESTO.md) § Endogenous-First principle
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/) (external)
- [GitHub MCP Server](https://github.com/github/github-mcp-server) (external)
