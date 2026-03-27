# `propose\_dogma\_edit`

propose_dogma_edit.py
---------------------
Propose dogma edits to the endogenic substrate using the back-propagation protocol.

Inputs:
  --input <session-file>    Path to a scratchpad session .md file
  --tier T1|T2|T3          Stability tier of the affected section
  --affected-axiom <str>   Name/heading of the affected axiom or section
  --proposed-delta <str>   Brief description of proposed text change (use "-" for stdin)
  --output <path>          Output path for the ADR-style Markdown proposal (default: stdout)

Outputs:
  ADR-style Markdown proposal with Date, Tier, Current Text, Proposed Text,
  Evidence, Coherence Check, Status sections.

Usage:
  uv run python scripts/propose_dogma_edit.py \
    --input .tmp/feat-value-encoding-fidelity/2026-03-09.md \
    --tier T3 \
    --affected-axiom "Focus-on-Descent" \
    --proposed-delta "Add signal-preservation rules for canonical examples" \
    --output /tmp/proposal.md

Exit codes:
  0 — Success, or coherence fails on a tier other than T1
  1 — Coherence check fails and tier is T1 (blocking)

## Usage

```bash
  uv run python scripts/propose_dogma_edit.py \
    --input .tmp/feat-value-encoding-fidelity/2026-03-09.md \
    --tier T3 \
    --affected-axiom "Focus-on-Descent" \
    --proposed-delta "Add signal-preservation rules for canonical examples" \
    --output /tmp/proposal.md
```

<!-- hash:ed9cd0a4ee4ee0d3 -->
