# `validate\_handoff\_permeability`

validate_handoff_permeability.py
--------------------------------

Purpose:
    Validates that cross-substrate handoffs preserve required signal types per
    membrane layer in agent fleet communication. Implements the signal preservation
    rules from AGENTS.md § Agent Communication → Focus-on-Descent / Compression-on-Ascent.

    Membranes in agent fleet communication enforce signal preservation while allowing
    context compression. This function validates that critical knowledge (Canonical
    examples, axiom citations) survives handoffs even when narrative context is
    compressed. This prevents value-encoding drift and ensures endogenous knowledge
    remains intact across delegation boundaries.

Inputs:
    --handoff-file PATH      Path to markdown file containing handoff text
    --membrane-type TYPE     One of: scout-to-synthesizer, synthesizer-to-reviewer,
                             reviewer-to-archivist
    --required-signals LIST  Comma-separated signal types to validate (optional;
                             defaults to all signals for membrane type)
    --output FILE            Write JSON report to file (default: stdout)
    --format json|text       Output format (default: json)

Outputs:
    JSON report:
    {
        "status": "pass" | "fail",
        "membrane_type": str,
        "missing_signals": [str],      # signal types not found
        "found_signals": [str],        # signal types detected
        "signal_counts": {             # detailed counts per signal type
            "canonical_example": int,
            "anti_pattern": int,
            "axiom_citation": int,
            "source_url": int
        },
        "warnings": [str],             # non-critical issues
        "report": str                  # human-readable markdown report
    }
    Exit code: 0 on success (pass or fail verdict clear); 1 on configuration error.

Usage examples:
    uv run python scripts/validate_handoff_permeability.py \
        --handoff-file .tmp/branch/2026-03-10.md \
        --membrane-type scout-to-synthesizer

    uv run python scripts/validate_handoff_permeability.py \
        --handoff-file /tmp/handoff.md \
        --membrane-type synthesizer-to-reviewer \
        --format text

## Usage

```bash
    uv run python scripts/validate_handoff_permeability.py \
        --handoff-file .tmp/branch/2026-03-10.md \
        --membrane-type scout-to-synthesizer

    uv run python scripts/validate_handoff_permeability.py \
        --handoff-file /tmp/handoff.md \
        --membrane-type synthesizer-to-reviewer \
        --format text
```

<!-- hash:7ec19d7c1acdd0e9 -->
