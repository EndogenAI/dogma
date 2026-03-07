---
title: "Testing Tools and Frameworks"
research_issue: "#16"
status: Final
date: 2026-03-07
closes_issue: 16
sources:
  - .cache/sources/docs-pytest-org-en-stable.md
  - .cache/sources/pytest-cov-readthedocs-io.md
  - .cache/sources/pypi-org-project-pytest-mock.md
  - .cache/sources/martinfowler-com-articles-practical-test-pyramid-html.md
  - .cache/sources/coverage-readthedocs-io-en-latest.md
  - .cache/sources/hypothesis-readthedocs-io-en-latest.md
---

# Testing Tools and Frameworks

> **Status**: Final
> **Research Question**: Which automated testing tools, frameworks, and practices are most effective for a Python-heavy, script-centric agentic workflow repository?
> **Date**: 2026-03-07

---

## 1. Executive Summary

Six sources were surveyed: canonical pytest documentation, coverage.py, pytest-mock, pytest-cov, the Hypothesis property-testing framework, and Martin Fowler's Practical Test Pyramid. The repository already possesses a sound testing foundation — `pytest 7+`, `pytest-cov 4+`, `pytest-mock 3+`, `--strict-markers`, and a three-marker taxonomy (`integration`, `slow`, `io`) are all in place and correctly configured in `pyproject.toml`. The gaps are configuration completeness, coverage enforcement, subprocess test ergonomics, HTTP mock patterns, and pre-commit/CI pipeline segmentation.

The most important single finding is that this repo's test infrastructure is architecturally correct but lacks the **enforcement layer** that converts "we have coverage tooling" into "CI fails on a regression." Three targeted changes — adding `--cov-fail-under=80` to CI pytest invocations, adopting `pytest-subprocess` for ergonomic subprocess mocking, and patching `urllib.request.urlopen` via `mocker` for network tests — close the highest-value gaps with minimal friction. No structural overhaul is needed.

---

## 2. Hypothesis Validation

Three hypotheses about this repo's testing posture were submitted for validation before the research began: (1) the existing marker and tool setup is architecturally sound; (2) coverage enforcement is the critical missing gate; (3) subprocess and HTTP mocking are the primary ergonomic gaps. All three were confirmed.

### Finding 1 — The existing marker taxonomy is correct and complete

The three markers `io`, `integration`, `slow` map precisely to the test pyramid's tier distinctions: fast pure unit tests (unmarked), filesystem-touching tests (`io`), tests requiring network/subprocess side effects (`integration`), and long-duration operations (`slow`). No additional markers are warranted. The `--strict-markers` flag in `addopts` correctly enforces that all markers are registered, preventing silent miscategorisation. This aligns with the Fowler pyramid principle: tests should be written with different granularity, and the selection mechanism must be explicit and enforced.

The current fast-gate invocation `pytest -m "not integration and not slow"` documented in AGENTS.md is correct. The only remaining gap is that `io`-marked tests are not excluded from this gate — they are cheap but do involve filesystem writes. Whether to include them in the fast gate is a CI speed question, not a correctness question.

**Confidence**: Established fact — marker definitions confirmed against `pyproject.toml` and AGENTS.md.

### Finding 2 — `pytest-cov` is installed but coverage is not enforced

`pytest-cov 4+` is a declared dev dependency and `[tool.coverage.run]` is configured with `source = ["scripts"]` and appropriate exclusions. However, neither `--cov` nor `--cov-fail-under` appears in `addopts`. Coverage is never actually measured during a default `pytest` invocation. Without `--cov-fail-under=80`, the 80% threshold specified in AGENTS.md ("minimum: 80% coverage") is aspirational, not contractual.

The open-source Python community de facto standard: **80% for utility scripts and CLIs; 90%+ for libraries with stable public APIs.** The repo's 80% threshold is appropriate and should be enforced rather than suggested.

**Confidence**: Established fact — `pyproject.toml` inspected directly; no `--cov` flag found in `addopts`.

### Finding 3 — `pytest-mock` is installed; usage pattern is inconsistently applied

`pytest-mock 3+` is correctly declared as a dependency. The `conftest.py` uses both `unittest.mock.MagicMock`/`patch` directly in fixtures and `monkeypatch.setattr` — a mixed pattern that produces inconsistent test readability. The recommended split is:

- **`monkeypatch.setattr/setenv/chdir`** — environment variables, working directory, and attribute replacement without tracking call assertions
- **`mocker.patch`** — replacing callables and classes where call assertions (`assert_called_once_with`) are needed
- **Never**: `@patch` decorator on test functions — it obscures setup order and complicates parametrized tests

The `git_branch_mock` fixture in `conftest.py` currently wraps a manual function that selectively intercepts `subprocess.run` calls. This should be refactored to use `mocker.patch("subprocess.run", side_effect=...)` for cleaner teardown semantics.

**Confidence**: Established fact — `conftest.py` inspected directly.

