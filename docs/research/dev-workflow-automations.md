---
title: "Development Workflow Automations"
research_issue: "#17"
status: Final
date: 2026-03-07
closes_issue: 17
sources:
  - .cache/sources/pre-commit-com.md
  - .cache/sources/docs-astral-sh-uv.md
  - .cache/sources/conventionalcommits-org-en-v1-0-0.md
  - .cache/sources/taskfile-dev.md
  - .cache/sources/github-com-astral-sh-ruff.md
  - .cache/sources/keepachangelog-com-en-1-1-0.md
  - .cache/sources/github-com-googleapis-release-please.md
---

# Development Workflow Automations

> **Status**: Final
> **Research Question**: What are the canonical development workflow automations for a Python-heavy, script-centric agentic OSS repository using `uv`, `pytest`, `ruff`, and GitHub Actions? Where are the current gaps, and what is the minimum stack to close them?
> **Date**: 2026-03-07

---

## 1. Executive Summary

Seven research questions were investigated across pre-commit hooks, CI/CD pipeline patterns, git conventions, file-watcher design, task runners, environment reproducibility, and release automation. The findings draw on both the fetched external sources and endogenous inspection of the existing repository (`pyproject.toml`, `.github/workflows/tests.yml`, `scripts/watch_scratchpad.py`).

The repository has a strong CI foundation — parallel test matrix, ruff + black lint gate, 80% coverage requirement, and a `required` blocking job — but carries three actionable gaps. First, there is no `.pre-commit-config.yaml`, which means all lint feedback arrives via CI round-trips rather than at commit time. Second, the CI coverage check is an anti-pattern that runs pytest twice. Third, despite Conventional Commits being adopted, there is no release automation that consumes them.

The highest-ROI actions in sequence are: (1) add `.pre-commit-config.yaml` with `ruff` + `ruff-format`, closing the local feedback loop in under 15 minutes; (2) consolidate `black` + `ruff` to `ruff format` alone, reducing dependency surface; (3) fix the double-pytest coverage anti-pattern; and (4) stage a `release-please` workflow for when the repo begins versioning artifacts.

---

## 2. Hypothesis Validation

### F1 — No `.pre-commit-config.yaml` is the largest single DX gap

The repo lists `ruff` and `black` in dev dependencies and runs both in CI, but has no `.pre-commit-config.yaml`. This means developers receive lint feedback only after a push to GitHub, introducing a round-trip that violates the local-compute-first principle. Pre-commit hooks are a local, zero-token, deterministic enforcement mechanism — they are the correct locus for style and format checks.

### F2 — The canonical Python/uv pre-commit stack is ruff-only

For a `uv`-managed Python repo in 2026, the optimal hook set is:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-merge-conflict
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

`ruff-format` is a drop-in black replacement. Maintaining both `black` and `ruff` creates two competing formatters with possible style divergence. The current `pyproject.toml` should converge on `ruff-format` alone.

### F3 — Slow hooks belong at pre-push, not pre-commit

Pre-commit supports a `stages` property per hook. The DX cost of a slow `pre-commit` step (e.g., full `pytest` suite or `mypy`) is avoidable: assign it to the `pre-push` stage. The `pre-commit` stage should complete in under 2 seconds; anything longer degrades commit ergonomics and incentivizes `--no-verify`. As a rule: formatters and fast linters at `pre-commit`; type-checkers and test suites at `pre-push` or CI only.

### F4 — CI coverage check has a double-run anti-pattern

The existing `tests.yml` coverage gate runs pytest twice: once to generate `coverage.xml` and once to parse `TOTAL` from stdout. This is fragile (the grep regex is brittle) and doubles compute. The correct solution is to add `--cov-fail-under=80` to `addopts` in `pyproject.toml` — pytest-cov will then enforce the floor in a single pass and produce a non-zero exit code when coverage drops below threshold.

### F5 — The CI job graph is correct; the `required` gate pattern is best practice

The existing `required` job (`needs: [test, lint]`) is the standard GitHub Actions pattern for branch protection. A single status check name (`All tests passed`) on `main` branch protection is easier to maintain than listing individual job names. This pattern is confirmed as canonical and should be preserved.

