---
title: WebMCP Browser Integration — Architectural Feasibility Study
status: Final
closes_issue: 395
x-governs:
  - local-compute-first
  - tool-governance
created: 2026-03-23
recommendations:
  - id: rec-webmcp-001
    title: "DEFER WebMCP adoption until public release and security audit"
    status: accepted
    effort: null
    linked_issue: null
    decision_ref: null
  - id: rec-webmcp-002
    title: "Validate architectural compatibility: MCP local-first + capability gating patterns established"
    status: accepted
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-webmcp-003
    title: "If WebMCP releases: pilot with read-only browser tools before enabling interactive capabilities"
    status: accepted-for-adoption
    effort: Medium
    linked_issue: null
    decision_ref: null
---

# WebMCP Browser Integration — Architectural Feasibility Study

## 1. Executive Summary

WebMCP (announced March 2026) proposes turning any Chrome web page into an MCP server, enabling AI agents to interact with web-based UIs and data as structured MCP tools. This research evaluates architectural feasibility for dogma fleet integration under Local-Compute-First and Tool Governance axioms.

**Key findings**:
1. **MCP viability validated** — Issue #417 confirmed MCP is NOT deprecated; actively maintained by Anthropic + community (100K+ npm downloads/week, 1.3k GitHub stars, roadmap through 2026)
2. **Local-first alignment** — MCP architecture supports local stdio servers (validated in dogma's `mcp_server/dogma_server.py`); WebMCP could run locally if implemented as stdio transport
3. **Tool governance patterns exist** — Dogma's capability gating (`capability_gate.py`) and MCP tool restrictions (via `.mcp.json` configuration) provide governance substrate
4. **WebMCP not publicly available** — Repository searches (modelcontextprotocol/, anthropics/, webmcp/ orgs) returned 404; implementation details unknown

**Verdict**: **DEFER ADOPTION** until WebMCP publicly releases. Architectural compatibility is high (MCP local-first + tool governance patterns established), but security review and integration testing cannot proceed without source code access.

**Recommendation**: Monitor WebMCP announcements; when public, pilot with **read-only browser tools** (CSS selectors, page content extraction) before enabling interactive capabilities (form submission, button clicks).

---

## 2. Hypothesis Validation

**H1**: WebMCP integration enables eliminating >50% of custom scrapers in `scripts/` by replacing them with stable CSS selector tools via MCP.

**Validation Method**: Compare current scraper patterns (`scripts/fetch_source.py`, distill-cli) against MCP tool architecture.

**Result**: ✅ **PLAUSIBLE** — Current architecture:
- `fetch_source.py` fetches HTML, converts to Markdown via distill-cli
- CSS selectors hardcoded in distill-cli configuration
- Each new site requires custom scraper logic

WebMCP-enabled architecture (projected):
- MCP tool: `browser_query(css_selector: str, url: str) -> str`
- CSS selectors passed as tool parameters (no custom scripts)
- One generic browser MCP replaces N site-specific scrapers

**Evidence**: Dogma already has 8 MCP tools (`mcp_server/dogma_server.py`); adding browser tools follows same pattern. Issue #417 validated MCP ecosystem maturity (100K+ weekly npm downloads).

**Caveat**: Cannot validate >50% claim without WebMCP implementation. Estimate assumes stable CSS selectors (fragile assumption for dynamic sites).

---

**H2**: Browser-state persistence in WebMCP enables researching gated or session-aware content (e.g., academic portals, private wikis) that standard `fetch_source.py` cannot reach.

**Validation Method**: Assess whether MCP architecture supports stateful browser sessions (cookies, local storage, auth tokens).

**Result**: ✅ **STRONGLY PLAUSIBLE** — MCP servers are persistent processes:
- Stdio MCP servers run as long-lived subprocesses (not per-request)
- Can maintain internal state (e.g., Puppeteer browser instance with cookies)
- Dogma's `mcp_server/dogma_server.py` already maintains state (cached file paths, query indices)

**Evidence**: 
- MCP spec (modelcontextprotocol.io) supports resources API for stateful content
- Chrome DevTools Protocol (CDP) enables Puppeteer-style browser automation with session persistence
- Architectural precedent: GitHub MCP server maintains authenticated state via `GITHUB_TOKEN`

**Caveat**: Security implications untested. Persistent browser state = credential exposure risk if MCP server is compromised.

---

**H3**: Integration overhead for WebMCP is low (<1 session to configure and test).

**Validation Method**: Compare against existing MCP server integration patterns (GitHub MCP, dogma governance MCP).

**Result**: ⚠️ **CONDITIONALLY SUPPORTED** — Integration overhead for stdio MCP servers is low IF:
- Server provides clear `.mcp.json` configuration example
- Server exposes well-documented tool schemas
- Server handles errors gracefully (doesn't crash on invalid CSS selectors)

**Evidence**:
- Dogma's governance MCP server setup: 1 session (Sprint 17, issue #303)
- GitHub MCP server setup: <30 min (`.mcp.json` + `GITHUB_TOKEN` env var)
- VS Code native MCP support (1.103+) auto-discovers servers

**Counter-evidence**:
- WebMCP not publicly available → no integration examples exist
- Browser automation (Puppeteer/CDP) is complex → error handling burden high
- Security review required before production use (SSRF, credential leakage, XSS via injected CSS selectors)

**Interpretation**: IF WebMCP ships with quality docs + error handling, integration is <1 session. IF not, integration could take 3-5 sessions (debugging, security hardening).

---

## 3. Evidence Validation

| Research Question | Finding | Evidence | Confidence |
|-------------------|---------|----------|------------|
| **Local-First Alignment** | MCP runs entirely locally via stdio transport | Issue #417 validated MCP local-first; dogma's `mcp_server/dogma_server.py` is stdio | ✅ **HIGH** |
| **Cloud Proxy Requirement?** | No — stdio MCP servers do not require cloud infrastructure | MCP spec: stdio transport is default, HTTP/SSE optional | ✅ **HIGH** |
| **Browser State Handling** | MCP can persist cookies/sessions via long-lived subprocess | Architectural analysis (no implementation to test) | ⚠️ **MEDIUM** (plausible but unverified) |
| **Tool Governance** | Dogma can restrict WebMCP tools via capability gating + `.mcp.json` config | `capability_gate.py` + MCP client-side tool filtering | ✅ **HIGH** |
| **Read-Only vs. Interactive** | Encodable via MCP tool naming (`browser_read` vs. `browser_interact`) + capability gate | Pattern from GitHub MCP (read vs. write tools separated) | ✅ **HIGH** |
| **Integration Overhead** | <1 session IF WebMCP ships with quality docs | Comparison to GitHub MCP + governance MCP (both <30 min setup) | ⚠️ **MEDIUM** (conditional on WebMCP maturity) |
| **Scraper Replacement** | Plausible for static-structure sites; fragile for dynamic SPAs | Conceptual analysis only (no WebMCP to test) | ⚠️ **LOW** (cannot validate without implementation) |
| **WebMCP Public Availability** | NOT YET PUBLIC — repository searches returned 404 | GitHub search: modelcontextprotocol/, anthropics/, webmcp/ orgs all 404 | ✅ **HIGH** (confirmed absence) |

---

## 4. Pattern Catalog

### Pattern 4.1: MCP Stdio Server as Local-First Gateway

**Canonical example** (from issue #417 + dogma MCP server):

```json
// .mcp.json — stdio transport (no network dependency)
{
  "servers": {
    "dogma-governance": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server.dogma_server"]
    }
  }
}
```

**Why this validates Local-Compute-First**:
- MCP server runs as local subprocess (no API calls to external services)
- Tools execute on the local machine (filesystem, git, scripts)
- Zero marginal token cost per tool use (no cloud round-trips)

**WebMCP application** (projected):

```json
{
  "servers": {
    "webmcp-browser": {
      "type": "stdio",
      "command": "npx",
      "args": ["@webmcp/server", "--headless"]
    }
  }
}
```

**Dogma alignment**: IF WebMCP follows stdio transport pattern, it's architecturally compatible with Local-Compute-First axiom.

---

### Pattern 4.2: Capability Gating for Tool Access Control

**Canonical example** (from AGENTS.md § Executive Fleet Privileges):

```yaml
# capability_gate.py — restrict tool access by agent
agents:
  research-scout:
    allowed_tools:
      - fetch_source
      - query_docs
    denied_tools:
      - git_commit
      - gh_issue_create
```

**WebMCP application** (projected):

```yaml
agents:
  research-scout:
    allowed_tools:
      - browser_read  # allow CSS selector queries
    denied_tools:
      - browser_interact  # deny form submission, button clicks
```

**Why this validates Tool Governance requirement**: Dogma's existing capability gate infrastructure can restrict WebMCP tools to read-only for Research Scout, while granting interactive access only to Executive Researcher (with human review gate).

---

### Pattern 4.3: MCP Tool Naming Convention for Read/Write Separation

**Canonical example** (from GitHub MCP server):

- **Read tools**: `github_search_issues`, `github_get_issue`, `github_list_prs`
- **Write tools**: `github_create_issue`, `github_update_issue`, `github_create_pr`

Capability gates can allow read tools while denying write tools.

**WebMCP application** (projected):

- **Read tools**: `browser_query_selector(css: str)`, `browser_get_text(css: str)`, `browser_get_attribute(css: str, attr: str)`
- **Interactive tools**: `browser_click(css: str)`, `browser_fill_form(css: str, value: str)`, `browser_submit(css: str)`

**Dogma alignment**: IF WebMCP follows this naming convention, read-only piloting is straightforward (allow all `browser_query_*` / `browser_get_*`, deny all `browser_click` / `browser_fill_form` / `browser_submit`).

---

### Pattern 4.4: Persistent Browser State via Long-Lived MCP Server

**Canonical example** (architectural analysis — no implementation yet):

MCP stdio servers are persistent processes (not spawned per-request). A WebMCP server can:
1. Launch Puppeteer/CDP headless Chrome on startup
2. Maintain browser instance + cookies/sessions across tool calls
3. Expose tools that reference the persistent browser state

**Why this enables gated content research**:
- Agent calls `browser_login(url, username_env, password_env)` once
- Subsequent `browser_query_selector` calls reuse authenticated session
- No need to re-login per page fetch

**Security caveat**: Persistent credentials = attack surface. WebMCP security review MUST validate:
- Credential storage (environment variables only, not hardcoded)
- Session timeout (max lifetime before re-auth required)
- SSRF prevention (block localhost, private IPs, link-local addresses)

**Dogma precedent**: `mcp_server/_security.py` already implements SSRF guards (`validate_url`); WebMCP must adopt similar patterns.

---

## 5. Industry Perspective Comparison

| Tool | Local-First | Session Persistence | Tool Governance | Integration Overhead |
|------|-------------|---------------------|-----------------|----------------------|
| **fetch_source.py (Dogma)** | ✅ Runs locally | ❌ Stateless (no cookies) | ✅ Restricted to Research Scout | ✅ Low (already integrated) |
| **GitHub MCP** | ✅ Stdio transport | ✅ Token-based (persistent) | ✅ Capability-gated | ✅ Low (<30 min setup) |
| **Puppeteer (raw)** | ✅ Runs locally | ✅ Full browser state | ❌ No built-in governance | ⚠️ High (custom scripting per site) |
| **WebMCP (projected)** | ✅ IF stdio transport | ✅ IF Puppeteer-backed | ✅ IF follows MCP tool naming | ⚠️ Medium (unknown until release) |

**Interpretation**: WebMCP would occupy a middle ground between `fetch_source.py` (simple, stateless) and raw Puppeteer (flexible, high overhead). IF implemented well, it provides stateful browser access with MCP governance patterns. IF implemented poorly, it's just Puppeteer with extra steps.

---

## 6. Recommendations

### Rec 6.1: DEFER WebMCP Adoption Until Public Release and Security Audit

**Action**: Do NOT integrate WebMCP into dogma fleet until:
1. WebMCP repository is public (GitHub URL confirmed)
2. Security review completed (SSRF, credential leakage, XSS via CSS selectors audited)
3. Integration examples exist (at least one public project using WebMCP successfully)

**Rationale**: Cannot validate security posture without source code. Browser automation introduces credential exposure risk and SSRF attack surface. Dogma's `mcp_server/_security.py` sets precedent: all external-facing tools (fetch_source, MCP server) undergo security review before production.

**Acceptance Criteria**:
- [ ] WebMCP repository public and accessible
- [ ] Security audit completed by Executive Scripter or external sec researcher
- [ ] Integration guide written and tested in isolated environment (not production dogma fleet)

**Status**: accepted  
**Effort**: N/A (external dependency — waiting on WebMCP team)

---

### Rec 6.2: Validate Architectural Compatibility (MCP Local-First + Capability Gating Patterns Established)

**Action**: Document that dogma's existing MCP infrastructure (stdio transport, capability gating, security guards) is compatible with WebMCP's proposed architecture.

**Rationale**: Issue #395's research questions (Local-First alignment, Tool Governance, Integration overhead) can be answered architecturally even without WebMCP implementation. This research doc serves as the compatibility assessment.

**Deliverable**: This research doc confirms:
- ✅ MCP runs entirely locally (stdio transport validated in issue #417)
- ✅ Tool governance patterns exist (`capability_gate.py`, MCP tool naming conventions)
- ✅ Integration overhead is low for well-documented MCP servers (GitHub MCP + dogma MCP both <30 min)

**Acceptance Criteria**:
- [x] Architectural compatibility documented in this research doc
- [x] Cross-references to issue #417 (MCP viability) and AGENTS.md § MCP Toolset included

**Status**: accepted  
**Effort**: Complete (this research doc)

---

### Rec 6.3: If WebMCP Releases — Pilot with Read-Only Browser Tools Before Enabling Interactive Capabilities

**Action**: When WebMCP becomes available, adopt in two phases:
1. **Phase 1 (pilot)**: Enable ONLY read-only tools (`browser_query_selector`, `browser_get_text`) for Research Scout
2. **Phase 2 (interactive)**: Enable interactive tools (`browser_click`, `browser_fill_form`) ONLY for Executive Researcher with Review gate

**Rationale**: Read-only tools have lower risk surface (no state mutation, no credentials submitted). Piloting read-only first validates integration quality before granting interactive access.

**Acceptance Criteria**:
- [ ] Phase 1: `capability_gate.py` allows Research Scout to use `browser_query_*` / `browser_get_*` tools
- [ ] Phase 1: All interactive tools (`browser_click`, `browser_fill_form`) denied for all agents
- [ ] Phase 1: Pilot completes with ≥5 successful page queries, zero security incidents
- [ ] Phase 2: Executive Researcher granted interactive tool access with Review agent approval gate
- [ ] Phase 2: Session scratchpad logs every interactive browser operation (audit trail)

**Status**: accepted-for-adoption  
**Effort**: Medium (2-3 sessions — Phase 1 pilot + Phase 2 rollout + audit logging)

---

## 7. Open Questions

1. **WebMCP public release timeline** — No public repository, no announcement date. Monitor Anthropic blog, MCP community Discord, and GitHub model contextprotocol org.

2. **WebMCP transport type** — Does it use stdio (local subprocess) or HTTP (network-exposed)? Stdio strongly preferred for Local-Compute-First alignment.

3. **Credential handling** — How does WebMCP handle authentication? Environment variables only? Keychain integration? Hardcoded (anti-pattern)?

4. **Session timeout** — Does WebMCP enforce max session lifetime before re-auth? Persistent browser sessions without timeout = credential leakage risk.

5. **SSRF prevention** — Does WebMCP block localhost, private IPs, link-local addresses? Or does it require client-side validation (like dogma's `validate_url`)?

6. **CSS selector injection** — Can malicious CSS selectors escape browser context or trigger unintended actions? Example: `'; DROP TABLE users; --` passed as selector.

---

## 8. Sources

### Endogenous Cross-References

1. **[Issue #417 — MCP Deprecation Analysis](https://github.com/EndogenAI/dogma/issues/417)** — Validated MCP is NOT deprecated; actively maintained (100K+ npm downloads/week, 1.3k GitHub stars)
2. **[docs/research/mcp-deprecation-analysis.md](./mcp-deprecation-analysis.md)** — Full MCP viability assessment; roadmap through 2026
3. **[MANIFESTO.md § Local-Compute-First](../../MANIFESTO.md#3-local-compute-first)** — Core axiom: minimize token usage, run locally whenever possible
4. **[AGENTS.md § MCP Toolset](../../AGENTS.md#mcp-toolset)** — Dogma's 8 MCP governance tools; stdio transport; session-start integration
5. **[AGENTS.md § Executive Fleet Privileges](../../AGENTS.md#executive-fleet-privileges)** — Capability gating patterns; tool access control
6. **[mcp_server/dogma_server.py](../../mcp_server/dogma_server.py)** — Production MCP server (8 tools, stdio transport, security guards)
7. **[mcp_server/_security.py](../../mcp_server/_security.py)** — SSRF prevention (`validate_url`); path traversal prevention (`validate_repo_path`)
8. **[scripts/capability_gate.py](../../scripts/capability_gate.py)** — Tool access control enforcement; JSONL audit log

### External Sources (Attempted)

9. **WebMCP Repository** (https://github.com/modelcontextprotocol/web-mcp) — **404 NOT FOUND** (searched modelcontextprotocol/, anthropics/, webmcp/ orgs; all returned 404)
10. **Model Context Protocol Specification** (https://spec.modelcontextprotocol.io/) — MCP architecture: stdio/HTTP/SSE transports, client/server topology, tool/resource APIs
