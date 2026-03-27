# Adoption Guide — Companion-Repo Onboarding

This guide explains how to use the **Adoption Agent** and `scripts/adopt_wizard.py` to onboard a new companion repository into the EndogenAI Workflows governance framework.

---

## Overview

The Adoption Agent automates companion-repo onboarding by:

1. Running `scripts/adopt_wizard.py` to scaffold governance artefacts from the `{{cookiecutter.project_slug}}/` template.
2. Generating a `client-values.yml` (Deployment Layer values file) pre-populated for your organisation and repository.
3. Generating an `AGENTS.md` skeleton that inherits Core Layer constraints from the dogma `MANIFESTO.md`.
4. Validating the generated files with `scripts/validate_agent_files.py` before handoff.

The workflow follows the **Endogenous-First** axiom: the template and wizard encode accumulated governance knowledge so new adopters start with a correct skeleton rather than authoring from scratch.

---

## Prerequisites

```bash
# Ensure the project toolchain is installed
uv sync
```

---

## Quick Start

### Step 1 — Orient (invoke once per session)

```bash
uv run python scripts/adopt_wizard.py --help
```

### Step 2 — Dry run

Always preview the output before writing files:

```bash
uv run python scripts/adopt_wizard.py \
  --org <your-github-org> \
  --repo <your-repo-name> \
  --output-dir ./output/<your-repo-name> \
  --dry-run
```

Inspect the listed files. If the output looks correct, proceed to Step 3.

### Step 3 — Scaffold

```bash
uv run python scripts/adopt_wizard.py \
  --org <your-github-org> \
  --repo <your-repo-name> \
  --output-dir ./output/<your-repo-name>
```

**Expected outputs in `--output-dir`:**

| File | Purpose |
|------|---------|
| `AGENTS.md` | Governance skeleton inheriting Core Layer constraints |
| `client-values.yml` | Deployment Layer values for your org/repo |
| `pyproject.toml` | Minimal project config |
| `README.md` | Onboarding README stub |

### Step 4 — Validate

```bash
uv run python scripts/validate_agent_files.py ./output/<your-repo-name>/AGENTS.md
```

Ensure the script exits 0 before committing any generated files.

### Step 5 — Customise `client-values.yml`

Open `./output/<your-repo-name>/client-values.yml` and:
- Replace any remaining placeholder values (e.g. `YOUR_ORG`).
- Add Deployment Layer constraints specific to your organisation.
- Do **not** override Core Layer axioms from `MANIFESTO.md` — `client-values.yml` may only *specialise* them.

---

## Non-Interactive Mode (CI pipelines)

For automated environments, pass `--non-interactive` to suppress all interactive prompts:

```bash
uv run python scripts/adopt_wizard.py \
  --org my-org \
  --repo my-project \
  --output-dir /tmp/my-project \
  --non-interactive
```

---

## What `adopt_wizard.py` Does

1. **Reads** the `{{cookiecutter.project_slug}}/` Cookiecutter template.
2. **Substitutes** `org` and `repo` context variables into all template files.
3. **Writes** the rendered output to `--output-dir`.
4. **Calls** `scripts/validate_agent_files.py` on the generated `AGENTS.md` and reports the result.

Exit codes:
- `0` — success, all files written and validated
- `1` — validation failure (check output for details)
- `2` — configuration or I/O error

---

## Invoking the Adoption Agent

Start a chat session in VS Code Copilot with the **Adoption Agent** active, then:

```
Please run the companion-repo onboarding for org=<your-org> repo=<your-repo>.
Output dir: ./output/<your-repo>. Run --dry-run first.
```

The agent will:
1. Execute a dry run and record the output in the session scratchpad.
2. Run the real wizard if the dry run looks correct.
3. Validate the generated files.
4. Route back to the Executive Orchestrator for commit.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `validate_agent_files.py` fails with "missing section" | Generated `AGENTS.md` has incomplete template | Check `{{cookiecutter.project_slug}}/AGENTS.md` for TODO placeholders |
| `client-values.yml` still has `YOUR_ORG` | `--org` was not passed to wizard | Re-run with `--org <value>` |
| Wizard exits 2 | Output dir is read-only or parent dir missing | Create the parent directory first |
| `uv run` fails | Toolchain not installed | Run `uv sync` from the repo root |

---

## Related Resources

- [`scripts/adopt_wizard.py`](../../scripts/adopt_wizard.py) — canonical onboarding script
- [`{{cookiecutter.project_slug}}/client-values.yml`](../../{{cookiecutter.project_slug}}/client-values.yml) — Deployment Layer template
- `docs/research/external-value-architecture.md` — Deployment Layer schema and rules (forthcoming)
- [`.github/agents/adoption.agent.md`](../../.github/agents/adoption.agent.md) — Adoption Agent definition
