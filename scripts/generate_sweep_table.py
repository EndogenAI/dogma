"""Generate and maintain the corpus sweep table for back-propagation planning.

Reads docs/plans/corpus-sweep-data.yml (manual fields) and auto-detects:
  - Recency tier: from YAML frontmatter `date` field in each research doc
  - Already cited: by scanning primary papers for links/references to each doc

Usage:
  uv run python scripts/generate_sweep_table.py
      -> writes docs/plans/2026-03-12-corpus-sweep-table.md

  uv run python scripts/generate_sweep_table.py --output PATH
      -> writes to specified path

  uv run python scripts/generate_sweep_table.py --mark-read DOCNAME
      -> update status to ✅ in corpus-sweep-data.yml, then regenerate table

  uv run python scripts/generate_sweep_table.py --mark-in-progress DOCNAME
      -> update status to ⏳ in corpus-sweep-data.yml, then regenerate table

  uv run python scripts/generate_sweep_table.py --dry-run
      -> print table to stdout without writing files

Inputs:
  docs/plans/corpus-sweep-data.yml — manual fields data
  docs/research/*.md — source research docs (for recency detection)
  docs/research/values-encoding.md — primary paper (for citation scan)
  docs/research/bubble-clusters-substrate.md — primary paper
  docs/research/endogenic-design-paper.md — primary paper

Outputs:
  docs/plans/2026-03-12-corpus-sweep-table.md (or --output path)

Exit codes:
  0 — success
  1 — doc not found in YAML (--mark-read / --mark-in-progress), or primary paper missing
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = REPO_ROOT / "docs" / "research"
DATA_FILE = REPO_ROOT / "docs" / "plans" / "corpus-sweep-data.yml"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "plans" / "2026-03-12-corpus-sweep-table.md"

PRIMARY_PAPER_NAMES = {
    "values": "values-encoding.md",
    "bubble": "bubble-clusters-substrate.md",
    "endogenic": "endogenic-design-paper.md",
}


def detect_recency(doc_path: Path) -> str:
    """Detect recency tier from YAML frontmatter date field.

    Returns: 'Recent' | 'Mid' | 'Old' | 'Unknown'
    """
    try:
        content = doc_path.read_text(encoding="utf-8")
    except OSError:
        return "Unknown"

    if not content.startswith("---"):
        return "Unknown"

    end = content.find("---", 3)
    if end == -1:
        return "Unknown"

    frontmatter_text = content[3:end].strip()
    try:
        fm = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return "Unknown"

    if not isinstance(fm, dict) or "date" not in fm:
        return "Unknown"

    date_val = fm["date"]
    if date_val is None:
        return "Unknown"

    # Convert to string, handling datetime.date objects parsed by PyYAML
    if hasattr(date_val, "strftime"):
        date_str = date_val.strftime("%Y-%m-%d")
    else:
        date_str = str(date_val)

    try:
        doc_date = date.fromisoformat(date_str[:10])
    except (ValueError, TypeError):
        return "Unknown"

    today = date.today()
    four_weeks_ago = today - timedelta(weeks=4)
    six_months_ago = today - timedelta(days=182)

    if doc_date >= four_weeks_ago:
        return "Recent"
    if doc_date >= six_months_ago:
        return "Mid"
    return "Old"


def detect_citations(primary_paper_path: Path, doc_name: str) -> bool:
    """Return True if doc_name appears anywhere in primary_paper_path content.

    Covers both markdown link references "[...](path/doc_name)" and bare
    filename references.
    """
    content = primary_paper_path.read_text(encoding="utf-8")
    return doc_name in content


def build_already_cited(doc_name: str, citations_map: dict) -> str:
    """Return a compact string describing which primary papers cite doc_name.

    Args:
        doc_name: basename of the source doc (e.g. "agent-fleet-design-patterns.md")
        citations_map: dict mapping short key ('values' | 'bubble' | 'endogenic')
                       to a set of cited doc basenames

    Returns:
        'Yes (all)' | 'Yes (values/bubble/endogenic)' (subset) | 'No'
    """
    paper_order = ["values", "bubble", "endogenic"]
    cited_in = [key for key in paper_order if doc_name in citations_map.get(key, set())]

    if not cited_in:
        return "No"
    if len(cited_in) == 3:
        return "Yes (all)"
    return "Yes (" + "/".join(cited_in) + ")"


def format_table(entries: list) -> str:
    """Generate the Markdown sweep table from a list of enriched entry dicts.

    Each entry must contain: name, doc_type, synthesises, recency,
    relevance_values_encoding, relevance_bubble_clusters,
    relevance_endogenic_design, already_cited, scout_depth,
    scout_depth_reason, status.

    Returns a Markdown table string (no trailing newline).
    """
    header = (
        "| Doc | Type | Synthesises | Recency | values-encoding | bubble-clusters"
        " | endogenic-design | Already Cited | Scout Depth | Status |"
    )
    separator = (
        "|-----|------|-------------|---------|----------------|----------------|"
        "-----------------|---------------|-------------|--------|"
    )
    rows = [header, separator]

    for entry in entries:
        synth_list = entry.get("synthesises") or []
        synthesises_cell = ", ".join(s.replace(".md", "") for s in synth_list) if synth_list else "\u2014"

        ve = entry["relevance_values_encoding"]
        bc = entry["relevance_bubble_clusters"]
        ed = entry["relevance_endogenic_design"]

        row = (
            f"| {entry['name']}"
            f" | {entry['doc_type']}"
            f" | {synthesises_cell}"
            f" | {entry.get('recency', 'Unknown')}"
            f" | {ve['rating']} \u2014 {ve['rationale']}"
            f" | {bc['rating']} \u2014 {bc['rationale']}"
            f" | {ed['rating']} \u2014 {ed['rationale']}"
            f" | {entry.get('already_cited', 'No')}"
            f" | {entry['scout_depth']} \u2014 {entry['scout_depth_reason']}"
            f" | {entry['status']} |"
        )
        rows.append(row)

    return "\n".join(rows)


def generate_header(entries: list, citations_map: dict) -> str:
    """Generate the file header section including summary counts and cross-ref pre-scan.

    Args:
        entries: enriched entry dicts (with recency and already_cited populated)
        citations_map: dict mapping short key to set of cited doc names

    Returns a string that ends with a blank line (ready to prepend the table).
    """
    total = len(entries)
    thorough_count = sum(1 for e in entries if e["scout_depth"] == "Thorough")
    skim_count = sum(1 for e in entries if e["scout_depth"] == "Skim")
    skip_count = sum(1 for e in entries if e["scout_depth"] == "Skip")
    synth_thorough = sum(1 for e in entries if e["scout_depth"] == "Thorough" and e["doc_type"] == "Synthesis")

    today = date.today().strftime("%Y-%m-%d")

    paper_order = [
        ("values", "values-encoding.md"),
        ("bubble", "bubble-clusters-substrate.md"),
        ("endogenic", "endogenic-design-paper.md"),
    ]
    xref_lines = []
    for key, label in paper_order:
        cited = sorted(citations_map.get(key, set()))
        xref_lines.append(f"Docs already cited in **{label}**: {', '.join(cited) if cited else 'none'}")

    return f"""# Corpus Sweep Table \u2014 docs/research/ vs Primary Papers

