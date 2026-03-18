---
name: conventional-commit
description: |
  Enforces Conventional Commits format for the EndogenAI Workflows repository. USE FOR: composing commit messages (type(scope): description format); reviewing commit message format before push; understanding allowed types (feat/fix/docs/chore/test/refactor/ci/perf) and scopes (scripts/agents/docs/tests/ci/deps/research). DO NOT USE FOR: release versioning decisions (use the Release Manager agent); PR template authoring.
argument-hint: "type(scope): what changed"
---

# Conventional Commit

This skill enacts the *Algorithms Before Tokens* axiom from [`MANIFESTO.md`](../../../MANIFESTO.md) by encoding commit message conventions as a reusable procedure, eliminating per-session re-prompting overhead. Commit discipline is governed by [`AGENTS.md`](../../../AGENTS.md) § Commit Discipline and [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) § Commit Discipline. When this skill and those documents conflict, the primary documents take precedence.

---

## 1. Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Rules for the first line:**
- Imperative mood: "add", "fix", "update" — not "adds", "fixed", "updating"
- Lowercase throughout (type, scope, description)
- No period at the end of the description
- Maximum 72 characters for the first line
- Scope is in parentheses, not brackets

**Valid**: `docs(guides): add session-management skill reference`
**Invalid**: `Updated the docs.` / `DOCS: Updates guides` / `docs(guides): Added session-management skill reference.`

---

## 2. Types

| Type | When to use | Example for this repo |
|------|-------------|----------------------|
| `feat` | New capability, new agent, new script | `feat(agents): add executive-docs agent` |
| `fix` | Correction to existing content or code | `fix(scripts): handle missing .tmp dir in prune_scratchpad` |
| `docs` | Documentation only — no code or script change | `docs(guides): clarify encoding checkpoint format` |
| `chore` | Tooling, scripts, templates, config — no production logic | `chore(scripts): add scaffold_workplan.py for plan generation` |
| `test` | New or updated tests | `test(scripts): add coverage for validate_synthesis error cases` |
| `refactor` | Restructuring without content or behaviour change | `refactor(agents): extract session-mgmt handoff to skill` |
| `ci` | CI configuration, workflow files, pre-commit hooks | `ci: add validate_skill_files check to lint job` |
| `perf` | Performance improvement | `perf(scripts): cache URL validation results in fetch_source` |

**Do not use `feat` for documentation.** A new research doc is `docs(research)`, not `feat(research)`. A new guide is `docs(guides)`.

---

## 3. Scopes

Scopes are lowercase, single-word identifiers describing the affected area of the codebase:

| Scope | Covers |
|-------|--------|
| `scripts` | Files in `scripts/` |
| `agents` | Files in `.github/agents/` |
| `skills` | Files in `.github/skills/` |
| `docs` | Files in `docs/` (guides, research, plans, decisions) |
| `tests` | Files in `tests/` |
| `ci` | Files in `.github/workflows/`, `.pre-commit-config.yaml` |
| `deps` | `pyproject.toml`, `uv.lock`, dependency changes |
| `research` | Research synthesis docs in `docs/research/` |
| `plans` | Workplan docs in `docs/plans/` |
| `manifesto` | `MANIFESTO.md` changes |
| `readme` | `README.md` changes |
| `guides` | Specific use when only `docs/guides/` files change |

**Scope is optional but strongly encouraged** for this repo — it makes `git log --oneline` readable and enables filtered history queries (e.g., `git log --oneline -- scripts/`).

---

## 4. Multi-Line Body Format

For commits that benefit from explanation (why, not just what), add a body after a blank line:

```
docs(agents): add session-management skill body section

The session-close procedure previously lacked the issue-comment step.
Added steps 6.2 and 6.3 to encode the gh issue comment + checkbox update
sequence from AGENTS.md § Agent Communication.

Closes #42
```

**Body guidelines:**
- Separate from the first line with exactly one blank line
- Wrap at 72 characters
- Explain *why* the change was made, not *what* (the diff shows what)
- Issue references on their own line at the end

