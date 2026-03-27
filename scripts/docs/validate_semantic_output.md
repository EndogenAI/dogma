# `validate\_semantic\_output`

scripts/validate_semantic_output.py
-------------------------------------
Validates agent return tokens against a declared output format and token ceiling.

Purpose:
    Enforces the Focus-on-Descent / Compression-on-Ascent contract from AGENTS.md:
    subagent output must match the declared format (bullets, table, single-line)
    and must not exceed the declared token ceiling.

    Tokens are approximated as: ceil(word_count / 0.75) — matches GPT-style
    tokenisation closely enough for ceiling enforcement without requiring a
    tokeniser library.

Inputs:
    --format <bullets|table|single-line>  Required. Declared format.
    --ceiling <N>                         Required. Maximum token count (integer).
    text positional arg or stdin          The agent output text to validate.

Outputs:
    Prints "OK: format=<format> tokens=<n> ceiling=<N>" on success.
    Prints "FORMAT MISMATCH: ..." on format violation.
    Prints "CEILING EXCEEDED: ..." on token overflow.

Usage example:
    echo "- item one
- item two" | uv run python scripts/validate_semantic_output.py --format bullets --ceiling 50
    uv run python scripts/validate_semantic_output.py --format single-line --ceiling 20 "Done."

Exit codes:
    0 — format matches AND token count <= ceiling
    1 — format mismatch
    2 — ceiling exceeded (format matched but too many tokens)

References:
    - AGENTS.md § Agent Communication — Focus-on-Descent / Compression-on-Ascent

## Usage

```bash
    echo "- item one
- item two" | uv run python scripts/validate_semantic_output.py --format bullets --ceiling 50
    uv run python scripts/validate_semantic_output.py --format single-line --ceiling 20 "Done."
```

<!-- hash:3db617e214cc221d -->
