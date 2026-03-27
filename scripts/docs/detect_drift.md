# `detect\_drift`

detect_drift.py
---------------
Purpose:
    Detects value-encoding drift in .agent.md files by measuring the presence
    of canonical watermark phrases from MANIFESTO.md axioms. A low score
    indicates the agent file may have drifted from foundational values.

Inputs:
    --agents-dir  PATH   Directory of .agent.md files (default: .github/agents/)
    --threshold   FLOAT  Warn if any agent's drift score falls below this value
                         (default: 0.33)
    --fail-below  FLOAT  Exit 1 if any agent scores below this threshold
                         (optional; default: disabled — advisory only)
    --output      FILE   Write JSON report to this file (default: stdout)
    --format      json|summary  Output format (default: json)

Outputs:
    JSON report: { "agents": [{"file", "drift_score", "missing"}],
                   "fleet_avg", "below_threshold" }
    Summary (--format summary): one line per agent with score and status
    Exit code: 0 if all agents meet --fail-below threshold (or no --fail-below
               set); 1 if any agent falls below --fail-below.

Usage examples:
    uv run python scripts/detect_drift.py
    uv run python scripts/detect_drift.py --format summary
    uv run python scripts/detect_drift.py --fail-below 0.5 --output /tmp/drift.json

## Usage

```bash
    uv run python scripts/detect_drift.py
    uv run python scripts/detect_drift.py --format summary
    uv run python scripts/detect_drift.py --fail-below 0.5 --output /tmp/drift.json
```

<!-- hash:0ae4960b7bf92340 -->
