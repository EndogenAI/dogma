# Workplan: Sprint 22 Secondary Research

**Branch**: `feat/recommendation-provenance-sprint`
**Date**: 2026-03-23
**Orchestrator**: Executive Orchestrator

---

## Objective

Execute 8 secondary research issues from the backlog with full synthesis documents following the D4 methodology. Sprint 22 focuses on secondary research (literature review and external source synthesis) across 5 themes: Security (#400), Infrastructure (#395, #417), Agent Architecture (#397), Developer Experience (#398, #420), and Governance (#329). Local Compute validation (#418) informs whether to reduce external API dependency. All primary research issues (#234, #396, #413, #414, #422) are deferred to a subsequent sprint pending protocol finalization (issue #422).

---

## Phase Plan

### Phase 1 — Issue #417 MCP Deprecation Analysis ✅
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/mcp-deprecation-analysis.md (Status: Final)
- Hypothesis validation: MCP deprecation claims assessed
- Recommendations: Continue MCP adoption strategy
- Issue #417 closed

**Depends on**: nothing
**CI**: validate_synthesis, lychee
**Status**: ✅ Complete (commit 48a4c4b)

### Phase 2 — Issue #400 Agent Breakout Security ⏳
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/agent-breakout-analysis.md (Status: Final)
- Failure taxonomy with canonical examples
- Blast radius comparison table
- Security guardrail recommendations aligned with MANIFESTO ethical constraints
- Issue #400 closed

**Depends on**: Phase 1 complete
**CI**: validate_synthesis, lychee
**Status**: ⏳ In Progress (sources cached, ready for synthesis)

### Phase 3 — Issue #418 Claude Code Local LLM Script ⬜
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/claude-code-local-llm.md (Status: Final)
- Script analysis and model compatibility assessment
- Cost-quality comparison: local vs. API
- Adoption recommendation for Local Compute-First axiom validation
- Issue #418 closed

**Depends on**: Phase 2 complete
**CI**: validate_synthesis, lychee
**Status**: ⬜ Not started

### Phase 4 — Issue #329 San Jose AI Governance Video ⬜
**Agent**: Executive Researcher → Research Scout (transcript-extraction skill) → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/san-jose-ai-governance.md (Status: Final)
- Transcript extraction from YouTube source
- Governance patterns aligned with civic-ai-governance.md corpus
- Recommendations for dogma governance framework
- Issue #329 closed

**Depends on**: Phase 3 complete
**CI**: validate_synthesis, lychee
**Status**: ⬜ Not started

### Phase 5 — Issue #397 Multi-Agent Collaboration Patterns ⬜
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/multi-agent-collaboration.md (Status: Final)
- Collaboration taxonomy: "true" collaboration vs. discrete orchestration
- Comparison table with dogma's handoff topology
- Recommendations for fleet evolution
- Issue #397 closed

**Depends on**: Phase 4 complete
**CI**: validate_synthesis, lychee
**Status**: ⬜ Not started

### Phase 6 — Issue #398 GitHub Blog Articles Review ⬜
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/github-blog-synthesis.md (Status: Final)
- Multi-source synthesis: context windows, Plan agent, TDD patterns
- Comparison table across 2-3 GitHub blog articles
- Pattern catalog relevant to dogma workflows
- Issue #398 closed

**Depends on**: Phase 5 complete
**CI**: validate_synthesis, lychee
**Status**: ⬜ Not started

### Phase 7 — Issue #420 InfoQ Human Fit Article ⬜
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/infoq-human-fit.md (Status: Final)
- Evidence table: external validation of Augmentive Partnership axiom (MANIFESTO foundational principle)
- Industry comparison: dogma values vs. external research
- Recommendations for values encoding refinement
- Issue #420 closed

**Depends on**: Phase 6 complete
**CI**: validate_synthesis, lychee
**Status**: ⬜ Not started

### Phase 8 — Issue #395 WebMCP Browser Integration ⬜
**Agent**: Executive Researcher → Research Scout → Synthesizer → Reviewer → Archivist
**Deliverables**:
- docs/research/webmcp-browser-integration.md (Status: Final)
- Architecture evaluation informed by Phase 1 finding (MCP actively maintained)
- Integration assessment with dogma MCP server
- Adoption recommendation
- Issue #395 closed

**Depends on**: Phase 7 complete
**CI**: validate_synthesis, lychee
**Status**: ⬜ Not started

### Phase 9 — Sprint Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- All 8 synthesis docs committed with Status: Final
- All 8 issues closed
- Milestone 26 "Sprint 22 — Secondary Research" closed
- Session retrospective: harvest lessons learned (session-retrospective skill)
- Scratchpad archived: `uv run python scripts/prune_scratchpad.py --force`
- Branch pushed: all commits synced to origin

**Depends on**: Phase 8 complete
**CI**: Full test suite, lychee, validate_synthesis (all research docs)
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [x] Phase 1 complete: Issue #417 closed with synthesis doc committed (48a4c4b)
- [ ] Phase 2 complete: Issue #400 closed with agent breakout security synthesis
- [ ] Phase 3 complete: Issue #418 closed with local LLM adoption recommendation
- [ ] Phase 4 complete: Issue #329 closed with governance patterns synthesis
- [ ] Phase 5 complete: Issue #397 closed with collaboration patterns synthesis
- [ ] Phase 6 complete: Issue #398 closed with GitHub blog synthesis
- [ ] Phase 7 complete: Issue #420 closed with human fit validation synthesis
- [ ] Phase 8 complete: Issue #395 closed with WebMCP integration assessment
- [ ] All 8 synthesis docs validated: pass `validate_synthesis.py` check
- [ ] All synthesis docs pass lychee link check
- [ ] Milestone 26 closed
- [ ] Session retrospective completed (lessons encoded into substrate)
- [ ] All changes pushed to origin
