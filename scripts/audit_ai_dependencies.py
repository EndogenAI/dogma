"""scripts/audit_ai_dependencies.py

Scan .github/agents and scripts/ for external AI API references and produce
a dependency inventory for the NIST AI RMF GOVERN 6.1 annual audit.

Purpose:
    Maps every external AI API call in dogma agent files and scripts to its
    provider, then outputs a structured inventory in YAML. The inventory is
    the input to the manual ENISA 8-dimension scoring step (recorded in
    data/enisa-lock-in-scoring.yml). This implements issue #381 and satisfies
    the NIST AI RMF GOVERN 6.1 control for third-party AI dependency tracking.

    Run annually (or when a new AI provider dependency is introduced) to
    produce an updated snapshot.

Inputs:
    .github/agents/*.agent.md   — fleet agent files (scanned for provider refs)
    scripts/*.py                — Python scripts (scanned for provider refs)
    --agents-dir DIR            — override agents directory (default: .github/agents)
    --scripts-dir DIR           — override scripts directory (default: scripts)
    --output FILE               — write YAML inventory to this file
                                  (default: stdout)
    --dry-run                   — print inventory to stdout without writing file

Outputs:
    YAML inventory with keys: scan_date, providers[], dependencies[]
    Each dependency: file, provider, reference_type, evidence_line, line_number

Exit codes:
    0   Scan completed (even if no providers found)
    1   No input directories found or fatal error
    2   I/O error

Usage examples:
    # Print inventory to stdout
    uv run python scripts/audit_ai_dependencies.py --dry-run

    # Write to file for review
    uv run python scripts/audit_ai_dependencies.py --output /tmp/ai-deps.yml

    # Custom dirs
    uv run python scripts/audit_ai_dependencies.py \\
        --agents-dir .github/agents \\
        --scripts-dir scripts \\
        --output /tmp/ai-deps.yml
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML is required. Run: uv sync --dev", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# Provider detection patterns
# Each entry: (provider_name, canonical_name, [regex_patterns])
# Patterns are applied case-insensitively.
# ---------------------------------------------------------------------------

PROVIDER_PATTERNS: list[tuple[str, str, list[str]]] = [
    (
        "claude",
        "Anthropic / Claude",
        [
            r"\banthropic\b",
            r"\bclaude\b",
            r"claude-\d",
            r"anthropic\.com",
            r"docs\.anthropic\.com",
        ],
    ),
    (
        "github_copilot",
        "GitHub Copilot",
        [
            r"github copilot",
            r"github\.com/features/copilot",
            r"copilot\.microsoft\.com",
            r"vscode.*copilot",
        ],
    ),
    (
        "openai",
        "OpenAI",
        [
            r"\bopenai\b",
            r"gpt-3\b",
            r"gpt-4\b",
            r"api\.openai\.com",
        ],
    ),
    (
        "ollama",
        "Ollama (local)",
        [
            r"\bollama\b",
            r"localhost:11434",
            r"local-localhost",
        ],
    ),
]

_COMPILED: list[tuple[str, str, list[re.Pattern]]] = [
    (pid, pname, [re.compile(pat, re.IGNORECASE) for pat in pats]) for pid, pname, pats in PROVIDER_PATTERNS
]


def _detect_providers(line: str) -> list[tuple[str, str]]:
    """Return list of (provider_id, canonical_name) found in a single line."""
    found = []
    for pid, pname, patterns in _COMPILED:
        for pat in patterns:
            if pat.search(line):
                found.append((pid, pname))
                break  # only report each provider once per line
    return found


def scan_file(path: Path) -> list[dict]:
    """Scan a single file and return dependency records."""
    records: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return records

    for lineno, line in enumerate(content.splitlines(), start=1):
        for pid, pname in _detect_providers(line):
            records.append(
                {
                    "file": str(path),
                    "provider_id": pid,
                    "provider_name": pname,
                    "line_number": lineno,
                    "evidence": line.strip()[:120],
                }
            )
    return records


def aggregate_by_provider(records: list[dict]) -> dict[str, dict]:
    """Aggregate raw records into a provider → file summary."""
    providers: dict[str, dict] = {}
    for rec in records:
        pid = rec["provider_id"]
        if pid not in providers:
            providers[pid] = {
                "provider_id": pid,
                "provider_name": rec["provider_name"],
                "files": set(),
                "reference_count": 0,
            }
        providers[pid]["files"].add(rec["file"])
        providers[pid]["reference_count"] += 1
    # Convert sets to sorted lists for YAML serialization
    for pid in providers:
        providers[pid]["files"] = sorted(providers[pid]["files"])
    return providers


def _get_root() -> Path:
    """Return the workspace root (parent of scripts/). Monkeypatched in tests."""
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan agent and script files for external AI API dependencies.")
    parser.add_argument(
        "--agents-dir",
        default=None,
        metavar="DIR",
        help="Directory containing .agent.md files (default: <root>/.github/agents)",
    )
    parser.add_argument(
        "--scripts-dir",
        default=None,
        metavar="DIR",
        help="Directory containing .py scripts (default: <root>/scripts)",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write YAML inventory to this file (default: stdout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print inventory to stdout without writing a file",
    )
    args = parser.parse_args(argv)

    root = _get_root()
    agents_dir = Path(args.agents_dir) if args.agents_dir else root / ".github" / "agents"
    scripts_dir = Path(args.scripts_dir) if args.scripts_dir else root / "scripts"

    missing = [d for d in (agents_dir, scripts_dir) if not d.is_dir()]
    if missing:
        for d in missing:
            print(f"ERROR: directory not found: {d}", file=sys.stderr)
        return 1

    # Collect files to scan
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    script_files = sorted(scripts_dir.glob("*.py"))
    all_files = agent_files + script_files

    # Scan
    all_records: list[dict] = []
    for f in all_files:
        all_records.extend(scan_file(f))

    provider_summary = aggregate_by_provider(all_records)

    # Build inventory
    inventory = {
        "scan_date": date.today().isoformat(),
        "scanned_directories": [str(agents_dir), str(scripts_dir)],
        "scanned_file_count": len(all_files),
        "providers": [
            {
                "provider_id": v["provider_id"],
                "provider_name": v["provider_name"],
                "reference_count": v["reference_count"],
                "files": v["files"],
            }
            for v in sorted(provider_summary.values(), key=lambda x: -x["reference_count"])
        ],
        "raw_references": [
            {
                "file": r["file"],
                "provider_id": r["provider_id"],
                "line_number": r["line_number"],
                "evidence": r["evidence"],
            }
            for r in all_records
        ],
    }

    yaml_output = yaml.dump(inventory, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if args.dry_run or args.output is None:
        print(yaml_output)
        return 0

    out_path = Path(args.output)
    try:
        out_path.write_text(yaml_output, encoding="utf-8")
        print(f"Inventory written to: {out_path}")
    except OSError as exc:
        print(f"ERROR writing {out_path}: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
