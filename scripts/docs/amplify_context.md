# `amplify\_context`

amplify_context.py — Context-Sensitive Axiom Amplification.

Purpose:
    Programmatic encoding of the Context-Sensitive Amplification lookup table
    from AGENTS.md. Given a task-type keyword, returns the amplified axiom
    name and expression hint for the session encoding checkpoint.

    The amplification table is loaded at startup from
    ``data/amplification-table.yml`` — update that file when AGENTS.md adds,
    removes, or renames rows. No code changes are required.

Inputs:
    Positional argument: task-type keyword (e.g. "research", "commit", "script")
    OR --list to print the full table.

Outputs:
    Matched row printed to stdout (text or JSON).
    Non-zero exit on no match or --list.

Usage:
    uv run python scripts/amplify_context.py research
    uv run python scripts/amplify_context.py commit --format json
    uv run python scripts/amplify_context.py --list

Exit codes:
    0 = keyword matched, result printed
    1 = no match (all rows printed as reference) or --list flag used
    2 = invalid arguments

## Usage

```bash
    uv run python scripts/amplify_context.py research
    uv run python scripts/amplify_context.py commit --format json
    uv run python scripts/amplify_context.py --list
```

<!-- hash:c57ecfc7119d7485 -->
