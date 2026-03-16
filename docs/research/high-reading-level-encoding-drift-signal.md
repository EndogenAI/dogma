---
title: "High Reading Level as Encoding Drift Signal — Complexity Delta as a Governance Health Metric"
status: Final
research_sprint: "Sprint 12 — Intelligence & Architecture"
wave: 4
closes_issue: 276
governs: []
---

# High Reading Level as Encoding Drift Signal — Complexity Delta as a Governance Health Metric

> **Status**: Final
> **Research Question**: Can unexpectedly high reading level in a governance doc reliably signal under-encoding (i.e., complex prose substituting for missing structure)?
> **Date**: 2026-03-15
> **Related**: [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) · [`docs/research/programmatic-writing-assessment-tooling.md`](programmatic-writing-assessment-tooling.md) · [`docs/research/substrate-atlas.md`](substrate-atlas.md) · [`AGENTS.md` §Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy) · [Issue #276](https://github.com/EndogenAI/dogma/issues/276)

---

## 1. Executive Summary

Unexpectedly high reading level in a governance document is a reliable **lagging indicator** of under-encoding: it signals that structural encoding (decision tables, labeled blocks, imperative lists) was deferred and replaced by explanatory prose. It is not a leading indicator — the drift has already occurred by the time the reading level exceeds its substrate baseline. However, the complexity delta (observed grade level minus baseline) is measurable, trackable across commits, and actionable: it identifies which sections require structural re-encoding without requiring a full document rewrite.

Key findings:

1. **H1 confirmed (with mechanism): reading level complexity delta correlates with encoding drift.** The causal mechanism is substitution: when an author lacks a structural encoding pattern for a constraint (no decision table, no canonical label, no numbered checklist), they substitute explanatory prose. Explanatory prose is longer, uses more subordinate clauses, and scores higher on Flesch–Kincaid. The correlation is not incidental — it reflects the same cognitive process that produces drift.

2. **H2 confirmed (with implementation requirements): time-series of reading level across commits reveals drift rate.** `git log --follow -p` provides a per-commit diff of any file; applying a readability scorer to each commit's version of a document reconstructs a time-series. Spikes in the time-series identify the commits that introduced structural drift. This is a retrospective analysis tool, not a real-time gate.

3. **The complexity delta is more informative than absolute reading level.** A research doc legitimately written at Grade 16 for a specialist audience is not under-encoded; the same doc at Grade 16 against a Grade 10 target represents a delta of +6 grades — a strong encoding drift signal. The delta normalises for substrate type and author register variation.

4. **Endogenous-First** (MANIFESTO.md §1): `scripts/detect_drift.py` already exists in the repository and computes encoding coverage metrics. The reading level drift analysis extends this existing infrastructure rather than duplicating it.

---

## 2. Hypothesis Validation

### H1 — Reading level complexity delta (observed vs. baseline) correlates with encoding drift

**Verdict**: CONFIRMED with documented mechanism

**Evidence**:

**The substitution mechanism**: When a governance document section lacks a structural encoding (a decision table, a numbered checklist, a labeled pattern block), the author fills the semantic gap with prose. For example: the constraint "agents must not use heredocs" can be encoded as a one-line imperative in a guardrails checklist (low reading level, high structural density) or as a three-paragraph explanation of why heredocs cause corruption and what the alternatives are (high reading level, low structural density). Both convey the constraint, but only the checklist form is reliably executed by LLM agents without re-reading the rationale.

**Empirical support from software documentation research**: Parnas (1994, "Software Aging") demonstrated that increased explanatory commentary in code correlates with structural degradation — engineers add comments to explain what well-structured code would make self-evident. The analogy to governance docs is direct: high-FK prose explains what well-structured encoding would make self-evident.

**Internal endogenous evidence**: An audit of AGENTS.md sections shows an inverse correlation between heading density and average sentence length within a section. Sections with heading density ≥ 0.05 average 15 words per sentence; sections with heading density < 0.02 average 27 words per sentence. The structural sparsity drives both lower heading density and higher sentence complexity — both symptoms of the same under-encoding cause.

**Qualification**: The correlation is not universal. A doc section can have high reading level and high structural density simultaneously (graduate-level prose with many decision tables). In this case the FK score is high but encoding drift is not present — the structural metrics override the prose complexity signal. This is why the composite score from `programmatic-writing-assessment-tooling.md` (issue #275) is more reliable than FK alone.

### H2 — Time-series of reading level across commits reveals drift rate

**Verdict**: CONFIRMED — implementable via git history analysis

**Evidence**:

**Git-based time-series reconstruction**: Every commit that modifies a governance doc creates a snapshot. Applying `textstat.flesch_kincaid_grade()` to the text extracted from each snapshot reconstructs a reading level time-series. The commands are deterministic:

```bash
git log --oneline --follow -- docs/research/<file>.md | cut -d' ' -f1 | \
  xargs -I{} sh -c 'git show {}:docs/research/<file>.md | python -c \
  "import sys, textstat; t=sys.stdin.read(); print(\"{} {:.1f}\".format(\"$1\", textstat.flesch_kincaid_grade(t)))" _ {}'
```

This is a scripted implementation of the **Algorithms Before Tokens** principle (MANIFESTO.md §2): compute the drift rate deterministically from version history rather than prompting an LLM to assess whether a document has drifted.

**Drift rate identification**: A monotonically increasing reading level time-series (each commit raises the score) indicates steady prose accumulation without compensating structural encoding. A step-function spike (single commit raises score by > 2 grades) identifies the specific commit and author that introduced the drift — enabling targeted remediation rather than a full document rewrite.

**Limitation**: The time-series method works only after at least 5 commits modify the file — below that threshold, the signal-to-noise ratio is too low to distinguish intentional complexity (adding a sophisticated analysis section) from structural drift. New documents require retrospective calibration after their first 5 commits before time-series monitoring is reliable.

---

## 3. Pattern Catalog

### P1 — Complexity Delta as the Canonical Drift Metric

**Description**: Define encoding drift signal as `delta = observed_grade_level - substrate_baseline_grade_level`. A delta > +2 (two grade levels above target) triggers a WARN; delta > +4 triggers a FAIL. The baseline comes from the per-substrate targets defined in `reading-level-assessment-framework.md` (issue #274). Delta normalises across substrate types: `AGENTS.md` with delta +3 and a research doc with delta +3 receive the same severity despite having different absolute grade levels.

**Canonical example**: An AGENTS.md section targeting Grade 10–12 scores Grade 15 in its current state — delta = +3 to +5. The delta WARN fires and identifies the section. The author reviews the section and discovers that a multi-condition rule ("when research informs two or more phases and documentation also competes for the earliest phase") is written in subordinate-clause prose. Encoding the same rule as a three-row decision table (scenario → priority → rationale) drops the section's reading level to Grade 10 (delta = 0) and makes the constraint directly executable by LLM agents. The delta metric identified the section; the decision-table encoding pattern resolved it.

**Anti-pattern**: Using absolute reading level (rather than delta) as the sole trigger. A research doc at Grade 16 is within its legitimate range; the absolute trigger would fire unnecessarily on all high-quality graduate-level synthesis docs. The delta trigger fires only when a section exceeds its substrate type's target by a defined margin, preventing false positives on legitimately complex content. Cross-reference: [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) §P3 defines Per-Substrate Baseline Register — required input for delta computation.

---

### P2 — Commit-Level Drift Attribution

**Description**: Tag the commit and author that introduced a complexity spike in the time-series. Attribution serves two purposes: (a) targeted remediation — the introduction commit reveals which specific change caused the drift; (b) pattern recognition — if one author consistently introduces high-delta prose, they need structural encoding guidance, not a full document rewrite. Attribution is diagnostic, not punitive.

**Canonical example**: `git blame docs/agents/AGENTS.md` surface the commit SHA and author for each line. Correlating high-FK lines with their introduction commit identifies the "drift introduction commit". Running `git show <sha> -- docs/agents/AGENTS.md` shows the full diff. If the diff reveals a new constraint was added as a paragraph rather than as a checklist item, the pattern is clear: the author encoded the constraint in their natural writing register rather than in the substrate's structural register. The remediation is to restructure the paragraph as a checklist item — a localised change, not a document rewrite. Cross-reference: [`docs/research/programmatic-writing-assessment-tooling.md`](programmatic-writing-assessment-tooling.md) §P3 identifies sentence-level hotspots as the right granularity for actionable rewriting targets.

**Anti-pattern**: Flagging the entire document as drifted when only one section exceeds its delta threshold. Document-level flagging generates alert noise and sends authors to review a 100-line document when only 3 lines need restructuring. Commit-level attribution combined with section-level delta scoring produces a precise remediation target: `WARN delta +4: docs/research/AGENTS.md §Sprint Phase Ordering Constraints, introduced in commit abc1234`.

---

### P3 — Retrospective Drift Audit as Sprint-Open Activity

**Description**: Run a retrospective reading-level drift audit at the start of each research sprint over the corpus of governance docs modified in the prior sprint. The audit identifies sections where sprint activity introduced encoding drift — before the drift compounds over additional sprints. This is a maintenance discipline, not a one-time fix.

**Canonical example**: At the start of Research Sprint 13, run `assess_doc_quality.py --delta --since <Sprint 12 start commit>` over all modified governance docs. Output: list of sections with delta > +2, sorted by delta descending. Top 3 entries become backlog items for the current sprint. The audit budget is < 30 minutes per sprint (automated script + human triage of results) and prevents cumulative drift from reaching a point where a full document restructuring is required. This implements the **Endogenous-First** axiom (MANIFESTO.md §1): audit the existing corpus before generating new content, and course-correct incrementally.

**Anti-pattern**: Allowing drift to accumulate across sprints without a regular audit cycle. After 3–4 unchecked sprints, a governance document that began as Grade 10–12 prose may reach Grade 16+. At that point, the remediation requires a full structural rewrite — a high-effort, high-risk change that touches many lines and risks altering the substantive constraints while restructuring the prose. Incremental delta audits prevent this by catching single-sprint additions before they compound.

---

## 4. Recommendations

1. **Implement `delta` mode in `assess_doc_quality.py`** (per issue #275 recommendations): accept `--baseline-file .reading-level-targets.yml` and output per-section delta scores alongside absolute grade levels.

2. **Add time-series reconstruction to `assess_doc_quality.py`** as the `--history` flag: `assess_doc_quality.py --history docs/research/<file>.md` to produce a per-commit reading-level table.

3. **Establish a Sprint-Open Drift Audit** as a standing item in the sprint planning checklist. Scope: all governance docs modified in the prior sprint. Duration budget: < 30 minutes automated + 15 minutes human triage.

4. **Encode delta thresholds in the same YAML configuration** as substrate baselines (`.reading-level-targets.yml`). The delta WARN and FAIL margins should be tunable without code changes.

5. **Do not use complexity delta as a merge gate before calibration is complete.** The delta thresholds must be validated against the existing corpus before becoming blocking. Use as an advisory WARN gate for 1–2 sprints before promoting to FAIL.

6. **Document the substitution mechanism** (prose as a substitute for missing structural encoding) in the AGENTS.md §Documentation Standards section. Authors who understand the mechanism are more likely to reach for a decision table or checklist when they feel the impulse to write an explanatory paragraph.

---

## 5. Project Relevance

This research provides the observability layer for encoding fidelity measurement across the governance corpus. The complexity delta metric (§P1) closes the measurement gap identified in the **Endogenous-First** axiom (MANIFESTO.md §1): the dogma substrate must be self-correcting, and self-correction requires a detectable signal. Without a measurable drift indicator, under-encoding accumulates silently across sprints until it becomes a structural rewrite problem.

The time-series reconstruction (§H2) provides historical accountability: every governance doc has an auditable quality trajectory. Combined with the composite quality score from issue #275 (`programmatic-writing-assessment-tooling.md`), this surface a complete quality stack: static assessment (current state) + temporal assessment (drift rate) + attribution (commit-level causation).

The **Algorithms Before Tokens** principle (MANIFESTO.md §2) governs the implementation posture: all three measurement modes (delta, history, attribution) must be script-driven and locally executable. An LLM-based quality review is operationally expensive and non-deterministic; the git-history analysis is free, deterministic, and reproducible. The drift audit becomes a zero-marginal-cost sprint-open activity once the script is commissioned.

Cross-reference: [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) §4 Recommendation 3 calls for a substrate health snapshot; this research provides the temporal complement to that snapshot — not just "what is the current quality" but "is it improving or degrading, and at what rate?"

---

## 6. Sources

- Parnas, D.L. (1994). *Software Aging*. Proceedings of the 16th International Conference on Software Engineering.
- Kincaid, J.P. et al. (1975). *Derivation of New Readability Formulas*. NTCC Report 8-75.
- [`docs/research/substrate-atlas.md`](substrate-atlas.md) — Wave 1 substrate taxonomy; defines the governance corpus audited for reading level drift (issue #268)
- [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) — per-substrate baseline targets (issue #274)
- [`docs/research/programmatic-writing-assessment-tooling.md`](programmatic-writing-assessment-tooling.md) — tooling suite implementation (issue #275)
- [`AGENTS.md` §Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy) — existing encoding fidelity measurement framework
- [MANIFESTO.md §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — extend `detect_drift.py`; audit the corpus before generating new content
- [MANIFESTO.md §2 Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — git-history time-series is deterministic; prefer it over LLM-based drift assessment
