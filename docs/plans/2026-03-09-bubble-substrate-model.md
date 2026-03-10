# Workplan: Bubble Clusters as Substrate Mental Model — Milestone 7 Continuation

**Milestone**: [Value Encoding & Fidelity](https://github.com/EndogenAI/Workflows/milestone/7)
**Date seeded**: 2026-03-09
**Status**: Active — open for pick-up
**Governing axiom**: Endogenous-First — read `docs/research/values-encoding.md` before acting on any phase
**Orchestrator**: Executive Orchestrator (any session picking up this milestone)

---

## Completed Issues (Closed — Do Not Re-Plan)

> The following issues were completed in prior sessions and have committed research docs or scripts.
> They are listed here for milestone completeness only. Do not create branches or PRs for these.

| Issue | Title | Artifact |
|-------|-------|---------|
| #85 | Context budget target | `docs/context_budget_target.md` |
| #84 | Doc interlinking / weave-links | `scripts/weave_links.py` |
| #80 | Queryable substrate | `scripts/query_docs.py` + `docs/research/queryable-substrate.md` |
| #78 | Provenance tracing | `scripts/audit_provenance.py` + `docs/research/provenance-tracing.md` |
| #75 | Handoff drift measurement | `docs/research/handoff-drift.md` |
| #73 | [4,1] encoding coverage audit | audit table in `docs/research/values-encoding.md` §6 |
| #71 | Drift detection scripts | `scripts/detect_drift.py` |
| #70 | 4-form encoding in MANIFESTO.md | committed MANIFESTO.md edits |
| #69 | Hermeneutics note | MANIFESTO.md "How to Read This Document" |
| #54 | Cross-reference density score | `scripts/audit_provenance.py` density metric |

---

## Objective

Execute the remaining open research issues in Milestone 7, anchored on the **bubble cluster substrate mental model** (#88). The bubble cluster model — where the system is a collection of discrete lower-dimensional bubbles (substrates) bounded by membranes that govern inter-substrate signal clarity — is a conceptual evolution of the "biological homology" framing in `docs/research/values-encoding.md`. Researching this model first (#88) unlocks the framing for all downstream encoding-extension and behavioral-testing work. Read `docs/research/values-encoding.md` in full before picking up any phase.

---

## Dependency Map

```
#88 (bubble clusters + neuroanatomy)  ──► #83 (external/client value architecture)
                                       └─► #72 (epigenetic tagging — AGENTS.md annotation)

#72 NOTE: already partially encoded in AGENTS.md §Context-Sensitive Amplification table;
          Phase B research = synthesis + formal doc, not implementation from scratch

#74 (LLM behavioral testing)          ──► soft dep on #13 (episodic memory infra)
                                           Constitutional AI scope can start independently

#76 (XML structuring in handoffs)     ──► standalone, no deps
#13 (episodic memory)                 ──► soft prereq for #74 (can run independently)
#14 (AIGNE AFS evaluation)            ──► standalone (informs #80 already done)
```

---

## Recommended Execution Order

---

### Phase A — Anchor: Bubble Clusters + Neuroanatomy ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #88 | Deep Dive Research - Bubble Clusters as Substrate Mental Model + Neuroanatomy | research | xl |

**Branch convention**: `research/bubble-clusters-phase-a-neuroanatomy`
**Agent**: Executive Researcher → Research Scout → Research Synthesizer → Research Reviewer → Research Archivist
**Depends on**: none — start here
**Gate deliverables**:
- [ ] `docs/research/bubble-clusters-substrate.md` committed with `Status: Final`
- [ ] Document covers: bubble/soap/bucket metaphor, neuroanatomical parallels (Allen Institute atlas), boundary membrane dynamics, echo chamber / socio-political dimension, mathematical bubble properties
- [ ] At least one `**Canonical example**:` and one `**Anti-pattern**:` in the Pattern Catalog section
- [ ] ≥ 2 explicit MANIFESTO.md axiom citations in the synthesis
- [ ] Issue #88 updated with comment linking to committed doc
- [ ] CI passes on PR

**Review gate**: Research Reviewer validates that the boundary-membrane framing is clearly distinguished from the existing biological-homology framing in `docs/research/values-encoding.md`, and that the Pattern Catalog contains concrete actionable implications for encoding methodology.

**Session notes (2026-03-09)**:
- Governing axiom confirmed: **Endogenous-First** — primary endogenous source: `docs/research/values-encoding.md`
- Bubble cluster model identified as conceptual evolution of §3 biological-homology framing in `values-encoding.md`
- Scout scaffolding sources: `values-encoding.md` §3 (Patterns 1–6, §H5), `docs/research/dogma-neuroplasticity.md`, `docs/research/skills-as-decision-logic.md`
- Phase A status updated: ⬜ → 🔄 (in progress)
- Branch: `research/bubble-clusters-phase-a-neuroanatomy`

---

### Phase B — Encoding Extensions ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #83 | Research: encoding external product and client values — layered value architecture for adoptions | research | xl |
| #72 | Research: context-sensitive axiom amplification — epigenetic tagging for task-type routing | research | m |

**Branch convention**: `research/encoding-extensions-phase-b`
**Agent**: Executive Researcher → Research Scout (per issue) → Research Synthesizer → Research Reviewer → Research Archivist; Executive Docs for #72 (partial implementation already in AGENTS.md)
**Depends on**: Phase A complete (bubble cluster framing informs layered value architecture)
**Sequencing note**: #83 and #72 can be researched in parallel on separate branches; merge order does not matter

**Gate deliverables**:
- [ ] `docs/research/external-value-architecture.md` committed with `Status: Final` (issue #83)
- [ ] `docs/research/epigenetic-tagging.md` committed with `Status: Final` (issue #72)
- [ ] #72 doc explicitly cross-references the existing AGENTS.md § Context-Sensitive Amplification table as the implementation artifact; research frames the theoretical basis
- [ ] Issues #83 and #72 each updated with comment linking to their committed docs
- [ ] CI passes on both PRs

**Review gate**: Research Reviewer confirms #83 synthesis addresses both inbound adoption (external product values) and outbound encoding (client-facing substrate layers). Reviewer confirms #72 synthesis validates or extends the existing AGENTS.md table rather than duplicating it.

---

### Phase C — LLM Behavioral Testing ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #74 | Research: LLM behavioral testing for value fidelity (Constitutional AI self-critique as post-session hook) | research | l |

**Branch convention**: `research/llm-behavioral-testing-phase-c`
**Agent**: Executive Researcher → Research Scout → Research Synthesizer → Research Reviewer → Research Archivist
**Depends on**: Phase A (bubble cluster framing clarifies what "value fidelity" means at substrate boundaries); #13 is a soft prerequisite for the full test infrastructure section — if #13 is unresolved, scope to Constitutional AI self-critique only and note the dependency gap explicitly in the doc
**Gate deliverables**:
- [x] `docs/research/llm-behavioral-testing.md` committed with `Status: Final`
- [x] Document covers: Constitutional AI self-critique as post-session hook, value-fidelity test taxonomy, property-based testing patterns for agent outputs
- [x] If #13 (episodic memory) is still open, doc contains explicit "Dependency Gap" section noting what would unlock the full test framework
- [x] Issue #74 updated with comment linking to committed doc
- [x] CI passes on PR

**Review gate**: Research Reviewer confirms the post-session hook design is concrete enough to be implemented as a script (not just theory), and that the test taxonomy maps to specific MANIFESTO.md axioms.

---

### Phase D — Low-Effort / Loose Ends ✅

**Issues**:

| Issue # | Title | Type | Effort |
|---------|-------|------|--------|
| #76 | Research: XML structuring in handoffs.prompt fields for complex orchestration instructions | research | xs |
| #13 | [Research] Episodic and Experiential Memory for Agent Sessions | research | l |
| #14 | [Research] AIGNE AFS Context Governance Layer Evaluation | research | l |

**Branch convention**: `research/loose-ends-phase-d` (or one branch per issue for xs/l split)
**Agent**: Executive Researcher for #76 (xs — may delegate directly to Research Synthesizer); Research Scout → Synthesizer → Reviewer → Archivist for #13 and #14
**Depends on**: none — all three are standalone; #13 should be completed before requesting #74 full test-framework expansion
**Sequencing note**: #76 is xs effort and can be completed in a single sitting; #13 and #14 are l effort and may need separate branches

**Gate deliverables**:
- [x] OQ-12-4 resolution appended to `docs/research/xml-agent-instruction-format.md` Section 11 (issue #76)
- [x] `docs/research/episodic-memory-agents.md` committed with `Status: Final` (issue #13)
- [x] `docs/research/aigne-afs-evaluation.md` committed with `Status: Final` (issue #14)
- [x] All three issues updated with comments linking to their committed docs
- [x] CI passes

**Review gate**: Research Reviewer confirms #14 AIGNE AFS evaluation includes a concrete recommendation (adopt / monitor / skip) with explicit rationale tied to Local Compute-First axiom.

---

## Deferred / Dependent Issues

| Issue # | Title | Status | Demarcation |
|---------|-------|--------|-------------|
| ~~#82~~ | Research: dogma neuroplasticity | Research doc already exists | `docs/research/dogma-neuroplasticity.md` — issue #82 needs closure |
| ~~#81~~ | Research: deterministic agent components | Research doc already exists | `docs/research/deterministic-agent-components.md` — issue #81 needs closure |
| ~~#79~~ | Research: skills as decision codifiers | Research doc already exists | `docs/research/skills-as-decision-logic.md` — issue #79 needs closure |

---

## Acceptance Criteria (Milestone Close)

- [x] Phase A complete: `docs/research/bubble-clusters-substrate.md` committed, issue #88 closed
- [x] Phase B complete: `docs/research/external-value-architecture.md` and `docs/research/epigenetic-tagging.md` committed, issues #83 and #72 closed
- [x] Phase C complete: `docs/research/llm-behavioral-testing.md` committed, issue #74 closed
- [x] Phase D complete: all three research docs committed, issues #76, #13, #14 closed
- [x] Deferred issues closed: #82, #81, #79 closed with reference to their existing research docs
- [x] Executive Docs notified if any findings require updates to `AGENTS.md`, `MANIFESTO.md`, or guides
- [x] `docs/research/values-encoding.md` updated with a forward-reference to `docs/research/bubble-clusters-substrate.md` once Phase A is committed

---

## Session Start Checklist

Any future session picking up a phase must complete these steps before acting:

1. Read `docs/research/values-encoding.md` — the primary endogenous source for this milestone
2. Read this workplan (`docs/plans/2026-03-09-bubble-substrate-model.md`) and note which phase is active (⬜ = not started, 🔄 = in progress, ✅ = complete)
3. Check branch status: `git log --oneline -5` and `git branch`
4. Read today's scratchpad: `cat .tmp/main/$(date +%Y-%m-%d).md`
5. State the governing axiom: "Endogenous-First — scaffold from existing research docs before reaching for external sources"
6. Run `uv run python scripts/prune_scratchpad.py --init` if today's scratchpad does not exist
