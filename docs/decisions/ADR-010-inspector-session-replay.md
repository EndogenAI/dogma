---
title: "MCP Inspector Session Replay Integration Contract"
status: Proposed
date: 2026-03-30
deciders: EndogenAI core team
closes_issue: 505
---

# ADR-010: MCP Inspector Session Replay Integration

## Title
MCP Inspector Session Replay Integration Contract

## Status
Proposed

## Context
Issue #505 requires a design contract for integrating MCP Inspector session replay capabilities into the dogma MCP server. During development and debugging, developers need the ability to capture, inspect, and replay MCP tool calls to reproduce failures, validate fixes, and build audit trails. The MCP Inspector provides a browser-based debugging interface using an HTTP proxy bridge with long-polling architecture. Session replay integration must preserve request/response fidelity while respecting privacy and security boundaries.

## Decision Drivers

- **Inspector protocol compatibility**: Must integrate with the MCP Inspector's HTTP bridge protocol (`/mcp/handshake`, `/mcp/browser/poll`, `/mcp/browser/respond`) using MCP JSON-RPC 2.0 format.
- **Privacy and security boundaries**: Replay data must redact credentials (`GITHUB_TOKEN`, API keys) and PII before persistence to prevent leakage in logs or cache files.
- **Storage efficiency**: Replay sessions must have bounded storage (time-based TTL) and compressed format to avoid unbounded disk growth.
- **Local-Compute-First**: Replay and inspection must run locally without external service dependencies.
- **Debugging reproducibility**: Captured sessions must be replayable deterministically to reproduce tool call behavior.

## Decision

### Adapter Layer Design
Reuse the existing `BrowserInspectorBridge` from MCP Inspector architecture as the proxy layer. Extend `mcp_server/dogma_server.py` to:
1. Register session start/end hooks via `_run_with_mcp_telemetry` wrapper.
2. Add `replay_mcp_call` tool to the canonical tool set for replaying captured sessions.
3. Implement session registration, request queue management, and Future-based async coordination using the Inspector's 30-second long-polling pattern.

### Replay Data Format
Use MCP JSON-RPC 2.0 format with the following fields per captured call:
- `method`: tool name (e.g., `tools/call`)
- `params`: tool arguments dict
- `result` or `error`: tool response
- `timestamp_utc`: ISO 8601 timestamp
- `session_id`: UUID for grouping related calls
- `request_id`: per-call unique identifier

### Storage Location and TTL
- **Location**: `.cache/mcp-session-replay/<date>/` (e.g., `.cache/mcp-session-replay/2026-03-30/session-<uuid>.jsonl`)
- **Format**: JSONL (one JSON object per line) for append-only efficiency and streaming replay
- **TTL**: 7-day rotation — delete sessions older than 7 days on startup
- **Gitignore**: Add `.cache/mcp-session-replay/` to `.gitignore`

### Security Redaction Rules
Before persisting any session data:
1. Redact all environment variables matching `*TOKEN*`, `*KEY*`, `*SECRET*`, `*PASSWORD*`
2. Redact `Authorization` headers and `gh auth token` output
3. Replace redacted values with placeholder `<REDACTED>`
4. Document redaction policy in `mcp_server/README.md`

### UI Prototype Deferral
The "Debug This Call" browser button and visual replay timeline are deferred to V2 implementation (follow-up issue). Phase 1 delivers only the data capture layer and `replay_mcp_call` CLI tool interface.

### Session Timeout
- **Session TTL**: 60 seconds (inherited from Inspector proxy session registration)
- **Request timeout**: 10 seconds per tool call
- **Error handling**: Graceful degradation if Inspector bridge is unreachable — log warning and continue

## Consequences

### Positive
- **Better debugging**: Developers can capture and replay failing MCP calls without manual reconstruction.
- **Audit trail**: Session logs provide verifiable record of tool invocations for compliance and governance review.
- **Reproducibility**: Deterministic replay enables regression testing and failure analysis.

### Negative
- **Storage overhead**: Replay sessions consume disk space (mitigated by 7-day TTL and JSONL compression).
- **PII risk**: Captured data may contain sensitive information if redaction rules are incomplete (requires security audit before production use).
- **Maintenance burden**: Session replay infrastructure requires monitoring for storage limits and redaction policy updates.

### Neutral
- **Requires implementation**: The design contract requires implementing session capture hooks in `_run_with_mcp_telemetry`, storage rotation script, and `replay_mcp_call` tool.
- **Inspector dependency**: Requires MCP Inspector HTTP bridge library (already adopted in issue #504).

## Alternatives Considered

### 1. Client-side replay only (no server persistence)
Keep replay sessions in browser memory only; discard on tab close.

**Rejected**: Loses audit trail and makes cross-session debugging impossible. Server-side persistence enables reproducibility across development environments.

### 2. No persistence (ephemeral debugging only)
Provide Inspector bridge integration without session capture.

**Rejected**: Loses the primary value of session replay — reproducibility and audit trail. Ephemeral debugging is insufficient for governance and compliance use cases.

### 3. Full request logging (no redaction)
Persist all request/response data verbatim for maximum fidelity.

**Rejected**: Creates unacceptable PII and credential leakage risk. Redaction is mandatory for any persistence layer.
