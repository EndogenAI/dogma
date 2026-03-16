"""check_divergence.py — Detect drift between a derived repo and the dogma template.

Purpose:
    Compares governance artefacts in a derived (cookiecutter-instantiated) repository
    against the local dogma template to surface structural divergence. Useful as a
    CI gate on derived repos to ensure they remain aligned with upstream governance.

Inputs:
    --repo PATH       Path to the derived repository root (required)
    --check           Exit 1 if any drift is found (CI gate mode)
    --dry-run         Print what would be compared without reading file contents; exit 0
    --export-hgt      Emit a YAML list of drift items as "HGT candidates" — sections
                      that changed in the derived repo vs template, potential upstream
                      learnings for dogma itself

Outputs:
    Text drift-delta report (added/removed/changed per artefact) printed to stdout.
    With --export-hgt: YAML candidate list appended to stdout after the report.

Artefacts compared:
    1. AGENTS.md              — H2 headings present in dogma vs derived repo
    2. .pre-commit-config.yaml — hook IDs present in dogma vs derived repo
    3. pyproject.toml         — presence of [project] and [tool.pytest.ini_options] sections
    4. client-values.yml      — file presence in derived repo root

Exit codes:
    0   No drift found (or --dry-run)
    1   Drift found with --check flag
    2   Error: invalid --repo path or unexpected I/O failure

Usage examples:
    uv run python scripts/check_divergence.py --repo ../my-project --check
    uv run python scripts/check_divergence.py --repo ../my-project --dry-run
    uv run python scripts/check_divergence.py --repo ../my-project --export-hgt
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Template root — the dogma repo directory containing this script's parent
# ---------------------------------------------------------------------------

TEMPLATE_ROOT = Path(__file__).parent.parent

# Artefact filenames (for dry-run listing)
ARTEFACTS = [
    "AGENTS.md",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    "client-values.yml",
]

# Required pyproject.toml sections in derived repos
REQUIRED_PYPROJECT_SECTIONS = {"project", "tool.pytest.ini_options"}


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def extract_h2_headings(text: str) -> list[str]:
    """Extract H2 heading text (without the '## ' prefix) from Markdown."""
    return re.findall(r"^## (.+)$", text, re.MULTILINE)


def extract_hook_ids(text: str) -> list[str]:
    """Extract hook IDs from .pre-commit-config.yaml content."""
    return re.findall(r"^\s+- id:\s+(\S+)", text, re.MULTILINE)


def extract_pyproject_sections(text: str) -> list[str]:
    """Extract section header names from pyproject.toml (e.g. 'project', 'tool.ruff')."""
    return re.findall(r"^\[([^\]]+)\]", text, re.MULTILINE)


# ---------------------------------------------------------------------------
# Per-artefact comparators
# ---------------------------------------------------------------------------


def _empty_result(file_name: str) -> dict[str, Any]:
    return {"file": file_name, "added": [], "removed": [], "changed": [], "errors": []}


def compare_agents_md(template_root: Path, derived_root: Path) -> dict[str, Any]:
    """Compare H2 headings in AGENTS.md between template and derived repo.

    'removed' = headings present in template but absent from derived repo.
    'added'   = headings present in derived repo but absent from template.
    """
    result = _empty_result("AGENTS.md")

    template_path = template_root / "AGENTS.md"
    derived_path = derived_root / "AGENTS.md"

    if not template_path.exists():
        result["errors"].append("Template AGENTS.md not found")
        return result
    if not derived_path.exists():
        result["errors"].append("Derived AGENTS.md not found")
        return result

    template_headings = set(extract_h2_headings(template_path.read_text(encoding="utf-8")))
    derived_headings = set(extract_h2_headings(derived_path.read_text(encoding="utf-8")))

    result["removed"] = sorted(template_headings - derived_headings)
    result["added"] = sorted(derived_headings - template_headings)
    return result


def compare_precommit(template_root: Path, derived_root: Path) -> dict[str, Any]:
    """Compare hook IDs in .pre-commit-config.yaml.

    'removed' = hook IDs in template missing from derived repo.
    'added'   = hook IDs in derived repo not present in template.
    """
    result = _empty_result(".pre-commit-config.yaml")

    template_path = template_root / ".pre-commit-config.yaml"
    derived_path = derived_root / ".pre-commit-config.yaml"

    if not template_path.exists():
        result["errors"].append("Template .pre-commit-config.yaml not found")
        return result
    if not derived_path.exists():
        result["errors"].append("Derived .pre-commit-config.yaml not found")
        return result

    template_ids = set(extract_hook_ids(template_path.read_text(encoding="utf-8")))
    derived_ids = set(extract_hook_ids(derived_path.read_text(encoding="utf-8")))

    result["removed"] = sorted(template_ids - derived_ids)
    result["added"] = sorted(derived_ids - template_ids)
    return result


def compare_pyproject(template_root: Path, derived_root: Path) -> dict[str, Any]:
    """Check that required sections exist in pyproject.toml of the derived repo.

    'removed' = required sections absent from derived pyproject.toml.
    The template pyproject.toml is not required to exist for this check.
    """
    result = _empty_result("pyproject.toml")

    derived_path = derived_root / "pyproject.toml"

    if not derived_path.exists():
        result["errors"].append("Derived pyproject.toml not found")
        return result

    derived_sections = set(extract_pyproject_sections(derived_path.read_text(encoding="utf-8")))
    missing = sorted(REQUIRED_PYPROJECT_SECTIONS - derived_sections)
    result["removed"] = missing
    return result


def check_client_values(derived_root: Path) -> dict[str, Any]:
    """Check whether client-values.yml exists in the derived repo root."""
    result = _empty_result("client-values.yml")

    derived_path = derived_root / "client-values.yml"
    if not derived_path.exists():
        result["removed"].append("client-values.yml (absent from derived repo root)")
    return result


# ---------------------------------------------------------------------------
# Drift detection and reporting
# ---------------------------------------------------------------------------


def has_drift(results: list[dict[str, Any]]) -> bool:
    """Return True if any result contains added, removed, changed, or error items."""
    return any(r.get("added") or r.get("removed") or r.get("changed") or r.get("errors") for r in results)


def format_report(results: list[dict[str, Any]]) -> str:
    """Format drift results as a human-readable text report."""
    separator = "=" * 48
    lines = ["Drift Delta Report", separator]

    for r in results:
        file_name = r["file"]
        drift = bool(r.get("added") or r.get("removed") or r.get("changed") or r.get("errors"))
        status = "DRIFT" if drift else "OK"
        lines.append(f"\n{file_name}: {status}")

        for err in r.get("errors", []):
            lines.append(f"  ERROR: {err}")
        for item in r.get("removed", []):
            lines.append(f"  - removed: {item}")
        for item in r.get("added", []):
            lines.append(f"  + added:   {item}")
        for item in r.get("changed", []):
            lines.append(f"  ~ changed: {item}")

    lines.append(f"\n{separator}")
    any_drift = has_drift(results)
    lines.append(f"Result: {'DRIFT DETECTED' if any_drift else 'NO DRIFT'}")
    return "\n".join(lines)


def build_hgt_candidates(results: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Build list of HGT (Horizontal Gene Transfer) candidates from drift results.

    Each candidate is a dict with keys: file, type (added/removed/changed), section.
    Candidates are governance sections that changed in the derived repo vs template —
    potential upstream learnings for dogma.
    """
    candidates: list[dict[str, str]] = []
    for r in results:
        for item in r.get("added", []):
            candidates.append({"file": r["file"], "type": "added", "section": item})
        for item in r.get("removed", []):
            candidates.append({"file": r["file"], "type": "removed", "section": item})
        for item in r.get("changed", []):
            candidates.append({"file": r["file"], "type": "changed", "section": item})
    return candidates


