# Workplan: XML Agent Instruction Format Research (Issue #12)

**Branch**: `feat/issue-2-formalize-workflows`
**Date**: 2026-03-06
**Orchestrator**: Executive Orchestrator
**Closes**: [#12 — [Research] XML-Tagged Agent Instruction Format](https://github.com/EndogenAI/Workflows/issues/12)

---

## Objective

Conduct a broad research sweep across agent frameworks (Anthropic, OpenAI, LangGraph, AutoGen, VS Code Copilot agents, and others) to determine the current landscape of XML/structured tagging conventions for agent instruction files. Produce a distilled source manifest (D1), fetched+distilled resource docs (D2s), individual synthesis reports (D3s), and an issue-specific aggregate synthesis (D4) that will inform the EndogenAI `.agent.md` format decision and future migration/validation tooling. Implementation deliverables (migrate script, validation script, schema spec) are deferred to the workplan informed by D4.

---

## Research Question

What XML or structured tagging conventions do major agent frameworks use for instruction files — and what schema, nesting rules, and tooling should EndogenAI adopt when migrating its `.agent.md` files from Markdown headings to XML tags?

---

## Phase Plan

### Phase 1 — Pre-warm Cache & Scout ⬜
**Agent**: Research Scout (via Executive Researcher)
**Deliverables**:
- D1: Source manifest — markdown table of all discovered sources (title, URL, local path, key relevance)
- Minimum 8 sources; ideally 12–15 spanning: Anthropic cookbook, Claude prompt engineering docs, OpenAI structured outputs, LangGraph agent config, AutoGen agent instructions, VS Code `.chatparticipant`/`.chatagent` spec, any migration tooling in the wild

**Depends on**: nothing
**Status**: Not started

---

### Phase 2 — Fetch & Distill D2s ⬜
**Agent**: `scripts/fetch_source.py` (direct; one per URL in D1)
**Deliverables**:
- D2s: One distilled `.md` file per source in `.cache/sources/` (already-cached sources reused)

**Depends on**: Phase 1 (D1 manifest with URLs)
**Status**: Not started

---

### Phase 3 — Per-Source Synthesis D3s ⬜
**Agent**: Research Synthesizer (one invocation per D2)
**Deliverables**:
- D3s: One full 8-section synthesis report per source in `docs/research/sources/`
- Format: full academic template (100+ lines, citation, research question, theoretical framework, methodology, key claims, critical assessment, cross-source connections, project relevance)

**Depends on**: Phase 2 (D2s available in cache)
**Status**: Not started

---

### Phase 4 — Aggregate Synthesis D4 ⬜
**Agent**: Research Synthesizer
**Deliverables**:
- D4: `docs/research/xml-agent-instruction-format.md` — issue-specific synthesis drawing from all D3s
- Sections: Executive Summary, Framework Comparison Table, Recommended Schema, Reference Card (XML tag inventory), Migration Considerations, Open Questions
- Status: Draft (for Review)

**Depends on**: Phase 3 (all D3s committed)
**Status**: Not started

---

### Phase 5 — Review D4 ⬜
**Agent**: Research Reviewer
**Deliverables**:
- Verdict: Approved / Revise with specific issues flagged
- Any gaps in framework coverage identified

**Depends on**: Phase 4
**Status**: Not started

---

### Phase 6 — Archive ⬜
**Agent**: Research Archivist
**Deliverables**:
- D4 committed with `Status: Final`
- Issue #12 updated with link and closed

**Depends on**: Phase 5 (Approved verdict)
**Status**: Not started

---

## Acceptance Criteria

- [ ] D1 manifest lists ≥ 8 sources spanning ≥ 3 frameworks
- [ ] D2s exist in `.cache/sources/` for every source in D1
- [ ] D3s committed in `docs/research/sources/` for every D2, using full 8-section template
- [ ] D4 `docs/research/xml-agent-instruction-format.md` committed with `Status: Final`
- [ ] D4 includes a Framework Comparison Table and a Reference Card section
- [ ] Issue #12 closed with link to committed D4
- [ ] All changes pushed and PR #11 up to date
