"""
generate_agent_manifest.py
--------------------------
Purpose:
    Enumerate all .agent.md files in .github/agents/, extract name, description,
    tools, posture, capabilities, and handoffs from their YAML frontmatter, and
    emit a structured manifest to stdout (JSON or Markdown table). Enables
    lazy-loading of agent metadata — orchestrators can select the right agent
    from ~100-token stubs without paying the full ~5K-token cost of loading each
    agent body.

Inputs:
    .github/agents/*.agent.md files with YAML frontmatter blocks.

Outputs:
    JSON manifest (default) or Markdown table to stdout, or to --output file.
    Each agent entry contains:
        name          — display name from frontmatter
        description   — one-line summary from frontmatter
        tools         — list of tool names from frontmatter
        posture       — derived from tools: "readonly" | "creator" | "full"
        capabilities  — 2-5 short lowercase-hyphenated tags from description
        handoffs      — list of agent names this agent can hand off to
        file          — repo-relative path to the .agent.md file
    Summary line is always written to stderr:
        Generated manifest: N agents

Usage examples:
    # Print JSON manifest to stdout
    uv run python scripts/generate_agent_manifest.py

    # Write manifest to a file
    uv run python scripts/generate_agent_manifest.py --output .github/agents/manifest.json

    # Emit a Markdown table
    uv run python scripts/generate_agent_manifest.py --format markdown

    # Dry-run: list files that would be processed without generating output
    uv run python scripts/generate_agent_manifest.py --dry-run

    # Use a custom agents directory
    uv run python scripts/generate_agent_manifest.py --agents-dir path/to/agents/

Exit codes:
    0  Success
    1  Agents directory not found, or one or more files failed to parse
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """
    Walk up from this file's directory until a directory containing AGENTS.md
    is found. Falls back to one level above scripts/ if no marker is found.
    """
    candidate = Path(__file__).resolve().parent
    while candidate != candidate.parent:
        if (candidate / "AGENTS.md").exists():
            return candidate
        candidate = candidate.parent
    # Fallback: one level up from scripts/
    return Path(__file__).resolve().parent.parent


def extract_frontmatter(text: str) -> str | None:
    """
    Return the raw YAML text between the leading '---' fences, or None if the
    file does not open with a frontmatter block.
    """
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    return match.group(1) if match else None


def parse_simple_yaml(yaml_text: str) -> dict:
    """
    Parse a subset of YAML that contains only top-level scalar strings and
    flat string lists (the schema used by .agent.md frontmatter).

    Does NOT support: nested objects, multi-line strings, anchors, or tags.
    Returns a dict mapping string keys to str or list[str] values.
    """
    result: dict = {}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip blank lines and comments
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        # Match a top-level key
        key_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)", line)
        if key_match:
            key = key_match.group(1)
            value = key_match.group(2).strip()
            if value:
                # Scalar — strip optional surrounding quotes
                result[key] = value.strip("\"'")
                i += 1
            else:
                # Block list — collect following "  - item" lines
                items: list[str] = []
                i += 1
                while i < len(lines):
                    item_match = re.match(r"^\s+-\s+(.*)", lines[i])
                    if item_match:
                        items.append(item_match.group(1).strip().strip("\"'"))
                        i += 1
                    elif not lines[i].strip():
                        # Blank line — could be separator; keep scanning
                        i += 1
                    elif lines[i][0] == " " or lines[i][0] == "\t":
                        # Indented non-list content; skip
                        i += 1
                    else:
                        # New top-level key — stop collecting
                        break
                result[key] = items
        else:
            i += 1
    return result


# ---------------------------------------------------------------------------
# Posture, capabilities, and handoffs derivation
# ---------------------------------------------------------------------------

# Tool sets used to classify agent posture
_FULL_TOOLS = frozenset({"execute", "terminal", "agent", "run", "browser"})
_CREATOR_TOOLS = frozenset({"edit", "write", "create", "notebook"})


def derive_posture(tools: list[str]) -> str:
    """
    Derive the agent's posture from its declared tools list.

    Returns:
        "full"     — tools include execute/terminal/agent/run/browser
        "creator"  — tools include edit/write/create/notebook (but not full)
        "readonly" — tools are read/search only, or list is empty
    """
    tool_set = {t.lower() for t in tools}
    if tool_set & _FULL_TOOLS:
        return "full"
    if tool_set & _CREATOR_TOOLS:
        return "creator"
    return "readonly"


# Words to filter when extracting capability tags
_CAP_SKIP = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "are", "be", "was", "were", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "can", "all", "any", "each", "every", "both", "either",
    "before", "after", "between", "into", "through", "during", "per", "via", "this",
    "that", "these", "those", "it", "its", "they", "their", "them", "not", "no",
    "if", "when", "while", "about", "vs", "end", "non", "also", "only", "just",
    "use", "used", "always", "never",
})


def derive_capabilities(description: str, max_tags: int = 5) -> list[str]:
    """
    Extract 2-5 discriminating capability tags from an agent description.

    Strategy:
        Split on phrase boundaries (em-dash, semicolons, commas, periods), then
        from each non-trivial segment form a tag from the first 1-2 significant
        words (filtered against _CAP_SKIP).  Earlier segments are preferred since
        they capture the agent's core mandate.

    Returns a list of lowercase-hyphenated tags, 2 <= len <= max_tags.
    """
    # Split on natural phrase boundaries
    segments = re.split(r"\s*[—;,\.]\s*", description)

    tags: list[str] = []
    seen: set[str] = set()

    def sig_words(text: str) -> list[str]:
        """Return significant tokens from text, preserving hyphens."""
        tokens = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)*", text)
        return [t for t in tokens if t.lower() not in _CAP_SKIP and len(t) > 2]

    for seg in segments:
        if len(tags) >= max_tags:
            break
        words = sig_words(seg)
        if not words:
            continue
        tag = f"{words[0].lower()}-{words[1].lower()}" if len(words) >= 2 else words[0].lower()
        if tag not in seen:
            tags.append(tag)
            seen.add(tag)

    # Fallback: ensure at least 2 tags using individual significant words
    if len(tags) < 2:
        for w in sig_words(description):
            t = w.lower()
            if t not in seen:
                tags.append(t)
                seen.add(t)
                if len(tags) >= 2:
                    break

    return tags[:max_tags]


def extract_handoff_agents(yaml_text: str) -> list[str]:
    """
    Extract unique agent names from the handoffs[] block in raw YAML frontmatter.

    The handoffs block uses the schema:
        handoffs:
          - label: "some label"
            agent: AgentName
            ...

    Returns a deduplicated list of agent name strings in declaration order.
    Returns an empty list if no handoffs block is present.
    """
    in_handoffs = False
    agents: list[str] = []
    seen: set[str] = set()

    for line in yaml_text.splitlines():
        # Detect start of handoffs top-level key
        if re.match(r"^handoffs\s*:", line):
            in_handoffs = True
            continue
        # A new non-indented key ends the handoffs block
        if in_handoffs and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", line):
            break
        # Within the handoffs block, extract agent: sub-fields
        if in_handoffs:
            m = re.match(r"^\s+agent\s*:\s*(.+)", line)
            if m:
                agent_name = m.group(1).strip().strip("\"'")
                if agent_name and agent_name not in seen:
                    agents.append(agent_name)
                    seen.add(agent_name)

    return agents


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process_agent_file(path: Path) -> dict | None:
    """
    Read one .agent.md file and return a manifest entry dict, or None on
    failure. Warnings are written to stderr; the caller tracks whether any
    failures occurred.

    Returned dict shape:
        {
            "name":         str,
            "description":  str,
            "tools":        list[str],
            "posture":      str,         # "readonly" | "creator" | "full"
            "capabilities": list[str],   # 2-5 lowercase-hyphenated tags
            "handoffs":     list[str],   # agent names this agent can delegate to
            "file":         str,         # absolute path — relativised by build_manifest()
        }
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: Cannot read {path}: {exc}", file=sys.stderr)
        return None

    frontmatter_raw = extract_frontmatter(text)
    if frontmatter_raw is None:
        print(
            f"WARNING: No YAML frontmatter found in {path.name} — skipping.",
            file=sys.stderr,
        )
        return None

    try:
        data = parse_simple_yaml(frontmatter_raw)
    except Exception as exc:  # noqa: BLE001
        print(
            f"WARNING: Failed to parse frontmatter in {path.name}: {exc} — skipping.",
            file=sys.stderr,
        )
        return None

    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    tools = data.get("tools", [])

    if not name:
        print(
            f"WARNING: 'name' field missing or empty in {path.name} — skipping.",
            file=sys.stderr,
        )
        return None

    tools_list: list[str] = tools if isinstance(tools, list) else [tools]

    return {
        "name": name,
        "description": description,
        "tools": tools_list,
        "posture": derive_posture(tools_list),
        "capabilities": derive_capabilities(description),
        "handoffs": extract_handoff_agents(frontmatter_raw),
        "file": str(path),
    }