def emit_hgt_yaml(candidates: list[dict[str, str]]) -> None:
    """Print HGT candidates as YAML to stdout."""
    print("\nHGT Candidates:")
    try:
        import yaml  # type: ignore[import-untyped]

        print(yaml.dump(candidates, default_flow_style=False, allow_unicode=True), end="")
    except ImportError:
        # Minimal fallback if PyYAML is unavailable
        for c in candidates:
            print(f"- file: {c['file']}")
            print(f"  type: {c['type']}")
            print(f"  section: {c['section']}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run comparisons, print report. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="Detect drift between a derived repo and the dogma template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        required=True,
        metavar="PATH",
        help="Path to the derived repository root (required)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any drift is found (CI gate mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be checked without comparing file contents; exit 0",
    )
    parser.add_argument(
        "--export-hgt",
        action="store_true",
        help="Output YAML list of HGT candidates (changed governance sections)",
    )

    args = parser.parse_args(argv)

    derived_root = Path(args.repo)
    if not derived_root.exists() or not derived_root.is_dir():
        print(
            f"Error: --repo path does not exist or is not a directory: {args.repo}",
            file=sys.stderr,
        )
        return 2

    if args.dry_run:
        print("Dry run — artefacts that would be checked:")
        for name in ARTEFACTS:
            print(f"  {name}")
        return 0

    results = [
        compare_agents_md(TEMPLATE_ROOT, derived_root),
        compare_precommit(TEMPLATE_ROOT, derived_root),
        compare_pyproject(TEMPLATE_ROOT, derived_root),
        check_client_values(derived_root),
    ]

    print(format_report(results))

    if args.export_hgt:
        candidates = build_hgt_candidates(results)
        emit_hgt_yaml(candidates)

    drift = has_drift(results)
    if args.check and drift:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
