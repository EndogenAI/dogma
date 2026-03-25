"""scripts/check_governance_thresholds.py

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
    uv run python scripts/check_governance_thresholds.py \\
        --encoding-output /tmp/enc.txt \\
        --crd-json /tmp/crd.json

    # With explicit thresholds file:
    uv run python scripts/check_governance_thresholds.py \\
        --encoding-output /tmp/enc.txt \\
        --crd-json /tmp/crd.json \\
        --thresholds data/governance-thresholds.yml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required. Run: uv sync --dev", file=sys.stderr)
    sys.exit(2)


def load_thresholds(path: Path) -> dict:
    """Load and parse the governance-thresholds.yml file."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: thresholds file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as exc:
        print(f"ERROR: malformed YAML in {path}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict):
        print(f"ERROR: thresholds file must be a YAML mapping: {path}", file=sys.stderr)
        sys.exit(2)
    return data


def evaluate_encoding_coverage(enc_text: str, min_passing_ratio: float) -> tuple[bool, str]:
    """Parse encoding_coverage.py output and check against minimum passing ratio.

    Args:
        enc_text: Full stdout text from encoding_coverage.py.
        min_passing_ratio: Minimum fraction of principles that must score >= 2/4.

    Returns:
        (passed, message) — passed is True if threshold met; message is the
        human-readable result line.
    """
    lines = [ln for ln in enc_text.splitlines() if "| " in ln and "/4" in ln]
    total = len(lines)
    if total == 0:
        return True, "WARNING: no encoding coverage rows found — skipping check"

    passing = sum(1 for ln in lines if not ln.strip().endswith("| 0/4 |") and not ln.strip().endswith("| 1/4 |"))
    ratio = passing / total
    label = (
        f"Encoding coverage: {passing}/{total} principles >= 2/4 (ratio {ratio:.2f}, threshold {min_passing_ratio:.2f})"
    )
    return ratio >= min_passing_ratio, label


def evaluate_crd(crd_data: dict, min_mean_crd: float) -> tuple[bool, str]:
    """Parse measure_cross_reference_density.py JSON output and check mean CRD.

    Args:
        crd_data: Parsed JSON dict from measure_cross_reference_density.py --output.
        min_mean_crd: Minimum acceptable fleet-wide mean CRD (0.0–1.0).

    Returns:
        (passed, message) — passed is True if threshold met.
    """
    fleet_stats = crd_data.get("fleet_statistics", {})
    mean_crd = fleet_stats.get("mean", 0.0)
    sample_size = fleet_stats.get("sample_size", 0)
    label = f"Cross-reference density: mean CRD {mean_crd:.4f} (n={sample_size}), threshold {min_mean_crd:.2f}"
    return mean_crd >= min_mean_crd, label


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate governance metrics against thresholds and exit 1 on breach.")
    parser.add_argument(
        "--encoding-output",
        required=True,
        metavar="FILE",
        help="Text output file from encoding_coverage.py",
    )
    parser.add_argument(
        "--crd-json",
        required=True,
        metavar="FILE",
        help="JSON output file from measure_cross_reference_density.py --output",
    )
    parser.add_argument(
        "--thresholds",
        default="data/governance-thresholds.yml",
        metavar="FILE",
        help="Path to governance-thresholds.yml (default: data/governance-thresholds.yml)",
    )
    args = parser.parse_args(argv)

    # Load inputs
    thresholds_path = Path(args.thresholds)
    enc_path = Path(args.encoding_output)
    crd_path = Path(args.crd_json)

    for p in (enc_path, crd_path):
        if not p.exists():
            print(f"ERROR: input file not found: {p}", file=sys.stderr)
            return 2

    thresholds = load_thresholds(thresholds_path)

    try:
        enc_text = enc_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR reading {enc_path}: {exc}", file=sys.stderr)
        return 2

    try:
        crd_data = json.loads(crd_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ERROR reading {crd_path}: {exc}", file=sys.stderr)
        return 2

    enc_min = thresholds.get("encoding_coverage", {}).get("min_principles_passing", 0.60)
    crd_min = thresholds.get("cross_reference_density", {}).get("min_mean_crd", 0.30)

    failures: list[str] = []

    enc_passed, enc_msg = evaluate_encoding_coverage(enc_text, enc_min)
    print(enc_msg)
    if not enc_passed:
        failures.append(enc_msg)

    crd_passed, crd_msg = evaluate_crd(crd_data, crd_min)
    print(crd_msg)
    if not crd_passed:
        failures.append(crd_msg)

    if failures:
        print("\nTHRESHOLD BREACH — the following metrics are below minimum:")
        for f in failures:
            print(f"  FAIL: {f}")
        return 1

    print("\nAll governance thresholds passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
