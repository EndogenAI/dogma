---
title: "Locally Distributed MCP Frameworks"
status: "Draft"
---

# Locally Distributed MCP Frameworks

> **Status**: Draft
> **Research Question**: How do we distribute MCP (Model Context Protocol) server infrastructure across a local network? What are best practices for multi-machine agent coordination without cloud dependency?
> **Date**: 2026-03-07
> **Related**: [`docs/guides/local-compute.md`](../guides/local-compute.md) · [`docs/research/local-copilot-models.md`](local-copilot-models.md)

---

## 1. Executive Summary

Model Context Protocol (MCP) is an open standard (Anthropic, 2024) for connecting AI models to external tools and services. It defines a client/server architecture where **MCP clients** (e.g., VS Code Copilot, Claude Desktop) communicate with **MCP servers** that expose tools, resources, and prompts. MCP servers can run locally (stdio), over local HTTP/SSE, or at remote HTTPS endpoints.

For the endogenic fleet, MCP servers are the primary mechanism for giving agents deterministic, composable access to local filesystem operations, databases, shell commands, and internal APIs — without requiring cloud round-trips. The key architectural insight: **tools run where servers are configured**, not necessarily where the agent is running.

VS Code has native MCP support (as of VS Code 1.103+): install from the extension gallery, configure via `mcp.json`, and servers auto-discovered by chat. Sandbox mode (macOS/Linux) restricts server filesystem and network access. Multi-machine distribution is achievable via HTTP MCP servers exposed on the local network.

**Endogenic relevance**: This directly enables the Local Compute-First axiom — agent tools (file I/O, git, testing, script execution) can run on a local machine without any cloud dependency, at zero marginal token cost per tool use.

---

## 2. Hypothesis Validation

### H1 — MCP servers can provide all agent tools locally

**Confirmed**. stdio MCP servers run as local processes launched by VS Code. The server communicates over stdin/stdout — no network required. Local MCP servers can expose:
- File system tools (read, write, search)
- Shell command execution
- Git operations
- Database queries (via SQLite MCP servers)
- Custom Python/Node scripts surfaced as tools

Tool invocations are zero-marginal-cost (no LLM tokens consumed) — only the model deciding which tool to call consumes tokens.

### H2 — Multi-machine MCP distribution is feasible without a cloud intermediary

**Confirmed** via HTTP MCP servers. An MCP server running as an HTTP/SSE service on a local network machine is accessible from any VS Code instance on the same network. Configuration:

```json
// .vscode/mcp.json — point to a remote machine on the LAN
{
  "servers": {
    "gpu-machine-tools": {
      "type": "http",
      "url": "http://192.168.1.100:3000/mcp"
    }
  }
}
```

The receiving machine runs an MCP HTTP server (e.g., `@modelcontextprotocol/server-*` packages or custom implementation). No internet required.

### H3 — Docker Compose is the appropriate distribution mechanism for local MCP clusters

**Supported** as a pattern. Docker Compose allows declarative multi-service MCP topologies:
- Each MCP server as a service in `docker-compose.yml`
- Services communicate via Docker internal network
- The VS Code machine mounts the Compose stack's HTTP endpoints
- Health checks via `docker inspect` ensure services are ready

Key advantage: reproducible setup, easy to commit, works across team machines.

**Caveat**: Docker adds operational overhead. For single-machine setups, stdio MCP servers are simpler and should be preferred.

### H4 — VS Code sandboxing sufficiently mitigates local MCP security risks

**Partially confirmed** (macOS/Linux only). VS Code's sandbox mode for stdio servers restricts:
- Filesystem writes to configured `allowWrite` paths
- Network access to configured `allowedDomains`

When sandboxing is enabled, tool calls are auto-approved (reducing prompt fatigue). When sandboxing is not available (Windows) or not enabled, each tool call requires explicit user confirmation. The trust workflow (required on first server start) provides a baseline gate.

**Security gap**: HTTP MCP servers on the local network have no authentication by default. Access control must be implemented at the network layer (firewall, VPN) or via application-level auth headers.

---

## 3. Pattern Catalog

### Pattern 1 — Single-Machine stdio MCP Stack (simplest)

All MCP servers run as local stdio processes. No networking required.

```json
// .vscode/mcp.json
{
  "servers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/workspace"],
      "sandboxEnabled": true,
      "sandbox": {
        "filesystem": {
          "allowWrite": ["${workspaceFolder}"]
        }
      }
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp"
    }
  }
}
```

Commit this to `.vscode/mcp.json` to share the server configuration with the team. Each team member runs the stdio servers locally; the GitHub MCP server runs at the cloud endpoint.

### Pattern 2 — Local Network HTTP MCP Server (multi-machine)

