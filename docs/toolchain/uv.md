# `uv` — Curated Agent Reference

> **Agent instruction**: use this file as your first lookup for `uv` command patterns on this repo.
> For exhaustive flag reference, run `uv <subcommand> --help` or see `.cache/toolchain/uv/`.

---

## Repo-Specific Conventions

| Convention | Value |
|---|---|
| Always invoke via | `uv run python scripts/<name>.py` — never bare `python` |
| Dev dependency install | `uv sync --extra dev` (NOT bare `uv sync`) |
| Dev deps declared under | `[project.optional-dependencies] dev = [...]` in `pyproject.toml` |
| Lockfile | `uv.lock` — never edit by hand |
| Python executables | Never use `.venv/bin/python` or `python3` directly |

---

## Run

```bash
uv run python scripts/<name>.py          # run a repo script
uv run python scripts/<name>.py --arg    # pass args
uv run pytest tests/                     # run tests
uv run pytest tests/test_foo.py -v       # single test file, verbose
uv run ruff check scripts/ tests/        # lint
uv run ruff format scripts/ tests/       # format
```

> **Why `uv run`?** It ensures the correct locked environment is used regardless of shell state. Always prefer it over activating the venv manually.

---

## Sync (install dependencies)

```bash
uv sync                   # install only non-dev dependencies
uv sync --extra dev       # install dev dependencies (pytest, ruff, pytest-mock)
uv sync --frozen          # use locked versions without updating
```

**Known Failure Mode**: `uv sync` (without `--extra dev`) does NOT install pytest or ruff. If `pytest` is not found after `uv sync`, run `uv sync --extra dev`.

---

## Add / Remove dependencies

```bash
uv add <package>                 # add production dependency
uv add --dev <package>           # add dev dependency
uv add --optional dev <package>  # add to [project.optional-dependencies] dev
uv remove <package>              # remove dependency
```

After adding/removing, `uv.lock` is automatically updated.

---

## Lock

```bash
uv lock             # regenerate uv.lock from pyproject.toml
uv lock --frozen    # validate lockfile is up to date (CI use)
```

---

## Python version management

```bash
uv python list              # list available Python versions
uv python install 3.11      # install a specific version
uv python pin 3.11          # pin version in .python-version
```

---

## Cache management

```bash
uv cache clean      # clear the uv download/build cache
uv cache dir        # print cache directory location
```

---

## Known Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| `pytest: command not found` after `uv sync` | Dev extras not installed | `uv sync --extra dev` |
| Script errors with "module not found" | Wrong venv activated | Use `uv run` instead of bare `python` |
| CI `uv sync` installs nothing | `uv pip install -e '.[dev]'` used instead | Change CI to `uv sync --extra dev` |
| Lockfile conflict | `uv.lock` edited manually | Delete `uv.lock` and re-run `uv lock` |
