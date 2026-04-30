# Security Policy

## Reporting a Vulnerability

We take the security of the EndogenAI Workflows (dogma) project seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities. Instead:

1. **Preferred**: Use [GitHub's Private Security Advisory feature](https://github.com/EndogenAI/dogma/security/advisories/new) to report the vulnerability privately
2. **Alternative**: Email security reports to **security@endogenai.com**

### What to Include

When reporting a vulnerability, please include:

- **Description** — clear description of the vulnerability and its potential impact
- **Steps to Reproduce** — detailed steps to reproduce the issue
- **Affected Versions** — which versions or branches are affected
- **Suggested Fix** (optional) — if you have a proposed solution

### Response Timeline

- **Acknowledgement**: We will acknowledge receipt within **48 hours** (2 business days)
- **Initial Assessment**: We will provide an initial assessment of severity and scope within **5 business days**
- **Fix Timeline**: Critical vulnerabilities will be addressed as soon as possible; we aim to release patches for high-severity issues within **14 days**
- **Disclosure**: We follow coordinated disclosure — vulnerabilities will be publicly disclosed after a fix is released, with credit to the reporter (unless you prefer to remain anonymous)

### Scope

Security reports are in scope for:

- **Agent tool security** — command injection, path traversal, SSRF in research scout, or privilege escalation in MCP tools
- **Dependency vulnerabilities** — outdated or compromised dependencies with known CVEs
- **Authentication/authorization bypasses** — if/when auth is implemented for MCP HTTP transport
- **Data exposure** — unintended leakage of credentials, API keys, or sensitive session data

Out of scope:
- Social engineering attacks on repository maintainers
- Denial-of-service against the public GitHub repository
- Issues in third-party dependencies that do not affect dogma's security model

### Security Model Overview

The dogma project implements a defense-in-depth security model:

1. **Path Traversal Protection** — All file operations validate paths against the repository root before execution (see `mcp_server/_security.py`)
2. **SSRF Protection** — Research scout validates URLs and blocks private IP ranges, loopback, and non-https schemes
3. **Subprocess Isolation** — All external script invocations use explicit argument lists (no `shell=True`)
4. **Two-Stage Guardrail Pipeline** — Irreversible operations (commits, pushes, issue creation) pass through rule-based gates (pre-commit hooks, MCP validators) and escalation paths for ambiguous cases

For detailed security architecture, see:
- [`docs/guides/security.md`](docs/guides/security.md) — Two-stage guardrail pipeline and agent tool gates
- [`docs/guides/runtime-action-behaviors.md`](docs/guides/runtime-action-behaviors.md) — Comprehensive catalog of irreversible actions
- [`mcp_server/README.md#security-model`](mcp_server/README.md#security-model) — MCP server security controls

### CVE Feed and Dependency Audits

The project maintains automated dependency auditing:

- `scripts/audit_dependencies.py` — audits Python dependencies against OSV database
- GitHub Actions workflow (`.github/workflows/quarterly-dependency-audit.yml`) — runs scheduled dependency audits quarterly

See [`docs/research/owasp-llm-threat-model.md`](docs/research/owasp-llm-threat-model.md) for the threat model and security design decisions.

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.23.x  | ✅ Current stable  |
| 0.22.x  | ✅ Security fixes  |
| < 0.22  | ❌ No longer supported |

We provide security patches for the current stable release and the previous minor version.

---

## Security-Related Configuration

### Environment Variables

- `DOGMA_MCP_AUTH_TOKEN` — Optional bearer token for HTTP transport mode (not enabled by default)
- `WEBMCP_CORS_ORIGINS` — CORS origins for dashboard sidecar (defaults to `http://localhost:5173`)

⚠️ **Never commit** `.env` files containing these variables to the repository.

### Pre-commit Hooks

Security-relevant pre-commit hooks (install with `uv run pre-commit install`):

- `no-heredoc-writes` — blocks heredoc file writes (prevents shell injection via content corruption)
- `no-terminal-file-io-redirect` — blocks terminal I/O redirection in scripts
- `validate-agent-files` — validates agent file schemas before commit
- `ruff` — lints for common security anti-patterns

---

## Public Disclosure Process

After a vulnerability is fixed:

1. A security advisory will be published on GitHub
2. The fix will be documented in `CHANGELOG.md` under the "Security" heading
3. Credit will be given to the reporter (unless anonymity is requested)
4. A CVE will be requested if the vulnerability is high-severity and broadly applicable

---

Thank you for helping keep EndogenAI Workflows secure.
