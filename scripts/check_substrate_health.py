"""scripts/check_substrate_health.py

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
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Import CRD computation utilities from sibling script.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from measure_cross_reference_density import extract_references  # noqa: E402

# ---------------------------------------------------------------------------
# Default startup-loaded file list
# ---------------------------------------------------------------------------

DEFAULT_FILES: list[str] = [
    "AGENTS.md",
    ".github/agents/executive-orchestrator.agent.md",
    ".github/agents/executive-docs.agent.md",
    ".github/agents/executive-researcher.agent.md",
    ".github/agents/executive-scripter.agent.md",
    ".github/agents/executive-fleet.agent.md",
    ".github/agents/executive-pm.agent.md",
    ".github/agents/executive-planner.agent.md",
    ".github/agents/github.agent.md",
    ".github/skills/session-management/SKILL.md",
]

_ATLAS_PATH = "data/substrate-atlas.yml"

# ---------------------------------------------------------------------------
# CRD computation
# ---------------------------------------------------------------------------

_WARN_DEFAULT = 0.25
_BLOCK_DEFAULT = 0.10


def compute_crd(filepath: Path) -> float | None:
    """Compute CRD for *filepath*.

    Returns the CRD value (0.0–1.0), or None if the file cannot be read.
    Files with zero references return 0.0.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError:
        return None

    # Determine file layer for classify_reference; default to "guide" for non-agent/skill files.
    if ".agent.md" in filepath.name:
        file_layer = "agent"
    elif filepath.name == "SKILL.md":
        file_layer = "skill"
    else:
        file_layer = "guide"

    references = extract_references(content, file_layer)
    if not references:
        return 0.0

    intra_count = sum(1 for r in references if r["type"] == "intra")
    return intra_count / len(references)


# ---------------------------------------------------------------------------
# Atlas summary
# ---------------------------------------------------------------------------


def load_atlas(repo_root: Path) -> list[dict]:
    """Load and return the substrate list from data/substrate-atlas.yml.

    Raises SystemExit(1) if the file cannot be read or parsed.
    """
    atlas_path = repo_root / _ATLAS_PATH
    if not atlas_path.exists():
        print(f"ERROR: Atlas file not found: {atlas_path}")
        sys.exit(1)
    try:
        data = yaml.safe_load(atlas_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"ERROR: Cannot parse {atlas_path}: {exc}")
        sys.exit(1)
    if not isinstance(data, dict) or "substrates" not in data:
        print(f"ERROR: {atlas_path} must have a top-level 'substrates' key.")
        sys.exit(1)
    return data["substrates"]


def print_atlas_summary(substrates: list[dict]) -> None:
    """Print a summary table of substrates by validation status.

    Substrates with validation 'none' are flagged as WARN.
    """
    # Group by normalised validation bucket
    groups: dict[str, list[dict]] = {
        "programmatic": [],
        "review": [],
        "none": [],
        "other": [],
    }
    for s in substrates:
        val = str(s.get("validation", "")).lower()
        if val == "none":
            groups["none"].append(s)
        elif "programmatic" in val or "pytest" in val or "ci" in val or "validate" in val:
            groups["programmatic"].append(s)
        elif "review" in val:
            groups["review"].append(s)
        else:
            groups["other"].append(s)

    total = len(substrates)
    print(f"\nSubstrate Atlas — {total} substrates from {_ATLAS_PATH}")
    print("=" * 60)

    col_name = 40
    col_tier = 22
    print(f"{'SUBSTRATE':<{col_name}} {'TIER':<{col_tier}} STATUS")
    print("-" * (col_name + col_tier + 8))

    for label, bucket in [
        ("programmatic", "PASS"),
        ("review", "PASS"),
        ("other", "INFO"),
        ("none", "WARN"),
    ]:
        entries = groups[label]
        if not entries:
            continue
        for s in entries:
            name = str(s.get("name", ""))[: col_name - 1]
            tier = str(s.get("tier", ""))[: col_tier - 1]
            print(f"{name:<{col_name}} {tier:<{col_tier}} {bucket}")

    print("-" * (col_name + col_tier + 8))
    warn_count = len(groups["none"])
    print(
        f"SUMMARY: {total} substrates — "
        f"{len(groups['programmatic'])} programmatic, "
        f"{len(groups['review'])} review-only, "
        f"{len(groups['other'])} other, "
        f"{warn_count} unvalidated (WARN)"
    )
    if warn_count:
        print(
            f"\nWARN: {warn_count} substrate(s) have validation: none — "
            "highest-risk encoding gap (see docs/research/substrate-atlas.md §H3)"
        )
    print()


# ---------------------------------------------------------------------------
# Status classification
# ---------------------------------------------------------------------------


def classify_status(crd: float, warn_below: float, block_below: float) -> str:
    """Return STATUS string for a given CRD value."""
    if crd < block_below:
        return "BLOCK"
    if crd < warn_below:
        return "WARN"
    return "PASS"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CRD health check for startup-loaded substrate files.",
        epilog="Exit 0 = all files PASS or WARN. Exit 1 = at least one BLOCK (or missing file).",
    )
    parser.add_argument(
        "--warn-below",
        type=float,
        default=_WARN_DEFAULT,
        metavar="N",
        help=f"CRD below this value emits WARN (default: {_WARN_DEFAULT}).",
    )
    parser.add_argument(
        "--block-below",
        type=float,
        default=_BLOCK_DEFAULT,
        metavar="N",
        help=f"CRD below this value emits BLOCK and exits 1 (default: {_BLOCK_DEFAULT}).",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        default=None,
        help="Files to check (relative to repo root). Defaults to the startup-loaded list.",
    )
    parser.add_argument(
        "--atlas",
        action="store_true",
        default=False,
        help="Print a substrate atlas summary from data/substrate-atlas.yml.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    # --atlas: load and print the atlas summary, then exit (additive mode).
    if args.atlas:
        substrates = load_atlas(repo_root)
        print_atlas_summary(substrates)
        return

    files_to_check: list[str] = args.files if args.files is not None else DEFAULT_FILES

    blocked = False
    col_file = max(len(f) for f in files_to_check) + 2

    print(f"{'FILE':<{col_file}} {'CRD':>6}  STATUS")
    print("-" * (col_file + 16))

    for rel_path in files_to_check:
        filepath = repo_root / rel_path
        if not filepath.exists():
            print(f"{rel_path:<{col_file}} {'---':>6}  ERROR (file not found)")
            blocked = True
            continue

        crd = compute_crd(filepath)
        if crd is None:
            print(f"{rel_path:<{col_file}} {'---':>6}  ERROR (read failure)")
            blocked = True
            continue

        status = classify_status(crd, args.warn_below, args.block_below)
        print(f"{rel_path:<{col_file}} {crd:>6.4f}  {status}")

        if status == "BLOCK":
            blocked = True

    print("-" * (col_file + 16))
    if blocked:
        print("RESULT: BLOCK — one or more files below the block threshold or missing.")
        sys.exit(1)
    else:
        print("RESULT: PASS — all files meet the health threshold.")
        sys.exit(0)


if __name__ == "__main__":
    main()
