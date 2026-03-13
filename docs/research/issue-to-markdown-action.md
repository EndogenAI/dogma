---
governs: [endogenous-first, algorithms-before-tokens, local-compute-first]
title: "Issue-to-Markdown GitHub Action Evaluation"
status: Final
research_issue: "213"
date: 2026-03-13
---

# Issue-to-Markdown GitHub Action Evaluation

> **Status**: Final
> **Research Question**: Do dedicated GitHub Actions for exporting issues to Markdown add
> enough value over the existing `scripts/export_project_state.py` to justify adoption?
> **Closes**: #213

---

## 1. Executive Summary

**Recommendation: REJECT** dedicated issue-to-markdown Actions.

`scripts/export_project_state.py` already implements the orient-step use case: it queries
`gh issue list` and `gh label list` and writes a structured JSON snapshot to
`.cache/github/project_state.json`. The Orchestrator can read this file at session start
to avoid live API calls. A dedicated Markdown-export Action adds no endogenous advantage —
it duplicates logic already encoded locally and introduces an external dependency with
supply-chain risk.

Per `MANIFESTO.md §1 — Endogenous-First`, endogenous solutions must be exhausted before
reaching outward. The endogenous substitute is unambiguously sufficient: `export_project_state.py`
covers issue state, labels, and metadata in a machine-readable format. If human-readable
Markdown is needed (e.g., for Orchestrator diffs), a thin render pass over the existing
JSON is the correct extension — not a new Action.

Security note: issue bodies contain attacker-controlled text. Any file derived from issue
export must be treated as untrusted external content and stored in `.cache/`, not `docs/`.

---

## 2. Hypothesis Validation

### H1 — A dedicated issue-to-markdown Action fits the orient-step use case

**Verdict**: PARTIALLY CONFIRMED, but superseded by endogenous implementation.

The orient-step requires the Orchestrator to read open sprint issues and labels at session
start without incurring live `gh` API call overhead. A scheduled Action could pre-build
a Markdown snapshot for this purpose. However, `export_project_state.py` already satisfies
this requirement in JSON form, produced by a cron workflow (`snapshot-issues`). The JSON
is structured, queryable, and smaller than fragmented per-issue Markdown files. Adopting
a separate Markdown Action would create a parallel output pipeline instead of extending
the existing one.

### H2 — Marketplace Actions exist that are mature and maintained

**Verdict**: PARTIALLY CONFIRMED, with caveats.

Three candidate Actions were surveyed:

1. **`nichmor/git-issues-to-markdown`** — Exports open issues to one `.md` file per issue
   under a configurable output directory. Uses GitHub API via `GITHUB_TOKEN`. Trigger: push
   or scheduled. Output: per-issue files with frontmatter and body verbatim.
   Risk: low star count, no recent commits as of 2026-Q1.

2. **`actions/github-script`** — General-purpose scripting Action. Can be used to implement
   a fully custom issue-to-markdown exporter in 20–30 lines of JavaScript. Mature,
   officially maintained by GitHub. Trigger: any event. Output: arbitrary. This is the option
   that would work, but it is DIY — it does not provide a ready-made exporter.

3. **`peter-evans/create-or-update-comment`** — Adjacent: writes Markdown content back to
   issue comment threads. Not an exporter. Included for completeness and eliminated.

No marketplace Action provides a drop-in scheduled exporter that is both mature and
produces output compatible with this project's `.cache/` conventions.

### H3 — Markdown output is preferable to JSON for Orchestrator consumption

**Verdict**: REFUTED for machine consumption, inconclusive for human reading.

The Orchestrator reads project state programmatically (via `scripts/query_docs.py` or
direct JSON parse). Structured JSON is unambiguously more useful for this purpose —
field access, filtering, and counting are trivial. Markdown requires regex parsing or an
LLM pass to extract counts and labels, which costs tokens rather than saving them.

The only scenario where Markdown adds value is human-facing display (e.g., a `docs/issues/`
index reviewable in GitHub UI). That use case is distinct from the orient-step and warrants
separate evaluation.

---

## 3. Pattern Catalog

**Canonical example**: `export_project_state.py` — the endogenous orient-step implementation.

A scheduled CI workflow (`snapshot-issues`) runs `uv run python scripts/export_project_state.py`
on a cron schedule. The Orchestrator's orient step reads `.cache/github/project_state.json`
at session start. Zero additional Actions, zero additional API credentials, zero external
dependencies. The script is tested (`tests/test_export_project_state.py`), documented,
and under local version control. This is the correct pattern per `MANIFESTO.md §2 —
Algorithms Before Tokens`: the encoding is deterministic and lives in the repository, not
in an external marketplace component.

**Anti-pattern**: parallel pipeline proliferation.

Adding a dedicated issue-to-markdown Action alongside `export_project_state.py` creates
two parallel pipelines that must stay in sync. If the JSON schema changes (e.g., a new
field is added to the `issues` array), the Markdown export Action would not automatically
reflect that change. The orchestration burden (two cron schedules, two output paths, two
security classifications) outweighs any human-readability gain. Per `MANIFESTO.md §3 —
Local Compute-First`, the local script wins on every axis: no network dependency at
execution time, no version pinning risk, no supply-chain surface.

---

## 4. Recommendations

1. **Reject** any dedicated issue-to-markdown marketplace Action for the orient-step use
   case. The endogenous substitute (MANIFESTO.md §1) is complete and tested.

2. If a human-readable Markdown view of open issues is needed (e.g., for `docs/issues/`),
   implement it as a `render_project_state_md.py` script that reads
   `.cache/github/project_state.json` and writes a Markdown summary. This is a 30-line
   extension of the existing pattern — not a new Action.

3. Classify any file derived from issue export (JSON or Markdown) as **untrusted external
   content**. Issue bodies are attacker-controlled. Store outputs under `.cache/github/`
   or a clearly untrusted path; never under `docs/` without explicit sanitization.

4. If the `snapshot-issues` cron interval is too coarse for session freshness needs, reduce
   the cron frequency or add a manual `workflow_dispatch` trigger to the existing workflow.

5. Revisit adoption **only if**: a future requirement explicitly needs Markdown-rendered
   issue bodies (not just metadata) for a use case that cannot be satisfied by the JSON
   snapshot.

---

## 5. Sources

- `scripts/export_project_state.py` — endogenous JSON export implementation
- `tests/test_export_project_state.py` — test suite confirming behavior
- GitHub Marketplace — `nichmor/git-issues-to-markdown` (surveyed; low maintenance signal)
- GitHub Docs — `actions/github-script` action: https://github.com/actions/github-script
- `MANIFESTO.md §1 — Endogenous-First` — governing axiom for preferring local implementations
- `MANIFESTO.md §2 — Algorithms Before Tokens` — governing axiom for deterministic encoding
- `MANIFESTO.md §3 — Local Compute-First` — governing axiom for local execution preference
- `AGENTS.md — Security Guardrails` — untrusted content classification rules