**Use case**: GPU machine runs a compute-intensive MCP server (e.g., embedding generation, local model inference wrapper); dev workstation connects to it.

```bash
# On the GPU machine (192.168.1.100) — run an HTTP MCP server
# Example: custom Python MCP server exposing local Ollama
uvx mcp run server.py --port 3000
# Or: node-based MCP server
npx -y @modelcontextprotocol/server-memory --port 3000
```

```json
// .vscode/mcp.json on dev workstation
{
  "servers": {
    "local-inference": {
      "type": "http",
      "url": "http://192.168.1.100:3000/mcp"
    }
  }
}
```

**Security**: Lock to LAN only via OS firewall. Do not expose to internet.

### Pattern 3 — Docker Compose MCP Cluster

For reproducible multi-server setups. Useful when multiple services need to collaborate (e.g., a database server, a search server, a code execution server).

```yaml
# docker-compose.yml
services:
  mcp-filesystem:
    image: node:20
    command: npx -y @modelcontextprotocol/server-filesystem /workspace
    volumes:
      - ./:/workspace
    ports:
      - "3001:3001"

  mcp-memory:
    image: node:20
    command: npx -y @modelcontextprotocol/server-memory --port 3002
    ports:
      - "3002:3002"
```

```json
// .vscode/mcp.json — point to Docker services
{
  "servers": {
    "filesystem": { "type": "http", "url": "http://localhost:3001/mcp" },
    "memory": { "type": "http", "url": "http://localhost:3002/mcp" }
  }
}
```

### Pattern 4 — Endogenic MCP Server for This Project

The endogenic project itself is a candidate MCP server provider. Key tools to expose:
- `scripts/fetch_source.py` — fetch and cache a URL
- `scripts/prune_scratchpad.py` — manage session scratchpad
- `scripts/validate_synthesis.py` — validate a research doc
- `scripts/generate_agent_manifest.py` — list available agents

A lightweight Python MCP server wrapping these scripts would allow any MCP-capable client to invoke project tooling without understanding the CLI interface. This is the **Algorithms Before Tokens** principle applied to MCP: encode the CLI as tools once; agents call them without re-deriving the syntax.

---

## 4. VS Code MCP Configuration Reference

### Key settings

| Setting | Description |
|---------|-------------|
| `.vscode/mcp.json` | Workspace-scoped server config; commit to share with team |
| User profile `mcp.json` | User-scoped; shared across all workspaces |
| `chat.mcp.autoStart` | Experimental — auto-restart on config change |

### Server types

| Type | Transport | Use case |
|------|-----------|---------|
| `stdio` | stdin/stdout | Local process; simplest; sandboxable |
| `http` | HTTP/SSE | Network server; local LAN or cloud |

### Trust workflow

Every server requires explicit trust on first start. Use `MCP: Reset Trust` (Command Palette) to revoke. When sandboxing is enabled, tool calls are auto-approved within the sandbox constraints.

---

## 5. Open Questions

- **Authentication for local HTTP MCP servers**: What is the recommended pattern for API key or token-based auth on LAN MCP servers? (No standard exists yet.)
- **MCP server for endogenic scripts**: Should `scripts/` be exposed as MCP tools? What are the security implications? (Candidate for Executive Scripter or MCP Architect agent.)
- **Agent fleet + MCP**: Which existing `.agent.md` files should explicitly list their MCP tool dependencies? Should MCP tool names be encoded in agent frontmatter?
- **Production stability of Docker MCP**: Are `@modelcontextprotocol/server-*` packages production-stable, or are they reference implementations only?

---

## 6. Recommendations

1. **Commit `.vscode/mcp.json` to this repo** with the GitHub MCP server and the endogenic filesystem server as the default configuration
2. **Design an endogenic MCP server** (`scripts/mcp_server.py`) that wraps key project scripts as tools — delegate to Executive Scripter to spec
3. **Use stdio servers by default**; upgrade to HTTP only when multi-machine distribution is required
4. **Enable sandboxing** on all stdio servers (macOS/Linux) with `allowWrite` restricted to `workspaceFolder`
5. **Defer Docker Compose MCP** until there is a specific use case requiring multi-machine compute distribution

---

## References

- [VS Code MCP Server documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) — primary source for VS Code integration
- [Model Context Protocol specification](https://modelcontextprotocol.io/) — protocol standard
- [GitHub MCP server registry](https://github.com/mcp) — curated server gallery
- [`docs/guides/local-compute.md`](../guides/local-compute.md) Strategy C — endogenic local network compute guide
- [GitHub Issue #6](https://github.com/EndogenAI/Workflows/issues/6) — tracking issue for this research arc