### F6 — For uv repos, Taskfile.dev is the idiomatic task runner over Makefile

`Makefile` is ubiquitous but carries platform quirks (Windows incompatibility, tab-sensitive syntax, implicit rules clashing with file names). VS Code tasks are non-portable. For a `uv`-managed repo targeting contributors on any OS, `Taskfile.dev` (YAML-based, single binary, cross-platform, smart caching) is the 2026 standard. It integrates directly with `uv run` commands and supports task dependencies. No Makefile or Taskfile currently exists in this repo.

### F7 — uv + uv.lock + .python-version = full reproducibility; system deps remain the gap

`uv.lock` (already committed ✅) guarantees exact package versions across machines. `uv run` resolves the lock before every execution. The only remaining gap is Python version pinning: `.python-version` (produced by `uv python pin 3.11`) is not present. Without it, contributors on different Python minor versions may encounter subtle compatibility differences. System-level C library dependencies are outside uv's scope and require Docker for full parity.

### F8 — release-please is the minimal correct release automation stack when the time comes

`release-please` (GitHub Action) reads Conventional Commit history and automatically maintains a Release PR that accumulates CHANGELOG entries and version bumps. When merged, it tags the commit and creates a GitHub Release. It requires only: Conventional Commits (already adopted ✅) and a single workflow addition. It does not depend on external services. For a documentation-only repo with no PyPI artifact, `release-please` can still generate release notes and tag milestones — the `simple` release type handles non-SemVer projects.

### F9 — Manual CHANGELOG is sustainable only for solo maintainers

Keep a Changelog format (`Added/Changed/Deprecated/Removed/Fixed/Security` under `[Unreleased]`) is human-readable and correct, but manual maintenance is brittle as contributor count grows. The correct trajectory: manual CHANGELOG now → `release-please` automation when the contributor pace exceeds 1–2 PRs/week.

### F10 — File watcher and pre-commit hook are complementary, not competing

`scripts/watch_scratchpad.py` (watchdog-based) reacts to save events continuously, non-blocking. A pre-commit hook reacts at commit time and can block the commit. The decision rule: use a watcher for real-time annotation or transformation that should not interrupt flow; use a hook for quality gates that must not be skippable. The scratchpad watcher is correctly categorized as a watcher. Format enforcement is correctly categorized as a hook.

---

## 3. Pattern Catalog

### R1 — Add `.pre-commit-config.yaml` immediately (Priority: High)

Create `.pre-commit-config.yaml` at repo root with `pre-commit-hooks` basics + `ruff` + `ruff-format`. Run `pre-commit install` in the onboarding docs. Add `pre-commit run --all-files` to the `Taskfile` (see R3). This closes the largest local feedback gap.

### R2 — Remove `black` from dev dependencies; consolidate on `ruff-format` (Priority: High)

`ruff-format` is a black superset. Remove `black` from `pyproject.toml [project.optional-dependencies].dev`. Update the `lint` CI job to run only `uv run ruff check` and `uv run ruff format --check`. This removes one dependency and eliminates the formatter conflict surface.

### R3 — Add `Taskfile.yml` as the project task runner (Priority: Medium)

A minimal `Taskfile.yml` covering:
- `task lint` → `uv run ruff check scripts/ tests/ && uv run ruff format --check scripts/ tests/`
- `task test` → `uv run pytest tests/ --cov=scripts --cov-fail-under=80 -v`
- `task test-fast` → `uv run pytest tests/ -m "not slow and not integration" -v`
- `task watch` → `uv run python scripts/watch_scratchpad.py`
- `task pre-commit` → `pre-commit run --all-files`

This replaces ad-hoc `uv run` invocations in AGENTS.md with a single canonical interface.

### R4 — Fix the double-run coverage anti-pattern in CI (Priority: Medium)

Add `--cov-fail-under=80` to `addopts` in `pyproject.toml`. Remove the second `Check coverage minimum` step in `tests.yml`. The `Run pytest with coverage` step will fail naturally when coverage drops below the floor.

### R5 — Pin Python version with `uv python pin` (Priority: Medium)

