# Workplan: Issue #23 OQ-12-1 Resolution — VS Code LM API XML Pass-Through

**Branch**: `feat/implement-research-findings`
**Date**: 2026-03-07
**Orchestrator**: Executive Orchestrator

---

## Objective

Resolve OQ-12-1 from `docs/research/xml-agent-instruction-format.md` and issue #23 D1: confirm or refute whether the VS Code Language Model API performs XML pre-processing, normalisation, or caching before forwarding to the Claude endpoint. The primary source (`code.visualstudio.com/api/extension-guides/ai/language-model`) has been fetched and read; the answer is a direct update to the existing synthesis document — no full Scout→Synthesizer pipeline required. Also document the secondary finding: LM API does not support system messages, meaning `.agent.md` body content reaches Claude as a User-role message.

---

## Phase Plan

### Phase 1 — Read Primary Source + Resolve OQ-12-1 ✅
**Agent**: Orchestrator (direct — source already cached and read)
**Deliverables**:
- Primary source read: `.cache/sources/code-visualstudio-com-api-extension-guides-ai-language-model.md` (295 lines)
- Supplementary sources read: Chat Extension API, VS Code API reference
- Finding confirmed: **LM API is a verbatim string passthrough; no XML normalisation; no system messages**
**Depends on**: nothing
**Status**: ✅ Complete

### Phase 2 — Update Synthesis Document ⬜
**Agent**: Orchestrator (direct file edit)
**Deliverables**:
- `docs/research/xml-agent-instruction-format.md` — Open Question 1 marked RESOLVED; Executive Summary caveat removed; new Sources row added; secondary finding (no system messages) documented
**Depends on**: Phase 1
**Status**: Not started

### Phase 3 — Update OPEN_RESEARCH.md + Validate ⬜
**Agent**: Orchestrator (direct)
**Deliverables**:
- `docs/research/OPEN_RESEARCH.md` — issue #23 D1 gate marked complete; status note updated
- `uv run python scripts/validate_synthesis.py docs/research/xml-agent-instruction-format.md` passes
**Depends on**: Phase 2
**Status**: Not started

### Phase 4 — Commit + Push + Close Gates ⬜
**Agent**: Orchestrator (direct terminal)
**Deliverables**:
- 1 atomic commit: `docs(research): resolve OQ-12-1 — VS Code LM API XML pass-through confirmed`
- Issue #23 D1 gate checked; Issue #26 item 6 checked
**Depends on**: Phase 3
**Status**: Not started

---

## Acceptance Criteria

- [x] Phase 1: Primary source read, finding determined
- [ ] Phase 2: `xml-agent-instruction-format.md` Open Question 1 marked RESOLVED
- [ ] Phase 3: `validate_synthesis.py` exits 0; OPEN_RESEARCH.md updated
- [ ] Phase 4: Commit pushed; issues #23 D1 + #26 item 6 confirmed checked
