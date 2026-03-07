---
title: "OSS Documentation Best Practices"
research_issue: "#18"
status: Final
date: 2026-03-07
closes_issue: 18
sources:
  - .cache/sources/makeareadme-com.md
  - .cache/sources/keepachangelog-com-en-1-1-0.md
  - .cache/sources/writethedocs-org-guide.md
  - .cache/sources/squidfunk-github-io-mkdocs-material.md
  - .cache/sources/docusaurus-io-docs.md
  - .cache/sources/docs-github-com-en-communities-setting-up-your-project-for-h.md
  - .cache/sources/github-com-matiassingers-awesome-readme.md
  - .cache/sources/pdoc-dev.md
---

# OSS Documentation Best Practices

> **Status**: Final
> **Research Question**: What are the canonical OSS documentation best practices in 2026, and how should they be applied to an early-stage Python-first documentation/agent-workflow repository with a `docs/` tree, agent files, and scripts?
> **Date**: 2026-03-07

---

## 1. Executive Summary

Eight sources were surveyed spanning README structure guides, changelog conventions,
technical writing community guidance, two static site generators, GitHub community
documentation policy, a curated README exemplar corpus, and API reference tooling.

This repo has a noticeably strong documentation foundation relative to its stage: a
principled `CONTRIBUTING.md`, a coherent `AGENTS.md`, detailed guides under
`docs/guides/`, and docstrings in every script. The gaps are primarily around
**discoverability** and **enforcement**: no `CHANGELOG.md`, no link checker in CI,
navigation that has grown complex enough to warrant a docsite, and a `README.md` that
lacks key affordances (CI badge, TOC). For an early-stage project the right investment
sequence is: `CHANGELOG.md` first (zero-friction, high user value), README hardening
second, MkDocs Material third (Python-native, flat-Markdown migration is trivial), and
versioned docs deferred until v1.0.

---

## 2. Hypothesis Validation

Seven research questions were submitted as hypotheses to validate against the surveyed
sources. All seven are addressed below.

### H1 — README structure: canonical for a tooling/framework repo in 2026?

**Verdict**: CONFIRMED — current README covers the essentials; three affordances are
missing.

`makeareadme.com` and the `awesome-readme` corpus identify mandatory README sections as:
project name + one-line description, badges (CI status, license), brief "what is this?",
installation/quick-start, usage examples, contributing pointer, and license. For a
**tooling/workflow repo** with no `pip install` step, the structure adapts: installation
becomes "quick start" (how to invoke the agent fleet or scripts), usage becomes "how to
use agents", and a project logo/visual is replaced by an architecture diagram or
directory tree.

The current `README.md` already has the description, core-principles section, quick-start,
and a file-directory table. What it lacks: (1) a CI status badge from GitHub Actions,
(2) a table of contents for the long document body, and (3) a one-sentence "who is this
for" statement above the fold. The awesome-readme exemplars consistently show these three
as the highest-leverage additions for a repository at this stage.

### H2 — CONTRIBUTING.md: what must it cover, and how does ours compare?

**Verdict**: MOSTLY CONFIRMED — our `CONTRIBUTING.md` is unusually thorough; two gaps
remain.

GitHub surfaces `CONTRIBUTING.md` in the repository overview tab, on every issue and PR
creation dialog, and in the sidebar — making it a high-traffic onboarding document. The
Rails and GitHub Docs examples cited in the GitHub contribution guidelines show that
best-practice files cover: development environment setup, branch naming, commit message
conventions, PR/issue creation process, code of conduct link, and test requirements.

Our `CONTRIBUTING.md` covers the branch naming (implicit), commit conventions, PR/issue
process, and test requirements well. The two gaps are: (1) a step-by-step development
environment setup section (`git clone` → `uv sync` → `uv run pytest`), and (2) explicit
mention of issue/PR templates, which do not yet exist.

### H3 — CHANGELOG conventions: what is right for an early-stage project?

**Verdict**: CONFIRMED — keepachangelog.com format is correct; we need a `CHANGELOG.md`
now.

Keep a Changelog is explicit: "Changelogs are for humans, not machines." It specifies
curated, reverse-chronological entries per version typed into `Added / Changed /
Deprecated / Removed / Fixed / Security` buckets, with ISO 8601 dates and an
`[Unreleased]` section at the top. A raw git log dump is explicitly an anti-pattern: "the
purpose of a commit is to document a step in the evolution of the source code; the purpose
of a changelog entry is to document the noteworthy difference, often across multiple
commits, to communicate them clearly to end users."