Run `uv python pin 3.11` to create `.python-version`. Commit it. This ensures all contributors use the same Python minor version with `uv run`, matching the matrix minimum in CI.

### R6 — Configure `main` branch protection on GitHub (Priority: Medium)

Require:
- Pull request before merge
- Status check: `All tests passed` (the `required` job name)
- Linear history (enable squash-merge only)
- Dismiss stale reviews on new commits

This is the minimum protection that makes the `required` gate pattern meaningful.

### R7 — Stage `release-please` workflow for when versioned releases begin (Priority: Low)

Add `.github/workflows/release-please.yml` with `release-type: simple` (or `python` when a PyPI package is added). The `release-please-action` GitHub Action handles the rest. This transforms the existing Conventional Commits discipline into machine-readable release notes retroactively.

---

## 4. Recommendations for This Repo

> *Actionable recommendations are embedded in §3 Pattern Catalog above. This section surfaces the opinionated synthesis across all findings.*

The five investments with the highest return on developer-time for this specific repo, in priority order:

1. **`.pre-commit-config.yaml`** — closes the local feedback loop; eliminates the most common CI failure class (formatting).
2. **`ruff-format` consolidation** — drop `black`; one formatter, one config, zero divergence surface.
3. **`--cov-fail-under=80` in `addopts`** — makes the coverage floor contractual, not aspirational; removes the fragile grep-based CI step.
4. **`.python-version` pin** — three-line addition that closes the environment parity gap.
5. **Branch protection on `main`** — the `required` job gate exists in CI but is not enforced unless the branch rule is configured on GitHub.

---

## 5. Open Questions

1. **mypy integration**: Should `mypy` be added to the CI lint job and the `pre-push` pre-commit stage? The scripts directory currently has no type annotations; adding mypy before annotations are present will produce noisy output. The question is whether the typing investment is worthwhile for a documentation-forward repo.

2. **Pre-commit in CI**: `pre-commit run --all-files` can be run as a CI step alongside the existing lint job (using `pre-commit/action@v3`). This ensures the local hook config stays in sync with CI. Is the redundancy beneficial or does it slow down the already-parallel CI pipeline?

3. **release-please for docs-only repos**: The `simple` release type treats all commits as patch increments unless `feat:` prefixes trigger minors. Is SemVer-style release tagging meaningful for a documentation-only repository, or should releases be milestone-based (e.g., quarterly)?

4. **uv.lock commit policy**: `uv.lock` is committed ✅, which is correct for applications. For a library being published to PyPI, the convention reverses (lockfile excluded, only `pyproject.toml` constraints committed). The policy should be documented in `CONTRIBUTING.md` before the first release.

5. **Taskfile vs VS Code tasks**: VS Code tasks already exist (Watch Scratchpad). A `Taskfile.yml` would create a second interface for the same operations. The recommended path is to keep VS Code tasks for IDE-specific workflows (running in the integrated terminal, problem matchers) and Taskfile for all general-purpose commands in `AGENTS.md`.

---

## 6. Sources

| Source | Role |
|--------|------|
| [pre-commit.com](https://pre-commit.com/) | Hook system docs, supported stages, canonical hook config |
| [docs.astral.sh/uv](https://docs.astral.sh/uv/) | uv environment model, lockfile semantics, `uv run` |
| [conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/) | Commit spec, SemVer mapping, squash-merge workflow |
| [taskfile.dev](https://taskfile.dev/) | Task runner feature set, cross-platform design |
| [github.com/astral-sh/ruff](https://github.com/astral-sh/ruff) | Ruff formatter (ruff-format) and linter capabilities |
| [keepachangelog.com](https://keepachangelog.com/en/1.1.0/) | CHANGELOG format spec, section conventions |
| [github.com/googleapis/release-please](https://github.com/googleapis/release-please) | Release automation, Release PR lifecycle, Conventional Commits integration |

---

*Endogenous sources inspected: `pyproject.toml`, `.github/workflows/tests.yml`, `.github/pull_request_template.md`, `scripts/watch_scratchpad.py`, `AGENTS.md`, `CONTRIBUTING.md`.*
