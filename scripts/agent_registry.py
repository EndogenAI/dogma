"""
agent_registry.py
-----------------
Purpose:
    Enumerate all .github/agents/*.agent.md files, extract per-agent metadata
    (name, tier, tools, area, description, file), derive posture from the tools
    list, and expose a filterable, CLI-accessible registry.

Inputs:
    .github/agents/*.agent.md files with YAML frontmatter blocks.
    Optional: --agents-dir to override the default agents directory path.

Outputs:
    Markdown table or JSON array written to stdout (or --output file).
    Each entry contains: name, tier, area, posture, tools (list), file (path).
    Summary counts are not written; this script emits only the requested format.

Usage examples:
    # List all agents as a markdown table
    uv run python scripts/agent_registry.py --list

    # Filter by tool and print markdown table
    uv run python scripts/agent_registry.py --list --filter-tool terminal

    # Emit JSON array
    uv run python scripts/agent_registry.py --json

    # Filter by tier and write JSON to file
    uv run python scripts/agent_registry.py --json --filter-tier executive --output out.json

    # Filter by area
    uv run python scripts/agent_registry.py --list --filter-area research

Exit codes:
    0  Success (all discovered files parsed without error)
    1  Agents directory not found, or one or more files failed to parse
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML helpers — same extraction pattern as generate_agent_manifest.py
# ---------------------------------------------------------------------------


def find_repo_root() -> Path:
    """Walk up from this file until a directory containing AGENTS.md is found."""
    candidate = Path(__file__).resolve().parent
    while candidate != candidate.parent:
        if (candidate / "AGENTS.md").exists():
            return candidate
        candidate = candidate.parent
    return Path(__file__).resolve().parent.parent


def extract_frontmatter(text: str) -> str | None:
    """Return the raw YAML text between the leading '---' fences, or None."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    return match.group(1) if match else None


def parse_simple_yaml(yaml_text: str) -> dict:
    """
    Parse a subset of YAML containing only top-level scalar strings and flat
    string lists (the schema used by .agent.md frontmatter).

    Does NOT support: nested objects, multi-line strings, anchors, or tags.
    Returns a dict mapping string keys to str or list[str] values.
    """
    result: dict = {}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        key_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)", line)
        if key_match:
            key = key_match.group(1)
            value = key_match.group(2).strip()
            if value:
                result[key] = value.strip("\"'")
                i += 1
            else:
                items: list[str] = []
                i += 1
                while i < len(lines):
                    item_match = re.match(r"^\s+-\s+(.*)", lines[i])
                    if item_match:
                        items.append(item_match.group(1).strip().strip("\"'"))
                        i += 1
                    elif not lines[i].strip():
                        i += 1
                    elif lines[i][0] in (" ", "\t"):
                        i += 1
                    else:
                        break
                result[key] = items
        else:
            i += 1
    return result


# ---------------------------------------------------------------------------
# Posture derivation
# ---------------------------------------------------------------------------

_FULL_TOOLS = frozenset({"execute", "terminal", "agent", "run", "browser"})
_CREATOR_TOOLS = frozenset({"edit", "write", "create", "notebook"})


def derive_posture(tools: list[str]) -> str:
    """
    Derive agent posture from its declared tools list.

    Returns:
        "full"     — tools include execute / terminal / agent / run / browser
        "creator"  — tools include edit / write / create / notebook (but not full)
        "readonly" — tools are read/search only, or list is empty
    """
    tool_set = {t.lower() for t in tools}
    if tool_set & _FULL_TOOLS:
        return "full"
    if tool_set & _CREATOR_TOOLS:
        return "creator"
    return "readonly"


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------