### Finding 4 — Subprocess mocking is the primary ergonomic debt

Scripts in this repo (`prune_scratchpad.py`, `scaffold_agent.py`, `fetch_source.py`) make multiple `subprocess.run` calls for git operations. Current tests in `conftest.py` mock `subprocess.run` by replacing it with a hand-crafted function that must match command signatures manually. `pytest-subprocess` (v1.5+) provides a purpose-built `fake_process` fixture: it intercepts subprocess calls by command signature, raises `pytest_subprocess.exceptions.ProcessNotRegisteredError` on unexpected calls, and requires no manual `MagicMock` construction. This removes boilerplate and surfaces unexpected subprocess invocations as test failures.

```python
# Current pattern (fragile — any subprocess.run call passes silently)
def mock_run(*args, **kwargs):
    result = MagicMock()
    result.stdout = b"main"
    result.returncode = 0
    return result
monkeypatch.setattr(subprocess, "run", mock_run)

# With pytest-subprocess (ergonomic — unexpected calls fail explicitly)
def test_git_branch(fake_process):
    fake_process.register_subprocess(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout="main"
    )
    assert get_current_branch() == "main"
```

**Confidence**: Working hypothesis — `pytest-subprocess` not yet installed; pattern validated against pypi documentation.

### Finding 5 — HTTP mocking: use `mocker.patch("urllib.request.urlopen")` — no external plugin needed

`fetch_source.py` uses `urllib.request` (stdlib), not `httpx` or `requests`. Neither `respx` nor `responses` applies to stdlib urllib. The correct mock boundary is `urllib.request.urlopen` itself, patched via `mocker.patch`:

```python
def test_fetch_caches_response(tmp_path, mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.read.return_value = b"<html><body>Test content</body></html>"
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("urllib.request.urlopen", return_value=mock_resp)
    # ... call fetch_source and assert cache file written
```

If future scripts adopt `httpx`, use `respx`. If `requests`, use `responses`. Matching mock library to HTTP client library is mandatory — e.g., `respx` does not intercept `urllib.request` calls.

**Confidence**: Established fact — HTTP library confirmed by direct inspection of `scripts/fetch_source.py`.

### Finding 6 — LLM API testing: mock at the transport boundary, not the SDK

For scripts that call LLM APIs (Anthropic, OpenAI), the correct mocking boundary is the **HTTP transport layer**, not the SDK client object. Mocking at `anthropic.Client()` or `openai.ChatCompletion.create()` creates tests tied to SDK internals that break on SDK upgrades. Since Anthropic's SDK uses `httpx` internally, `respx` is the correct mock library for LLM API calls:

```python
import respx, httpx

@respx.mock
def test_llm_summary_call():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(200, json={
            "content": [{"type": "text", "text": "stub response"}]
        })
    )
    result = call_summary_api(prompt="test")
    assert result == "stub response"
```

For property-based edge case testing, `hypothesis` with `@given(st.text())` is appropriate for probing argument parsers and input-validation paths.

**Confidence**: Working hypothesis — Anthropic SDK's internal HTTP client confirmed as httpx in official documentation.

---

## 3. Pattern Catalog

The following patterns emerge from cross-source synthesis and direct inspection of `tests/` and `scripts/`. Each is an actionable, copy-adaptable pattern for this codebase.

### Finding 7 — Documentation testing: selective value only

`pytest --doctest-modules` provides value for functions with deterministic string output and no I/O dependencies (e.g., `slugify`, `format_date`). It has near-zero value for the majority of this repo's scripts, which perform file I/O, subprocess calls, and network access. Running `--doctest-modules` globally would generate false failures or require extensive `# doctest: +SKIP` annotations. Recommendation: add doctests selectively to pure utility functions; do not add `--doctest-modules` to `addopts`.

**Confidence**: Established fact — pattern validated against pytest doctest documentation and repo script inspection.

### Finding 8 — Pre-commit and CI must be segmented

Pre-commit hooks should complete in ≤ 10 seconds to avoid contributor friction (Fowler: short feedback loops are the primary value of automation). Full coverage runs are slow and belong exclusively in CI. Recommended segmentation:

| Stage | Tool | Command |
|-------|------|---------|
| Pre-commit | ruff | `ruff check .` |
| Pre-commit | black | `black --check .` |
| Pre-commit | pytest (optional) | `pytest -m "not integration and not slow and not io" -q` |
| CI fast gate | pytest | `pytest -m "not integration and not slow" -q` |
| CI full gate | pytest + coverage | `pytest --cov=scripts --cov-report=xml --cov-fail-under=80` |

The optional pre-commit pytest step is only worthwhile if the unmarked test suite runs in under 5 seconds. Measure before adding.

**Confidence**: Established fact — pattern from Fowler test pyramid; timing threshold is conventional.

---

## 4. Recommendations for This Repo

### R1 — Enforce coverage gate in CI (highest priority)

