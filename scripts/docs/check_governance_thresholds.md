# `check\_governance\_thresholds`

scripts/check_governance_thresholds.py

Evaluate encoding coverage and cross-reference density metrics against
thresholds defined in data/governance-thresholds.yml. Exits 0 if all
thresholds pass; exits 1 if any threshold is breached (caller should open
a tracking issue). Used by .github/workflows/quarterly-audit.yml.

Purpose:
    Implements the T4 enforcement gate for the quarterly values review cycle
    (issue #386). Reads pre-generated metric outputs (encoding_coverage.py
    stdout and measure_cross_reference_density.py --output JSON) and compares
    them against documented thresholds. If any metric is below its threshold,
    prints a failure report to stdout and exits 1.

    This script is intentionally decoupled from the metric-collection scripts
    so it can be unit-tested independently without filesystem side effects.

Inputs:
    --encoding-output FILE   Text output from encoding_coverage.py (required)
    --crd-json FILE          JSON output from measure_cross_reference_density.py
                             (required)
    --thresholds FILE        Path to governance-thresholds.yml
                             (default: data/governance-thresholds.yml)

Outputs:
    stdout: Pass/fail summary with metric values and thresholds
    exit 0: All thresholds pass
    exit 1: One or more thresholds breached (breach details on stdout)
    exit 2: I/O error (missing file, malformed YAML/JSON)

Usage examples:
    # Typical CI invocation (after running the metric scripts):
    uv run python scripts/encoding_coverage.py > /tmp/enc.txt
    uv run python scripts/measure_cross_reference_density.py --output /tmp/crd.json
    uv run python scripts/check_governance_thresholds.py \
        --encoding-output /tmp/enc.txt \
        --crd-json /tmp/crd.json

    # With explicit thresholds file:
    uv run python scripts/check_governance_thresholds.py \
        --encoding-output /tmp/enc.txt \
        --crd-json /tmp/crd.json \
        --thresholds data/governance-thresholds.yml

## Usage

```bash
    # Typical CI invocation (after running the metric scripts):
    uv run python scripts/encoding_coverage.py > /tmp/enc.txt
    uv run python scripts/measure_cross_reference_density.py --output /tmp/crd.json
    uv run python scripts/check_governance_thresholds.py \
        --encoding-output /tmp/enc.txt \
        --crd-json /tmp/crd.json

    # With explicit thresholds file:
    uv run python scripts/check_governance_thresholds.py \
        --encoding-output /tmp/enc.txt \
        --crd-json /tmp/crd.json \
        --thresholds data/governance-thresholds.yml
```

<!-- hash:b551c30fb4f909e6 -->
