# `pytest` — Curated Agent Reference

> **Agent instruction**: use this file as your first lookup for `pytest` command patterns on this repo.
> Always invoke via `uv run pytest` — never bare `pytest`.

---

## Repo-Specific Conventions

| Convention | Value |
|---|---|
| Test location | `tests/` |
| Test naming | `tests/test_<script_name>.py` mirroring `scripts/<script_name>.py` |
| Test invocation | `uv run pytest tests/` |
| Coverage | `uv run pytest tests/ --cov=scripts --cov-report=term-missing` |
| Coverage threshold | **None** — do not add `--cov-fail-under` (subprocess-style tests yield low measured coverage; see repo memory) |
| Minimum real coverage | 80% per new script (enforced by code review, not gate) |

---

## Running Tests

```bash
uv run pytest tests/                                    # all tests
uv run pytest tests/test_foo.py                         # single file
uv run pytest tests/test_foo.py::test_my_function       # single test
uv run pytest tests/ -v                                 # verbose output
uv run pytest tests/ -q                                 # quiet (failures only)
uv run pytest tests/ -x                                 # stop on first failure
uv run pytest tests/ --tb=short                         # shorter tracebacks
```

---

## Filtering by Marker

```bash
uv run pytest tests/ -m io                              # file I/O tests only
uv run pytest tests/ -m integration                     # network/subprocess tests
uv run pytest tests/ -m slow                            # slow tests only
uv run pytest tests/ -m "not slow and not integration"  # fast local dev run
```

---

## Coverage

```bash
uv run pytest tests/ --cov=scripts --cov-report=term-missing   # measure + report
uv run pytest tests/ --cov=scripts --cov-report=xml            # CI XML report
```

> **Important**: `--cov=scripts` measures coverage of `scripts/` only. Many tests in this repo use `subprocess` invocation patterns that do not register as covered lines even when the script runs successfully. This is expected — do NOT add `--cov-fail-under`.

---

## Test Markers (this repo)

| Marker | Meaning | Usage |
|--------|---------|-------|
| `@pytest.mark.io` | Performs real file I/O | File creation, reading, writing in `tmp_path` |
| `@pytest.mark.integration` | Hits network or spawns subprocess | Web fetches, real `gh` CLI calls |
| `@pytest.mark.slow` | Takes > 1 second | Long-running scripts, large fixture setup |

Declare markers in `pyproject.toml` under `[tool.pytest.ini_options].markers`; all three are already registered there.

---

## Test Patterns Used in This Repo

```python
# subprocess-style (most tests): invoke script via subprocess.run
result = subprocess.run(
    ["uv", "run", "python", "scripts/my_script.py", "--dry-run"],
    capture_output=True, text=True
)
assert result.returncode == 0
assert "expected output" in result.stdout

# import-style (preferred for new tests): import and call directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import my_script
result = my_script.do_thing(arg)
assert result == expected

# mocking subprocess calls (for network/gh tests)
from unittest.mock import patch
with patch("my_script._run", return_value=("output", 0)):
    rc = my_script.fetch_docs(tmp_path)
assert rc == 0
```

---

## conftest.py Fixtures

| Fixture | Provides |
|---------|---------|
| `tmp_path` | Per-test temporary directory (pytest built-in) |
| `capsys` | Capture stdout/stderr (pytest built-in) |

---

## Known Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| `pytest: command not found` | Dev extras not installed | `uv sync --extra dev` |
| All tests show 0% coverage | Subprocess invocation pattern | Expected — do not add coverage gate; write import-style tests for new scripts |
| `PytestUnknownMarkWarning` | New marker not registered | Add to `markers` list in `pyproject.toml` `[tool.pytest.ini_options]` |
| `ModuleNotFoundError` on import | `sys.path.insert` missing | Add `sys.path.insert(0, str(Path(...) / "scripts"))` before the import |
