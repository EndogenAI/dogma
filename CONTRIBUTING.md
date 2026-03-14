# Contributing to EndogenAI Workflows

Thank you for contributing to this repo. This document covers the conventions and process for making changes.

---

## Core Principles

Before contributing, read [`MANIFESTO.md`](MANIFESTO.md) and [`AGENTS.md`](AGENTS.md). All contributions must align with the three core axioms:

- **Endogenous-First** — scaffold from existing system knowledge; absorb and encode external best practices
- **Algorithms Before Tokens** — prefer deterministic, encoded solutions over interactive token burn
- **Local Compute-First** — minimize token burn; run locally whenever possible

See [`MANIFESTO.md#the-three-core-axioms`](MANIFESTO.md#the-three-core-axioms) for full details, and [`MANIFESTO.md#guiding-principles-cross-cutting`](MANIFESTO.md#guiding-principles-cross-cutting) for the seven guiding principles that cross-cut all contributions.

---

## What Belongs in This Repo

| ✅ Yes | ❌ No |
|--------|-------|
| Agent files (`.agent.md`) | Application source code |
| Agent authoring guides and governance docs | Build artifacts or compiled output |
| Workflow scripts (`scripts/`) | Large binary assets |
| Best practice guides (`docs/guides/`) | Project-specific implementation details |
| Research notes and literature reviews (`docs/research/`) | Secrets or credentials |
| Issue and PR templates | |

---

## Every Artifact Links to a Decision

Before creating any agent, skill, or script, **create or reference the GitHub issue that defines it**. 

The issue is the source of truth. Every artifact (`.agent.md`, `SKILL.md`, script) must encode:
- A link to the defining GitHub issue (number and title)
- The milestone it targets (from issue assignment)
- The effort estimate and priority (from issue labels)
- How it satisfies the issue's acceptance criteria

See [`docs/guides/issue-and-artifact-discipline.md`](docs/guides/issue-and-artifact-discipline.md) for the complete discipline and validation checklist.

---

> **Start here if you're setting up a local dev environment for script development or testing.**

```bash
# 1. Clone the repo
git clone https://github.com/EndogenAI/dogma.git
cd Workflows

# 2. Install dependencies (uv manages the virtual environment)
uv sync

# 3. Install pre-commit hooks (runs ruff, ruff-format, validate-synthesis, validate-agent-files on every git commit)
uv run pre-commit install

# 4. Run the test suite
uv run pytest tests/

# 5. Run the full test suite with coverage
uv run pytest tests/ --cov=scripts --cov-report=term-missing

# 6. Run only fast tests (skip IO and integration)
uv run pytest tests/ -m "not slow and not integration"
```

**Always use `uv run`** — never invoke `python` or executables directly.

### GitHub Projects Access

If you'll be working with GitHub Projects v2:

```bash
gh auth refresh -s project
gh auth status  # verify "project" appears in scopes
```

This is required once per machine. The `project` scope is needed for:
- Reading and writing Projects v2 boards (`gh project` commands)

> **Note**: `uv run python scripts/seed_labels.py` uses `gh label create/delete` and does **not** require the `project` scope — only standard repo permissions.

---

## Workflow

### For Documentation Changes

1. Branch from `main`: `git checkout -b docs/<short-description>`
2. Edit or add `.md` files under `docs/`, or update root docs (`README.md`, `MANIFESTO.md`, `AGENTS.md`)
3. Commit: `docs(<scope>): <description>`
4. Open a PR — reference any related issue

### For New or Updated Agent Files

1. Branch: `git checkout -b feat/agent-<name>`
2. Read [`.github/agents/AGENTS.md`](.github/agents/AGENTS.md) before authoring
3. Create `.github/agents/<name>.agent.md` following the frontmatter schema
4. Update [`.github/agents/README.md`](.github/agents/README.md) to add the agent to the catalog
5. Commit: `feat(agents): add <name> agent`
6. Open a PR

### For New or Updated Scripts

> **Before implementing**: write your README entry first — see the [README-Driven Development Convention](scripts/README.md#readme-driven-development-convention) in `scripts/README.md`.

1. Branch: `git checkout -b chore/scripts-<name>`
2. Write the script with a module docstring (purpose, inputs, outputs, usage, exit codes)
3. Add a `--dry-run` flag if the script writes or deletes files
4. Update [`scripts/README.md`](scripts/README.md) to add the script to the catalog
5. Commit: `chore(scripts): add <name> script`
6. Open a PR

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

| Type | Scope examples | When to use |
|------|---------------|-------------|
| `feat` | `agents`, `docs` | New agent, new guide |
| `fix` | `agents`, `scripts` | Correction to existing content |
| `docs` | `manifesto`, `readme`, `guides` | Documentation only |
| `chore` | `scripts`, `templates` | Tooling, scripts, templates |
| `refactor` | `agents`, `docs` | Restructuring without content change |

---

## Commit Discipline

> Small, incremental commits. One logical change per commit.

Do not create one giant commit at the end of a session. Instead, commit frequently as you complete each logical unit of work:

- **Docs change** → commit immediately
- **Script change** → commit immediately  
- **Agent file change** → commit immediately
- **Test or validation** → commit immediately

Good commit cadence prevents merge conflicts, makes history readable, and allows fine-grained rollbacks if needed. It also enforces the endogenic principle: work that is worth doing is worth committing early.

**Example workflow:**
```bash
# Update docs/guides/workflows.md
git add docs/guides/workflows.md
git commit -m "docs(guides): clarify evaluator-optimizer loop pattern"

# Create a new script
git add scripts/fetch_all_sources.py
git add scripts/README.md
git commit -m "chore(scripts): add fetch_all_sources.py for batch URL caching"

# Create an agent file
git add .github/agents/executive-researcher.agent.md
git add .github/agents/README.md
git commit -m "feat(agents): add executive-researcher agent"

# Open PR with all three commits — history is clear and granular
```

---

## Pull Request Template

All PRs use the template in [`.github/pull_request_template.md`](.github/pull_request_template.md).

**Merge strategy**: this repo uses **rebase and merge** only. Squash merge is disabled. Keep PR commits clean — each commit should be a valid Conventional Commit message, because all commits land on `main` individually. See [docs/guides/github-workflow.md](docs/guides/github-workflow.md#9-pr-merge-strategy) for the full rationale.

**Before opening a PR, verify:**
- [ ] Content aligns with [`MANIFESTO.md`](MANIFESTO.md) principles
- [ ] Agent files follow the frontmatter schema in [`.github/agents/AGENTS.md`](.github/agents/AGENTS.md)
- [ ] New scripts have a docstring and are listed in [`scripts/README.md`](scripts/README.md)
- [ ] New docs are linked from the relevant index or guide
- [ ] No secrets, credentials, or personal data included
- [ ] New scripts are **idempotent** — running twice produces the same result as running once
- [ ] New scripts are **legible** — another agent can infer intent from the docstring and function names alone, without reading every line
- [ ] Side-effectful scripts have a `--dry-run` flag
- [ ] **Legibility**: Script code is readable in a single top-to-bottom pass — complex logic is extracted to named functions with docstrings.
- [ ] **Idempotency**: Scripts that write files, create issues, or modify state are idempotent — running them twice produces the same result as running them once.

---

## Proposing New Research Topics

Open a GitHub Issue using the **Research** template. Good research topics include:
- External tools or frameworks to evaluate for adoption
- Methodologies from other fields (neuroscience, cognitive science, software engineering) to synthesize
- Open questions about the endogenic methodology itself

---

## Questions?

Open an issue or start a discussion. This repo is meant to grow — contributions that improve the methodology, extend the agent fleet, or add useful scripts are all welcome.