**Generated**: {today}
**Primary papers assessed**:
- `values-encoding.md`
- `bubble-clusters-substrate.md`
- `endogenic-design-paper.md`

**Sweep covers**: {total} source docs (excludes OPEN_RESEARCH.md and the 3 primary papers)

---

## Summary Counts

- **Thorough**: {thorough_count} (of which {synth_thorough} are Synthesis docs \u2014 read first)
- **Skim**: {skim_count}
- **Skip**: {skip_count}
- **Total**: {total}

## Scout Strategy

**Phase 1 reading order**:
1. Read all Thorough-rated **Synthesis** docs first (higher signal density)
2. For each Synthesis doc, check whether its `Synthesises` constituents contain signals the synthesis missed
3. Descend into constituent Raw Research docs only if synthesis appears incomplete for that signal
4. Then read all remaining Thorough-rated Raw Research / Bridge docs

---

## Cross-Reference Pre-scan

{xref_lines[0]}

{xref_lines[1]}

{xref_lines[2]}

---

## Sweep Table

"""


def update_status(data_file: Path, doc_name: str, new_status: str) -> None:
    """Update the status field of a named doc in the YAML data file.

    Args:
        data_file: path to corpus-sweep-data.yml
        doc_name: basename with or without .md extension
        new_status: new status string (e.g. "✅", "⏳")

    Exits with code 1 if the doc is not found in the data file.
    """
    if not doc_name.endswith(".md"):
        doc_name = doc_name + ".md"

    with open(data_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    found = False
    for entry in data["docs"]:
        if entry["name"] == doc_name:
            entry["status"] = new_status
            found = True
            break

    if not found:
        print(f"Error: doc '{doc_name}' not found in {data_file}", file=sys.stderr)
        sys.exit(1)

    with open(data_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate corpus sweep table for back-propagation planning.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for the sweep table (default: docs/plans/2026-03-12-corpus-sweep-table.md)",
    )
    parser.add_argument(
        "--mark-read",
        metavar="DOCNAME",
        default=None,
        help="Mark a doc as read (\u2705) in corpus-sweep-data.yml, then regenerate table",
    )
    parser.add_argument(
        "--mark-in-progress",
        metavar="DOCNAME",
        default=None,
        help="Mark a doc as in-progress (\u23f3) in corpus-sweep-data.yml, then regenerate table",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print table to stdout without writing files",
    )
    # Hidden args for testing — not shown in --help
    parser.add_argument("--data-file", type=Path, default=DATA_FILE, help=argparse.SUPPRESS)
    parser.add_argument("--research-dir", type=Path, default=RESEARCH_DIR, help=argparse.SUPPRESS)
    args = parser.parse_args()

    output_path = args.output or DEFAULT_OUTPUT
    data_file: Path = args.data_file
    research_dir: Path = args.research_dir

    primary_papers = {key: research_dir / fname for key, fname in PRIMARY_PAPER_NAMES.items()}

    # Apply status updates before reading/generating
    if args.mark_read:
        update_status(data_file, args.mark_read, "\u2705")
    elif args.mark_in_progress:
        update_status(data_file, args.mark_in_progress, "\u23f3")

    # Load manual data
    with open(data_file, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)
    entries = raw_data["docs"]

    # Validate primary papers exist before scanning
    for key, paper_path in primary_papers.items():
        if not paper_path.exists():
            print(f"Error: primary paper not found: {paper_path}", file=sys.stderr)
            sys.exit(1)

    # Build citations map: key -> set of doc basenames cited in that paper
    citations_map: dict = {}
    for key, paper_path in primary_papers.items():
        content = paper_path.read_text(encoding="utf-8")
        citations_map[key] = {entry["name"] for entry in entries if entry["name"] in content}

    # Augment each entry with auto-detected fields
    for entry in entries:
        doc_path = research_dir / entry["name"]
        if not doc_path.exists():
            print(f"Warning: research doc not found: {doc_path}", file=sys.stderr)
            entry["recency"] = "Unknown"
        else:
            entry["recency"] = detect_recency(doc_path)
        entry["already_cited"] = build_already_cited(entry["name"], citations_map)

    header = generate_header(entries, citations_map)
    table = format_table(entries)
    full_output = header + table + "\n"

    if args.dry_run:
        print(full_output, end="")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_output, encoding="utf-8")
        print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
