"""scripts/export_scratchpad.py — Export scratchpad files to structured formats.

Purpose
-------
Export .tmp/<branch>/<date>.md scratchpad files to JSON, YAML, or Markdown
formats for archival, external tool integration, or migration to future
substrates. Preserves structured session state, phase outputs, audit logs,
and telemetry.

Inputs
------
- Scratchpad file path (positional arg) OR --all flag
- --format {json,yaml,markdown} (default: json)
- --output PATH (optional; default: stdout)
- --all: Export all .tmp/*/*.md files to .cache/scratchpad-exports/

Outputs
-------
- JSON format: Structured object with metadata, session_state, audit_trail,
  telemetry, and phases arrays
- YAML format: Same structure as JSON, YAML-formatted
- Markdown format: Clean pass-through copy (archival)
- Exit code: 0 on success, 1 on validation failure, 2 on usage error

Usage examples
--------------
# Export single file to JSON (stdout)
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md

# Export to YAML file
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md --format yaml -o /tmp/export.yml

# Export all scratchpads to cache
uv run python scripts/export_scratchpad.py --all --format json

# Markdown pass-through (archival)
uv run python scripts/export_scratchpad.py .tmp/feat-my-branch/2026-04-13.md --format markdown -o archive.md

Exit codes
----------
0  Success
1  Validation failure (scratchpad does not meet schema)
2  Invalid usage or file not found

Round-trip guarantee
--------------------
Exported JSON/YAML can be parsed back to preserve all structural sections.
To validate round-trip:

    uv run python scripts/export_scratchpad.py <file> --format json -o /tmp/export.json
    python3 -c "import json; d=json.load(open('/tmp/export.json')); assert 'session_state' in d"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: uv sync", file=sys.stderr)
    sys.exit(2)

# Import validation functions from validate_scratchpad
# (validate before export to ensure structural integrity)
try:
    from validate_scratchpad import (
        extract_session_state_yaml,
        find_section_bounds,
    )
except ImportError:
    print(
        "ERROR: validate_scratchpad.py not found. Ensure scripts/ is in PYTHONPATH.",
        file=sys.stderr,
    )
    sys.exit(2)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_OUTPUT_DIR = Path(".cache/scratchpad-exports")
_SUPPORTED_FORMATS = ["json", "yaml", "markdown"]

# Phase section patterns
_PHASE_OUTPUT_PATTERN = re.compile(r"^## (Phase \d+ Output)(.*)$", re.MULTILINE)
_PHASE_REVIEW_PATTERN = re.compile(r"^## ((?:Phase \d+ )?Review Output)(.*)$", re.MULTILINE)

# Audit trail table row pattern
_AUDIT_ROW_PATTERN = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")

# Telemetry table row pattern
_TELEMETRY_ROW_PATTERN = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")

# ---------------------------------------------------------------------------
# Extraction Functions
# ---------------------------------------------------------------------------


def extract_metadata(file_path: Path, content: str) -> dict[str, Any]:
    """Extract metadata from scratchpad file path and content."""
    # Parse branch and date from file path: .tmp/<branch-slug>/<YYYY-MM-DD>.md
    parts = file_path.parts
    if len(parts) >= 2 and parts[-2] != file_path.parent.name:
        branch_slug = file_path.parent.name
    else:
        branch_slug = file_path.parent.name

    filename = file_path.name
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})\.md$", filename)
    file_date = date_match.group(1) if date_match else None

    return {
        "branch": branch_slug,
        "date": file_date,
        "source_file": str(file_path),
        "exported_at": datetime.now().isoformat(),
    }


def extract_audit_trail(content: str, section_start: int, section_end: int) -> list[dict[str, str]]:
    """Extract audit trail entries from table rows."""
    section_content = content[section_start:section_end]
    lines = section_content.split("\n")

    entries = []
    for line in lines:
        match = _AUDIT_ROW_PATTERN.match(line.strip())
        if match and match.group(1).strip().lower() not in ["agent", ""]:
            # Skip separator rows (e.g., | --- | --- | --- | --- |)
            cells = [match.group(i).strip() for i in range(1, 5)]
            if all(re.match(r"^-+$", cell) for cell in cells):
                continue

            entries.append(
                {
                    "agent": match.group(1).strip(),
                    "decision": match.group(2).strip(),
                    "justification": match.group(3).strip(),
                    "time": match.group(4).strip(),
                }
            )

    return entries


def extract_telemetry(content: str, section_start: int, section_end: int) -> dict[str, str]:
    """Extract telemetry metrics from table rows."""
    section_content = content[section_start:section_end]
    lines = section_content.split("\n")

    metrics = {}
    for line in lines:
        match = _TELEMETRY_ROW_PATTERN.match(line.strip())
        if match and match.group(1).strip().lower() not in ["metric", ""]:
            key = match.group(1).strip()
            value = match.group(2).strip()
            metrics[key] = value

    return metrics


def extract_phases(content: str) -> list[dict[str, Any]]:
    """Extract phase output sections with content."""
    phases = []

    # Find all Phase N Output sections
    for match in _PHASE_OUTPUT_PATTERN.finditer(content):
        heading = match.group(1)
        phase_num_match = re.search(r"Phase (\d+)", heading)
        phase_num = int(phase_num_match.group(1)) if phase_num_match else 0

        start = match.end()
        # Find next H2 section or end of file
        next_h2 = re.search(r"\n## ", content[start:])
        end = start + next_h2.start() if next_h2 else len(content)

        phase_content = content[start:end].strip()

        phases.append(
            {
                "phase_num": phase_num,
                "title": heading,
                "content": phase_content,
            }
        )

    # Sort by phase number
    phases.sort(key=lambda p: p["phase_num"])

    return phases


def export_to_dict(file_path: Path, content: str) -> dict[str, Any]:
    """
    Export scratchpad to structured dictionary.

    Returns dict with keys: metadata, session_state, audit_trail, telemetry, phases.
    """
    # Extract metadata
    metadata = extract_metadata(file_path, content)

    # Extract session state YAML
    session_state_bounds = find_section_bounds(content, "Session State")
    if session_state_bounds:
        session_state = extract_session_state_yaml(content, *session_state_bounds)
    else:
        session_state = None

    # Extract audit trail
    audit_bounds = find_section_bounds(content, "Audit Trail")
    if audit_bounds:
        audit_trail = extract_audit_trail(content, *audit_bounds)
    else:
        audit_trail = []

    # Extract telemetry
    telemetry_bounds = find_section_bounds(content, "Telemetry")
    if telemetry_bounds:
        telemetry = extract_telemetry(content, *telemetry_bounds)
    else:
        telemetry = {}

    # Extract phases
    phases = extract_phases(content)

    return {
        "metadata": metadata,
        "session_state": session_state or {},
        "audit_trail": audit_trail,
        "telemetry": telemetry,
        "phases": phases,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_scratchpad(file_path: Path) -> bool:
    """
    Run validate_scratchpad.py on the file.

    Returns True if valid, False otherwise.
    """
    import subprocess

    _validate_script = Path(__file__).parent / "validate_scratchpad.py"
    result = subprocess.run(
        ["uv", "run", "python", str(_validate_script), str(file_path), "--check-only"],
        capture_output=True,
    )

    return result.returncode == 0


# ---------------------------------------------------------------------------
# Export Functions
# ---------------------------------------------------------------------------


def export_json(data: dict[str, Any], output: Path | None) -> None:
    """Export to JSON format."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json_str)
    else:
        print(json_str)


