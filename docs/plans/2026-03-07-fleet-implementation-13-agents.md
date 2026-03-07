# Plan: Fleet Implementation — 13 New Agents (Adopt + Investigate)
**Date**: 2026-03-07
**Branch**: research/fleet-expansion-planning
**Status**: Complete
**Tracking PR**: #46

---

## Objective

Author `.agent.md` files for all 13 non-deferred agents from the fleet expansion plan (issues #41–#44). Update fleet README, assign issues to milestones, add to project board, open PR, and tag user for review.

**Scope**: Adopt-now (4) + Investigate (9) = 13 agents. Defer tier (6) is explicitly excluded.

---

## Agent Roster

### Phase A — Adopt-Now (4 agents)

| ID | Agent | File | Issue |
|----|-------|------|-------|
| A1 | Security Researcher | `security-researcher.agent.md` | #41 |
| A2 | Local Compute Scout | `local-compute-scout.agent.md` | #41 |
| B1 | Release Manager | `release-manager.agent.md` | #42 |
| D1 | Issue Triage Agent | `issue-triage.agent.md` | #44 |

### Phase B — Investigate (9 agents)

| ID | Agent | File | Issue |
|----|-------|------|-------|
| A3 | MCP Architect | `mcp-architect.agent.md` | #41 |
| A4 | Values Research Agent | `values-researcher.agent.md` | #41 |
| B2 | Env Validator | `env-validator.agent.md` | #42 |
| B3 | Test Coordinator | `test-coordinator.agent.md` | #42 |
| B4 | CI Monitor | `ci-monitor.agent.md` | #42 |
| C1 | DevRel Strategist | `devrel-strategist.agent.md` | #43 |
| C2 | Community Pulse Agent | `community-pulse.agent.md` | #43 |
| D2 | LLM Cost Optimizer | `llm-cost-optimizer.agent.md` | #44 |
| D3 | Documentation Linter | `docs-linter.agent.md` | #44 |

---

## Acceptance Criteria

- [ ] All 13 `.agent.md` files created in `.github/agents/`
- [ ] All agent names unique across fleet
- [ ] All descriptions ≤ 200 characters
- [ ] All handoff targets resolve to existing agents
- [ ] Fleet README (`README.md`) updated with new catalog sections
- [ ] Issues #41–#44 assigned to milestones and added to project board
- [ ] PR opened on `research/fleet-expansion-planning`
- [ ] @conorjmcnamara tagged in PR for review

---

## Phase Plan

### Phase A — Adopt-Now Agents

**Deliverables**: 4 `.agent.md` files (A1, A2, B1, D1)
**Gate**: All 4 pass `validate_synthesis`-style checks; commit before Phase B

### Phase B — Investigate Agents

**Deliverables**: 9 `.agent.md` files (A3, A4, B2–B4, C1–C2, D2–D3)
**Gate**: All 9 valid; commit then update README

### Phase C — Housekeeping

**Deliverables**: README updated, issues linked to milestones, PR open, user tagged