For a pre-release project: create `CHANGELOG.md` with only an `[Unreleased]` section.
This signals intent, orients contributors, and costs nothing. When v1.0 ships, move the
unreleased block into the first versioned entry. The `dev-workflow-automations` research
(issue #17) already identifies `release-please` as the automation layer for when
versioning begins — that decision and this one compose cleanly.

### H4 — Docsite tooling: when does it become worth it, and which tool?

**Verdict**: CONFIRMED with qualification — the threshold has been crossed; MkDocs
Material is the correct choice.

Write the Docs identifies the docsite threshold as "when readers need to navigate between
documents as part of normal use." This repo has 20+ Markdown files across `docs/`
subdirectories: `guides/`, `research/`, `plans/`, `sessions/`. GitHub's flat file viewer
is no longer a sufficient navigation surface. The threshold has been crossed.

**MkDocs Material vs. Docusaurus**: Docusaurus's own documentation compares: "MkDocs is
a good option if you don't need a single-page application and don't plan to leverage
React." For a Python-first, Markdown-only content repo, MkDocs Material is the clear
choice — Python toolchain, `mkdocs.yml` configuration, no Node.js, zero content
rewriting required. FastAPI and SQLModel — both documentation-quality benchmarks — use
Material for MkDocs. Migration path: add `mkdocs.yml` (10 minutes), `mkdocs serve` to
verify, add `mkdocs build --strict` CI step. The existing `docs/` tree migrates without
any content changes.

### H5 — Reference docs for script-centric repos: what does good look like?

**Verdict**: CONFIRMED — the current `scripts/README.md` catalog is the right approach;
`pdoc` adds marginal value here.

pdoc auto-generates API documentation from Python module hierarchies and docstrings.
It targets importable libraries with public APIs. For a scripts-only repo (`scripts/`
contains executable scripts, not an importable package), pdoc's output would be a flat
page of function signatures — useful only if scripts are invoked programmatically by
external tools. They are not.

The existing `scripts/README.md` catalog — with per-script purpose, usage, and exit
code documentation — is the human-readable reference contributors actually need. The
Documentation-First principle already enforces docstrings on all scripts, meaning the
information exists; the catalog is the correct rendering mechanism. The one gap: add a
header summary table to `scripts/README.md` linking script name → brief purpose → link
to the full entry, mirroring the directory table in `README.md`.

### H6 — Documentation-as-code: how to validate docs stay in sync?

**Verdict**: CONFIRMED — link checking and a docsite build gate are the two highest-value
CI additions; the existing `validate_synthesis.py` should also run in CI.

Write the Docs categorizes docs-as-code as applying software engineering workflows to
documentation: version control, review, CI builds, and automated validation. Concrete
tools for this repo: (1) `lychee` or `markdown-link-check` as a GitHub Actions step
catches dead internal links before merge — the current `docs/` and `scripts/README.md`
files are link-heavy; (2) `mkdocs build --strict` as a CI gate once the docsite is added
(strict mode fails on any broken link or missing nav reference); (3) the existing
`validate_synthesis.py` is already a docs-as-code quality gate but only runs manually —
it should run in CI on every PR touching `docs/research/`.

### H7 — Versioning docs: is it worth it before v1.0?

**Verdict**: CONFIRMED — defer versioned docs until after the first tagged release.

The overhead of versioned documentation sites — separate build directories per version,
a version-switcher UI widget, maintaining parallel doc trees — is substantial for a small
team. Until a `v1.0.0` tag is applied, a single `main`-branch docsite is sufficient and
"latest" implicitly means current. Versioned docs via `mike` (MkDocs) or Docusaurus's
built-in versioning should be staged only after the first release, when a prior version
worth preserving actually exists.

---

## 3. Pattern Catalog

Seven patterns distilled from the surveyed sources, ordered by applicability to this repo.

### P1 — CHANGELOG-First Commit

Create `CHANGELOG.md` at repo root before first external announcement. Open with only
`## [Unreleased]`. Keeps contributors oriented without requiring a release. Source:
keepachangelog.com.

### P2 — README Layering: Scope → Start → Use → Contribute

Structure README as a progressive funnel: one-line project scope (above the fold) →
prerequisite context → quick-start → usage examples → contributing pointer. Separate
philosophy sections from operational instructions — MANIFESTO.md exists for the former.
Source: makeareadme.com, awesome-readme corpus.

### P3 — Python-Native Docsite (MkDocs Material)

For Python-first projects, MkDocs Material is the canonical docsite: zero JS,
Markdown-native, `uv add mkdocs-material --dev` installable, no framework churn. Flat
`docs/` Markdown migrations require only an `mkdocs.yml` nav config. Trusted by FastAPI,
SQLModel, and 50,000+ projects. Source: squidfunk.github.io/mkdocs-material.

### P4 — Docs-as-Code Gate: `--strict` Build in CI

Once a docsite build exists, add `mkdocs build --strict` to CI. This catches all broken
internal links, missing pages, and invalid nav entries before merge. Analogous to
`mypy --strict` for documentation. Source: Write the Docs docs-as-code guidance.

### P5 — Script Reference = Catalog + Docstring, Not Auto-Generator

For script-only repos, the correct reference documentation is a human-authored catalog
that links to in-file docstrings. Auto-generators (pdoc, mkdocstrings) are valuable for
importable libraries; they add process overhead without user value for scripts. Source:
pdoc.dev, endogenous inspection of `scripts/README.md`.

### P6 — CONTRIBUTING.md = Onboarding + Norms (Not Just Process)

CONTRIBUTING.md is the most-visible community health file on GitHub. It should cover
development environment setup — not just branch/commit conventions — because it is shown
on every issue and PR creation dialog. A missing setup section is the single highest
contributor-friction gap before good code conventions. Source: docs.github.com.

### P7 — One High-Signal Badge, Not Many

The CI status badge from GitHub Actions has clear signal value: it tells contributors
whether tests pass before they begin work. Coverage and license badges are informational.
Decorative badges (star count, activity) should be deferred. One badge, well-placed,
is more honest than a badge wall. Source: awesome-readme corpus.

---

## 4. Recommendations for This Repo

Actions ordered by impact/effort ratio. All are directly applicable to the current
`docs/` structure and repo state.

**R1 — Add `CHANGELOG.md` (immediate, 10 minutes)**
Create `CHANGELOG.md` at the repo root with `## [Unreleased]` and the keepachangelog
header comment. Commit as `docs: add CHANGELOG.md`. No tooling required. Stage
`release-please` (from the dev-workflow-automations plan) as the future automation layer.

**R2 — Add CI badge + TOC to `README.md` (immediate, 20 minutes)**
Add the GitHub Actions CI status badge (`![CI](https://github.com/.../.../actions/...`)
below the repo title. Add a `## Contents` section with anchor links to the major
sections. These are the two highest-signal affordances missing from the current README.

**R3 — Add development environment setup to `CONTRIBUTING.md` (immediate, 15 minutes)**
Add a "Development Setup" section: `git clone` → `uv sync` → `source .venv/bin/activate`
→ `uv run pytest` to verify. This closes the highest contributor-friction gap in the
current `CONTRIBUTING.md`. Reference the `uv run` convention from `AGENTS.md`.

**R4 — Add MkDocs Material docsite (near-term, 1–2 hours)**
Add `mkdocs-material` to dev dependencies. Create `mkdocs.yml` with a nav config mapping
the existing `docs/` tree. Add `mkdocs build --strict` as a CI step. No content migration
required — all docs are already Markdown. Deploy to GitHub Pages on the `gh-pages` branch.

**R5 — Add link checker to CI (near-term, 30 minutes)**
Add `lychee` (fast Rust-based link checker) as a GitHub Actions step to catch dead
internal links before merge. Target `docs/**/*.md` and `README.md`. The link density
in the current docs tree makes this a high-value, low-effort addition.

**R6 — Run `validate_synthesis.py` in CI (near-term, 15 minutes)**
Add a GitHub Actions step that runs `python scripts/validate_synthesis.py` against all
files matching `docs/research/*.md` on every PR touching `docs/research/`. This encodes
the Documentation-First principle as a machine-enforced gate rather than a guideline.

---

## 5. Open Questions

1. **Docsite hosting domain**: Should the MkDocs site be published to GitHub Pages on
   a `gh-pages` branch, or will the project eventually have a custom domain? GitHub Pages
   is zero-infrastructure for now; the domain question belongs in the roadmap.

2. **CHANGELOG automation scope**: Should `release-please` manage the CHANGELOG
   automatically from Conventional Commits, or should it be hand-curated per
   keepachangelog.com guidance? The tradeoff is automation fidelity vs. human narrative
   quality. A hybrid is possible: auto-generate a draft, then edit before release.

3. **Architecture diagram in README**: Several `awesome-readme` exemplars use a Mermaid
   diagram as the key visual element. For this repo, a diagram showing the agent fleet
   delegation topology would serve this role. Is it worth adding now, or after the fleet
   stabilises post-research-sprint?

4. **`scripts/README.md` header table autogeneration**: The P5 recommendation proposes
   a summary table in `scripts/README.md`. Should this be autogenerated from script
   docstrings (programmatic-first), or hand-authored? Given the programmatic-first
   principle, a generator script (`scripts/generate_script_catalog.py`) is the right
   answer once the format is settled.

5. **Issue and PR templates**: `CONTRIBUTING.md` implies templates exist, but none are
   present in `.github/`. Bug report and feature request issue templates, plus a PR
   checklist template, would close the contributor-friction gap for external
   contributors and are GitHub-surfaced prominently alongside `CONTRIBUTING.md`.

---

## 6. Sources

- `.cache/sources/makeareadme-com.md` — Make a README guide (makeareadme.com)
- `.cache/sources/keepachangelog-com-en-1-1-0.md` — Keep a Changelog v1.1.0 (keepachangelog.com)
- `.cache/sources/writethedocs-org-guide.md` — Software Documentation Guide (writethedocs.org)
- `.cache/sources/squidfunk-github-io-mkdocs-material.md` — Material for MkDocs (squidfunk.github.io)
- `.cache/sources/docusaurus-io-docs.md` — Docusaurus documentation (docusaurus.io)
- `.cache/sources/docs-github-com-en-communities-setting-up-your-project-for-h.md` — Setting guidelines for repository contributors (docs.github.com)
- `.cache/sources/github-com-matiassingers-awesome-readme.md` — Awesome README (github.com/matiassingers)
- `.cache/sources/pdoc-dev.md` — pdoc auto-generates API documentation (pdoc.dev)