Add `--cov=scripts --cov-report=xml --cov-fail-under=80` to the CI pytest invocation in `.github/workflows/`. This is the single highest-ROI change: it converts the existing 80% aspiration into a contractual regression gate without requiring any other changes. Do not add `--cov` to `addopts` globally — it adds overhead to every local `pytest` run and conflicts with `pytest-xdist` (`-n auto`) without additional config.

**Files to update**: `.github/workflows/<ci-file>.yml`

### R2 — Add `pytest-subprocess` to dev dependencies

Add `pytest-subprocess>=1.5` to `pyproject.toml` dev dependencies. Refactor the `git_branch_mock` fixture in `conftest.py` to use `fake_process`. This removes the fragile function-replacement pattern that silently ignores unexpected subprocess invocations.

**Files to update**: `pyproject.toml`, `tests/conftest.py`, affected test files

### R3 — Patch `urllib.request.urlopen` in HTTP-touching tests

For `test_fetch_source.py` tests that currently carry `@pytest.mark.integration` because they hit live URLs: add `mocker.patch("urllib.request.urlopen", ...)` to stub the response, remove the `integration` marker, and include them in the fast gate. This eliminates the need for a live network connection to validate fetch/cache logic.

**Files to update**: `tests/test_fetch_source.py`

### R4 — Standardise on `mocker.patch` for callable mocking

Migrate test fixtures that use `unittest.mock.patch` directly to `mocker.patch`. Specifically, refactor `git_branch_mock` in `conftest.py`. Keep `monkeypatch.setattr/setenv/chdir` for environment and path manipulation — this split is idiomatic and correct.

**Files to update**: `tests/conftest.py`

### R5 — Add `pytest-xdist` for CI parallelisation (low-friction speedup)

Add `pytest-xdist>=3.0` to dev dependencies. In the CI full-gate command, add `-n auto`. Do **not** add to `addopts` (it requires explicit `--dist` configuration to work correctly with coverage collection).

**Files to update**: `pyproject.toml`, `.github/workflows/<ci-file>.yml`

### R6 — Add `respx` for LLM API mocking when needed

When scripts that call the Anthropic or OpenAI API are added, add `respx>=0.21` to dev dependencies and mock at the transport layer as shown in Finding 6. This pattern should be documented in `docs/guides/testing.md` so future contributors apply it consistently.

**Files to update**: `pyproject.toml`, `docs/guides/testing.md`

---

## 5. Open Questions

1. **CI workflow file**: No `.github/workflows/` YAML was read during this session. R1 and R5 require reading the actual workflow file to confirm the correct pytest invocation point.

2. **Current coverage baseline**: The actual coverage percentage for `scripts/` is unknown. If below 80%, a remediation sprint is needed before R1 is enforced on `main` (to avoid blocking the branch). Run `pytest --cov=scripts --cov-report=term` to establish the baseline before adding `--cov-fail-under`.

3. **Pre-commit pytest step**: Whether to add `pytest -m "not integration and not slow and not io" -q` to pre-commit hooks depends on how fast the pure-unit suite runs. Measure with `pytest -m "not integration and not slow and not io" --co -q | wc -l` before committing.

4. **Hypothesis adoption scope**: Property-based testing is most valuable for transformation functions with well-defined invariants. If `scripts/` has few pure functions (most interact with I/O), Hypothesis provides limited ROI beyond probing argument parsers.

5. **`pytest-subprocess` vs `mocker.patch("subprocess.run")`**: `pytest-subprocess` is a meaningful ergonomic improvement but not a correctness requirement. If the team prefers to stay with `mocker.patch`, the existing pattern is acceptable — the key improvement is ensuring unexpected subprocess calls raise rather than silently pass.

---

## 6. Sources

| Source | Type | URL | Cache |
|--------|------|-----|-------|
| pytest documentation | Documentation | https://docs.pytest.org/en/stable/ | `.cache/sources/docs-pytest-org-en-stable.md` |
| pytest-cov documentation | Documentation | https://pytest-cov.readthedocs.io/ | `.cache/sources/pytest-cov-readthedocs-io.md` |
| pytest-mock (PyPI) | Documentation | https://pypi.org/project/pytest-mock/ | `.cache/sources/pypi-org-project-pytest-mock.md` |
| Practical Test Pyramid — Fowler | Blog | https://martinfowler.com/articles/practical-test-pyramid.html | `.cache/sources/martinfowler-com-articles-practical-test-pyramid-html.md` |
| coverage.py documentation | Documentation | https://coverage.readthedocs.io/en/latest/ | `.cache/sources/coverage-readthedocs-io-en-latest.md` |
| Hypothesis documentation | Documentation | https://hypothesis.readthedocs.io/en/latest/ | `.cache/sources/hypothesis-readthedocs-io-en-latest.md` |
| `pyproject.toml` (this repo) | Codebase | — | Direct read |
| `tests/conftest.py` (this repo) | Codebase | — | Direct read |
