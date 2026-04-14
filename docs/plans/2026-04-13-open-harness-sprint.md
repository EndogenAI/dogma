# Open Harness Architecture Sprint — Workplan

**Created**: 2026-04-13  
**Branch**: TBD (will be `feat/open-harness-sprint` or similar)  
**Epic**: Validate DogmaMCP as open harness + mature scratchpad to production-grade memory substrate  
**Issues**: #551 (DogmaMCP Open Harness Validation), #552 (Scratchpad Maturity)  
**Context**: Research from #550 (harness-memory-governance.md) revealed that DogmaMCP architecture aligns with "open harness" concept and identified scratchpad as MVP memory substrate needing maturation. This is a MAJOR product positioning opportunity.

---

## Objectives

1. **Validate DogmaMCP as open harness** — research and document whether DogmaMCP meets open harness criteria (model-agnostic, standards-based, user-owned memory, portable, self-hostable, open source)
2. **Mature scratchpad from MVP to robust OSS memory substrate** — schema definition, export tooling, cross-session retrieval, provenance tracking, standards compliance
3. **Position DogmaMCP strategically** — synthesize findings into marketing/docs narrative that differentiates from proprietary agent platforms

**Governing axiom**: Endogenous-First (read existing corpus + competitor research before implementation)  
**Primary endogenous source**: docs/research/harness-memory-governance.md (H4, R1)

---

## Coupling Rationale

These two issues are intentionally **sequenced** (not parallel):
- DogmaMCP validation research (Phase 1) will surface **specific requirements** for what the scratchpad needs to satisfy "open harness" memory standards
- Scratchpad maturity implementation (Phase 2+) will implement those requirements
- Without validation research first, we risk building features that don't align with industry standards or user needs

**Exception**: Phase 1A (competitor research) is shared between both issues — scout once, apply findings to both.

---

## Phase Breakdown

### Phase 0 — Workplan Review Gate (Mandatory)

**Agent**: Review  
**Task**: Validate workplan against AGENTS.md phase ordering constraints (research-first, cross-cutting research in Phase 1, documentation-first)  
**Deliverables**: `## Workplan Review Output` in scratchpad with APPROVED verdict  
**Depends on**: Nothing  
**Gate**: Phase 1 does not begin until APPROVED  
**Effort**: XS (15 min)  
**Status**: ✅ Complete

---

### Phase 1 — Competitor Research & Standards Survey (Shared)

**Agent**: Executive Researcher → Research Scout  
**Task**: 
- Corpus check: existing DogmaMCP, MCP, scratchpad, memory governance docs
- Competitor research: Scout ≥5 production agent platforms for harness characteristics + memory substrate approaches
  - Harness criteria: model-agnostic, standards-based, user-owned memory, portable, self-hostable, license
  - Memory criteria: persistence, export formats, cross-session retrieval, retention, standards compliance
- Standards survey: agents.md, agentskills.io, MCP memory tools, OpenTelemetry
- Cache all sources: `.cache/sources/`

**Deliverables**: 
- Scout findings in scratchpad (`## Phase 1 Output`)
- Cached sources (≥5 external + corpus references)

**Depends on**: Phase 0 APPROVED  
**Gate**: Phase 1 Review does not start until deliverables logged  
**Effort**: L (3-4 hours)  
**Status**: ✅ Complete

---

### Phase 1 Review — Review Gate

**Agent**: Review  
**Task**: Validate Phase 1 Scout findings logged in scratchpad; confirm ≥5 sources cached  
**Deliverables**: `## Phase 1 Review Output` with APPROVED verdict  
**Depends on**: Phase 1 complete  
**Gate**: Phase 2 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ✅ Complete

---

### Phase 2 — DogmaMCP Open Harness Validation (Synthesis)