def build_manifest(agent_entries: list[dict], repo_root: Path) -> dict:
    """
    Assemble the top-level manifest dict and relativise file paths against
    repo_root so the output is portable.
    """
    entries = []
    for entry in agent_entries:
        e = dict(entry)
        try:
            e["file"] = str(Path(e["file"]).relative_to(repo_root))
        except ValueError:
            pass  # keep absolute if somehow outside repo root
        entries.append(e)

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "agent_count": len(entries),
        "agents": entries,
    }


def format_markdown(manifest: dict) -> str:
    """Render the manifest as a plain Markdown table (no trailing newline)."""
    rows = [
        "| Agent | Description | Posture | Capabilities | Handoffs |",
        "|-------|-------------|---------|--------------|----------|",
    ]
    for agent in manifest["agents"]:
        name = agent["name"]
        desc = agent["description"]
        posture = agent.get("posture", "")
        caps = ", ".join(agent.get("capabilities", []))
        handoffs = ", ".join(agent.get("handoffs", []))
        rows.append(f"| {name} | {desc} | {posture} | {caps} | {handoffs} |")
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a skills manifest of all .agent.md files. "
            "Outputs JSON (default) or a Markdown table to stdout or --output."
        )
    )
    parser.add_argument(
        "--agents-dir",
        default=None,
        metavar="DIR",
        help=(
            "Path to directory containing .agent.md files. "
            "Default: .github/agents/ relative to the repo root."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write the manifest to this file instead of stdout.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the list of .agent.md files that would be processed, then exit.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format: json (default) or markdown.",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()

    if args.agents_dir:
        agents_dir = Path(args.agents_dir).expanduser().resolve()
    else:
        agents_dir = repo_root / ".github" / "agents"

    if not agents_dir.is_dir():
        print(f"ERROR: Agents directory not found: {agents_dir}", file=sys.stderr)
        return 1

    agent_files = sorted(agents_dir.glob("*.agent.md"))

    # --dry-run: list files and exit without reading or writing anything
    if args.dry_run:
        print(
            f"Dry-run: would process {len(agent_files)} file(s):",
            file=sys.stderr,
        )
        for f in agent_files:
            try:
                rel = f.relative_to(repo_root)
            except ValueError:
                rel = f
            print(f"  {rel}")
        return 0

    # Parse each agent file
    had_errors = False
    entries: list[dict] = []
    for path in agent_files:
        entry = process_agent_file(path)
        if entry is None:
            had_errors = True
        else:
            entries.append(entry)

    if had_errors:
        return 1

    manifest = build_manifest(entries, repo_root)

    # Render output
    if args.format == "markdown":
        output_text = format_markdown(manifest) + "\n"
    else:
        output_text = json.dumps(manifest, indent=2) + "\n"

    # Write or print
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
        print(
            f"Generated manifest: {len(entries)} agents → {output_path}",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(output_text)
        print(f"Generated manifest: {len(entries)} agents", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
