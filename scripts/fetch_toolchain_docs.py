"""
fetch_toolchain_docs.py — Cache CLI tool help output as structured Markdown.

Purpose
-------
Run ``gh help`` and ``gh <subcommand> --help`` for every top-level subcommand,
convert the output to structured Markdown, and write it to the local
``.cache/toolchain/`` directory.  Agents can then read command syntax locally
without burning tokens or network round-trips.

Per the programmatic-first principle in AGENTS.md: agents repeatedly look up
``gh`` CLI syntax interactively (e.g. ``gh issue create``, ``gh pr merge``
flags).  That task has happened more than twice and is now encoded here.

Inputs
------
- Optional ``--tool gh``        Currently only ``gh`` is supported.  Default: ``gh``.
- Optional ``--output-dir PATH`` Where to write cache files.  Default: ``.cache/toolchain/``.
- Optional ``--check``          Skip refresh if cache files are < 24 hours old.
- Optional ``--force``          Always re-fetch, ignoring cache age.
- Optional ``--dry-run``        Print what would be written without writing anything.

Outputs
-------
- ``.cache/toolchain/gh/<subcommand>.md``  Per-subcommand structured Markdown.
- ``.cache/toolchain/gh/index.md``         All subcommands with one-line descriptions.
- ``.cache/toolchain/gh.md``               Single aggregate file (all subcommands).

Per-subcommand Markdown format::

    # gh <subcommand>
    > <description>

    ## Usage
    ## Flags  (table: Flag | Description)
    ## Examples

Usage Examples
--------------
# Fetch and cache gh CLI docs (writes to .cache/toolchain/)
uv run python scripts/fetch_toolchain_docs.py

# Explicitly specify tool and output dir
uv run python scripts/fetch_toolchain_docs.py --tool gh --output-dir .cache/toolchain/

# Skip refresh if cached within last 24 hours
uv run python scripts/fetch_toolchain_docs.py --check

# Force re-fetch even if recently cached
uv run python scripts/fetch_toolchain_docs.py --force

# Dry run — print what would be written without touching the filesystem
uv run python scripts/fetch_toolchain_docs.py --dry-run

Exit Codes
----------
0  Success (all subcommands cached or cache is fresh and --check used)
1  Error (tool not on PATH, no subcommands found, or usage error)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / ".cache" / "toolchain"
CACHE_MAX_AGE_HOURS = 24

# Subcommand list per tool.
# - None  → auto-discover by parsing `<tool> --help`
# - list  → use this fixed list (tools with too many subcommands, e.g. git)
# - []    → single-command tool; capture `<tool> --help` output directly
TOOL_SUBCOMMANDS: dict[str, list[str] | None] = {
    "gh": None,  # handled by fetch_gh_docs — uses colon-separated help format
    "uv": None,  # auto-discover from `uv --help`
    "ruff": ["check", "format", "rule", "linter", "clean", "config"],
    "git": [
        "add",
        "branch",
        "checkout",
        "commit",
        "diff",
        "fetch",
        "log",
        "merge",
        "pull",
        "push",
        "rebase",
        "remote",
        "reset",
        "restore",
        "stash",
        "status",
        "switch",
        "tag",
    ],
    "pytest": [],  # single-command tool; no subcommand dispatch
}

# ---------------------------------------------------------------------------
# Help-output parser
# ---------------------------------------------------------------------------


def _run(args: list[str]) -> tuple[str, int]:
    """Run *args* as a subprocess and return (stdout+stderr combined, returncode)."""
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )
    combined = result.stdout + result.stderr
    return combined, result.returncode


def parse_top_level_subcommands(help_text: str) -> list[tuple[str, str]]:
    """Extract ``(subcommand, description)`` pairs from the top-level ``gh help`` output.

    Matches lines of the form::

        <spaces><word>:<spaces><description>

    as used in the "CORE COMMANDS" and "ADDITIONAL COMMANDS" sections of ``gh help``.
    Returns pairs in the order they appear, deduplicated.
    """
    import re

    pattern = re.compile(r"^\s{2,}([\w][\w-]*):\s{1,}(.+)$")
    seen: set[str] = set()
    results: list[tuple[str, str]] = []
    for line in help_text.splitlines():
        m = pattern.match(line)
        if m:
            name, desc = m.group(1).strip(), m.group(2).strip()
            if name not in seen:
                seen.add(name)
                results.append((name, desc))
    return results


def parse_commands_section(help_text: str) -> list[tuple[str, str]]:
    """Extract (subcommand, description) pairs from 'Commands:'-style help text.

    Handles tools that use the format::

        Commands:
          run      Run a command or script
          add      Add dependencies

    Returns pairs in the order they appear, deduplicated.
    """
    import re

    pattern = re.compile(r"^\s{2,}([\w][\w-]*)\s{2,}(.+)$")
    seen: set[str] = set()
    results: list[tuple[str, str]] = []
    for line in help_text.splitlines():
        m = pattern.match(line)
        if m:
            name, desc = m.group(1).strip(), m.group(2).strip()
            if name not in seen:
                seen.add(name)
                results.append((name, desc))
    return results


def _split_sections(text: str) -> dict[str, list[str]]:
    """Split ``gh <sub> --help`` output into labelled sections.

    Section headings are ALL-CAPS lines (possibly followed by a colon), e.g.
    ``USAGE``, ``FLAGS``, ``EXAMPLES``.  Returns a dict mapping normalised
    section name to the list of lines belonging to that section.  Lines before
    the first heading go under the key ``"PREAMBLE"``.
    """
    import re

    sections: dict[str, list[str]] = {}
    current = "PREAMBLE"
    sections[current] = []

    heading_re = re.compile(r"^([A-Z][A-Z ]{2,}[A-Z]):?\s*$")
    for line in text.splitlines():
        m = heading_re.match(line.rstrip())
        if m:
            current = m.group(1).strip()
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)
    return sections


def _extract_description(sections: dict[str, list[str]], fallback: str) -> str:
    """Return the short description from the preamble, falling back to *fallback*."""
    for line in sections.get("PREAMBLE", []):
        stripped = line.strip()
        if stripped:
            return stripped
    return fallback


def _extract_usage(sections: dict[str, list[str]]) -> str:
    """Return a code block for the USAGE section, or empty string."""
    lines = sections.get("USAGE", [])
    body = "\n".join(line.rstrip() for line in lines).strip()
    if not body:
        return ""
    return f"```\n{body}\n```"


def _extract_flags_table(sections: dict[str, list[str]]) -> str:
    """Convert FLAGS / INHERITED FLAGS lines to a Markdown table.

    Lines that look like ``  --flag    description`` are turned into table rows.
    Returns an empty string if no flags are found.
    """
    import re

    flag_re = re.compile(r"^\s{2,}(-[\w,\s\-\[\]<>]+?)\s{2,}(.+)$")
    rows: list[tuple[str, str]] = []
    seen_flags: set[str] = set()

    for section_key in ("FLAGS", "INHERITED FLAGS"):
        for line in sections.get(section_key, []):
            m = flag_re.match(line)
            if m:
                flag_text = m.group(1).strip()
                desc_text = m.group(2).strip()
                if flag_text not in seen_flags:
                    seen_flags.add(flag_text)
                    rows.append((flag_text, desc_text))

    if not rows:
        return ""

    lines = [
        "| Flag | Description |",
        "|------|-------------|",
    ]
    for flag, desc in rows:
        # Escape pipe characters that would break the Markdown table
        flag_cell = flag.replace("|", "\\|")
        desc_cell = desc.replace("|", "\\|")
        lines.append(f"| `{flag_cell}` | {desc_cell} |")
    return "\n".join(lines)


def _extract_examples(sections: dict[str, list[str]]) -> str:
    """Return a fenced code block for the EXAMPLES section, or empty string."""
    lines = sections.get("EXAMPLES", [])
    body = "\n".join(line.rstrip() for line in lines).strip()
    if not body:
        return ""
    return f"```\n{body}\n```"


def build_subcommand_markdown(subcommand: str, help_text: str, fallback_desc: str) -> str:
    """Convert raw ``<tool> <subcommand> --help`` output to structured Markdown.

    *subcommand* should be the full command string, e.g. ``gh issue`` or ``uv run``.
    """
    sections = _split_sections(help_text)
    description = _extract_description(sections, fallback_desc)
    usage_block = _extract_usage(sections)
    flags_table = _extract_flags_table(sections)
    examples_block = _extract_examples(sections)

    parts: list[str] = [
        f"# {subcommand}",
        f"> {description}",
        "",
    ]

    parts.append("## Usage")
    if usage_block:
        parts.append(usage_block)
    else:
        parts.append(f"```\n{subcommand} [flags]\n```")
    parts.append("")

    parts.append("## Flags")
    if flags_table:
        parts.append(flags_table)
    else:
        parts.append("_No flags documented._")
    parts.append("")

    parts.append("## Examples")
    if examples_block:
        parts.append(examples_block)
    else:
        parts.append("_No examples documented._")

    return "\n".join(parts).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Cache freshness check
# ---------------------------------------------------------------------------


def _cache_is_fresh(index_path: Path, max_age_hours: int = CACHE_MAX_AGE_HOURS) -> bool:
    """Return True if *index_path* exists and is younger than *max_age_hours*."""
    if not index_path.exists():
        return False
    mtime = datetime.fromtimestamp(index_path.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    return age_hours < max_age_hours


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def fetch_gh_docs(
    output_dir: Path,
    *,
    check: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Fetch ``gh`` CLI help and write structured Markdown to *output_dir*.

    Returns the process exit code (0 = success, 1 = error).
    """
    # Verify gh is on PATH
    if not shutil.which("gh"):
        print("[fetch_toolchain_docs] Error: 'gh' not found on PATH.", file=sys.stderr)
        return 1

    subcommand_dir = output_dir / "gh"
    index_path = subcommand_dir / "index.md"
    aggregate_path = output_dir / "gh.md"

    # --check: skip if fresh
    if check and not force and _cache_is_fresh(index_path):
        print(f"[fetch_toolchain_docs] Cache is fresh (< {CACHE_MAX_AGE_HOURS}h old). Skipping.")
        return 0

    # Get top-level help
    top_help, rc = _run(["gh", "help"])
    if rc != 0 and not top_help.strip():
        print(f"[fetch_toolchain_docs] Error: 'gh help' failed (exit {rc}).", file=sys.stderr)
        return 1

    subcommands = parse_top_level_subcommands(top_help)
    if not subcommands:
        print("[fetch_toolchain_docs] Error: no subcommands found in 'gh help' output.", file=sys.stderr)
        return 1

    print(f"[fetch_toolchain_docs] Found {len(subcommands)} subcommands.")

    if dry_run:
        print(f"[dry-run] Would create directory: {subcommand_dir}")
        for name, desc in subcommands:
            print(f"[dry-run] Would write: {subcommand_dir / name}.md  ({desc[:60]})")
        print(f"[dry-run] Would write: {index_path}")
        print(f"[dry-run] Would write: {aggregate_path}")
        return 0

    # Create output dir
    subcommand_dir.mkdir(parents=True, exist_ok=True)

    # Fetch per-subcommand docs
    per_subcommand_docs: list[tuple[str, str, str]] = []  # (name, desc, markdown)

    for name, desc in subcommands:
        sub_help, sub_rc = _run(["gh", name, "--help"])
        if sub_rc != 0 and not sub_help.strip():
            print(f"[fetch_toolchain_docs] Warning: 'gh {name} --help' failed — skipping.", file=sys.stderr)
            continue

        md = build_subcommand_markdown(f"gh {name}", sub_help, desc)
        out_path = subcommand_dir / f"{name}.md"
        out_path.write_text(md, encoding="utf-8")
        per_subcommand_docs.append((name, desc, md))
        try:
            display = out_path.relative_to(REPO_ROOT)
        except ValueError:
            display = out_path
        print(f"  wrote {display}")

    if not per_subcommand_docs:
        print("[fetch_toolchain_docs] Error: no subcommand docs were written.", file=sys.stderr)
        return 1

    # Build index.md
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index_lines: list[str] = [
        "# gh — Command Index",
        "",
        f"_Generated {now_str} by `fetch_toolchain_docs.py`._",
        "",
        "| Subcommand | Description |",
        "|------------|-------------|",
    ]
    for name, desc, _ in per_subcommand_docs:
        index_lines.append(f"| [`gh {name}`]({name}.md) | {desc} |")
    index_lines.append("")

    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    try:
        display_index = index_path.relative_to(REPO_ROOT)
    except ValueError:
        display_index = index_path
    print(f"  wrote {display_index}")

    # Build aggregate gh.md
    aggregate_parts: list[str] = [
        "# gh CLI Reference",
        "",
        f"_Generated {now_str} by `fetch_toolchain_docs.py`._",
        "",
        "---",
        "",
    ]
    for _, _, md in per_subcommand_docs:
        aggregate_parts.append(md)
        aggregate_parts.append("\n---\n")

    aggregate_path.write_text("\n".join(aggregate_parts), encoding="utf-8")
    try:
        display_agg = aggregate_path.relative_to(REPO_ROOT)
    except ValueError:
        display_agg = aggregate_path
    print(f"  wrote {display_agg}")

    print(f"[fetch_toolchain_docs] Done — {len(per_subcommand_docs)} subcommands cached.")
    return 0