def load_registry(agents_dir: Path) -> tuple[list[dict], bool]:
    """
    Load all agent entries from agents_dir.

    Returns:
        (entries, had_errors) — entries is a list of dicts; had_errors is True
        if the directory was missing or any file failed to parse.
    """
    if not agents_dir.is_dir():
        print(f"ERROR: Agents directory not found: {agents_dir}", file=sys.stderr)
        return [], True

    entries: list[dict] = []
    had_errors = False

    for path in sorted(agents_dir.glob("*.agent.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"WARNING: Cannot read {path}: {exc}", file=sys.stderr)
            had_errors = True
            continue

        frontmatter_raw = extract_frontmatter(text)
        if frontmatter_raw is None:
            print(f"WARNING: No YAML frontmatter in {path.name} — skipping.", file=sys.stderr)
            had_errors = True
            continue

        try:
            data = parse_simple_yaml(frontmatter_raw)
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARNING: Failed to parse frontmatter in {path.name}: {exc} — skipping.",
                file=sys.stderr,
            )
            had_errors = True
            continue

        name = data.get("name", "").strip()
        if not name:
            print(f"WARNING: Missing 'name' in {path.name} — skipping.", file=sys.stderr)
            had_errors = True
            continue

        tools_raw = data.get("tools", [])
        if isinstance(tools_raw, str):
            # Handle inline flow sequence written as a single-line value
            tools: list[str] = [
                t.strip().strip("[]'\"") for t in tools_raw.strip("[]").split(",") if t.strip().strip("[]'\"")
            ]
        else:
            tools = list(tools_raw)

        tier_raw = data.get("tier")
        tier = tier_raw.strip() if isinstance(tier_raw, str) and tier_raw.strip() else "unset"

        area_raw = data.get("area")
        area = area_raw.strip() if isinstance(area_raw, str) and area_raw.strip() else "unset"

        entries.append(
            {
                "name": name,
                "tier": tier,
                "area": area,
                "description": data.get("description", "").strip(),
                "tools": tools,
                "posture": derive_posture(tools),
                "file": str(path),
            }
        )

    return entries, had_errors


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def apply_filters(
    entries: list[dict],
    filter_tool: str | None = None,
    filter_tier: str | None = None,
    filter_area: str | None = None,
) -> list[dict]:
    """Narrow entries by tool membership, tier, and/or area (case-insensitive)."""
    result = entries
    if filter_tool:
        ft = filter_tool.lower()
        result = [e for e in result if any(ft == t.lower() for t in e["tools"])]
    if filter_tier:
        ft = filter_tier.lower()
        result = [e for e in result if e["tier"].lower() == ft]
    if filter_area:
        fa = filter_area.lower()
        result = [e for e in result if e["area"].lower() == fa]
    return result


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_markdown_table(entries: list[dict]) -> str:
    """Render entries as a padded Markdown table."""
    headers = ["Name", "Tier", "Area", "Posture", "Tools", "File"]
    rows = [
        [
            e["name"],
            e["tier"],
            e["area"],
            e["posture"],
            ", ".join(e["tools"]),
            e["file"],
        ]
        for e in entries
    ]

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    lines = [fmt_row(headers), sep, *[fmt_row(row) for row in rows]]
    return "\n".join(lines)


def render_json(entries: list[dict]) -> str:
    """Render entries as a JSON array."""
    return json.dumps(entries, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Capability-aware, filterable registry of all fleet agents.")
    p.add_argument("--list", action="store_true", help="Print agents as a markdown table.")
    p.add_argument("--json", action="store_true", help="Emit JSON array instead of markdown table.")
    p.add_argument("--filter-tool", metavar="TOOL", help="Only show agents whose tools list contains TOOL.")
    p.add_argument("--filter-tier", metavar="TIER", help="Only show agents matching TIER.")
    p.add_argument("--filter-area", metavar="AREA", help="Only show agents matching AREA.")
    p.add_argument("--output", metavar="PATH", help="Write output to file instead of stdout.")
    p.add_argument("--agents-dir", metavar="DIR", help="Override path to agents directory.")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = find_repo_root()
    agents_dir = Path(args.agents_dir) if args.agents_dir else repo_root / ".github" / "agents"

    entries, had_errors = load_registry(agents_dir)
    if not entries and had_errors:
        return 1

    entries = apply_filters(
        entries,
        filter_tool=args.filter_tool,
        filter_tier=args.filter_tier,
        filter_area=args.filter_area,
    )

    use_json = args.json
    use_list = args.list or not use_json  # noqa: F841 — default to list when neither flag set

    if use_json:
        output = render_json(entries)
    else:
        output = render_markdown_table(entries)

    if args.output:
        out_path = Path(args.output)
        try:
            out_path.write_text(output + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: Cannot write to {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 1 if had_errors else 0


if __name__ == "__main__":
    sys.exit(main())
