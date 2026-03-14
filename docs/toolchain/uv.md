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

## Script Execution Safety — Three-Tier Validation

Before running any repo script that modifies state, apply this three-tier validation ladder:

| Tier | When | Purpose |
|------|------|---------|
| **Tier 0** — Pre-execution | Before any run | Verify prerequisites: cache state, file existence, estimated scope |
| **Tier 1** — Dry-run gate | First attempt | Preview side effects with `--dry-run` or `--check` — no writes |
| **Tier 3** — Static gate | On commit | CI or pre-commit hook enforces final compliance |

> **Why skip Tier 2?** Tier 2 is text-constraint encoding (AGENTS.md decision tables). For runtime execution, the operative tiers are pre-execution (0), safe preview (1), and static gate (3). See [`AGENTS.md` § Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy) for the full tier definitions.

---

### `fetch_source.py` — Source Cache Validation

**Tier 0** — check if the URL is already cached before fetching:

```bash
uv run python scripts/fetch_source.py <url> --check
# Exit 0 = already cached; exit 2 = not cached (safe to fetch)
```

**Tier 1** — dry-run: verify the URL resolves without writing to disk:

```bash
uv run python scripts/fetch_source.py <url> --dry-run
```

**Tier 3** — after fetching, confirm the source is registered in the manifest:

```bash
uv run python scripts/fetch_source.py --list | grep "<slug>"
```

---

### `prune_scratchpad.py` — Scratchpad Safety

**Tier 0** — verify the scratchpad is non-empty before pruning:

```bash
BRANCH=$(git branch --show-current | tr '/' '-')
test -s ".tmp/${BRANCH}/$(date +%Y-%m-%d).md" \
  && echo "OK — scratchpad exists" \
  || echo "MISSING — run --init first"
```

**Tier 1** — dry-run prune to review what will be compressed before writing:

```bash
uv run python scripts/prune_scratchpad.py --dry-run
```

**Tier 3** — after pruning, verify live sections remain intact:

```bash
BRANCH=$(git branch --show-current | tr '/' '-')
grep "^## " ".tmp/${BRANCH}/$(date +%Y-%m-%d).md"
```

---

### `validate_agent_files.py` — Agent File Compliance

**Tier 0** — confirm the baseline passes before making any edits:

```bash
uv run python scripts/validate_agent_files.py --all
# Exit 0 = clean baseline; non-zero = pre-existing failures to fix first
```

**Tier 1** — after editing, validate the specific file before staging:

```bash
uv run python scripts/validate_agent_files.py .github/agents/<name>.agent.md
```

**Tier 3** — CI runs `validate_agent_files.py --all` automatically on every PR touching `.github/agents/`. To replicate locally before pushing:

```bash
uv run python scripts/validate_agent_files.py --all
```

---

## Known Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| `pytest: command not found` after `uv sync` | Dev extras not installed | `uv sync --extra dev` |
| Script errors with "module not found" | Wrong venv activated | Use `uv run` instead of bare `python` |
| CI `uv sync` installs nothing | `uv pip install -e '.[dev]'` used instead | Change CI to `uv sync --extra dev` |
| Lockfile conflict | `uv.lock` edited manually | Delete `uv.lock` and re-run `uv lock` |
