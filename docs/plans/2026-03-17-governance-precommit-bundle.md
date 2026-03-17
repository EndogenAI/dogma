---
title: "Governance Pre-commit Bundle — Standalone Installable Package"
status: "Active"
closes_issue: 305
date: 2026-03-17
sprint: 15
related_research:
  - docs/research/mcp-production-pain-points.md
---

## Objective

Expose dogma's governance validators as a standalone `pip`/`uv`-installable package, enabling derived repos (from the cookiecutter template) to install and run the same pre-commit hooks without copying scripts. Initial scope: `validate_synthesis`, `validate_agent_files`, `validate_skill_files`, `validate_adr`, `check_relative_links`, and the `no-heredoc-writes` hook.

## Prerequisites

None — this is standalone work with no blocking dependencies.

## Phases

### Phase 1 — Package Structure

**Agent**: Executive Scripter
**Description**: Migrate governance validators into a proper `src/dogma/` package layout with entry points.

**Tasks**:
- `pyproject.toml` extras: `[project.optional-dependencies] governance = [...]`, `precommit = ["pre-commit>=3.0"]`
- Entry points (`[project.scripts]`): `dogma-validate-synthesis = "dogma.core.validate_synthesis:main"`, etc.
- `src/dogma/` layout: move `validate_synthesis.py`, `validate_agent_files.py`, `validate_skill_files.py`, `validate_adr.py`, `check_relative_links.py` into package
- Keep `scripts/` as thin shims calling package functions (backward compatibility for existing users)
- Test: `uv pip install -e ".[governance]"` in CI matrix; all existing imports still resolve

**Deliverables**:
- D1: `src/dogma/` layout present with all nominated validators
- D2: `scripts/` shims updated and backward-compatible
- D3: `uv pip install -e ".[governance]"` succeeds; existing tests still pass

**Depends on**: nothing
**Gate**: Phase 2 does not start until D3 confirmed and no import regressions in test suite.

---

### Phase 2 — Pre-commit Hook Definitions

**Agent**: Executive Automator
**Description**: Author `.pre-commit-hooks.yaml` so derived repos can reference dogma as a pre-commit repo.

**Tasks**:
- `.pre-commit-hooks.yaml` at repo root: define `id: validate-synthesis`, `id: validate-agent-files`, `id: no-heredoc-writes`, etc.
- `entry:` fields point to installed entry-point scripts from Phase 1
- Test: derived repo installs `- repo: https://github.com/EndogenAI/dogma` in `.pre-commit-config.yaml` and passes `pre-commit run --all-files`

**Deliverables**:
- D1: `.pre-commit-hooks.yaml` committed at repo root with all nominated hook IDs
- D2: Integration test passing for derived-repo hook installation

**Depends on**: Phase 1 (entry points must exist before hooks can reference them)
**Gate**: Phase 3 does not start until derived-repo integration test confirmed passing.

---

### Phase 3 — Cookiecutter Template Integration

**Agent**: Executive Scripter
**Description**: Update the cookiecutter template to consume the published hooks rather than copying scripts.

**Tasks**:
- Update `{{cookiecutter.project_slug}}/pyproject.toml` to include `dogma` dependency with `[governance]` extra
- Update `{{cookiecutter.project_slug}}/.pre-commit-config.yaml` to use published hooks (remove local script paths)
- Verify: `cookiecutter . --no-input` generates a repo that runs `pre-commit install` successfully
- Test: `pytest tests/test_cookiecutter_hooks.py`

**Deliverables**:
- D1: Template `pyproject.toml` and `.pre-commit-config.yaml` updated
- D2: `tests/test_cookiecutter_hooks.py` green

**Depends on**: Phase 2 (hooks must be defined before template references them)
**Gate**: Phase 4 does not start until `tests/test_cookiecutter_hooks.py` passes.

---

### Phase 4 — Release and Documentation

**Agent**: Executive Docs + Release Manager
**Description**: Bump version, update changelog, document the bundle for derived repo users, and coordinate release.

**Tasks**:
- Bump version to `0.9.0` in `pyproject.toml` (minor version — new public API)
- `CHANGELOG.md` entry for bundle under `v0.9.0`
- `docs/guides/governance-bundle-install.md` — installation guide for derived repos
- `docs/guides/release.md` — document PyPI publish workflow before automating it
- Release Manager to tag and publish

**Deliverables**:
- D1: `pyproject.toml` version set to `0.9.0`
- D2: `CHANGELOG.md` entry present
- D3: `docs/guides/governance-bundle-install.md` committed
- D4: `docs/guides/release.md` committed (publish workflow documented)

**Depends on**: Phase 3
**Gate**: All four deliverables confirmed before Release Manager tags.

---

### Phase 5 — Review & Commit

**Agent**: Review → GitHub
**Description**: Validate all changed files; commit and push.

**Deliverables**: All phases committed; PR updated; CI green.
**Depends on**: All prior phases.

## Acceptance Criteria

- [ ] `uv pip install "dogma[governance]"` installs all validator entry points
- [ ] `pre-commit run --all-files` passes on a fresh cookiecutter-generated repo using the published hooks
- [ ] `scripts/` shims work unchanged for existing dogma users (backward compatibility)
- [ ] `docs/guides/governance-bundle-install.md` documents install instructions for derived repos
- [ ] Test coverage ≥ 80% for new package layout; all existing tests still pass
- [ ] `CHANGELOG.md` entry added for `v0.9.0`

## Risks

- Moving scripts to `src/dogma/` requires updating imports in all existing scripts and tests; plan a migration pass before Phase 1 commits.
- Version bump from 0.8.0 to 0.9.0 requires Release Manager coordination.
