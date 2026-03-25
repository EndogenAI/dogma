---
title: "AI Provider Dependency Audit 2026 — NIST AI RMF GOVERN 6.1"
status: "Final"
date: "2026-03-25"
auditor: "Executive Orchestrator"
x-governs: [ai-dependency-tracking, nist-govern-6-1, enisa-lock-in, third-party-ai-risk]
closes_issue: 381
source: "docs/research/ai-platform-lock-in-risks.md (Recommendation 7)"
next_review_due: "2027-01-01"
recommendations:
  - id: rec-ai-dep-audit-2026-001
    title: "Add LiteLLM adaptor layer to rate_limit_gate.py for provider switching"
    status: accepted
    linked_issue: 381
  - id: rec-ai-dep-audit-2026-002
    title: "Agent-format-portability spike — assess exporting .agent.md to Cursor/Continue.dev"
    status: accepted
    linked_issue: 381
  - id: rec-ai-dep-audit-2026-003
    title: "Document MCP server as provider-agnostic governance layer in mcp_server/README.md"
    status: accepted
    linked_issue: 381
  - id: rec-ai-dep-audit-2026-004
    title: "Track GitHub Copilot as single-point-of-failure in governance-metrics.md"
    status: accepted
    linked_issue: 381
  - id: rec-ai-dep-audit-2026-005
    title: "Monitor OpenAI GPT-3.5/4 references as a potential migration target"
    status: deferred
---

# AI Provider Dependency Audit 2026 — NIST AI RMF GOVERN 6.1

**Status**: Final  
**Date**: 2026-03-25  
**Auditor**: Executive Orchestrator (Phase 0 Session)  
**Next review due**: 2027-01-01

---

## 1. Executive Summary

