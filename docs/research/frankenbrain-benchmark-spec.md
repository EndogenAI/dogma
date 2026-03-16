---
title: "FrankenBrAIn 2.0 Benchmark Spec — Dogma Adoption Baseline"
status: "Draft"
closes_issue: 206
date: 2026-03-16
---

# FrankenBrAIn 2.0 Benchmark Spec — Dogma Adoption Baseline

## 1. Executive Summary

[AccessiTech/FrankenBrAIn](https://github.com/AccessiTech/FrankenBrAIn) is the organizational ancestor of the dogma substrate. It represents the pre-dogma state: an experimental AGI-oriented codebase that evolved informally without a formalized methodology, agent fleet, or encoded operational constraints. This document defines a **1.0 → 2.0 benchmark** to measure dogma's concrete impact when FrankenBrAIn is rebuilt as FrankenBrAIn 2.0 using the dogma cookiecutter as its foundation.

The benchmark is intentionally minimal — four metrics, each derivable from session artifacts already produced by dogma-based development. The document serves as a planning spec and measurement framework for the adoption experiment.

---

## FrankenBrAIn 1.0 Baseline

FrankenBrAIn 1.0 is the pre-dogma reference system. Key characteristics:

- **MCP framework**: experimental Model Context Protocol tooling as the primary coordination mechanism
- **Informal methodology**: no formalized session management, scratchpad convention, or phase-gate FSM
- **No agent fleet**: ad-hoc prompting; no `.agent.md` role files, SKILL.md procedures, or encoded guardrails
- **No test coverage for scripts**: automation existed but lacked the testing-first discipline
- **No provenance tracking**: no `governs:` annotations, no drift detection, no `annotate_provenance.py` equivalent

The 1.0 baseline is reconstructed from repository artifacts and session notes. Where quantitative data is unavailable, qualitative descriptions suffice.

---

## FrankenBrAIn 2.0 Plan

FrankenBrAIn 2.0 is a greenfield rebuild of the same system using the dogma cookiecutter as its morphogenetic seed:

```bash
uvx cookiecutter gh:EndogenAI/dogma
```

The 2.0 codebase inherits:
- Full AGENTS.md constraint set
- Pre-commit hooks (heredoc guard, ruff, validate-agent-files)
- Session management scratchpad convention
- Phase-gate FSM (`data/phase-gate-fsm.yml`)
- Agent fleet scaffold (executive-orchestrator, review, github agents)
- HGT upstream learning slot at sprint close

The rebuild begins with the domain-specific persona layer (client-values.yml) and the first sprint workplan.

---

## 2. Hypothesis Validation

The central hypothesis is: **dogma substrate adoption produces measurable, directional improvement across four session-lifecycle dimensions** compared to an unstructured pre-dogma baseline.

Four metrics operationalize this hypothesis. Each is derivable from session artifacts already produced by dogma-based development, enabling an empirical comparison between the 1.0 (estimated) and 2.0 (measured) systems:

| Metric | Description | Measurement Method | Target (2.0) |
|--------|-------------|-------------------|-------------|
| **Session coherence** | Scratchpad utilization rate | Count sessions where `## Session Summary` was written / total sessions × 100 | ≥ 85% |
| **Handoff quality** | Phase gate passage rate | Count Review gates returning APPROVED on first pass / total Review gates × 100 | ≥ 75% |
| **Token spend per phase** | Average token cost per implementation phase | Derive from session summaries; compare 1.0 (estimated) vs 2.0 (measured) | ≤ 60% of 1.0 |
| **Architectural coherence** | Time to first validated workplan | Calendar days from session 1 to first committed `docs/plans/` workplan with Review APPROVED | ≤ 3 sessions |

**Dogma baseline** (2026-03-13 sprint): Review first-pass APPROVED rate = 100% (4/4). This is the reference datum for handoff quality.

The hypothesis is confirmed if all four metrics meet their targets by FrankenBrAIn 2.0's fifth sprint. Partial confirmation (three of four) is interpretable; total failure (zero of four) would indicate the dogma cookiecutter adoption pattern requires revision. Every metric that misses its target should be traced to a specific substrate gap and addressed via a follow-up issue.

---

## 3. Pattern Catalog

This spec applies four dogma substrate patterns to the FrankenBrAIn adoption experiment:

**Canonical example — Cookiecutter as morphogenetic seed**: The `dogma` cookiecutter encodes the full AGENTS.md constraint set, pre-commit hooks, and agent fleet scaffold as a template. Adopting it gives FrankenBrAIn 2.0 a complete governance layer from session 1, rather than building it ad-hoc. See [`hooks/post_gen_project.py`](../../hooks/post_gen_project.py) for the scaffolding entry point.

**Canonical example — HGT Learning Slot**: At each FrankenBrAIn 2.0 sprint close, learnings are classified as Upstream (propagate to `dogma`) or Internal (keep in the derived repo). This closes the feedback loop between adoption experiments and substrate improvement. See [`docs/guides/session-management.md` § HGT Learning Slot](../guides/session-management.md#hgt-learning-slot).

**Canonical example — Benchmark-driven adoption**: Collecting the four metrics across sprints 1–5 transforms the adoption from anecdotal ("it helped") to empirical ("it improved handoff quality from X% to Y%"). This supports the Algorithms Before Tokens axiom (MANIFESTO.md §2): encode the evaluation as a measurement protocol, not as a subjective assessment.

**Anti-pattern — Undocumented 1.0 baseline**: Beginning the 2.0 rebuild without first documenting the 1.0 architecture leaves no control condition for the benchmark. The 1.0 baseline must be written as a `docs/research/sources/` D3 note before FrankenBrAIn 2.0's first sprint begins.

**Anti-pattern — Metric collection deferred to retrospective**: Waiting until sprint 5 to think about measurement means data that could have been collected passively (session summaries, Review verdict counts) is unrecoverable. All four metrics must be collected from sprint 1 onward.

**Anti-pattern — Mixing 1.0 and 2.0 tooling**: Running MCP-style ad-hoc prompting alongside the dogma agent fleet in the same codebase contaminates the session coherence signal. FrankenBrAIn 2.0 must commit to the dogma session management pattern from session 1 — no hybrid usage.

---

## 4. Recommendations

1. **Cross-link**: Once a FrankenBrAIn 2.0 tracking issue is created in AccessiTech/FrankenBrAIn, add its URL here and to the dogma `OPEN_RESEARCH.md`.
2. **Document 1.0 architecture first**: Write a pre-dogma baseline description in `docs/research/sources/frankenbrain-1.0-baseline.md` covering session patterns, tooling, and known pain points — before 2.0 begins. This is the control condition for the benchmark.
3. **Begin 2.0 adoption**: Initialize FrankenBrAIn 2.0 using the dogma cookiecutter. Run `scripts/check_divergence.py` at each sprint close to surface HGT-eligible learnings.
4. **Collect metrics from sprint 1**: Do not defer metric collection to the retrospective. Session coherence, handoff quality, and architectural coherence are observable from session 1; token spend requires deliberate annotation from the first sprint.
5. **Retrospective at sprint 5**: At FrankenBrAIn 2.0's fifth sprint close, collect the four benchmark metrics and publish a D4 research synthesis comparing 1.0 vs 2.0. Use this spec doc as the measurement framework.

---

## Sources

- [`AGENTS.md`](../../AGENTS.md) — Guiding constraints; HGT Learning Slot definition; MANIFESTO.md §2 Algorithms Before Tokens axiom (encode evaluation as a measurement protocol)
- [`docs/guides/session-management.md`](../guides/session-management.md) — Session lifecycle and HGT slot procedure
- [`cookiecutter.json`](../../cookiecutter.json) — Dogma cookiecutter template configuration
- [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) — Phase-gate FSM adopted by 2.0
- [`scripts/check_divergence.py`](../../scripts/check_divergence.py) — Template drift detector; run at each sprint close to surface HGT candidates
- [`docs/guides/product-fork-initialization.md`](../guides/product-fork-initialization.md) — Full cookiecutter initialization guide for FrankenBrAIn 2.0 onboarding
- [`MANIFESTO.md §2`](../../MANIFESTO.md) — Algorithms Before Tokens axiom: prefer encoded evaluation protocols over subjective assessment

---

## Open Questions

1. **1.0 token spend estimation**: No machine-readable session logs exist for FrankenBrAIn 1.0. Estimation will require reconstructing from commit message cadence and issue comment density. Precision ± 30% is acceptable for a benchmark comparison.
2. **Benchmark frequency**: Should metrics be collected at every sprint close or only at sprint 5? Recommendation: collect at every sprint for trend data, with sprint 5 as the formal evaluation point.
3. **Generalizability**: Will the benchmark metrics transfer to other dogma-fork adoption experiments beyond FrankenBrAIn? If yes, this spec should be referenced from a more general dogma adoption research note.
4. **Scratchpad availability for 1.0**: FrankenBrAIn 1.0 may not have `.tmp/` scratchpad files. Session coherence for 1.0 is estimated at 0% by assumption (no structured session management existed), unless surviving session artifacts indicate otherwise.
5. **Review gate definition for 1.0**: FrankenBrAIn 1.0 had no formal Review agent or gate step. Handoff quality for 1.0 is estimated at 0% APPROVED rate, establishing a minimum baseline for comparison.
6. **Cookiecutter version pin**: FrankenBrAIn 2.0 should pin to a specific `dogma` commit SHA at initialization to ensure the benchmark comparison reflects a stable template baseline. Note the commit in the workplan.
7. **Metric tooling**: Consider scripting the four metric calculations into a `scripts/collect_benchmark_metrics.py` at sprint 2 — collecting them manually across five sprints risks inconsistency. Flag for the Executive Scripter.
8. **External validity**: The benchmark is designed for a single adoption experiment. A larger study would require at least three independent `dogma`-fork adoptions to produce generalizable conclusions.