**Issue reference formats:**
- `Closes #N` — closes the issue when the commit lands on main (via PR merge)
- `Refs #N` — references without closing
- `Part of #N` — partial progress on a larger issue

---

## 5. Breaking Changes

### Inline `!` suffix

For a breaking change in the first line:

```
feat(agents)!: rename executive-researcher to research-executive
```

### BREAKING CHANGE footer

For breaking changes with a description:

```
refactor(scripts): consolidate fetch scripts into single entry point

BREAKING CHANGE: fetch_source.py and fetch_all_sources.py now require
--manifest flag; direct URL argument is removed. Update any scripts
or CI steps that call these with bare URLs.
```

Both methods are valid. Use `!` for simple renames/removals; use the footer when a migration note is needed.

---

## 6. Examples Representative of This Repo

```bash
# New agent added to the fleet
feat(agents): add executive-docs agent for documentation governance

# Bug fix in a script
fix(scripts): correct branch slug calculation for paths with multiple slashes

# Research synthesis doc added
docs(research): add agent-skills-integration synthesis — status: Final

# ADR committed
docs(decisions): add ADR-006 agent skills adoption

# CI gate added
ci: run validate_skill_files.py on PRs touching .github/skills/

# Workplan created at session start
docs(plans): add 2026-03-07-agent-skills-implementation workplan

# Pre-compact safety commit (no scope needed)
chore: pre-compact checkpoint — session state saved to scratchpad

# Dependency update
chore(deps): bump uv.lock after adding mkdocs-material

# Test coverage for a new script
test(scripts): add tests for scaffold_workplan.py happy path and error exits

# Docs-only correction (no functional change)
docs(guides): fix broken link to session-synthesis source stub
```

---

## 7. What NOT to Do

| Anti-pattern | Why it fails | Correct alternative |
|---|---|---|
| `update docs` | Vague — what was updated? No type, no scope | `docs(guides): clarify programmatic-first decision table` |
| `WIP` or `wip: stuff` | Not a valid type; not revertable safely | Commit the specific logical unit; use feature branches |
| `feat: update scripts and docs and agents` | Multiple unrelated changes in one commit | Three separate commits, each with its own scope |
| `Fix #42` | No type, no scope, no description | `fix(agents): correct tool restriction for executive-docs (Closes #42)` |
| `docs(guides): Added new section.` | Past tense + trailing period | `docs(guides): add new section` |
| `chore: checkpoint` | Too vague for a non-checkpoint session commit | Use for pre-compact checkpoints only; otherwise be specific |
| `feat(everything): massive refactor` | Scope "everything" is not a real scope | Break into per-scope commits |
| Skipping scope entirely when scope is clear | Makes history unfiltered | Always include scope when the change is clearly localized |

---

## 8. Commit Cadence

Per [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) § Commit Discipline: commit frequently as you complete each logical unit of work — not one giant commit at the end of a session.

| Unit of work | Commit timing |
|---|---|
| Docs change | Commit immediately after the file is saved |
| Script change | Commit immediately; tests committed in the same or next commit |
| Agent file change | Commit immediately; also update `README.md` catalog in same commit |
| Workplan created | Commit before Phase 1 executes |
| Pre-compact | Commit all in-flight changes before running `/compact` |
| Session end | Commit the Session Summary scratchpad content (if extracted to a doc) |

This repo uses **rebase and merge** only — squash merge is disabled. Every commit message lands on `main` individually, so every commit message must be valid and meaningful standing alone.

---

## 9. Governing Constraint

This skill is governed by [`AGENTS.md`](../../../AGENTS.md) § Commit Discipline and [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) § Commit Discipline. The Conventional Commits specification is at [conventionalcommits.org](https://www.conventionalcommits.org/).

The encoding inheritance chain is:

[`MANIFESTO.md`](../../../MANIFESTO.md) → [`AGENTS.md`](../../../AGENTS.md) → agent files → this skill → session behaviour.

A commit message is not decoration — it is the durable record of a logical change. Low-quality messages degrade the endogenic substrate: future sessions cannot reconstruct intent from history, and CI cannot identify regressions by type. Write commit messages as if a future agent will rely on them to understand the codebase.
