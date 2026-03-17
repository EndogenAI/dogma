---
governs: [sprint-15, mcp-packaging, scratchpad-architecture, local-rag]
sprint: 15
milestone: "Sprint 15 — MCP Packaging & Scratchpad Architecture"
branch: feat/sprint-15-mcp-scratchpad-arch
created: 2026-03-17
closes_issues: [285, 284, 304, 297, 294, 303, 305]
---

# Sprint 15 Workplan — MCP Packaging & Scratchpad Architecture

## Objective

Execute Sprint 15 research sprints across five research issues (#285, #284, #304,
#294, #297) and create actionable implementation workplans for two feature issues
(#303, #305). All research phases follow the Scout → Synthesizer → Review → Commit
sequence with 20-minute inter-phase sleeps to manage rate limits.

**Governing axiom**: Endogenous-First — read prior sprint docs before any external
fetch. Sprint 12 MCP, RAG, and A2A research is directly relevant to at least three
phases.

**Phase ordering rationale**: #285 (MCP pain points) is Phase 1A because it gates
#303 scoping and informs #297. #304 (scratchpad architecture) is Phase 1C rather
than 1A because it is a comparatively heavier research question but does not block
the lighter Phase 1A/1B issues. #297 is Phase 2 because it requires conclusions
from both #285 and #304. The feat issues (#303, #305, #294) are Phase 3, sequenced
after all research resolves so their workplans can incorporate research findings.

## Sprint 15 Issue Registry

| # | Title | Type | Priority | Gates / Gated by |
|---|---|---|---|---|
| #285 | MCP production pain points | research | high | Gates #303, informs #297 |
| #284 | Claude Code CLI productivity patterns | research | medium | Informs #303 surface |
| #304 | Scratchpad architecture decision | research | high | Gates #128, #129, #297 |
| #294 | Local RAG: LanceDB + BGE-Small companion repo | research/feat | medium | Builds on Sprint 12 |
| #297 | MCP-mediated scratchpad query | research | medium | Gated by #304 + #285 |
| #303 | dogma governance tools as MCP server | feat | high | Gated by #285, #297 |
| #305 | Standalone pip/uv governance pre-commit bundle | feat | medium | Independent |

## Prior Art (Endogenous Sources)

- [`docs/research/mcp-state-architecture.md`](../research/mcp-state-architecture.md) — Sprint 12 MCP three-layer state architecture
- [`docs/research/local-inference-rag.md`](../research/local-inference-rag.md) — Sprint 12: LanceDB + BGE-Small-EN-v1.5 recommendation
- [`docs/research/greenfield-repo-candidates.md`](../research/greenfield-repo-candidates.md) — Sprint 12: LanceDB scores 5/5
- [`docs/research/agent-to-agent-communication-protocol.md`](../research/agent-to-agent-communication-protocol.md) — A2A research, MCP-mediated scratchpad proposal
- [`docs/research/intelligence-architecture-synthesis.md`](../research/intelligence-architecture-synthesis.md) — Sprint 12 synthesis, Tier 2/3 recommendations
- `docs/research/competitor-landscape-agentic-frameworks.md` — Sprint 15 precursor: Taskmaster MCP model recommendation (pending merge via PR #302)

---

## Phase 1A — #285: MCP Production Pain Points

**Agent**: Research Scout → Research Synthesizer → Review Agent
**Deliverable**: `docs/research/mcp-production-pain-points.md` (D4 synthesis, Status: Final)
**Closes**: #285
**Depends on**: nothing — gates Phase 2

**Acceptance criteria**:
- [ ] Article cached: The New Stack, "MCP's biggest growing pains for production use will soon be solved"
- [ ] Prior research read: `docs/research/mcp-state-architecture.md` §Tier 2/3
- [ ] D4 doc addresses 4 research questions from issue #285
- [ ] Pain points mapped to dogma architecture impact (high/medium/low per component)
- [ ] Recommendations state whether Tier 2/3 guidance from `intelligence-architecture-synthesis.md` needs revision
- [ ] Passes `uv run python scripts/validate_synthesis.py docs/research/mcp-production-pain-points.md`
- [ ] Review agent returns APPROVED

**Post-phase**: SLEEP 20 MINUTES before Phase 1B Scout

---

## Phase 1A Review Gate

**Agent**: Review
**Deliverable**: `## Phase 1A Review Output` in scratchpad, verdict: APPROVED
**Status**: ⬜ Not started

---

## Phase 1B — #284: Claude Code CLI Productivity Patterns

**Agent**: Research Scout → Research Synthesizer → Review Agent
**Deliverable**: `docs/research/claude-code-cli-productivity-patterns.md` (D4 synthesis, Status: Final)
**Closes**: #284
**Depends on**: Phase 1A APPROVED + 20 min sleep

**Acceptance criteria**:
- [ ] Article cached: Joe Njenga, Medium, "Use These 6 CLI Tools to Make Working with Claude Code 3x Better"
- [ ] All 6 tools evaluated against dogma's existing `scripts/` and pre-commit hooks
- [ ] Overlap analysis: which tools already covered by existing scripts?
- [ ] Adoption recommendations: which tools (if any) should be added? Which replaced?
- [ ] Passes `uv run python scripts/validate_synthesis.py`
- [ ] Review agent returns APPROVED

**Post-phase**: SLEEP 20 MINUTES before Phase 1C Scout

---

## Phase 1B Review Gate

**Agent**: Review
**Deliverable**: `## Phase 1B Review Output` in scratchpad, verdict: APPROVED
**Status**: ⬜ Not started

---

## Phase 1C — #304: Scratchpad Architecture Decision

**Agent**: Research Scout → Research Synthesizer → Review Agent
**Deliverable**: `docs/research/scratchpad-architecture-decision.md` (D4 synthesis, Status: Final)
**Closes**: #304
**Depends on**: Phase 1B APPROVED + 20 min sleep

**Acceptance criteria**:
- [ ] Three candidates fully evaluated: A (flat Markdown status quo), B (SQLite+FTS5), C (MCP-mediated/hybrid)
- [ ] Trade-offs table covers: read latency, write complexity, query capability, migration cost, local-compute-first compliance, agent compatibility
- [ ] Decision section explicitly recommends one candidate with migration path
- [ ] Impact section states which of #128, #129, #297 are greenlit/scoped/superseded by the decision
- [ ] Prior art from `agent-to-agent-communication-protocol.md` referenced
- [ ] Passes `uv run python scripts/validate_synthesis.py`
- [ ] Review agent returns APPROVED

**Post-phase**: SLEEP 20 MINUTES before Phase 2 Scout

---

## Phase 1C Review Gate

**Agent**: Review
**Deliverable**: `## Phase 1C Review Output` in scratchpad, verdict: APPROVED
**Status**: ⬜ Not started

---

## Phase 2 — #297: MCP-Mediated Scratchpad Query

**Agent**: Research Scout → Research Synthesizer → Review Agent
**Deliverable**: `docs/research/mcp-scratchpad-query.md` (D4 synthesis, Status: Final)
**Closes**: #297
**Depends on**: Phase 1C APPROVED (scratchpad architecture winner) + Phase 1A APPROVED (MCP pain points) + 20 min sleep

**Acceptance criteria**:
- [ ] MCP tool interface specified: tool name(s), input schema, output format
- [ ] Transport recommendation: stdio vs SSE, informed by #285 pain points
- [ ] Query capability scope defined (within-session, cross-session, full corpus)
- [ ] Implementation path aligned with Phase 1C scratchpad architecture winner
- [ ] Passes `uv run python scripts/validate_synthesis.py`
- [ ] Review agent returns APPROVED

---

## Phase 2 Review Gate

**Agent**: Review
**Deliverable**: `## Phase 2 Review Output` in scratchpad, verdict: APPROVED
**Status**: ⬜ Not started

---

## Phase 3 — Implementation Workplans (#294, #303, #305)

**Agent**: Direct orchestration (workplan authoring, no Scout needed)
**Deliverables**:
- `docs/plans/2026-03-17-local-rag-companion-repo.md` — implementation workplan, closes #294
- `docs/plans/2026-03-17-mcp-server-governance-tools.md` — implementation workplan, closes #303
- `docs/plans/2026-03-17-governance-precommit-bundle.md` — implementation workplan, closes #305
**Depends on**: Phase 2 APPROVED (MCP findings inform #303 scope)

**Acceptance criteria**:
- [ ] Each workplan has: Objective, phases with agents/deliverables/gates, acceptance criteria per phase
- [ ] #294 workplan references Sprint 12 LanceDB recommendation as starting point
- [ ] #303 workplan incorporates MCP pain points (#285) and scratchpad architecture (#304) findings
- [ ] #305 workplan specifies pip/uv installable bundle structure (pyproject.toml extras, pre-commit hooks)
- [ ] All three workplans committed and pushed

---

## Session Close

- [ ] Sprint 15 branch pushed: `git push -u origin feat/sprint-15-mcp-scratchpad-arch`
- [ ] PR opened targeting main
- [ ] Issue body checkboxes updated for all completed issues
- [ ] Progress comments posted on #285, #284, #304, #297, #303, #305, #294
- [ ] `## Session Summary` written to scratchpad
