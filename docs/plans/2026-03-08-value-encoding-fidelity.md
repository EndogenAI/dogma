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
- [x] `MANIFESTO.md` updated with "How to Read This Document" note (exact text in issue body) *(done ce8ee48 / PR #53 — pre-existing)*
- [x] `AGENTS.md` cross-reference updated to cite the hermeneutics note *(done PR #86)*
- [x] Audit table committed to `docs/research/values-encoding.md` §6 appendix *(done PR #86)*
- [x] Priority-ordered gap list ready to drive Phase 3 *(done PR #86)*
- [x] CI passes; changes committed and PR opened *(PR #86 — all CI green)*

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

### Phase 2 Detailed Checklist

**Issue**: #85 | **Branch**: `research/context-window-budget` (off `feat/value-encoding-fidelity`)

---

#### Step 1 — Branch Setup
**Owner: Executive Orchestrator**

- [ ] Ensure `feat/value-encoding-fidelity` is up to date: `git fetch origin && git checkout feat/value-encoding-fidelity && git pull`
- [ ] Create branch: `git checkout -b research/context-window-budget`
- [ ] Push branch: `git push -u origin research/context-window-budget`
- [ ] Verify: `git branch -vv` confirms tracking remote

---

#### Step 2 — Pre-Flight Source Cache Warm
**Owner: Executive Orchestrator → Research Scout**

- [ ] Warm cache: `uv run python scripts/fetch_all_sources.py`
- [ ] Check priority URLs before fetching (re-fetching cached sources wastes tokens):

| URL to survey | Topic |
|---|---|
| Anthropic prompt caching docs | Instruction caching strategies |
| LangChain context management guide | Retrieval-augmented governance |
| `tiktoken` library docs (OpenAI/PyPI) | Token measurement methodology |
| Lilian Weng "Prompt Engineering" (lilianweng.github.io) | Instruction compression patterns |
| `docs/research/values-encoding.md` (endogenous) | Pattern 7, R2 — retrieval-augmented governance |

- [ ] Read `.cache/sources/` listing post-warm: confirm ≥ 3 relevant sources cached before Scout begins

---

#### Step 3 — Scratchpad Init
**Owner: Executive Orchestrator**

- [ ] Run: `uv run python scripts/prune_scratchpad.py --init`
- [ ] Confirm active scratchpad at `.tmp/research-context-window-budget/2026-03-08.md`
- [ ] Write `## Session Start` with governing axiom (Endogenous-First) and primary endogenous source (`docs/research/values-encoding.md`)

---

#### Step 4 — Research Delegation Brief to Executive Researcher
**Owner: Executive Orchestrator (hands off to Executive Researcher)**

Delegate with this scope:

> **Research question**: How do we prevent instruction volume from saturating the session context window while preserving full fidelity of encoded values?
>
> **Hypotheses to validate** (structured verdict blocks required):
> - Q1: Instruction context fraction in a typical Executive Orchestrator session exceeds 30% of usable context
> - Q2: Adherence measurably degrades above a measurable instruction-to-task ratio
> - Q3: Retrieval-augmented governance (Pattern 7 from `values-encoding.md`) yields the best cost/impact ratio among: compression / retrieval / extraction / pruning
>
> **Cross-references required** (read before writing):
> - `docs/research/values-encoding.md` §3 Pattern 7 and §4 R2
> - Issues #14 (AIGNE AFS), #13 (episodic memory), #75 (handoff drift), #80 (queryable docs), #79 (skills-as-decision), #82 (neuroplasticity)
>
> **Exclusions**: Do not modify MANIFESTO.md, AGENTS.md, or any agent file. Research-read and synthesis-write only.

---

#### Step 5 — Research Scout Survey
**Owner: Research Scout (under Executive Researcher)**

- [ ] Survey the pre-warmed cache and fetch any missing priority sources
- [ ] Measure token counts for instruction layers using tiktoken methodology:
  - `AGENTS.md` alone
  - Executive Orchestrator system prompt (estimated)
  - Full session context at a typical mid-session state
- [ ] Return compressed handoff (≤ 2,000 tokens) to scratchpad under `## Scout Output`

---

#### Step 6 — Synthesizer Produces D4 Document
**Owner: Research Synthesizer**

**Target file**: `docs/research/context-budget-balance.md`

**Required D4 frontmatter**:
```yaml
---
title: "Context Window Budget — Research Synthesis"
status: Draft
---
```

**Required section outline**:
```
# Context Window Budget — Research Synthesis
## 1. Executive Summary
## 2. Hypothesis Validation
  ### Q1 — Instruction Fraction Baseline   (Verdict: CONFIRMED/REFUTED/INCONCLUSIVE/DEFERRED)
  ### Q2 — Adherence Degradation Threshold (Verdict: …)
  ### Q3 — Intervention Cost/Impact Ranking (Verdict: …)
## 3. Pattern Catalog   (≥ 3 patterns; each: Name, Evidence, Endogenous applicability)
## 4. Recommendations  (Ranked R1–R4; each: Action, Cost, Impact, Depends-on issue)
## 5. Sources
```

**Cross-reference requirement**: ≥ 1 explicit reference to `../../MANIFESTO.md` or `../../AGENTS.md` before closing `## 4. Recommendations`.

---

#### Step 7 — Policy Document Draft
**Owner: Research Synthesizer (same pass as D4 doc)**

**Target file**: `docs/context_budget_target.md`

**Required schema**: status header, Tiers table (T1 Instruction / T2 Session / T3 Output / T4 Reserve with budget ceilings derived from D1 baseline), Intervention Triggers table, Derivation section referencing synthesis, Related Issues list (#85, #80, #13).

---

#### Step 8 — Reviewer Validation Gate
**Owner: Research Reviewer**

- [ ] Run: `uv run python scripts/validate_synthesis.py docs/research/context-budget-balance.md` (must exit 0)
- [ ] YAML frontmatter has `title` and `status`; all five required headings present in order
- [ ] ≥ 3 hypothesis verdicts recorded; ≥ 1 MANIFESTO/AGENTS cross-reference
- [ ] Update `status: Draft` → `status: Final` after checklist passes
- [ ] Record Reviewer verdict in scratchpad under `## Reviewer Verdict`

---

#### Step 9 — Commit Sequence
**Owner: Research Archivist**

```bash
git add docs/research/context-budget-balance.md docs/research/sources/
git commit -m "docs(research): add context-budget-balance synthesis — status: Final

Closes #85. D4 synthesis: D1 baseline, D2 threshold, D3 ranked interventions.
Refs #14, #13, #75, #80, #79, #82"

git add docs/context_budget_target.md
git commit -m "docs: add context_budget_target.md policy draft"

git push origin research/context-window-budget
```

---

#### Step 10 — Workplan Update & Issue Close
**Owner: Research Archivist**

- [ ] Mark Phase 2 gate deliverables `[x]` in this workplan
- [ ] Write close comment to temp file and post: `gh issue comment 85 --body-file /tmp/issue-85-close.md`
- [ ] Close: `gh issue close 85` then verify: `gh issue view 85`

---

#### Acceptance Criteria Summary

| Deliverable | Path | Status check |
|---|---|---|
| D1 baseline | §2 Q1 in synthesis | Reviewer verdict |
| D2 threshold | §2 Q2 in synthesis | Reviewer verdict |
| D3 recommendations | §4 in synthesis | `validate_synthesis.py` exit 0 |
| D4 synthesis doc | `docs/research/context-budget-balance.md` | `status: Final` in frontmatter |
| D5 policy draft | `docs/context_budget_target.md` | Committed on branch |
| CI | branch CI | `gh run list --limit 3` all green before PR |

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
