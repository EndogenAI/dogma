# Workplan — Implement Research Findings (Sprint 1)

**Date**: 2026-03-06  
**Branch**: `feat/implement-research-findings`  
**Session type**: Implementation sprint  

---

## Objective

Implement the three outstanding action items derived from the three Final research documents
merged in PR #11 (`agentic-research-flows.md`, `xml-agent-instruction-format.md`,
`agent-fleet-design-patterns.md`). These are programmatic and documentation outputs — not
further research.

---

## Phase Plan

### Phase 1 — Scratchpad Section-Scope Convention

**Agent**: Executive Orchestrator (direct implementation)  
**Deliverables**:
- `AGENTS.md` — new subsection under Agent Communication documenting section-scope rule (each
  agent appends only to its own named heading and reads only its own prior section; Executive
  is sole integration point). Add one-liner naming the Focus-on-Descent / Compression-on-Ascent
  principle with handoff token target (≤ 2,000 tokens).
- `docs/guides/session-management.md` — matching update under "During a Session / Writing to
  the Scratchpad" documenting the section-scope isolation rule.
- `docs/AGENTS.md` — no change required (no agent authoring convention implicated).
- `.github/agents/AGENTS.md` — no change required.

**Depends on**: nothing  
**Gate**: Phase 2 does not begin until Phase 1 changes are committed  
**Status**: ⬜ Not started  

---

### Phase 2 — `scripts/validate_synthesis.py`

**Agent**: Executive Orchestrator (direct implementation)  
**Deliverables**:
- `scripts/validate_synthesis.py` — programmatic synthesis quality gate. Checks: file exists,
  ≥ 100 lines, all 8 section headings present (`## 1. Citation` through `## 8. Project
  Relevance`), frontmatter has `status`, `source_url`, `cache_path`. Exit 0 = pass, 1 = fail
  with specific gap reported.
- `scripts/README.md` — new entry documenting the script.
- `.github/agents/research-archivist.agent.md` — Workflow updated to run
  `uv run python scripts/validate_synthesis.py <path>` before any commit. Completion criteria
  updated to include the gate check.

**Depends on**: Phase 1 committed  
**Gate**: Phase 3 does not begin until Phase 2 changes are committed  
**Status**: ⬜ Not started  

---

### Phase 3 — `scripts/migrate_agent_xml.py` + `scaffold_agent.py` update

**Agent**: Executive Orchestrator (direct implementation)  
**Deliverables**:
- `scripts/migrate_agent_xml.py` — bulk migration script per xml-agent-instruction-format.md
  §8 spec. Flags: `--dry-run`, `--file`, `--all`, `--min-lines` (default 30),
  `--model-scope` (default: claude). Maps `## SectionName` → XML tag wrapping per §4 tag
  inventory. Does not touch YAML frontmatter. Exit 0 = success, 1 = error.
- `scripts/scaffold_agent.py` — updated TEMPLATE to emit hybrid XML-format stubs (sections
  wrapped in `<instructions>`, `<constraints>` etc.).
- `scripts/README.md` — new entry for migrate_agent_xml.py.
- `.github/agents/AGENTS.md` — note that new agents must use hybrid XML schema; scaffold
  emits XML by default.

**Depends on**: Phase 2 committed  
**Gate**: Session closes when Phase 3 is committed and pushed  
**Status**: ⬜ Not started  

---

## Acceptance Criteria

- [ ] AGENTS.md names the Focus-on-Descent / Compression-on-Ascent principle with ≤ 2,000 token target
- [ ] AGENTS.md documents per-agent section-scope isolation rule for `.tmp/` scratchpad
- [ ] `docs/guides/session-management.md` mirrors these two additions
- [ ] `scripts/validate_synthesis.py` exits 0 on a valid D3 file and 1 with a specific error on an invalid one
- [ ] `research-archivist.agent.md` Workflow runs validation before commit
- [ ] `scripts/migrate_agent_xml.py --dry-run --file <agent>` produces correct diff without writing
- [ ] `scripts/scaffold_agent.py --dry-run` emits XML-tagged stubs
- [ ] All three phases committed with Conventional Commit messages
- [ ] Branch pushed to origin; PR opened