def fetch_generic_tool_docs(
    tool: str,
    output_dir: Path,
    *,
    check: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Fetch help output for *tool* and write structured Markdown to *output_dir*.

    Dispatches based on TOOL_SUBCOMMANDS[tool]:
    - ``None`` → auto-discover subcommands from ``<tool> --help``
    - ``[list]`` → use fixed subcommand list
    - ``[]`` → single-command tool; write one aggregate file only

    Returns the process exit code (0 = success, 1 = error).
    """
    if not shutil.which(tool):
        print(f"[fetch_toolchain_docs] Error: '{tool}' not found on PATH.", file=sys.stderr)
        return 1

    fixed_subcommands = TOOL_SUBCOMMANDS.get(tool)
    is_single_command = fixed_subcommands is not None and len(fixed_subcommands) == 0

    # For single-command tools the aggregate file IS the main artifact.
    subcommand_dir = output_dir / tool
    index_path = subcommand_dir / "index.md"
    aggregate_path = output_dir / f"{tool}.md"
    freshness_path = aggregate_path if is_single_command else index_path

    if check and not force and _cache_is_fresh(freshness_path):
        print(f"[fetch_toolchain_docs] Cache is fresh (< {CACHE_MAX_AGE_HOURS}h old). Skipping.")
        return 0

    if is_single_command:
        # --- Single-command tool (e.g. pytest) ---
        help_text, rc = _run([tool, "--help"])
        if rc != 0 and not help_text.strip():
            print(
                f"[fetch_toolchain_docs] Error: '{tool} --help' failed (exit {rc}).",
                file=sys.stderr,
            )
            return 1

        md = build_subcommand_markdown(tool, help_text, f"{tool} — {help_text.splitlines()[0].strip()}")
        if dry_run:
            print(f"[dry-run] Would write: {aggregate_path}")
            return 0
        output_dir.mkdir(parents=True, exist_ok=True)
        aggregate_path.write_text(md, encoding="utf-8")
        try:
            display = aggregate_path.relative_to(REPO_ROOT)
        except ValueError:
            display = aggregate_path
        print(f"  wrote {display}")
        print(f"[fetch_toolchain_docs] Done — {tool} cached.")
        return 0

    # --- Subcommand-based tools ---
    top_help, rc = _run([tool, "--help"])
    if rc != 0 and not top_help.strip():
        print(
            f"[fetch_toolchain_docs] Error: '{tool} --help' failed (exit {rc}).",
            file=sys.stderr,
        )
        return 1

    if fixed_subcommands is None:
        # Auto-discover
        subcommand_list = parse_commands_section(top_help)
    else:
        # Fixed list — look up descriptions from auto-parsed top-level help
        desc_map = dict(parse_commands_section(top_help))
        subcommand_list = [(s, desc_map.get(s, s)) for s in fixed_subcommands]

    if not subcommand_list:
        print(
            f"[fetch_toolchain_docs] Error: no subcommands found for '{tool}'.",
            file=sys.stderr,
        )
        return 1

    print(f"[fetch_toolchain_docs] Found {len(subcommand_list)} subcommands for {tool}.")

    if dry_run:
        print(f"[dry-run] Would create directory: {subcommand_dir}")
        for name, desc in subcommand_list:
            print(f"[dry-run] Would write: {subcommand_dir / name}.md  ({desc[:60]})")
        print(f"[dry-run] Would write: {index_path}")
        print(f"[dry-run] Would write: {aggregate_path}")
        return 0

    subcommand_dir.mkdir(parents=True, exist_ok=True)

    per_subcommand_docs: list[tuple[str, str, str]] = []
    for name, desc in subcommand_list:
        sub_help, sub_rc = _run([tool, name, "--help"])
        if sub_rc != 0 and not sub_help.strip():
            print(
                f"[fetch_toolchain_docs] Warning: '{tool} {name} --help' failed — skipping.",
                file=sys.stderr,
            )
            continue
        md = build_subcommand_markdown(f"{tool} {name}", sub_help, desc)
        out_path = subcommand_dir / f"{name}.md"
        out_path.write_text(md, encoding="utf-8")
        per_subcommand_docs.append((name, desc, md))
        try:
            display = out_path.relative_to(REPO_ROOT)
        except ValueError:
            display = out_path
        print(f"  wrote {display}")

    if not per_subcommand_docs:
        print(
            f"[fetch_toolchain_docs] Error: no subcommand docs written for '{tool}'.",
            file=sys.stderr,
        )
        return 1

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build index.md
    index_lines: list[str] = [
        f"# {tool} — Command Index",
        "",
        f"_Generated {now_str} by `fetch_toolchain_docs.py`._",
        "",
        "| Subcommand | Description |",
        "|------------|-------------|",
    ]
    for name, desc, _ in per_subcommand_docs:
        index_lines.append(f"| [`{tool} {name}`]({name}.md) | {desc} |")
    index_lines.append("")
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    try:
        display_index = index_path.relative_to(REPO_ROOT)
    except ValueError:
        display_index = index_path
    print(f"  wrote {display_index}")

    # Build aggregate <tool>.md
    agg_parts: list[str] = [
        f"# {tool} CLI Reference",
        "",
        f"_Generated {now_str} by `fetch_toolchain_docs.py`._",
        "",
        "---",
        "",
    ]
    for _, _, md in per_subcommand_docs:
        agg_parts.append(md)
        agg_parts.append("\n---\n")
    aggregate_path.write_text("\n".join(agg_parts), encoding="utf-8")
    try:
        display_agg = aggregate_path.relative_to(REPO_ROOT)
    except ValueError:
        display_agg = aggregate_path
    print(f"  wrote {display_agg}")

    print(f"[fetch_toolchain_docs] Done — {len(per_subcommand_docs)} subcommands cached for {tool}.")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fetch_toolchain_docs.py",
        description=(
            "Cache CLI tool help output as structured Markdown under .cache/toolchain/. "
            "Allows agents to look up command syntax locally without burning tokens."
        ),
    )
    parser.add_argument(
        "--tool",
        default="gh",
        choices=list(TOOL_SUBCOMMANDS.keys()),
        help="CLI tool to document.  Default: gh.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        metavar="PATH",
        help="Root directory for cache output.  Default: .cache/toolchain/",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Skip refresh if cache files are < 24 hours old.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always re-fetch, ignoring cache age.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without touching the filesystem.",
    )
    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()

    if args.tool == "gh":
        rc = fetch_gh_docs(
            output_dir,
            check=args.check,
            force=args.force,
            dry_run=args.dry_run,
        )
    else:
        rc = fetch_generic_tool_docs(
            args.tool,
            output_dir,
            check=args.check,
            force=args.force,
            dry_run=args.dry_run,
        )
    sys.exit(rc)


if __name__ == "__main__":
    main()
