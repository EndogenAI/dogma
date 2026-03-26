# `verify-script-usage`

verify-script-usage.py — Pre-commit hook that flags CLI invocations in agent/skill
markdown files without adjacent --help verification.

Inputs: one or more .md file paths (passed by pre-commit as positional args)
Outputs: exit 0 if clean (or advisory mode), exit 1 if violations found + --strict
Usage:
    uv run python scripts/verify-script-usage.py .github/agents/my-agent.agent.md
    uv run python scripts/verify-script-usage.py --strict .github/agents/my-agent.agent.md
    uv run python scripts/verify-script-usage.py --help

## Usage

```bash
    uv run python scripts/verify-script-usage.py .github/agents/my-agent.agent.md
    uv run python scripts/verify-script-usage.py --strict .github/agents/my-agent.agent.md
    uv run python scripts/verify-script-usage.py --help
```

<!-- hash:f0364472040f267e -->
