# `check\_plan\_to\_intent\_drift`

Detect plan-to-intent drift: workplan deliverables vs. intent contract.

Purpose:
    Detect plan-to-intent drift: workplan completion that diverges from the
    original user intent. Compares workplan acceptance criteria against an
    intent contract file. Source: readiness-false-positive-analysis.md Rec 4.

Inputs:
    --workplan  PATH  : path to workplan .md file
    --contract  PATH  : path to intent-contract.yml or intent-contract.md
                        (optional; if omitted, looks for docs/plans/<slug>/intent-contract.md)
    --check     FLAG  : dry-run, print findings but always exit 0

Outputs:
    Exit 0  : contract satisfied (or --check mode, or no contract found)
    Exit 1  : drift detected (deliverables don't cover contract intent)
    Stdout  : list of uncovered acceptance test items from the contract

Usage:
    uv run python scripts/check_plan_to_intent_drift.py --workplan docs/plans/foo.md
    uv run python scripts/check_plan_to_intent_drift.py --workplan docs/plans/foo.md         --contract docs/plans/foo/intent-contract.yml

## Usage

```bash
    uv run python scripts/check_plan_to_intent_drift.py --workplan docs/plans/foo.md
    uv run python scripts/check_plan_to_intent_drift.py --workplan docs/plans/foo.md         --contract docs/plans/foo/intent-contract.yml
```

<!-- hash:0a2d386f6ee13a9c -->
