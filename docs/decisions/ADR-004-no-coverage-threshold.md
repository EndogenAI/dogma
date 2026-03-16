---
Status: Accepted
Date: 2026-03-07
Deciders: EndogenAI core team
---

# ADR-004: Do Not Enforce a Coverage Percentage Threshold in CI

---

## Context

The CI pipeline runs `pytest --cov=scripts` to measure code coverage. A `--cov-fail-under=80` threshold was added with the intent of preventing untested code from shipping.

In practice, the test suite achieves approximately **6% direct import coverage** of `scripts/` even when all 100+ tests pass. The reason: the majority of tests invoke scripts via `subprocess.run(["uv", "run", "python", "scripts/..."])` rather than importing script functions directly. Subprocess invocations spawn a child process; coverage tooling only measures the parent process. Only `test_seed_labels.py` uses a direct import pattern (`sys.path.insert + import seed_labels`), which is why `seed_labels.py` shows ~90% coverage while all other scripts show 0%.

The 80% threshold was copied from general project templates without accounting for this structural difference. Its effect in practice:
- It causes a CI failure that is misleading — tests are full and meaningful, but coverage numbers suggest no testing at all.
- It discourages the subprocess testing pattern, which is appropriate here because scripts expose `if __name__ == "__main__"` entry points designed for subprocess invocation.

## Decision Drivers

- Coverage percentage is structurally inaccurate for subprocess-style tests (child process not instrumented)
- The 80% threshold was copied from templates without project-specific validation; it produced misleading CI failures
- Test quality is better evaluated by exit codes and test case content than by a coverage number

## Considered Options

1. **Keep `--cov-fail-under=80`** — causes misleading CI failures; discourages the correct subprocess testing pattern
2. **Lower threshold (e.g. `--cov-fail-under=10`)** — arbitrary; still inaccurate and misleading
3. **Remove `--cov-fail-under` entirely; keep coverage reporting** — honest signal; Codecov still shows trends (**chosen**)
4. **Migrate all tests to direct-import pattern** — significant rework; inappropriate for CLI-entry-point scripts

## Decision

**Remove `--cov-fail-under=N` from CI.** Coverage is still measured and uploaded to Codecov for visibility and trend tracking, but it is not a gate.

## Consequences

- CI `test:` job no longer fails because of low measured coverage.
- Codecov still receives `coverage.xml` on every push; trend graphs remain useful for tracking progress if the codebase migrates toward direct-import test patterns.
- Future scripts that export testable functions (rather than only a CLI entry point) should follow the `test_seed_labels.py` import pattern to achieve meaningful coverage numbers.

## The Right Coverage Signal

Coverage numbers are meaningful only when tests import modules directly. For this project:

| Test approach | Coverage measured | Coverage accurate? |
|---|---|---|
| `subprocess.run(["uv", "run", "python", "scripts/..."])` | ~0% | No — child process not instrumented |
| `sys.path.insert + import script_module` | Full function coverage | Yes |

The test suite quality for subprocess-style tests is best evaluated by reading test cases and checking exit codes, not by a coverage percentage.

## References

- [`tests/test_seed_labels.py`](../../tests/test_seed_labels.py) — canonical example of direct-import test pattern
- [`pyproject.toml`](../../pyproject.toml) — `[tool.coverage.run]` configuration
- [`AGENTS.md`](../../AGENTS.md) — Testing-First Requirement for Scripts
