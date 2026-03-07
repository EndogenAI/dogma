# Automated Testing in Endogenic Development

> Tests encode known-good behavior and prevent re-discovery of bugs. Every script ships with its tests.

---

## Why We Test

Testing is not optional in this project. It is a first-class value encoded in [`MANIFESTO.md`](../../MANIFESTO.md#testing-first). Here's why:

### 1. Tests Encode Specification

A test suite is a **living specification** of what a script does. When you modify a script, the tests document:
- What inputs are valid
- What outputs are expected
- What edge cases matter
- What error conditions exist

Without tests, this knowledge lives only in the author's head (or in past sessions you've forgotten).

### 2. Tests Prevent Regression

When you modify a script (or when an agent modifies it), tests catch breakage immediately:
- **Interactive debugging is expensive**: Without tests, an agent discovers a bug by running the script, seeing it fail, and iterating to fix it. That's token burn.
- **Tests are cheap**: A test fails immediately, the error is clear, and the fix is quick.
- **Re-discovery is expensive**: If a bug slips past, the next session that touches the script will re-discover it interactively. Tests prevent that re-discovery.

### 3. Tests Reduce Review Burden

Code review becomes deterministic:
- **Without tests**: "Does this look right?" (subjective, error-prone, relies on reviewer attention)
- **With tests**: "Do tests pass?" (objective, deterministic, automated)

A test failure is evidence; passing tests are confidence.

### 4. Tests Are Executable Documentation

Reading a test shows exactly:
- How to invoke the script
- What command-line flags exist
- What outputs are expected
- How errors are reported

This is more precise than a README.

### 5. Tests Reduce Token Burn

If a script is broken, an agent discovers it via test failure (fast, deterministic) instead of re-discovering the bug interactively (slow, expensive in tokens).

---

## Test Structure

### Directory Layout

```
tests/
  __init__.py
  conftest.py              # Shared fixtures (tmp_repo, git_branch_mock, samples)
  test_prune_scratchpad.py # Tests for prune_scratchpad.py
  test_scaffold_agent.py   # Tests for scaffold_agent.py
  test_validate_synthesis.py
  test_fetch_source.py
  test_remaining_scripts.py # Other scripts (scaffold_workplan, generate_agent_manifest, etc.)
```

### Test File Naming

- **test_<script_name>.py** for each script in `scripts/`
- Test classes: **Test<FunctionName>** or **Test<Feature>**
- Test functions: **test_<scenario>**

Example:
```python
class TestPruneScrapbookAnnotation:
    def test_annotate_adds_line_ranges(self):
        """Annotation adds [Lstart–Lend] to H2 headings."""
```

### Test Markers

Tests are marked by category for selective runs:

```python
@pytest.mark.io          # Tests that perform file I/O
@pytest.mark.integration  # Tests that hit network or external systems
@pytest.mark.slow        # Tests that take >1 second
```

Usage:
```bash
# Run all tests
uv run pytest tests/

# Run only fast tests (skip slow + integration)
uv run pytest tests/ -m "not slow and not integration"

# Run only unit tests (no I/O)
uv run pytest tests/ -m "not io"

# Run only integration tests
uv run pytest tests/ -m integration
```

---

## Test Fixtures

Test fixtures (in `tests/conftest.py`) provide reusable test data and mocks:

### `tmp_repo` — Isolated Git Repository

```python
def test_git_aware_script(tmp_repo):
    """Test a script that calls git commands."""
    result = subprocess.run(["python", "scripts/my_script.py"], cwd=tmp_repo)
    assert result.returncode == 0
```

Yields a temporary git repo with:
- `git init` already run
- User configured
- Initial commit made

### `git_branch_mock` — Mock Git Branch

```python
def test_with_custom_branch(git_branch_mock):
    """Test script behavior on different branches."""
    git_branch_mock("feat/custom-branch")
    # Script now sees: git rev-parse --abbrev-ref HEAD → feat/custom-branch
```

### `sample_markdown`, `sample_agent_md`, `sample_d3_synthesis` — Test Data

Fixtures that provide valid sample content for testing validation and parsing:

```python
def test_annotates_markdown(tmp_path, sample_markdown):
    """Test against real markdown structure."""
    file = tmp_path / "test.md"
    file.write_text(sample_markdown["content"])
    # Test annotation logic
```

---

## Writing Tests

### 1. Test Happy Path + Error Cases

```python
class TestScaffoldAgent:
    def test_creates_valid_agent(self):
        """Happy path: valid args → agent file created."""
        # Successful case
    
    def test_rejects_missing_name(self):
        """Error case: missing --name → exit 1."""
        # Error case
    
    def test_rejects_description_too_long(self):
        """Error case: description >200 chars → exit 1."""
        # Error case
```

### 2. Test Exit Codes Explicitly

Every script has documented exit codes. Test them:

