---
Status: Accepted
Date: 2026-03-07
Deciders: EndogenAI core team
---

# ADR-001: Adopt `uv` as the Sole Python Package and Environment Manager

---

## Context

This project requires a Python toolchain that:
- Manages virtual environments and dependencies in a single tool
- Produces a lockfile for reproducible installs across machines and CI
- Supports fast installs (critical for CI and agent-driven scripting)
- Works cleanly with `pyproject.toml` as the single configuration source
- Satisfies the Local Compute-First axiom — minimal cloud dependency, fast local startup

## Decision Drivers

- Single-tool philosophy: avoid managing multiple separate tools (`pip`, `venv`, `virtualenv`)
- Reproducible installs via lockfile: critical for CI and agent-driven scripting across machines
- Speed: `uv` is 10–100× faster than `pip`+`venv` for install operations

## Considered Options

1. `pip` + `venv` — standard but slow, no single lockfile, fragmented tooling
2. `poetry` — feature-rich but heavier; slower than `uv`; separate `pyproject.toml` divergence
3. `pipenv` — declining ecosystem adoption; known performance issues
4. `conda` — too heavyweight for a pure-Python project; cloud-dependency risk
5. `hatch` — fewer guarantees on lock reproducibility at the time of evaluation
6. `uv` — fast, unified, lockfile-native, `pyproject.toml`-aligned (**chosen**)

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

- [`docs/research/dev-workflow-automations.md`](../research/infrastructure/dev-workflow-automations.md) — F7: uv + uv.lock + .python-version = full reproducibility
- [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