def export_yaml(data: dict[str, Any], output: Path | None) -> None:
    """Export to YAML format."""
    yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(yaml_str)
    else:
        print(yaml_str)


def export_markdown(content: str, output: Path | None) -> None:
    """Export to Markdown format (pass-through copy)."""
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content)
    else:
        print(content)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export scratchpad files to structured formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Path to scratchpad file to export (required unless --all)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all .tmp/*/*.md files to .cache/scratchpad-exports/",
    )

    parser.add_argument(
        "--format",
        choices=_SUPPORTED_FORMATS,
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: stdout; with --all: auto-generated)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.file:
        print("ERROR: Either provide a file path or use --all", file=sys.stderr)
        parser.print_help(sys.stderr)
        return 2

    if args.all and args.file:
        print("ERROR: Cannot use both file path and --all", file=sys.stderr)
        return 2

    # Single file export
    if args.file:
        if not args.file.exists():
            print(f"ERROR: File not found: {args.file}", file=sys.stderr)
            return 2

        # Validate before export
        if not validate_scratchpad(args.file):
            print(f"ERROR: Scratchpad validation failed: {args.file}", file=sys.stderr)
            print("Run: uv run python scripts/validate_scratchpad.py <file>", file=sys.stderr)
            return 1

        content = args.file.read_text()

        if args.format == "markdown":
            export_markdown(content, args.output)
        else:
            data = export_to_dict(args.file, content)
            if args.format == "json":
                export_json(data, args.output)
            elif args.format == "yaml":
                export_yaml(data, args.output)

        if args.output:
            print(f"Exported to: {args.output}", file=sys.stderr)

        return 0

    # Batch export (--all)
    if args.all:
        tmp_dir = Path(".tmp")
        if not tmp_dir.exists():
            print("ERROR: .tmp directory not found", file=sys.stderr)
            return 2

        scratchpad_files = list(tmp_dir.glob("*/*.md"))
        if not scratchpad_files:
            print("No scratchpad files found in .tmp/*/", file=sys.stderr)
            return 0

        # Prepare output directory
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = _DEFAULT_OUTPUT_DIR / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        exported_count = 0
        failed_count = 0

        for scratchpad_file in scratchpad_files:
            # Skip _index.md files
            if scratchpad_file.name == "_index.md":
                continue

            # Validate before export
            if not validate_scratchpad(scratchpad_file):
                print(f"SKIP (validation failed): {scratchpad_file}", file=sys.stderr)
                failed_count += 1
                continue

            content = scratchpad_file.read_text()

            # Generate output filename
            branch_slug = scratchpad_file.parent.name
            date_str = scratchpad_file.stem

            if args.format == "json":
                output_file = output_dir / f"{branch_slug}_{date_str}.json"
                data = export_to_dict(scratchpad_file, content)
                export_json(data, output_file)
            elif args.format == "yaml":
                output_file = output_dir / f"{branch_slug}_{date_str}.yml"
                data = export_to_dict(scratchpad_file, content)
                export_yaml(data, output_file)
            elif args.format == "markdown":
                output_file = output_dir / f"{branch_slug}_{date_str}.md"
                export_markdown(content, output_file)

            exported_count += 1

        print(f"Exported {exported_count} file(s) to: {output_dir}", file=sys.stderr)
        if failed_count > 0:
            print(f"Skipped {failed_count} invalid file(s)", file=sys.stderr)

        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
