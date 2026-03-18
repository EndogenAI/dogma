"""Check and count all VS Code Problems panel diagnostic sources in this repo.

Provides the authoritative baseline count for each diagnostic category generated
by the agent/skill file fleet. Replaces ad-hoc grep for error counting.

Categories audited:
  A — `Attribute 'governs' is not supported`  (Copilot Chat prompts-diagnostics-provider)
      Source: any `governs:` key in .agent.md / SKILL.md YAML frontmatter.
      Fix:    rename governs: → x-governs: (issue #390)

  B — `Unknown tool 'X'`  (Copilot Chat MCP tool static validation)
      Source: tool references in `tools:` frontmatter that are not registered in
              .vscode/mcp.json or are not built-in VS Code tool namespaces.
      Fix:    remove inactive extension tool refs from tools: lists.

Usage:
    uv run python scripts/check_problems_panel.py          # full audit + counts
    uv run python scripts/check_problems_panel.py --json   # machine-readable JSON

Exit codes:
    0 — no diagnostic sources found
    1 — diagnostic sources present (counts printed to stdout)
    2 — I/O or parse error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Namespaces that VS Code's built-in tool validator recognises — no error fired.
_KNOWN_NAMESPACES = frozenset(
    [
        "read",
        "edit",
        "execute",
        "search",
        "web",
        "agent",
        "browser",
        "vscode",
    ]
)

# Extension-namespaced tools that are conditionally available (fire when extension
# is not active or MCP server is offline).
_CONDITIONAL_PATTERNS = re.compile(
    r"(github\.vscode-pull-request-github/|vscode\.mermaid-chat-features/|dogma-governance/|\btodo\b)"
)


def _frontmatter(text: str) -> str:
    """Return the raw YAML frontmatter string from a file, or empty string."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    return text[3:end]


def _tools_from_frontmatter(fm: str) -> list[str]:
    """Extract tool names from YAML frontmatter (array or flow-sequence format)."""
    # Array format: `- tool_name` lines after `tools:`
    array_m = re.search(r"^tools:\s*\n((?:[ \t]+-[^\n]+\n?)+)", fm, re.MULTILINE)
    if array_m:
        return [re.sub(r"^[ \t]+-\s*", "", line).strip() for line in array_m.group(1).splitlines() if line.strip()]
    # Flow-sequence format: `tools: [a, b, c]`
    flow_m = re.search(r"^tools:\s*\[([^\]]+)\]", fm, re.MULTILINE | re.DOTALL)
    if flow_m:
        return [t.strip() for t in flow_m.group(1).split(",") if t.strip()]
    return []


def audit(repo_root: Path) -> dict:
    """Return counts and file lists for each diagnostic category."""
    cat_a: list[str] = []  # governs: present
    cat_b: list[tuple[str, list[str]]] = []  # (file, [unknown tools])

    targets = list((repo_root / ".github" / "agents").glob("*.agent.md"))
    targets += list((repo_root / ".github" / "skills").rglob("SKILL.md"))

    for fpath in sorted(targets):
        text = fpath.read_text(encoding="utf-8", errors="replace")
        fm = _frontmatter(text)

        # Category A: governs: in frontmatter (bare key, not x-governs:)
        if re.search(r"^governs\s*:", fm, re.MULTILINE):
            cat_a.append(str(fpath.relative_to(repo_root)))

        # Category B: unknown / conditional tools
        tools = _tools_from_frontmatter(fm)
        unknown = []
        for t in tools:
            namespace = t.split("/")[0] if "/" in t else t
            if namespace not in _KNOWN_NAMESPACES and _CONDITIONAL_PATTERNS.search(t):
                unknown.append(t)
        if unknown:
            cat_b.append((str(fpath.relative_to(repo_root)), unknown))

    return {
        "category_a": {
            "label": "Attribute 'governs' is not supported",
            "count": len(cat_a),
            "fix": "rename governs: → x-governs: (issue #390)",
            "files": cat_a,
        },
        "category_b": {
            "label": "Unknown tool references (extension tools / MCP offline)",
            "count": sum(len(tools) for _, tools in cat_b),
            "fix": "remove inactive extension tool refs from tools: lists",
            "files": {f: tools for f, tools in cat_b},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit VS Code Problems panel diagnostic sources in agent/skill fleet."
    )
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    try:
        result = audit(REPO_ROOT)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    total = result["category_a"]["count"] + result["category_b"]["count"]

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if total == 0 else 1

    # Human-readable output
    print("=== Problems Panel Diagnostic Audit ===\n")

    ca = result["category_a"]
    print(f"Category A — {ca['label']}")
    print(f"  Count : {ca['count']} files")
    print(f"  Fix   : {ca['fix']}")
    if ca["files"]:
        for f in ca["files"]:
            print(f"    {f}")
    print()

    cb = result["category_b"]
    print(f"Category B — {cb['label']}")
    print(f"  Count : {cb['count']} tool refs across {len(cb['files'])} files")
    print(f"  Fix   : {cb['fix']}")
    if cb["files"]:
        for fname, tools in cb["files"].items():
            print(f"    {fname}")
            for t in tools:
                print(f"      - {t}")
    print()

    print(f"Total diagnostic sources  : {total}")
    if total == 0:
        print("✓ Clean — no Problems panel sources found.")
        return 0
    else:
        print("✗ Diagnostic sources present — see above for fix guidance.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