This document records the annual AI provider dependency audit for the dogma
repository, implementing NIST AI RMF GOVERN 6.1 ("Policies, processes, procedures,
and practices are in place for mapping risks or impacts associated with AI-enabled
systems and models to third-party entities").

**Research basis**: `docs/research/ai-platform-lock-in-risks.md` Recommendation 7 (Sprint 18, issue #381).

**Governing axioms**: [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) (audit from internal codebase knowledge first), [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) (Ollama path as lock-in mitigation).

**Scan summary** (performed by `scripts/audit_ai_dependencies.py` on 2026-03-25):

| Stat | Value |
|------|-------|
| Directories scanned | `.github/agents/` + `scripts/` |
| Files scanned | 114 |
| Providers detected | 4 (Claude, Ollama, OpenAI, GitHub Copilot) |
| Claude references | 38 across 13 files |
| Ollama references | 19 across 7 files |
| OpenAI references | 17 across 7 files |
| GitHub Copilot | Implicit runtime dependency (not in scripts) |

**Key finding**: GitHub Copilot scores 4/5 on composite lock-in risk (high-priority-action)
due to maximum ecosystem dependency depth (5/5) and high exit costs (4/5). The MCP server
is the primary mitigation lever — it exposes governance tools via an open protocol
callable from any compliant client. Anthropic/Claude scores 3/5 (accepted-with-mitigation);
local Ollama scores 1/5 (accepted) and directly validates the Local-Compute-First axis.

---

## 2. Hypothesis Validation

**Hypothesis**: dogma's primary AI provider dependency (Claude via VS Code Copilot Chat)
represents a moderate-to-high lock-in risk that can be partially mitigated through the
open MCP protocol layer and the existing Ollama local-compute path.

| Dimension | Predicted | Observed | Validated? |
|-----------|-----------|----------|-----------|
| Claude is the primary inference dependency | Yes | 38 code references across 13 files | ✅ |
| GitHub Copilot creates higher lock-in than Claude | Yes | Copilot 4/5 vs Claude 3/5 | ✅ |
| Ollama provides meaningful lock-in mitigation | Yes | Ollama 1/5; explicit fallback path in rate_limit_config.py | ✅ |
| MCP protocol is the most portable layer | Yes | MCP spec is open; `.vscode/mcp.json` tools callable from any MCP client | ✅ |
| OpenAI is not an active runtime dependency | Yes | 17 references are rate-limit profiles and comparison docs, not calls | ✅ |

**Conclusion**: Hypothesis validated. The NIST GOVERN 6.1 control surfaced one
high-priority dependency (GitHub Copilot ecosystem depth = 5/5) and confirmed the
Local-Compute-First mitigation path is structurally sound. Remaining risk is
concentrated in the model portability dimension for both hosted providers (both score 5/5 —
neither publishes downloadable weights).

---

## 3. Pattern Catalog

**Canonical example — Low lock-in via open protocol (MCP server)**:
The `.vscode/mcp.json` + `mcp_server/dogma_server.py` stack exposes 8 governance tools
via the open Model Context Protocol. Any MCP-compliant client (Claude Desktop, Cursor,
Windsurf, or a custom CLI) can invoke the same tools without modification. This instantiates
[MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first): governance
tooling encoded as durable infrastructure, not tied to a specific IDE or API.

**Anti-pattern — Hardcoded provider defaults**:
`scripts/rate_limit_gate.py --provider claude` and `scripts/rate_limit_config.py`
hard-code `claude` as the default provider. If Anthropic's API becomes unavailable,
all scripts that call `rate_limit_gate.py` without an explicit `--provider` flag will
fail or produce incorrect budget estimates. The mitigation is a LiteLLM adaptor layer
so provider selection is config-driven, not source-code-driven.

**Canonical example — Local-Compute-First as structural lock-in mitigation**:
`scripts/detect_rate_limit.py` profiles the `local-localhost` provider with a threshold
of 999 (effectively unlimited) and 0s sleep delay. This programmatically encodes the
[MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) axiom:
the codebase already knows how to fail over to a local runtime, which directly reduces
the composite risk score of both hosted providers.

**Anti-pattern — Implicit IDE-layer coupling**:
All dogma agents are defined as VS Code Custom Agents (`.agent.md` files targeting the
VS Code Copilot Chat extension). The agent invocation model is not documented in a
provider-agnostic format. If the VS Code extension changes its schema or the organization
switches IDE, all agent definitions require reformatting. The mitigation is a portability
spike that maps `.agent.md` fields to at least one alternative format (e.g., Cursor
`.cursorrules` or a system-prompt YAML).

---

## Provider Inventory

### Dependency 1 — Anthropic / Claude

| Field | Value |
|-------|-------|
| **Role** | Primary inference provider |
| **Integration type** | Cloud REST API |
| **Primary integration points** | `scripts/rate_limit_gate.py`, `scripts/detect_rate_limit.py`, `scripts/rate_limit_config.py`, `AGENTS.md § claude -p policy`, `.github/agents/executive-orchestrator.agent.md` |
| **Composite risk score** | **3 / 5** (accepted-with-mitigation) |

ENISA dimension scores:

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Data portability | 2 | Prompts are source-controlled; no per-conversation retention |
| API portability | 3 | Messages API similar to OpenAI but adaptor work required |
| Trained-model portability | **5** | Cloud-only; no local deployment option |
| Service continuity | 2 | Commercial SLAs; historically stable; no contractual guarantee at API tier |
| Pricing transparency | 1 | Public per-token pricing; integrated into rate\_limit\_gate.py tracking |
| Compliance auditability | 2 | API logs available; zero-retention option documented |
| Exit costs | 3 | ~3 scripts + AGENTS.md sections; estimated 2–3 sprints |
| Ecosystem dependency depth | 3 | Multiple scripts default to Claude; Ollama fallback path exists |

**Verdict**: Accepted-with-mitigation. The only truly high dimension is trained-model
portability (no local option). All other scores are low-to-moderate.

**Mitigations**:
- Add a LiteLLM adaptor layer to `rate_limit_gate.py` to enable provider switching via config (create follow-up issue)
- Document Ollama fallback as explicit contingency in `docs/guides/claude-code-integration.md`
- Track Claude-specific AGENTS.md sections as abstraction candidates

---

### Dependency 2 — GitHub Copilot

| Field | Value |
|-------|-------|
| **Role** | IDE integration layer — agent invocation model |
| **Integration type** | VS Code extension (proprietary) |
| **Primary integration points** | `.github/agents/*.agent.md` (VS Code Custom Agents format), `.vscode/mcp.json`, AGENTS.md VS Code Customization Taxonomy |
| **Composite risk score** | **4 / 5** (high-priority-action) |

ENISA dimension scores:

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Data portability | 3 | Conversation history limited export; agent definitions are source-controlled |
| API portability | 4 | VS Code Custom Agent format is proprietary; no 1:1 export to Cursor/Windsurf |
| Trained-model portability | **5** | Azure-hosted; no weights available |
| Service continuity | 2 | Azure SLAs; GitHub enterprise reliability; low operational risk |
| Pricing transparency | 2 | Public per-seat pricing; predictable |
| Compliance auditability | 3 | Enterprise audit logs require GitHub Enterprise tier |
| Exit costs | 4 | Full fleet port estimated 3–5 sprints; MCP protocol is portable |
| Ecosystem dependency depth | **5** | Fleet cannot be invoked without Copilot Chat today |

**Verdict**: High-priority-action. The combination of high exit costs and maximum
ecosystem dependency depth makes this the most significant lock-in risk. The
MCP server (`.vscode/mcp.json`) is a mitigating factor — the MCP protocol is open
and the 8 governance tools are portable to any compliant MCP client.

**Mitigations**:
- Create a spike issue: agent-format-portability — assess exporting `.agent.md` files as Cursor `.cursorrules` or system-prompt YAML
- Document MCP server as the provider-agnostic layer; update `mcp_server/README.md`
- Track GitHub Copilot as a single-point-of-failure in `docs/governance/governance-metrics.md`
- Evaluate Continue.dev or similar open-source VS Code extension as a fallback invocation path

---

### Dependency 3 — Ollama (local inference)

| Field | Value |
|-------|-------|
| **Role** | Local-compute contingency path (LCF axis) |
| **Integration type** | Local runtime + OpenAI-compatible REST API |
| **Primary integration points** | `.github/agents/local-compute-scout.agent.md`, `scripts/rate_limit_config.py` (local-localhost profile) |
| **Composite risk score** | **1 / 5** (accepted) |

All 8 ENISA dimensions score 1 or 2 (all data local; open-source; fully portable weights;
no vendor dependency). This dependency validates the MANIFESTO.md §3 Local-Compute-First
axiom: Ollama's existence in the fleet directly reduces the composite risk of the Claude
dependency by providing an operational fallback.

**Verdict**: Accepted. No mitigation required.

---

## Composite Risk Summary

| Provider | Composite Score | Verdict | Action Required |
|----------|----------------|---------|----------------|
| Anthropic / Claude | 3 / 5 | Accepted-with-mitigation | LiteLLM adaptor layer; Ollama fallback docs |
| GitHub Copilot | 4 / 5 | High-priority-action | MCP portability docs; format spike issue |
| Ollama (local) | 1 / 5 | Accepted | None |

**Fleet-wide weighted mean**: ~2.7 / 5 — Moderate overall lock-in posture.

---

## Recommendations

1. **[ADOPT]** Create follow-up issue: "Add LiteLLM adaptor layer to `rate_limit_gate.py` to enable provider switching via config" — reduces Claude exit costs from 3 → 2.

2. **[IMPLEMENT]** Create follow-up issue: "Agent-format-portability spike — assess exporting `.agent.md` Custom Agent files to Cursor / Continue.dev format" — reduces GitHub Copilot exit costs from 4 → 3.

3. **[ADOPT]** Update `mcp_server/README.md` to explicitly document MCP server as the provider-agnostic governance layer, callable from any MCP-compliant client (not only VS Code Copilot Chat).

4. **[IMPLEMENT]** Add GitHub Copilot as a tracked single-point-of-failure in `docs/governance/governance-metrics.md` — makes it visible to quarterly governance reviews.

5. **[DEFER]** OpenAI (GPT-3.5/4) references exist in `rate_limit_config.py` as non-default profiles. No active dependency today; monitor as a potential migration target. No action required this cycle.

---

## Audit Methodology

1. **Inventory scan**: `uv run python scripts/audit_ai_dependencies.py --dry-run` — automated pattern matching against 4 provider signatures across 114 files
2. **Manual scoring**: Each dependency scored on 8 ENISA dimensions using the rationale-per-dimension format in `data/enisa-lock-in-scoring.yml`
3. **Composite risk**: Arithmetic mean of 8 dimension scores, rounded to nearest integer
4. **Verdict mapping**: ≤2 = accepted; 3 = accepted-with-mitigation; ≥4 = high-priority-action
5. **Machine-readable record**: Full scoring stored in `data/enisa-lock-in-scoring.yml` for programmatic access by future tooling

---

## References

- [NIST AI RMF GOVERN 6.1](https://airc.nist.gov/Docs) — third-party AI dependency tracking control
- [ENISA Cloud Service Switching Framework](https://www.enisa.europa.eu/publications/cloud-service-switching) — 8 lock-in dimensions
- `docs/research/ai-platform-lock-in-risks.md` — Sprint 18 source research (AI platform lock-in risks)
- `data/enisa-lock-in-scoring.yml` — machine-readable scoring table
- `scripts/audit_ai_dependencies.py` — automated dependency scanner
- `.github/workflows/annual-ai-audit.yml` — CI reminder workflow
- [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — governing axiom for lock-in mitigation posture
