# `check\_substrate\_health`

scripts/check_substrate_health.py

CRD (cross-reference density) health check for startup-loaded substrate files.

Cross-reference density measures how many references in a file point to intra-subsystem
sources (MANIFESTO.md, AGENTS.md, CONTRIBUTING.md, README.md) vs. external subsystems
(docs/, scripts/, .github/). A CRD below 0.25 in files that agents load at session start
signals drift risk — the file has shifted from encoding core principles toward referencing
implementation details.

Purpose:
    Check CRD for all startup-loaded substrate files and report PASS/WARN/BLOCK status.
    Emit a structured per-file report and exit 1 if any file is below the block threshold.

    With --atlas: load data/substrate-atlas.yml and print a summary table of substrates
    by validation mechanism; highlight substrates with validation: none as WARN.

Inputs:
    --warn-below     CRD threshold below which STATUS = WARN  (default: 0.25)
    --block-below    CRD threshold below which STATUS = BLOCK (default: 0.10)
    --files          Space-separated list of files to check (relative to repo root).
                     Defaults to the hardcoded startup-loaded file list.
    --atlas          Print a substrate atlas summary (loads data/substrate-atlas.yml).
                     Existing CRD functionality is unchanged when this flag is absent.

Outputs:
    stdout: Structured report — one row per file: FILE | CRD | STATUS
    stderr: Nothing (all output goes to stdout)

Exit codes:
    0  All files pass or warn (no BLOCK-level CRD)
    1  One or more files are below the block threshold (CRD < --block-below)
       Also exits 1 if a listed file does not exist.
       Also exits 1 if --atlas is given and data/substrate-atlas.yml cannot be loaded.

Usage examples:
    # Check all default startup-loaded files
    uv run python scripts/check_substrate_health.py

    # Use custom thresholds
    uv run python scripts/check_substrate_health.py --warn-below 0.30 --block-below 0.15

    # Check a custom file list
    uv run python scripts/check_substrate_health.py --files AGENTS.md MANIFESTO.md

    # Print substrate atlas summary (highlights unvalidated substrates)
    uv run python scripts/check_substrate_health.py --atlas

    # Integrate into CI lint job (non-zero exit blocks the job)
    uv run python scripts/check_substrate_health.py || exit 1

## Usage

```bash
    # Check all default startup-loaded files
    uv run python scripts/check_substrate_health.py

    # Use custom thresholds
    uv run python scripts/check_substrate_health.py --warn-below 0.30 --block-below 0.15

    # Check a custom file list
    uv run python scripts/check_substrate_health.py --files AGENTS.md MANIFESTO.md

    # Print substrate atlas summary (highlights unvalidated substrates)
    uv run python scripts/check_substrate_health.py --atlas

    # Integrate into CI lint job (non-zero exit blocks the job)
    uv run python scripts/check_substrate_health.py || exit 1
```

<!-- hash:9b1c881e7a660adc -->
