"""Detect plan-to-intent drift: workplan deliverables vs. intent contract.

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
    uv run python scripts/check_plan_to_intent_drift.py --workplan docs/plans/foo.md \
        --contract docs/plans/foo/intent-contract.yml
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _load_contract(contract_path: Path) -> dict | None:
    """Load and parse the contract file. Returns None on failure."""
    if not contract_path.exists():
        return None

    text = contract_path.read_text(encoding="utf-8", errors="replace")

    # Strip YAML fences if the file is Markdown-embedded
    if contract_path.suffix in {".md", ".markdown"}:
        import re

        match = re.search(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL)
        if match:
            text = match.group(1)

    if yaml is None:
        print(
            "warning: PyYAML is not installed; contract parsing unavailable",
            file=sys.stderr,
        )
        return {}

    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        print(f"warning: malformed YAML in {contract_path} — {exc}", file=sys.stderr)
        return {}


def _resolve_contract_path(workplan: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    # Derive slug from workplan filename stem (strip date prefix if present)
    import re

    stem = workplan.stem
    if re.match(r"^\d{4}-\d{2}-\d{2}-.+", stem):
        slug = stem[11:]  # len("YYYY-MM-DD-") == 11
    else:
        slug = stem
    return workplan.parent / slug / "intent-contract.md"


def _find_uncovered(acceptance_tests: list[dict], workplan_text: str) -> list[str]:
    """Return test names not referenced in the workplan (case-insensitive substring)."""
    lower_text = workplan_text.lower()
    missing = []
    for test in acceptance_tests:
        name = str(test.get("name", "")).strip()
        command = str(test.get("command", "")).strip()
        if not name and not command:
            continue
        # Match if name OR command appears anywhere in workplan
        name_found = name and name.lower() in lower_text
        cmd_found = command and command.lower() in lower_text
        if not name_found and not cmd_found:
            missing.append(name or command)
    return missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect drift between a workplan and its intent contract.")
    parser.add_argument("--workplan", required=True, help="Path to workplan .md file")
    parser.add_argument(
        "--contract",
        default=None,
        help="Path to intent-contract.yml/.md (auto-detected if omitted)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Advisory mode — always exit 0",
    )
    args = parser.parse_args(argv)

    workplan_path = Path(args.workplan)
    if not workplan_path.exists():
        print(f"error: workplan not found: {workplan_path}", file=sys.stderr)
        return 0 if args.check else 1

    workplan_text = workplan_path.read_text(encoding="utf-8", errors="replace")

    contract_path = _resolve_contract_path(workplan_path, Path(args.contract) if args.contract else None)

    if not contract_path.exists():
        print(f"No intent contract found at {contract_path}; drift check skipped")
        return 0

    contract = _load_contract(contract_path)

    if contract is None:
        # File exists but couldn't be read
        print(f"warning: could not load {contract_path}; drift check skipped")
        return 0

    if not isinstance(contract, dict) or "acceptance_tests" not in contract:
        print(f"advisory: {contract_path} has no acceptance_tests key; drift check skipped")
        return 0

    acceptance_tests = contract.get("acceptance_tests") or []
    if not isinstance(acceptance_tests, list):
        print(f"advisory: acceptance_tests in {contract_path} is not a list; skipped")
        return 0

    missing = _find_uncovered(acceptance_tests, workplan_text)

    if missing:
        print(f"plan-to-intent drift detected — {len(missing)} acceptance test(s) not referenced in {workplan_path}:")
        for item in missing:
            print(f"  - {item}")
        return 0 if args.check else 1

    print(f"OK — all {len(acceptance_tests)} acceptance test(s) covered in {workplan_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
