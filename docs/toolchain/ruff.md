# `ruff` — Curated Agent Reference

> **Agent instruction**: use this file as your first lookup for `ruff` command patterns on this repo.
> For exhaustive flag reference, see `.cache/toolchain/ruff/`.

---

## Repo-Specific Conventions

| Convention | Value |
|---|---|
| Always invoke via | `uv run ruff check ...` / `uv run ruff format ...` |
| Config location | `[tool.ruff.lint]` section in `pyproject.toml` |
| Target paths | `scripts/ tests/` for both check and format |
| CI gates | `ruff check` (lint rules) **and** `ruff format --check` (formatter) — both must pass |

---

## Check (lint)

```bash
uv run ruff check scripts/ tests/        # lint — report errors
uv run ruff check --fix scripts/ tests/  # lint + auto-fix fixable errors
uv run ruff check --select E501 .        # run a specific rule only
```

---

## Format

```bash
uv run ruff format scripts/ tests/          # format in-place
uv run ruff format --check scripts/ tests/  # dry-run check (CI use)
uv run ruff format --diff scripts/ tests/   # show diff without applying
```

---

## Rule lookup

```bash
uv run ruff rule E501     # describe a specific rule
uv run ruff linter        # list all available linters/plugins
```

---

## Clean

```bash
uv run ruff clean         # remove ruff cache (.__ruff_cache/)
```

---

## Known Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| CI lint passes but format fails | `ruff check --fix` does not fix formatting | Always run both `ruff check --fix` **and** `ruff format` before committing |
| `[tool.ruff]` lint rules silently ignored | Rules placed under `[tool.ruff]` instead of `[tool.ruff.lint]` | Move `select`, `ignore` to `[tool.ruff.lint]` |
| Auto-fix removes needed import | Ruff removes an import used only in a type annotation | Add `# noqa: F401` or enable `TC` rules |
| Sort errors on E402 (import order) | `sys.path.insert` before imports in test files | Add `# noqa: E402` on the import line after `sys.path.insert` |

---

## Pre-commit Integration

Ruff runs as a pre-commit hook (see `.pre-commit-config.yaml`). If hooks run on commit and report errors, fix them before retrying the commit — do not use `--no-verify` to bypass.
