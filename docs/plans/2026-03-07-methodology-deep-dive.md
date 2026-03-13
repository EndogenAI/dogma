# Workplan: Endogenic Methodology Deep Dive

**Date**: 2026-03-07
**Branch**: `feat/methodology-deep-dive`
**Issue**: [#59](https://github.com/EndogenAI/dogma/issues/59)
**Seed document**: `docs/research/methodology-review.md` (Status: Final)

---

## Objective

Exhaustively research the four validated hypotheses from the methodology review, build a programmatic citation infrastructure (ACM format), and produce:
1. Per-sprint synthesis documents (one per hypothesis cluster)
2. A main synthesis document (fully cited, internally and externally linked)
3. A formal academic paper on **Endogenic Design and Development**

---

## Phase Plan

### Phase 0 — Infrastructure

**Agent**: Executive Orchestrator (direct execution)
**Deliverables**:
- `scripts/scaffold_manifest.py` + tests
- `scripts/add_source_to_manifest.py` + tests
- `scripts/format_citations.py` + `docs/research/bibliography.yaml` + tests
- `scripts/scan_research_links.py` + tests
- `scripts/fetch_all_sources.py` updated (`--manifest` flag) + tests
- `docs/guides/deep-research.md` — recursive deep dive research workflow
- `.github/agents/deep-research.agent.md`
- `docs/research/manifests/` directory (scaffold)
- Initial manifest generated from `scan_research_links.py` run

**Depends on**: nothing
**Gate**: All scripts pass `uv run pytest`, ruff check + format pass, initial manifest committed
**Status**: ⬜ Not started

---

### Phase 1 — Programmatic Source Discovery

**Agent**: Executive Orchestrator / scan_research_links.py
**Deliverables**:
- `docs/research/manifests/methodology-deep-dive.json` — populated with all discovered URLs from:
  - `docs/research/*.md` cross-references
  - `docs/research/sources/*.md` links
  - `.cache/sources/*.md` internal links
- Sources triage: annotated with sprint assignment (A–E) and priority

**Depends on**: Phase 0 (scan script must exist)
**Gate**: Manifest committed; `fetch_all_sources.py --manifest <path> --dry-run` reports URLs to fetch
**Status**: ⬜ Not started

---

### Phase 2 — H1 Exhaustive Scouting (Novelty Verification)

**Agent**: Research Scout (delegated by Executive Researcher)
**Deliverables**: Raw Scout findings in scratchpad under `## Sprint A Scout Output`
**Scope**:
- Academic: arXiv, ACM DL, IEEE Xplore, Google Scholar
- Practitioner: conference talks, flagship blogs
- Grey literature: theses, preprints
- Primary question: Is the endogenic synthesis genuinely novel at the specified intersection?

**Depends on**: Phase 1 (manifest as seed list)
**Gate**: ≥10 unique academic sources examined; novelty claim either substantiated or challenged
**Status**: ⬜ Not started

---

### Phase 3 — H2–H4 Broad Scouting

**Agent**: Research Scout (delegated by Executive Researcher)
**Deliverables**: Raw Scout findings in scratchpad under `## Sprint B/C/D Scout Output`
**Scope** (parallel per sprint within this phase):
- Sprint B: Turing morphogenesis, Maturana/Varela autopoiesis, L-systems, Kauffman NK
- Sprint C: Engelbart NLS, Bush memex, modern HCI augmentation + LLM collaboration papers
- Sprint D: Knuth literate programming, IaC evolution, living documentation convergence

**Depends on**: Phase 1
**Gate**: Each sprint has ≥5 examined sources; primary works located in `.cache/` or bibliographied
**Status**: ⬜ Not started

---

### Phase 4 — Fetch Manifest + Triage

**Agent**: Executive Orchestrator (direct: `fetch_all_sources.py --manifest`)
**Deliverables**:
- All manifest URLs fetched into `.cache/sources/`
- 404s / garbled responses removed from manifest
- Sources distributed across sprint buckets A–E
- `bibliography.yaml` populated with structured metadata for each source

**Depends on**: Phases 2–3 (full manifest populated by Scout)
**Gate**: `fetch_all_sources.py --manifest ... --dry-run` shows 0 unfetched non-404 sources
**Status**: ⬜ Not started

---

### Phase 5A — Sprint A Synthesis (H1 Novelty)

**Agent**: Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/methodology-H1-novelty.md` (Status: Final)
**Depends on**: Phase 4 (Sprint A sources fetched)
**Gate**: Committed, CI passing
**Status**: ⬜ Not started

---

### Phase 5B — Sprint B Synthesis (H2 Biological Metaphors)

**Agent**: Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/methodology-H2-bio-metaphors.md` (Status: Final)
**Depends on**: Phase 4
**Gate**: Committed, CI passing
**Status**: ⬜ Not started

---

### Phase 5C — Sprint C Synthesis (H3 Augmentation)

**Agent**: Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/methodology-H3-augmentation.md` (Status: Final)
**Depends on**: Phase 4
**Gate**: Committed, CI passing
**Status**: ⬜ Not started

---

### Phase 5D — Sprint D Synthesis (H4 Encode-Before-Act)

**Agent**: Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/methodology-H4-encode-before-act.md` (Status: Final)
**Depends on**: Phase 4
**Gate**: Committed, CI passing
**Status**: ⬜ Not started

---

### Phase 5E — Sprint E Synthesis (Cross-Cutting)

**Agent**: Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/methodology-E-pattern-catalog.md` (Status: Final)
**Scope**: Pattern Catalog Adopt/Gap items; internal cross-references; interconnect mapping
**Depends on**: Phases 5A–5D (all sprint syntheses complete)
**Gate**: Committed, CI passing
**Status**: ⬜ Not started

---

### Phase 6 — Main Synthesis Document

**Agent**: Research Synthesizer → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/methodology-synthesis.md`
**Content**:
- Fully cited (all citations via `bibliography.yaml` + `format_citations.py`)
- Links to all sprint synthesis docs
- Links to external primary sources (DOIs, arXiv IDs)
- Comprehensive cross-reference index

**Depends on**: Phase 5A–5E (all sprint syntheses)
**Gate**: Committed, CI passing; `format_citations.py` renders reference list cleanly
**Status**: ⬜ Not started

---

### Phase 7 — Academic Paper

**Agent**: Research Synthesizer (academic mode) → Research Reviewer → Research Archivist
**Deliverables**: `docs/research/endogenic-design-paper.md`
**Format**: ACM SIG Proceedings structure (Abstract, Introduction, Related Work, Methodology, Results, Discussion, References)
**Depends on**: Phase 6 (main synthesis complete)
**Gate**: Committed, CI passing; all references in `bibliography.yaml`
**Status**: ⬜ Not started

---

### Phase 8 — Review + PR

**Agent**: Review → GitHub
**Deliverables**: PR opened, CI passing, Copilot review requested
**Depends on**: Phase 7
**Gate**: All CI checks pass; PR URL confirmed
**Status**: ⬜ Not started

---

## Acceptance Criteria

- [ ] All Phase 0 scripts have tests; `uv run pytest tests/` passes
- [ ] `ruff check scripts/ tests/` and `ruff format --check scripts/ tests/` pass
- [ ] Initial manifest committed with ≥20 URLs from scan
- [ ] Sprints A–E syntheses committed (Status: Final)
- [ ] Main synthesis committed with complete citation list
- [ ] Academic paper committed in ACM structure
- [ ] PR #59 referenced in all sprint synthesis frontmatter
- [ ] `validate_synthesis.py` passes on all new research docs
- [ ] No dead links in lychee CI check

---

## Session Notes

**Session 1** (2026-03-07): Phase 0 — infrastructure build.
- Branch: `feat/methodology-deep-dive`
- Issue: #59
- Phases 1–8 are multi-session; each sprint synthesis is a full Research Scout → Synthesizer → Reviewer → Archivist chain.
