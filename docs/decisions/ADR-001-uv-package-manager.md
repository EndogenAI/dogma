# ADR-001: Adopt `uv` as the Sole Python Package and Environment Manager

**Date**: 2026-03-07
**Status**: Accepted
**Deciders**: EndogenAI core team

---

## Context

This project requires a Python toolchain that:
- Manages virtual environments and dependencies in a single tool
- Produces a lockfile for reproducible installs across machines and CI
- Supports fast installs (critical for CI and agent-driven scripting)
- Works cleanly with `pyproject.toml` as the single configuration source
- Satisfies the Local Compute-First axiom — minimal cloud dependency, fast local startup

Alternatives considered: `pip` + `venv`, `poetry`, `pipenv`, `conda`, `hatch`.

## Decision

**Use `uv` exclusively.** All scripts are invoked via `uv run python scripts/<name>.py`. All dependency management uses `uv add`, `uv sync`, and `uv lock`. No other tool is used for package or environment management.

`poetry` was the strongest alternative but `uv` is 10–100× faster on install, has a simpler mental model (single binary, no separate virtualenv step), and is more aligned with the emerging `pyproject.toml`-native ecosystem.

## Consequences

- **AGENTS.md** guardrail: "Always use `uv run` — never invoke Python or package executables directly."
- `uv.lock` must be committed and kept current.
- A `.python-version` file should be added (`uv python pin <version>`) to close the environment reproducibility gap.
- CI must use `uv sync` before all test runs.
- Scripts that call subprocesses must use `uv run` for nested Python invocations.

## References

- [`docs/research/dev-workflow-automations.md`](../research/dev-workflow-automations.md) — F7: uv + uv.lock + .python-version = full reproducibility
- [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