**Agent**: Executive Researcher → Research Synthesizer  
**Task**:
- Synthesize Scout findings into structured analysis:
  - **Mapping**: Does DogmaMCP satisfy each open harness criterion? (model-agnostic ✓/✗, standards-based ✓/✗, etc.)
  - **Gap analysis**: Where does DogmaMCP fall short? What needs to mature?
  - **Competitor comparison**: How do proprietary platforms (LangChain, Letta) compare?
- Deliverable format: D4 research doc OR ADR (user preference TBD)
  - If D4: `docs/research/dogmamcp-open-harness-validation.md` (status: Final)
  - If ADR: `docs/decisions/ADR-XXX-dogmamcp-open-harness.md`

**Deliverables**: 
- Synthesis doc committed (D4 or ADR)
- Issue closed (DogmaMCP validation issue)

**Depends on**: Phase 1 Review APPROVED  
**Gate**: Phase 2 Review does not start until doc committed  
**Effort**: M (2-3 hours)  
**Status**: ✅ Complete

---

### Phase 2 Review — Review Gate

**Agent**: Review  
**Task**: Validate synthesis doc against D4 schema (if D4) or ADR template (if ADR); confirm mapping table complete  
**Deliverables**: `## Phase 2 Review Output` with APPROVED verdict  
**Depends on**: Phase 2 complete  
**Gate**: Phase 3 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ✅ Complete

---

### Phase 3 — Scratchpad Current State Audit

**Agent**: Executive Scripter  
**Task**:
- Audit all `.tmp/*/` folders: structure conventions, size patterns, retention behavior
- Audit `prune_scratchpad.py`: what does it do? when does it archive?
- User needs inventory: What do agents/humans/CI need from scratchpad?
- Gap analysis: Compare current state to competitor best practices (from Phase 1) + user needs
- **Deliverable**: Findings doc in scratchpad (`## Phase 3 Output`) with must-have vs. nice-to-have gaps

**Deliverables**: Audit findings logged in scratchpad; gap analysis table  
**Depends on**: Phase 2 Review APPROVED (because Phase 2 will surface memory requirements that inform gaps)  
**Gate**: Phase 3 Review does not start until findings logged  
**Effort**: M (2 hours)  
**Status**: ✅ Complete

---

### Phase 3 Review — Review Gate

**Agent**: Review  
**Task**: Validate audit findings completeness; confirm gap analysis distinguishes must-have vs. nice-to-have  
**Deliverables**: `## Phase 3 Review Output` with APPROVED verdict  
**Depends on**: Phase 3 complete  
**Gate**: Phase 4 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ✅ Complete

---

### Phase 4 — Scratchpad Schema Design & Validation

**Agent**: Executive Scripter  
**Task**:
- Design schema: `data/scratchpad-schema.yml` (structure, required fields, validation rules)
- Implement validator: `scripts/validate_scratchpad.py` (checks structure on write/read)
- Add CI gate: Pre-commit hook or phase-gate-sequence step for scratchpad validation
- Test: Validate existing `.tmp/*/` files against schema; fix any violations

**Deliverables**: 
- Schema committed: `data/scratchpad-schema.yml`
- Validator committed: `scripts/validate_scratchpad.py`
- Tests committed: `tests/test_validate_scratchpad.py`
- CI hook updated (if applicable)

**Depends on**: Phase 3 Review APPROVED  
**Gate**: Phase 4 Review does not start until deliverables committed  
**Effort**: L (3-4 hours)  
**Status**: ✅ Complete

---

### Phase 4 Review — Review Gate

**Agent**: Review  
**Task**: Validate schema design against audit findings; confirm validator runs on sample scratchpad; test coverage ≥80%  
**Deliverables**: `## Phase 4 Review Output` with APPROVED verdict  
**Depends on**: Phase 4 complete  
**Gate**: Phase 5 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ✅ Complete

---

### Phase 5 — Export & Import Tooling

**Agent**: Executive Scripter  
**Task**:
- Implement export: `scripts/export_scratchpad.py --format json|yaml|markdown`
- Implement import (optional): `scripts/import_scratchpad.py`
- Test round-trip: Export session → import → validate identical structure
- Document in `docs/guides/scratchpad-architecture.md` (initial draft)

