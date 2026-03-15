---
governs: [endogenous-first, algorithms-before-tokens, local-compute-first]
title: "Issue Metrics GitHub Action Evaluation"
status: Final
research_issue: "214"
date: 2026-03-13
---

# Issue Metrics GitHub Action Evaluation

> **Status**: Final
> **Research Question**: Does a scheduled issue-metrics GitHub Action generating
> `docs/issues/metrics.md` add enough value over `scripts/export_project_state.py` for
> the Orchestrator orient-step to justify adoption?
> **Closes**: #214

---

## 1. Executive Summary

**Recommendation: DEFER** dedicated issue-metrics Actions.

`scripts/export_project_state.py` already captures the raw data (open issue counts,
labels, state) needed by the Orchestrator orient-step in a machine-readable JSON snapshot.
A formatted Markdown metrics document adds human-readable display value but does not
materially reduce token cost for machine consumers — the structured JSON is cheaper to
parse than a Markdown table.

Per `MANIFESTO.md §1 — Endogenous-First`, adopt this pattern only when issue volume or
team size makes throughput visualization a meaningful bottleneck. The condition for adoption
is: issue backlog exceeds ~100 open items, or a human-facing health dashboard in the
GitHub UI becomes a team requirement. Neither condition currently applies.

If the condition is met, implement as a thin render script over the existing JSON
snapshot rather than a standalone Action, consistent with `MANIFESTO.md §2 — Algorithms
Before Tokens`.

---

## 2. Hypothesis Validation

### H1 — A scheduled issue-metrics Action reduces Orchestrator orient-step token cost

**Verdict**: WEAKLY CONFIRMED for token reduction; REFUTED as the optimal mechanism.

A pre-built Markdown snapshot at `.github/issues/metrics.md` would allow the Orchestrator
to read a single file instead of running `gh issue list` + `gh label list` + `gh api`
calls. Estimated token savings: 3–5 live API calls avoided per session start, each call
incurring ~100–200 tokens of query + response overhead. Total: ~300–800 tokens per session
start. On a daily cadence (1 session/day), this is ~6,000–16,000 tokens/month.

However, `export_project_state.py` already eliminates these live API calls via the
`snapshot-issues` cron workflow. The JSON snapshot at `.cache/github/project_state.json`
is the canonical source. The incremental token saving from a secondary Markdown render
is near-zero once the JSON snapshot is in place.

### H2 — Marketplace Actions exist that are mature and maintained

**Verdict**: PARTIALLY CONFIRMED — one official candidate is notably strong.

Three candidate Actions were surveyed:

1. **`github/issue-metrics`** (official GitHub Action, previously `nickmcsweeny/issue-metrics`) —
   Generates a Markdown report of issue/PR throughput metrics for a configurable time window.
   Output: a Markdown file with tables of time-to-first-response, time-to-close, and total
   counts. Trigger: cron or `workflow_dispatch`. Maintained by GitHub staff.
   URL: https://github.com/github/issue-metrics

2. **`lowlighter/metrics`** — Comprehensive GitHub profile and repo metrics as SVG/PNG
   charts. Very broad scope (profile cards, activity, languages). Overkill for issue-health
   dashboards. High maintenance burden, large docker image.

3. **`cicirello/issue-completion-stats`** — Lightweight Action tracking the fraction of
   issues closed per week/month. Generates a Markdown summary of completion velocity.
   Maintained but narrowly scoped; does not produce label-distribution or backlog-age data.

`github/issue-metrics` is the strongest candidate if adoption is triggered.

### H3 — A Markdown metrics file is preferable to JSON for Orchestrator orient-step reads

**Verdict**: REFUTED for machine consumers; CONFIRMED for human consumers.

For the Orchestrator reading project state at session start, JSON is strictly superior:
field access, filtering, and aggregation are O(1) with a JSON parse vs. regex extraction
from Markdown tables. The only scenario where Markdown adds value is when a human needs
to read the health dashboard in the GitHub UI without running a local command.

