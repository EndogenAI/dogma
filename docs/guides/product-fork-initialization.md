# Product Fork Initialization Guide

## Overview

This guide explains how to initialize a product fork from the dogma repository — the canonical source for endogenic agentic workflow practices. It covers the full adoption sequence from forking to validated, axiom-aligned baseline. It is written for engineers and teams who want to adopt dogma's governance substrate in a new or existing project.

---

## Prerequisites

Before starting, ensure the following are in place:

- Git access to GitHub and permission to create repositories
- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python ≥ 3.11
- A GitHub personal access token with `repo` and `project` scopes (set as `GITHUB_TOKEN`)
- `gh` CLI installed and authenticated (`gh auth login`)

---

## Step 1 — Fork or Template the Repo

Use the GitHub UI or the `gh` CLI to create your fork:

```bash
gh repo fork EndogenAI/dogma --clone
cd dogma
```

Or create from the template (Greenfield):

```bash
gh repo create my-org/my-project --template EndogenAI/dogma --clone
cd my-project
```

**Alternatively, scaffold directly with the cookiecutter template** (no GitHub fork required):

```bash
uvx cookiecutter gh:EndogenAI/dogma
```

This runs interactively, prompts for `project_name`, `domain`, `team_size`, `ci`, and
`pre_commit` preferences, then generates a minimal dogma-aligned project directory with
`AGENTS.md`, `client-values.yml`, `pyproject.toml`, and CI workflow stubs. After generation,
continue from Step 2 to complete the Deployment Layer configuration.

> **Anti-pattern**: Stopping here. A raw fork or template copy contains no `client-values.yml`, no Deployment Layer comment, and no axiom emphasis. Agents will operate against dogma's own Core Layer defaults rather than your project's specialized priorities. The `validate-agent-files` pre-commit hook will fail on first commit. *This step alone is insufficient.*

---

## Step 2 — Run the Adoption Wizard

Run the adoption wizard to generate your Deployment Layer configuration:

```bash
uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo
```

The wizard:

1. Elicits your project's mission, priorities, and axiom emphasis interactively
2. Writes `client-values.yml` with `mission`, `priorities`, `axiom_emphasis`, and `constraints` fields
3. Copies and annotates `AGENTS.md` with a Deployment Layer comment instructing agents to read `client-values.yml` before their first action
4. Runs `validate_agent_files.py` automatically; exit code 0 confirms the fork starts with a valid, axiom-aligned configuration

**Canonical example**: Running `uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo` produces `client-values.yml` and an annotated `AGENTS.md`. `validate_agent_files.py` runs automatically; exit code 0 confirms the fork starts with a valid, axiom-aligned configuration. Contrast with cloning the repo and manually editing files: without the wizard, `client-values.yml` is absent, agents cannot read the Deployment Layer, and the first commit fails the validate-agent-files pre-commit hook.

---

## Step 3 — Customize `client-values.yml`

`client-values.yml` is your fork's **Deployment Layer** file — it specializes dogma's Core Layer axioms for your project without overriding them.

Open the generated `client-values.yml` and review or extend:

- `mission` — one sentence describing your project's purpose
- `priorities` — ordered list of your team's primary concerns (e.g., security, cost, latency)
- `axiom_emphasis` — which of dogma's axioms to amplify (e.g., `local-compute-first` for cost-sensitive projects)
- `constraints` — any domain-specific guardrails (e.g., `no-external-api-calls`)

**Constraint**: `client-values.yml` may NOT override MANIFESTO.md Core Layer constraints (Endogenous-First, Algorithms Before Tokens, Local Compute-First). It may only specialize or add priorities at the Deployment Layer.

Refer to [`AGENTS.md`](../../AGENTS.md) (§ Deployment Layer integration) for the full interpretation rules agents apply when reading this file and the schema for the full external-value schema and Supremacy constraint reference.

---

## Step 4 — Validate the Fork

Install pre-commit hooks and run the full validation suite:

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
uv run pre-commit run --all-files
```

Run the fast test suite:

```bash
uv run pytest tests/ -m "not slow and not integration" -q
```

Both must pass before you make your first commit. A clean baseline means:

- All agent files pass frontmatter and structure checks
- `client-values.yml` is present and syntactically correct
- No heredoc writes or terminal I/O redirections in any committed script
- The Deployment Layer comment is present in `AGENTS.md`

If `validate_agent_files.py` reports failures, re-run `adopt_wizard.py` or manually add the missing fields to `client-values.yml`.

---

## Step 5 — Track Upstream Changes (optional)

To keep your fork synchronized with upstream dogma governance improvements, use the `--track` flag when running the wizard:

```bash
uv run python scripts/adopt_wizard.py --org MyOrg --repo myrepo --track
```

This writes a `.dogma.json` file at the repo root containing:

- The upstream dogma commit SHA at initialization time
- The `adopt_wizard.py` version used
- The `axiom_emphasis` recorded at initialization

To check for governance drift later:

```bash
uv run python scripts/adopt_wizard.py --check
```

This compares your `.dogma.json` against the current upstream dogma schema and reports any new required fields or governance changes you have not yet absorbed. A non-zero exit code means your fork is behind — review the diff and apply relevant changes manually.

> **Note**: The `--track` flag and `--check` mode are pending implementation (tracked in the dogma backlog). Until available, record your initialization commit SHA manually in a `FORK_PROVENANCE.md` at the repo root.

---

## Troubleshooting

### `client-values.yml` is missing after template initialization

**Cause**: GitHub's "Use this template" button creates a static copy with no variable substitution and no wizard run. `client-values.yml` is not committed to the dogma template repo by default (it is fork-specific).

**Fix**: Run `uv run python scripts/adopt_wizard.py` after template initialization to generate `client-values.yml`. Do not proceed to commit without it.

---

### `adopt_wizard.py` not found

**Cause**: The script is present in dogma but may not have been included if you cherry-picked files rather than cloning the full repo.

**Fix**: Verify the file exists: `ls scripts/adopt_wizard.py`. If missing, re-clone or copy from the dogma repo directly. Then run `uv sync` to ensure the virtual environment is current.

---

### Pre-commit hooks fail after `uv run pre-commit install`

**Cause**: Common causes include: `client-values.yml` absent, agent files missing the Deployment Layer comment, or Python version mismatch (requires ≥ 3.11).

**Fix**:
1. Run `uv run pre-commit run --all-files 2>&1 | head -40` to see the specific failing hook.
2. For `validate-agent-files` failures: re-run the adoption wizard.
3. For `ruff` failures: run `uv run ruff format scripts/ tests/` then `uv run ruff check scripts/ tests/ --fix`.
4. For Python version issues: confirm `python --version` reports ≥ 3.11 in the `uv` environment.

---

## Related

- [`docs/research/product-fork-initialization.md`](../research/product-fork-initialization.md) — research synthesis underlying this guide
- [`AGENTS.md`](../../AGENTS.md) — root agent constraints; Deployment Layer integration rules
- [`MANIFESTO.md`](../../MANIFESTO.md) — core dogma; Endogenous-First axiom (§1); Deployment Layer constraint model