**Deliverables**: 
- Export tool committed: `scripts/export_scratchpad.py`
- Import tool committed: `scripts/import_scratchpad.py` (if scoped in)
- Tests committed: `tests/test_export_scratchpad.py`, `tests/test_import_scratchpad.py`
- Guide draft: `docs/guides/scratchpad-architecture.md` (export/import section)

**Depends on**: Phase 4 Review APPROVED  
**Gate**: Phase 5 Review does not start until deliverables committed  
**Effort**: L (3-4 hours)  
**Status**: ✅ Complete

---

### Phase 5 Review — Review Gate

**Agent**: Review  
**Task**: Validate export tool produces valid JSON/YAML; test round-trip passes; guide section clear  
**Deliverables**: `## Phase 5 Review Output` with APPROVED verdict  
**Depends on**: Phase 5 complete  
**Gate**: Phase 6 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ✅ Complete

---

### Phase 6 — Cross-Session Retrieval (RAG Foundation)

**Agent**: Executive Scripter  
**Task**:
- Extend `scripts/query_docs.py` OR create `scripts/query_sessions.py`
- Index all `.tmp/*/` files (BM25 or vector embeddings — user preference TBD)
- Implement search CLI: `uv run python scripts/query_sessions.py "memory governance" --branch all`
- MCP tool integration (optional): `query_session_memory(topic, branch)` tool for agents
- Test: Index 10 sessions → query "scratchpad protocol" → verify results

**Deliverables**: 
- Query tool committed: `scripts/query_sessions.py` OR updated `scripts/query_docs.py`
- Tests committed: `tests/test_query_sessions.py`
- MCP tool (if scoped in): `mcp_server/tools/query_session_memory.py`
- Guide update: `docs/guides/scratchpad-architecture.md` (retrieval section)

**Depends on**: Phase 5 Review APPROVED  
**Gate**: Phase 6 Review does not start until deliverables committed  
**Effort**: XL (4-5 hours — depends on vector vs. BM25 choice)  
**Status**: ⬜ Not started

---

### Phase 6 Review — Review Gate

**Agent**: Review  
**Task**: Validate query tool returns relevant results; test coverage ≥80%; MCP tool (if present) passes check_substrate  
**Deliverables**: `## Phase 6 Review Output` with APPROVED verdict  
**Depends on**: Phase 6 complete  
**Gate**: Phase 7 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ⬜ Not started

---

### Phase 7 — Provenance Integration