```python
def test_exit_codes():
    result = subprocess.run([...])
    assert result.returncode == 0  # Success
    # OR
    assert result.returncode == 1  # Expected failure
```

### 3. Use Descriptive Docstrings

The docstring is the test specification:

```python
def test_annotate_idempotent(self):
    """Annotating twice produces identical result (idempotent)."""
    # Test body
```

When this test fails, the docstring tells you what property was violated.

### 4. Test Isolation

Each test should:
- Be **independent** (not depend on side effects of other tests)
- Use **tmp_path** or fixtures to create isolated environments
- **Clean up after itself** (pytest handles tmp_path cleanup automatically)

### 5. Avoid Mocking Unless Necessary

- **Prefer real files**: Use `tmp_path` for file I/O tests (not mocked filesystem)
- **Mock network**: Mock HTTP calls (network is external)
- **Mock git commands**: If testing script behavior on different branches (git calls are slow)

Examples:
```python
# Good: Real file I/O
@pytest.mark.io
def test_creates_file(tmp_path):
    script_path = tmp_path / "test.md"
    script_path.write_text("content")
    assert script_path.exists()

# Good: Mocked network
@pytest.mark.integration
def test_handles_404(monkeypatch):
    def mock_request(*args, **kwargs):
        return MagicMock(status_code=404)
    monkeypatch.setattr(requests, "get", mock_request)
```

---

## Mocking Conventions

### Use `mocker.patch` for callable mocking

Always use `mocker.patch` (from `pytest-mock`) when replacing callables where call assertions (`assert_called_once_with`, etc.) are needed. Never use the `@patch` decorator on test functions — it obscures setup order and complicates parametrised tests.

```python
# Correct
def test_reads_branch(mocker):
    mocker.patch("subprocess.run", return_value=MagicMock(stdout=b"main", returncode=0))
    assert get_current_branch() == "main"

# Do not use
@patch("subprocess.run")
def test_reads_branch(mock_run):
    mock_run.return_value = MagicMock(stdout=b"main", returncode=0)
    assert get_current_branch() == "main"
```

Keep `monkeypatch.setattr/setenv/chdir` for environment variables, working directory, and attribute replacements where no call assertions are needed.

### HTTP mocking: `urllib.request.urlopen`

`fetch_source.py` uses `urllib.request` (stdlib). Neither `respx` nor `responses` intercepts stdlib urllib calls. The correct mock boundary is `urllib.request.urlopen` itself:

```python
def test_fetch_caches_response(tmp_path, mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.read.return_value = b"<html><body>Test content</body></html>"
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("urllib.request.urlopen", return_value=mock_resp)
```

Matching mock library to HTTP client is mandatory — using the wrong library means calls pass through unintercepted.

### Subprocess mocking: `pytest-subprocess`

For scripts that invoke `subprocess.run` (git operations, etc.), `pytest-subprocess` (`fake_process` fixture) is preferred over hand-crafted `MagicMock` replacements. It raises `ProcessNotRegisteredError` on unexpected calls, surfacing gaps that a blanket `MagicMock` would silently swallow.

```python
def test_git_branch(fake_process):
    fake_process.register_subprocess(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout="main"
    )
    assert get_current_branch() == "main"
```

Add `pytest-subprocess>=1.5` to dev dependencies in `pyproject.toml`.

### LLM API mocking: `respx`

If scripts call the Anthropic SDK (which uses `httpx` internally), mock at the HTTP transport layer using `respx` — not at the SDK client level. Mocking SDK methods creates tests tied to SDK internals that break on version upgrades.

```python
import respx, httpx

@respx.mock
def test_llm_call():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(200, json={
            "content": [{"type": "text", "text": "stub response"}]
        })
    )
    result = call_summary_api(prompt="test")
    assert result == "stub response"
```

Add `respx>=0.21` to dev dependencies when first needed.

---

## Running Tests

### Local Development

```bash
# Run all tests
uv run pytest tests/

# Run with coverage report
uv run pytest tests/ --cov=scripts --cov-report=html

# Run only fast tests (development loop)
uv run pytest tests/ -m "not slow and not integration" -v

# Run single test file
uv run pytest tests/test_scaffold_agent.py -v

# Run single test
uv run pytest tests/test_scaffold_agent.py::TestScaffoldAgentValidation::test_requires_name_and_description -v

# Watch mode (requires pytest-watch)
ptw tests/

# Parallel runs (optional — CI speedup with pytest-xdist)
uv run pytest tests/ -n auto
```

> **`pytest-xdist` (optional)**: `-n auto` requires `pytest-xdist>=3.0` as a dev dependency. Not required currently — the test suite runs in seconds — but available as a no-configuration CI speedup. Do **not** add `-n auto` to `addopts` without additional `--dist` configuration; it requires extra setup to work correctly alongside coverage collection.

### Continuous Integration

Tests are run on every commit (see `.github/workflows/tests.yml`):