### H4 — `export_project_state.py` JSON already provides the raw metrics data

**Verdict**: CONFIRMED.

The JSON snapshot includes: issue state (open/closed), labels (name, description, count),
title, number, and a `generated_at` timestamp. Derived metrics — open issue count by label,
backlog age, sprint completion velocity — can be computed from this data without an
additional Action. The gap is rendering (human-readable tables), not data collection.

---

## 3. Pattern Catalog

**Canonical example**: `github/issue-metrics` scheduled workflow — if adopted.

When adoption is triggered (backlog > 100 issues or team health dashboard required), the
correct implementation is a `.github/workflows/issue-metrics.yml` using the official
`github/issue-metrics` Action. Configure with a weekly cron trigger
(`0 6 * * 1`), output to `.cache/github/metrics.md` (not `docs/`), and classify the
output as untrusted external content. The Orchestrator reads the cached Markdown at
orient-step if the orient-step template explicitly requests a human-readable summary.
This pattern satisfies `MANIFESTO.md §2 — Algorithms Before Tokens`: the encoding is
deterministic, scheduled, and produces a stable artifact rather than per-session API calls.

**Anti-pattern**: adopting a metrics Action before the JSON snapshot is stale.

Installing `github/issue-metrics` before the `snapshot-issues` / `export_project_state.py`
pipeline is operationally stable creates two competing project-state pipelines with different
schemas, different cron schedules, and different cache invalidation policies. If the JSON
snapshot already satisfies orient-step reads, adding a second Action is premature
optimization. Per `MANIFESTO.md §1 — Endogenous-First`, endogenous solutions (the JSON
pipeline) must be exhausted before adopting external marketplace dependencies. The correct
order is: (1) use JSON snapshot, (2) if rendering gap emerges, add a thin local render
script, (3) only then consider a marketplace Action if the render script proves insufficient.

---

## 4. Recommendations

1. **Defer** all issue-metrics GitHub Actions until one of these conditions is met:
   - Open issue backlog consistently exceeds 100 items; or
   - A human-facing health dashboard in the GitHub UI becomes a documented team requirement.

2. If a Markdown metrics view is needed before adoption conditions are met, implement
   `scripts/render_issue_metrics.py` — a thin script that reads
   `.cache/github/project_state.json` and writes a Markdown table to
   `.cache/github/metrics.md`. Total implementation: ~40 lines. No external dependency.

3. When adoption is triggered, use **`github/issue-metrics`** (official, GitHub-maintained).
   Configure: weekly cron, `output: .cache/github/metrics.md`, scope to open issues only.

4. Classify all Action output as **untrusted external content**. Issue titles, bodies, and
   label names are attacker-controlled. Never write Action output directly to `docs/` without
   a sanitization pass.

5. Document the token savings measurement: after enabling the JSON snapshot cron, instrument
   one session to count actual `gh` API calls during orient-step. This gives a data-driven
   baseline before any further investment in metrics tooling.

6. Per `MANIFESTO.md §3 — Local Compute-First`: prefer `scripts/export_project_state.py`
   at orient-step over any live API call or cloud-only Action output that is not locally
   cached.

---

## 5. Sources

- `scripts/export_project_state.py` — endogenous JSON snapshot implementation
- `github/issue-metrics` — official GitHub Action for issue throughput metrics:
  https://github.com/github/issue-metrics
- `lowlighter/metrics` — broad GitHub metrics Action (surveyed; too broad in scope):
  https://github.com/lowlighter/metrics
- `cicirello/issue-completion-stats` — issue completion velocity Action (surveyed):
  https://github.com/cicirello/issue-completion-stats
- `MANIFESTO.md §1 — Endogenous-First` — governing axiom: local solutions exhausted first
- `MANIFESTO.md §2 — Algorithms Before Tokens` — governing axiom: deterministic encoding preferred
- `MANIFESTO.md §3 — Local Compute-First` — governing axiom: minimize external dependencies
- `AGENTS.md — Security Guardrails` — untrusted content classification rules for fetched data
