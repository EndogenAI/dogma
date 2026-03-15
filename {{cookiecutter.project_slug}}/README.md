# {{ cookiecutter.project_name }}

Created from [EndogenAI/dogma](https://github.com/EndogenAI/dogma) template.

> **Domain**: {{ cookiecutter.domain }} | **Team size**: {{ cookiecutter.team_size }}

## Overview

This repository uses the dogma endogenic agentic workflow substrate. Agents operate
under governance constraints defined in `AGENTS.md` and specialized for this project
in `client-values.yml`.

## Quickstart

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type pre-push

# Run tests
uv run pytest tests/ -m "not slow and not integration" -q
```

## Governance

- `AGENTS.md` — operational constraints for all AI agents in this repo
- `client-values.yml` — Deployment Layer configuration (mission, priorities, axiom emphasis)

For the full initialization and adoption workflow, see  
[docs/guides/product-fork-initialization.md](docs/guides/product-fork-initialization.md)  
or the upstream guide at  
<https://github.com/EndogenAI/dogma/blob/main/docs/guides/product-fork-initialization.md>.