```bash
# CI runs this before allowing merge
uv run pytest tests/ --cov=scripts --cov-report=term-missing --cov-fail-under=80
```

If coverage drops below 80%, the PR is blocked.

> **Note**: Do not add `--cov` to `addopts` in `pyproject.toml`. Coverage collection in `addopts` adds overhead to every local `pytest` run and conflicts with `pytest-xdist` (`-n auto`). The CI command above is the correct and only enforcement point for the coverage gate.

---

## Test Requirements and Coverage

### Minimum Test Coverage

Every script must have:
- **Unit tests**: Happy path + all error cases
- **Integration tests**: For I/O and network operations (marked `@pytest.mark.integration`)
- **≥80% code coverage** (measured by `pytest-cov`)
- **Exit code coverage**: Every `sys.exit(N)` is tested

### Coverage Report

```bash
uv run pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```

The HTML report shows:
- Which lines are covered
- Which lines are not covered
- Coverage % per file

### Coverage Exceptions

Some code can be excluded from coverage using `# pragma: no cover`:

```python
if __name__ == "__main__":  # pragma: no cover
    main()
```

Use sparingly. Most code should be tested.

---

## Common Test Patterns

### Testing File Operations

```python
@pytest.mark.io
def test_writes_file(tmp_path):
    """Script writes file to expected location."""
    output_file = tmp_path / "output.md"
    subprocess.run(["python", "scripts/my_script.py", str(output_file)])
    assert output_file.exists()
    assert "expected content" in output_file.read_text()
```

### Testing Exit Codes

```python
def test_exit_on_error():
    """Script exits 1 on validation error."""
    result = subprocess.run(["python", "scripts/my_script.py", "--invalid-flag"])
    assert result.returncode == 1
```

### Testing CLI Arguments

```python
def test_respects_flag():
    """--flag changes behavior."""
    result1 = subprocess.run(["python", "scripts/my_script.py"])
    result2 = subprocess.run(["python", "scripts/my_script.py", "--dry-run"])
    assert result1.stdout != result2.stdout
```

### Testing Idempotency

```python
def test_idempotent_annotation(tmp_path, sample_markdown):
    """Annotating twice produces same result."""
    file = tmp_path / "test.md"
    file.write_text(sample_markdown["content"])
    
    # Annotate once
    subprocess.run(["python", "scripts/prune_scratchpad.py", "--annotate", str(file)])
    content1 = file.read_text()
    
    # Annotate again
    subprocess.run(["python", "scripts/prune_scratchpad.py", "--annotate", str(file)])
    content2 = file.read_text()
    
    assert content1 == content2  # Idempotent
```

---

## Debugging Failed Tests

### Verbose Output

```bash
uv run pytest tests/test_prune_scratchpad.py -vv
```

`-vv` shows full output and diffs.

### Stop on First Failure

```bash
uv run pytest tests/ -x  # Stop after first failure
```

Useful for development.

### Print Debug Output

```python
def test_something(capsys):
    print("Debug info")
    result = run_script()
    print(f"Result: {result}")
    captured = capsys.readouterr()
    print(captured.out)
```

### Interactive Debugging

```bash
uv run pytest tests/ --pdb  # Drop to debugger on failure
```

---

## Adding Tests to a New Script

Before committing a new script:

1. Create `tests/test_<script_name>.py`
2. Add test classes for each major function/feature
3. Write tests for happy path + all error cases
4. Run locally: `uv run pytest tests/test_<script_name>.py -v`
5. Check coverage: `uv run pytest tests/test_<script_name>.py --cov=scripts`
6. Ensure coverage ≥80%
7. Commit script + tests together

Example commit:
```
feat(scripts): add my_script.py

- Implements feature X
- Tests cover happy path, error cases, exit codes
- Coverage: 85%
```

---

## When Tests Fail in CI

If tests fail on GitHub (but pass locally):

1. **Check Python version**: CI runs on Python 3.9+; your local environment might differ.
   ```bash
   python --version
   uv py list  # Show available Python versions
   ```

2. **Check environment differences**: CI has a clean environment; your local machine might have extra packages.
   ```bash
   uv pip list  # Show installed packages
   ```

3. **Re-run tests locally**: Delete `.pytest_cache` and try again.
   ```bash
   rm -rf .pytest_cache
   uv run pytest tests/
   ```

4. **Check for git issues**: Some tests depend on git state.
   ```bash
   git status  # Any uncommitted changes?
   git log --oneline -3  # Recent commits?
   ```

---

## Resources

- [`tests/conftest.py`](../../tests/conftest.py) — Shared fixtures
- [`pyproject.toml`](../../pyproject.toml) — Pytest configuration
- [Pytest documentation](https://docs.pytest.org/en/latest/)
- [Pytest fixtures](https://docs.pytest.org/en/latest/fixture.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

*This guide is a living document. As testing practices evolve, update this guide and the test suite together.*