**Agent**: Executive Scripter  
**Task**:
- Link scratchpad → commits: Auto-annotate scratchpad entries with commit SHAs after each phase
- Link scratchpad → issues/PRs: Fetch issue metadata at session start; log in Session State YAML
- Lightweight structured logging: Implement `.cache/session-events.jsonl` event stream for queryable provenance
  - Event schema: `{timestamp, event_type, phase, agent, issue, commit_sha, branch, deliverables}`
  - Query examples: `jq '.[] | select(.issue == 551)' .cache/session-events.jsonl`
  - OTel-compatible schema (migration path to full distributed tracing via issue #554)
- Tool: `scripts/annotate_scratchpad_provenance.py` (called after each commit)
- Tool: `scripts/sync_scratchpad_issues.py` (called at session init)
- Tool: `scripts/scratchpad_provenance.py` writes events to `.cache/session-events.jsonl`
- Test: Commit → verify scratchpad auto-annotates; session init → verify issue metadata present; event stream contains expected entries

**Deliverables**: 
- Provenance tools committed: `scripts/annotate_scratchpad_provenance.py`, `scripts/sync_scratchpad_issues.py`, `scripts/scratchpad_provenance.py`
- Tests committed: `tests/test_annotate_scratchpad_provenance.py`, `tests/test_sync_scratchpad_issues.py`, `tests/test_scratchpad_provenance.py`
- Event stream schema: `data/session-events-schema.yml`
- Guide update: `docs/guides/scratchpad-architecture.md` (provenance section, event stream query examples)
- AGENTS.md update (optional): Add provenance as phase-gate-sequence step

**Note**: OpenTelemetry integration deferred to issue #554 (user decision Q4). This phase implements lightweight JSON logging baseline only.

**Depends on**: Phase 6 Review APPROVED  
**Gate**: Phase 7 Review does not start until deliverables committed  
**Effort**: L (3-4 hours)  
**Status**: ⬜ Not started

---

### Phase 7 Review — Review Gate

**Agent**: Review  
**Task**: Validate provenance tools run successfully; test coverage ≥80%; guide section clear  
**Deliverables**: `## Phase 7 Review Output` with APPROVED verdict  
**Depends on**: Phase 7 complete  
**Gate**: Phase 8 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ⬜ Not started

---

### Phase 8 — Documentation & Standards Compliance

**Agent**: Executive Docs  
**Task**:
- Finalize `docs/guides/scratchpad-architecture.md` (consolidate all draft sections from Phases 5-7)
- Standards compliance matrix: Document DogmaMCP scratchpad alignment with agents.md, agentskills.io, MCP patterns
- AGENTS.md update: Add "Scratchpad Governance" section (required structure, tools, retention policy, R1 integration)
- README update: Mention scratchpad as key feature ("inspectable, exportable, portable working memory")

**Deliverables**: 
- Guide finalized: `docs/guides/scratchpad-architecture.md` (all sections complete)
- Standards matrix: `docs/governance/scratchpad-standards-compliance.md` OR section in guide
- AGENTS.md updated: "Scratchpad Governance" section committed
- README updated: Scratchpad feature mention

**Depends on**: Phase 7 Review APPROVED  
**Gate**: Phase 8 Review does not start until deliverables committed  
**Effort**: M (2-3 hours)  
**Status**: ⬜ Not started

---

### Phase 8 Review — Review Gate

**Agent**: Review  
**Task**: Validate guide completeness; confirm AGENTS.md update links correctly; README mention accurate  
**Deliverables**: `## Phase 8 Review Output` with APPROVED verdict  
**Depends on**: Phase 8 complete  
**Gate**: Phase 9 does not begin until APPROVED  
**Effort**: XS (10 min)  
**Status**: ⬜ Not started

---

### Phase 9 — Integration Testing & CI Gates

**Agent**: Executive Scripter  
**Task**:
- Run `scripts/validate_scratchpad.py` on all `.tmp/*/` files
- Test export → import round-trip on real session
- Test cross-session query on ≥10 indexed sessions
- Test provenance: Commit → verify auto-annotation
- Add CI gate: Pre-push hook runs `validate_scratchpad.py` on active session
- Update `.pre-commit-config.yaml` (if new hooks added)

**Deliverables**: 
- All integration tests pass
- CI gates committed: `.pre-commit-config.yaml` updated (if applicable)
- Test suite green: `uv run pytest tests/ -m "not slow"`

**Depends on**: Phase 8 Review APPROVED  
**Gate**: Phase 9 Review does not start until CI green  
**Effort**: M (2 hours)  
**Status**: ⬜ Not started

---

### Phase 9 Review — Review Gate (Final)

**Agent**: Review  
**Task**: Validate all CI gates pass; integration tests cover key workflows; no regressions in existing tests  
**Deliverables**: `## Phase 9 Review Output` with APPROVED verdict  
**Depends on**: Phase 9 complete  
**Gate**: PR merge eligibility  
**Effort**: XS (10 min)  
**Status**: ⬜ Not started

---

### Phase 10 — GitHub Agent Execution (Commit, PR, Merge)

**Agent**: GitHub  
**Task**:
- Commit all changes: `git commit -m "feat(scratchpad): schema, export, retrieval, provenance, docs (closes #551, closes #552)"`
- Push branch: `git push -u origin feat/open-harness-sprint`
- Open PR: Link to both issues closed; summarize phases in description
- Wait for CI: All checks green
- Request Copilot review (automatic on PR open)
- Triage review: Address all blocking comments; batch-reply and resolve threads
- Merge: Once APPROVED and CI green

**Deliverables**: 
- PR opened with both issues linked
- CI green
- Copilot review triaged
- PR merged to main
- Both issues closed (auto-closed by PR merge)

**Depends on**: Phase 9 Review APPROVED  
**Gate**: Session closes after PR merged  
**Effort**: S (1 hour — mostly waiting for CI/review)  
**Status**: ⬜ Not started

---

## Issue Mapping

| Issue | Phases Covered | Deliverables |
|-------|----------------|--------------|
| **#551: DogmaMCP Open Harness Validation** | Phase 1 (research), Phase 2 (synthesis) | D4 or ADR doc validating DogmaMCP as open harness |
| **#552: Scratchpad Maturity** | Phase 3 (audit), Phase 4 (schema), Phase 5 (export), Phase 6 (retrieval), Phase 7 (provenance), Phase 8 (docs), Phase 9 (CI) | Schema, validator, export/import tools, cross-session query, provenance tools, guide, AGENTS.md update, CI gates |

---

## Effort Estimate

| Phase | Effort | Time (hours) |
|-------|--------|--------------|
| Phase 0 | XS | 0.25 |
| Phase 1 | L | 3-4 |
| Phase 2 | M | 2-3 |
| Phase 3 | M | 2 |
| Phase 4 | L | 3-4 |
| Phase 5 | L | 3-4 |
| Phase 6 | XL | 4-5 |
| Phase 7 | L | 3-4 |
| Phase 8 | M | 2-3 |
| Phase 9 | M | 2 |
| Phase 10 | S | 1 |
| **Total** | **~23-30 hours** | |

**Sprint duration**: 2-3 days (focused work) OR 1 week (parallel with other work)

---

## Open Questions

1. **Synthesis format for DogmaMCP validation** (Phase 2): D4 research doc OR ADR? (User preference TBD)
2. **Cross-session retrieval approach** (Phase 6): BM25 (fast, simple) OR vector embeddings (semantic, requires model)? (User preference TBD)
3. **Import tooling scope** (Phase 5): Build import tool now OR defer to follow-up issue when external harness migration use case arises?
4. **OpenTelemetry integration** (Phase 7): Include in this sprint OR defer to follow-up issue as advanced provenance feature?

**Decision rule**: User answers these before Phase 1 delegation → prevents mid-phase scope changes

---

## Success Signal

✅ **DogmaMCP validated as open harness** — synthesis doc committed with mapping table (criterion → ✓/✗)  
✅ **Scratchpad matured to production-grade** — schema ✓, export ✓, retrieval ✓, provenance ✓, docs ✓, CI ✓  
✅ **Both issues closed** — PR merged with all deliverables committed  
✅ **Positioning narrative clear** — README, AGENTS.md, and guides articulate DogmaMCP's memory ownership advantage

---

## Next Steps (Pre-Delegation)

1. **User review**: Present this workplan + both issue drafts for scope approval
2. **Answer open questions**: User decides D4 vs. ADR, BM25 vs. vector, import scope, OTel scope
3. **Create issues**: Post both issue bodies to GitHub (DogmaMCP validation, scratchpad maturity)
4. **Commit workplan**: Save this doc to `docs/plans/2026-04-13-open-harness-sprint.md`
5. **Create feature branch**: `git checkout -b feat/open-harness-sprint && git push -u origin feat/open-harness-sprint`
6. **Initialize scratchpad**: `uv run python scripts/prune_scratchpad.py --init`
7. **Delegate Phase 0**: Invoke Review agent for workplan validation
8. **Proceed**: Once Phase 0 APPROVED, delegate Phase 1 to Executive Researcher

**Session disposition**: HOLD until user approves scope → IMMEDIATE delegation once approved
