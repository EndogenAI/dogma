# Workplan: LLM Performance & Costs Comparison 2026

**Branch**: `feat/llm-benchmarks-2026`
**Date**: 2026-03-27
**Orchestrator**: Executive Researcher

---

## Objective

Execute a deep research sprint on issue #396 to compare LLM performance and token costs across providers (Anthropic, OpenAI, Vertex AI, Ollama) and produce a D4 research document providing quantitative evidence for model selection.

---

## Phase Plan

### Phase 1 — Workplan Review ⬜
**Agent**: Review Agent
**Deliverables**:
- [ ] workplan APPROVED status in scratchpad

**Depends on**: nothing
**CI**: Auto-validate
**Status**: Not started

### Phase 2 — Corpus Scouting & Source Warming ⬜
**Agent**: Research Scout
**Deliverables**:
- [ ] Search for 2026 benchmarks (Sonnet 3.5/3.7, GPT-4o, DeepSeek-V3)
- [ ] List prices for Anthropic, Vertex AI, OpenRouter
- [ ] Cache findings in `.cache/sources/`

**Depends on**: Phase 1
**CI**: Auto-validate
**Status**: Not started

### Phase 3 — Synthesis & Drafting ⬜
**Agent**: Synthesizer
**Deliverables**:
- [ ] Draft `docs/research/llm-performance-costs-comparison-2026.md` (Status: Draft)
- [ ] Pricing table (cost per 1M tokens)
- [ ] Performance table (eval scores: HumanEval, BigCodeBench)
- [ ] Recommendation 1: Preferred Model Tiering (linking to #469)

**Depends on**: Phase 2
**CI**: validate_synthesis.py
**Status**: Not started

### Phase 4 — Review & Finalization ⬜
**Agent**: Reviewer
**Deliverables**:
- [ ] D4 Research Doc APPROVED status
- [ ] Finalize `docs/research/llm-performance-costs-comparison-2026.md` (Status: Final)

**Depends on**: Phase 3
**CI**: validate_synthesis.py
**Status**: Not started

### Phase 5 — Fleet Integration & Session Close ⬜
**Agent**: Executive Orchestrator
**Deliverables**:
- [ ] Fleet integration check (`uv run python scripts/check_fleet_integration.py`)
- [ ] Recommendation registry update (`uv run python scripts/index_recommendations.py`)
- [ ] Session summary & branch push

**Depends on**: Phase 4
**CI**: Auto-validate
**Status**: Not started

---

## Acceptance Criteria

- [ ] doc including pricing and performance tables committed
- [ ] Recommendation 1 links back to #469
- [ ] validate_synthesis.py passes on the final doc

## PR Description Template

<!-- Copy to PR description when opening the PR -->

Closes #396
