# Workplan: Value Encoding & Fidelity Research Agenda

**Milestone**: [Value Encoding & Fidelity](https://github.com/EndogenAI/Workflows/milestone/7)
**Date seeded**: 2026-03-08
**Status**: Active — open for pick-up
**Governing axiom**: Endogenous-First — every session must read `docs/research/values-encoding.md` before acting
**Orchestrator**: Executive Orchestrator (any session picking up this milestone)

---

## Objective

Execute the full Value Encoding & Fidelity milestone: deepen the endogenic substrate's ability to preserve value signal across all layers of the inheritance chain (MANIFESTO.md → AGENTS.md → agent files → session behavior), make enforcement programmatic, make the substrate queryable and self-referential, and establish a governed process for the dogma to evolve through neuroplasticity.

**Primary research document**: [`docs/research/values-encoding.md`](../research/values-encoding.md) — Final synthesis that generated all issues in this milestone. Read it in full before picking up any issue.

---

## Dependency Map

```
#73 ([4,1] audit)           ──► #70 (4-form encoding MANIFESTO)
#69 (hermeneutics note)     ──► standalone, no deps — start here
#85 (context budget)        ──► coordinates and prioritises interventions below:
    ├─► #80 (queryable docs)
    ├─► #79 (skills-as-decision)
    ├─► #81 (deterministic components)
    └─► #82 (neuroplasticity)
#54 (cross-ref density)     ──► #78 (provenance tracing)
#71 (drift detection)       ──► #78 (provenance tracing)
#75 (handoff drift)         ──► #85 (context budget signal)
#72 (epigenetic tagging)    ──► #79 (skills-as-decision)
#83 (external values)       ──► deferred until #69 + #70 complete
#84 (doc interweb)          ──► staged: #54 first, then #84
#74 (LLM behavioral test)   ──► deferred until local compute (#13 prereq)
#76 (XML handoffs)          ──► standalone, low priority
#13 (episodic memory)       ──► prerequisite for #74
#14 (AIGNE AFS)             ──► informs #80 and #85
```

---

## Recommended Execution Order

Phases are ordered by impact-to-cost ratio and dependency satisfaction. Each phase should run as its own branch + PR.

---

### Phase 1 — Quick Wins (no external dependencies)

**Issues**: #69, #73
**Branch convention**: `feat/value-encoding-phase-1-quick-wins`
**Agent**: Executive Docs (#69), Explore subagent for audit work (#73)

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #69 | Add hermeneutics note to MANIFESTO.md | docs | xs |
| #73 | [4,1] encoding coverage audit | chore | xs |

**Gate deliverables**:
- [ ] `MANIFESTO.md` updated with "How to Read This Document" note (exact text in issue body)
- [ ] `AGENTS.md` cross-reference updated to cite the hermeneutics note
- [ ] Audit table committed to `docs/research/values-encoding.md` §5 appendix
- [ ] Priority-ordered gap list ready to drive Phase 3
- [ ] CI passes; changes committed and PR opened

**Review gate**: Review agent validates MANIFESTO.md edit against existing axiom structure — no contradictions, no axiom reordering.

---

### Phase 2 — Context Budget (the meta-issue)

**Issue**: #85
**Branch convention**: `research/context-window-budget`
**Agent**: Executive Researcher → Research Scout

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #85 | Context window budget — balance dogma volume against adherence degradation | research | m |

This phase is the **measurement baseline** for the entire milestone. Its findings determine which of the four intervention categories (compression / retrieval / extraction / pruning) to prioritise in later phases. Run this before committing to heavy implementation work.

**Gate deliverables**:
- [ ] Baseline measurement: instruction context fraction in a sample Executive Orchestrator session
- [ ] Degradation threshold identified
- [ ] Ranked intervention recommendations with cost/impact
- [ ] `docs/research/context-budget-balance.md` committed (Final status)
- [ ] `context_budget_target.md` policy draft

**Review gate**: Research Reviewer validates synthesis quality per D4 standard.

---

### Phase 3 — Encode the Four Forms

**Issue**: #70
**Branch convention**: `feat/value-encoding-phase-3-four-forms`
**Agent**: Executive Docs
**Depends on**: Phase 1 (#73 audit output as the gap inventory)

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #70 | Encode each core axiom in 4 forms (principle + example + anti-pattern + gate) | docs | s |

**Gate deliverables**:
- [ ] MANIFESTO.md updated: canonical examples (form 2) for all three axioms
- [ ] MANIFESTO.md updated: programmatic gate references (form 4) for all three axioms
- [ ] Changes informed by #73 audit gap list (no redundant additions)
- [ ] CI passes

**Review gate**: Review agent checks that form 2 examples are concrete (not abstract), and form 4 gates link to real existing scripts/checks.

---

### Phase 4 — Programmatic Fidelity Infrastructure

**Issues**: #54, #78, #71
**Branch convention**: `feat/value-encoding-phase-4-programmatic`
**Agent**: Executive Scripter (leads), Research Scout (for #78 survey)

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #54 | `generate_agent_manifest.py` cross-reference density score | feature | s |
| #71 | Semantic drift detection for agent files | research | m |
| #78 | Programmatic value signal provenance — `audit_provenance.py` | research | l |

#54 first (density count), then #71 (drift detection), then #78 (provenance tracing that builds on both).

**Gate deliverables**:
- [ ] `generate_agent_manifest.py` emits per-agent cross-reference density score and fleet average
- [ ] `scripts/detect_drift.py` (or `validate_agent_files.py --semantic`) prototype with per-agent drift score
- [ ] `scripts/audit_provenance.py` prototype with per-file provenance report
- [ ] Tests for all new scripts (≥80% coverage each)
- [ ] CI integration decision documented for each script

**Review gate**: Review agent validates new scripts don't introduce security issues (SSRF, injection) and follow AGENTS.md programmatic-first conventions.

---

### Phase 5 — Queryable Substrate & Doc Interweb

**Issues**: #80, #84
**Branch convention**: `research/queryable-substrate`
**Agent**: Executive Researcher (#80 survey + design), Executive Scripter (#80 and #84 implementation)
**Informed by**: Phase 2 (#85) findings on compression/retrieval tradeoff

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #80 | Queryable documentation substrate | research | l |
| #84 | Programmatic doc interlinking — citation interweb | research | m |

**Gate deliverables**:
- [ ] `scripts/query_docs.py` CLI tool (BM25 baseline) implemented and tested
- [ ] `data/link_registry.yml` schema and initial population
- [ ] `scripts/weave_links.py` prototype with dry-run mode
- [ ] `docs/research/queryable-substrate.md` committed (Final)
- [ ] `docs/research/doc-interweb.md` committed (Final)

**Review gate**: Research Reviewer validates both synthesis docs.

---

### Phase 6 — Skills as Decision Codifiers

**Issues**: #79, #81, #72
**Branch convention**: `research/skills-decision-logic`
**Agent**: Executive Fleet (#79 audit + skill authoring), Executive Researcher (#81 survey)
**Informed by**: Phase 2 (#85) findings on extraction intervention

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #79 | Skills as decision codifiers — delegation routing and phase-gate extraction | research | m |
| #81 | Deterministic agent components — FSMs and pre-LLM architectures | research | l |
| #72 | Context-sensitive axiom amplification — epigenetic tagging | research | m |

**Gate deliverables**:
- [ ] Audit of decision patterns appearing in ≥2 agent bodies; token savings estimate
- [ ] `delegation-routing` SKILL.md prototype
- [ ] `phase-gate-sequence` SKILL.md prototype
- [ ] FSM state specification for the orchestration phase-gate loop
- [ ] Epigenetic tagging recommendation (metadata / AGENTS.md selector / script)
- [ ] `docs/research/skills-as-decision-logic.md` + `docs/research/deterministic-agent-components.md` committed

**Review gate**: Executive Fleet Review validates new skills against `agent-file-authoring` SKILL.md and `validate_agent_files.py`.

---

### Phase 7 — Neuroplasticity & Back-Propagation

**Issues**: #82, #75
**Branch convention**: `research/dogma-neuroplasticity`
**Agent**: Executive Researcher → Research Scout → Synthesizer → Archivist
**Informed by**: Phase 6 (what's extractable), Phase 4 (drift measurement provides signal source)

| Issue | Title | Type | Effort |
|-------|-------|------|--------|
| #82 | Dogma neuroplasticity — back-propagation protocol | research | m |
| #75 | Empirical value drift at handoff boundaries | research | m |

**Gate deliverables**:
- [ ] Back-propagation protocol: evidence threshold, proposal format, coherence check, ADR template
- [ ] Stability tier model for substrate (Axioms / Principles / Operational Constraints)
- [ ] `scripts/propose_dogma_edit.py` specification
- [ ] Per-boundary degradation analysis from #75 (Scout → Synthesizer → Archive)
- [ ] `docs/research/dogma-neuroplasticity.md` + OQ-VE-5 appended to `values-encoding.md`

**Review gate**: Executive Docs reviews protocol for consistency with existing ADR process in `docs/decisions/`.

---

### Phase 8 — External Value Encoding (Deferred)

**Issue**: #83
**Branch convention**: `research/external-value-encoding`
**Agent**: Executive Researcher
**Depends on**: Phase 1 (#69 + #70 complete — the core layer must be solid before adding external layers); Adopt wizard (#56) design stable

| Issue | Title | Effort |
|-------|-------|--------|
| #83 | Encoding external product and client values — layered value architecture | xl |

**Note**: This phase is intentionally last. The layered value architecture requires the core encoding layer to be stable and well-specified before client-layer additions can be designed coherently. Confirm framing assumption in issue body before starting.

---

### Deferred / Dependent Issues

| Issue | Title | Deferred until |
|-------|-------|----------------|
| #74 | LLM behavioral testing for value fidelity | Local compute resolved (#13 prerequisite) |
| #76 | XML structuring in `handoffs.prompt` fields | Low priority; pick up opportunistically |
| #13 | Episodic/experiential memory | Local compute baseline (#1 in OPEN_RESEARCH.md) |
| #14 | AIGNE AFS context governance | Local compute baseline; informs #80 and #85 |

---

## Acceptance Criteria (Milestone Close)

- [ ] All non-deferred issues closed with committed deliverables
- [ ] `docs/research/values-encoding.md` §5 Open Questions all marked RESOLVED with resolution citations
- [ ] `MANIFESTO.md` updated with hermeneutics note and 4-form axiom encoding
- [ ] `scripts/detect_drift.py` (or equivalent) in CI
- [ ] `scripts/query_docs.py` functional and documented
- [ ] `delegation-routing` and `phase-gate-sequence` skills committed to `.github/skills/`
- [ ] Back-propagation protocol documented in `docs/research/dogma-neuroplasticity.md`
- [ ] `docs/research/context-budget-balance.md` committed

---

## Session Session-Start Checklist

Every session picking up a phase in this milestone must complete this before acting:

1. Read `docs/research/values-encoding.md` in full (or the relevant section if resuming)  
2. Read this workplan and note which phase is active  
3. Check the branch for in-progress commits: `git log --oneline -5`  
4. Read today's scratchpad: `cat .tmp/<branch>/<date>.md`  
5. State the governing axiom for today's work (Endogenous-First unless a specific phase changes it)  
6. Run `uv run python scripts/prune_scratchpad.py --init` to initialise the scratchpad  
