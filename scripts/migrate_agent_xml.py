"""scripts/migrate_agent_xml.py

Bulk-migrate .agent.md body sections to hybrid Markdown + XML format.

Purpose:
    Transform one or more .github/agents/*.agent.md files from plain-prose bodies
    to the hybrid Markdown + XML schema recommended by the EndogenAI xml-agent-
    instruction-format research (docs/research/xml-agent-instruction-format.md).

    The hybrid schema keeps `## Section` headings as the outer document skeleton
    (for human readability and IDE navigation) while wrapping each section's prose
    content in a semantic XML tag for Claude's instruction parsing.

    YAML frontmatter is never modified. Only the body below the closing `---` fence
    is transformed.

Behaviour:
    1. Parse YAML frontmatter — preserve verbatim, do not touch.
    2. Split body into sections at `## Heading` boundaries.
    3. For each section, look up the canonical XML tag from the heading-to-tag map.
    4. If a tag is found and the section body has ≥ MIN_BODY_LINES non-empty lines,
       wrap the body in <tag>...</tag> preserving all blank lines and indentation.
    5. Sections not in the tag map, or with fewer than MIN_BODY_LINES lines, are
       passed through unchanged.
    6. Validate resulting XML well-formedness (all opened tags closed).
    7. Output: --dry-run prints unified diff to stdout; without --dry-run, writes
       in-place.

Tag map (heading keyword → XML tag):
    Persona, Role                         → <persona>
    Instructions, Behavior, Workflow      → <instructions>
    Context, Environment, Endogenous      → <context>
    Examples                              → <examples>
    Tools, Tool Guidance                  → <tools>
    Constraints, Guardrails, Scope        → <constraints>
    Output Format, Response Format,
      Deliverables, Completion Criteria   → <output>

Inputs:
    --file <path>    Single file to migrate.
    --all            Migrate all *.agent.md in .github/agents/.
    --dry-run        Print diff without writing.
    --min-lines <n>  Skip files whose body has fewer than N non-empty lines.
                     (default: 30)
    --model-scope    Only migrate files where `model` field starts with this value.
                     Use 'all' to disable filtering. (default: disabled — all files)
    --tag-map <json> JSON string overriding section heading → tag mapping.

Outputs:
    stdout: dry-run diff output, or confirmation of written files.
    stderr: warnings (skipped files, well-formedness issues).

Exit codes:
    0  Success (no parse/well-formedness errors), including no-op runs.
    1  Parse error or well-formedness failure.

Usage examples:
    # Dry-run a single file
    uv run python scripts/migrate_agent_xml.py \\
        --file .github/agents/executive-researcher.agent.md --dry-run

    # Migrate a single file in-place
    uv run python scripts/migrate_agent_xml.py \\
        --file .github/agents/executive-researcher.agent.md

    # Dry-run all agent files
    uv run python scripts/migrate_agent_xml.py --all --dry-run

    # Migrate all files, skip those with < 40 body lines
    uv run python scripts/migrate_agent_xml.py --all --min-lines 40

    # Preview with a custom tag override (JSON)
    uv run python scripts/migrate_agent_xml.py --file agent.md --dry-run \\
        --tag-map '{"Workflow": "instructions", "Philosophy": "context"}'
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).parent.parent / ".github" / "agents"

# Minimum number of non-empty body lines before we apply XML wrapping to a section.
MIN_BODY_LINES: int = 3

# ---------------------------------------------------------------------------
# Heading → XML tag mapping
# Keys are matched case-insensitively as substrings of the heading text.
# The first match wins.
# ---------------------------------------------------------------------------

DEFAULT_TAG_MAP: dict[str, str] = {
    # Persona / identity
    "persona": "persona",
    "role": "persona",
    # Primary instructions
    "instructions": "instructions",
    "behavior": "instructions",
    "behaviour": "instructions",
    "workflow": "instructions",
    # Context / environment
    "context": "context",
    "environment": "context",
    "endogenous sources": "context",
    # Examples
    "examples": "examples",
    # Tool guidance
    "tool guidance": "tools",
    "tools": "tools",
    # Constraints / guardrails
    "constraints": "constraints",
    "guardrails": "constraints",
    "scope": "constraints",
    # Output format / deliverables
    "output format": "output",
    "response format": "output",
    "deliverables": "output",
    "completion criteria": "output",
}

# ---------------------------------------------------------------------------
# YAML frontmatter parsing
# ---------------------------------------------------------------------------

_FM_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_block, body).

    frontmatter_block includes the opening and closing '---' fences plus a
    trailing newline so it can be concatenated directly with the body.
    """
    match = _FM_PATTERN.match(text)
    if match:
        return match.group(0), text[match.end() :]
    return "", text


def get_frontmatter_field(fm_text: str, key: str) -> str:
    """Return the raw string value of a YAML frontmatter key, or ''."""
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", fm_text, re.MULTILINE)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# Body section parsing
# ---------------------------------------------------------------------------


def split_into_sections(body: str) -> list[tuple[str, str]]:
    """Split body text into a list of (heading_line, content) pairs.

    The first item may have an empty heading_line for any text that appears
    before the first ## heading (e.g., a preamble paragraph).

    Lines inside fenced code blocks (``` or ~~~) are ignored for heading
    detection so that example Markdown headings in code blocks don't create
    spurious section splits.
    """
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_lines: list[str] = []
    in_code_fence = False

    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        # Toggle code fence state
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_fence = not in_code_fence

        if not in_code_fence and line.startswith("## "):
            # Save the accumulated section
            sections.append((current_heading, "".join(current_lines)))
            current_heading = line.rstrip("\n")
            current_lines = []
        else:
            current_lines.append(line)

    # Flush the final section
    sections.append((current_heading, "".join(current_lines)))
    return sections


def non_empty_line_count(text: str) -> int:
    """Count non-empty lines in a string."""
    return sum(1 for line in text.splitlines() if line.strip())


# ---------------------------------------------------------------------------
# Tag lookup
# ---------------------------------------------------------------------------


def lookup_tag(heading: str, tag_map: dict[str, str]) -> str | None:
    """Return the XML tag name for *heading*, or None if not in map."""
    heading_lower = heading.lstrip("#").strip().lower()
    for keyword, tag in tag_map.items():
        if keyword in heading_lower:
            return tag
    return None


# ---------------------------------------------------------------------------
# XML wrapping
# ---------------------------------------------------------------------------


def wrap_in_tag(tag: str, content: str) -> str:
    """Wrap *content* in <tag>...</tag>, preserving leading/trailing blank lines.

    Inserts a blank line after the opening tag and before the closing tag so
    the human-readable document still breathes visually.
    """
    # Preserve leading blank line (if any) before the opening tag
    stripped = content.lstrip("\n")
    leading_blank = "\n" if len(content) - len(stripped) > 0 else ""

    trailing_stripped = content.rstrip("\n")
    trailing_newlines = "\n" * (len(content) - len(trailing_stripped))
    trailing_newlines = trailing_newlines or "\n"

    return f"{leading_blank}<{tag}>\n{trailing_stripped}\n</{tag}>{trailing_newlines}"


def validate_xml_wellformed(body: str, known_tags: set[str]) -> list[str]:
    """Check that every opening wrapper tag we added has a matching closing tag.

    We only validate the tags from our known tag set, not arbitrary XML in the
    content (e.g. code blocks may contain '<slug>' which would break full XML
    parsing). This is a structural sanity check, not a full XML parse.
    """
    errors: list[str] = []
    for tag in known_tags:
        open_count = body.count(f"<{tag}>")
        close_count = body.count(f"</{tag}>")
        if open_count != close_count:
            errors.append(f"Mismatched tag <{tag}>: {open_count} opening, {close_count} closing")
    return errors


# ---------------------------------------------------------------------------
# Migration logic
# ---------------------------------------------------------------------------


def migrate_text(original: str, tag_map: dict[str, str], min_body_lines: int) -> str:
    """Return the migrated text, or the original if no changes were needed."""
    frontmatter, body = split_frontmatter(original)
    sections = split_into_sections(body)

    output_parts: list[str] = [frontmatter]

    for heading, content in sections:
        if not heading:
            # Preamble (before first ## heading)
            output_parts.append(content)
            continue

        tag = lookup_tag(heading, tag_map)

        if tag is None or non_empty_line_count(content) < min_body_lines:
            # No mapping or too short — pass through unchanged
            output_parts.append(heading + "\n" + content)
            continue

        # Check if already wrapped — idempotent migration
        content_stripped = content.strip()
        if content_stripped.startswith(f"<{tag}>") and content_stripped.endswith(f"</{tag}>"):
            output_parts.append(heading + "\n" + content)
            continue

        wrapped = wrap_in_tag(tag, content)
        output_parts.append(heading + "\n" + wrapped)

    return "".join(output_parts)


# ---------------------------------------------------------------------------
# File-level processing
# ---------------------------------------------------------------------------


def process_file(
    path: Path,
    tag_map: dict[str, str],
    dry_run: bool,
    min_lines: int,
    model_scope: str | None,
) -> bool | None:
    """Process a single agent file.

    Returns:
        True   — a change was made (or would be in dry-run mode).
        False  — file was skipped or required no change.
        None   — well-formedness failure; the file was not written.
    """
    try:
        original = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: cannot read {path}: {exc}", file=sys.stderr)
        return False

    # Model scope filter
    if model_scope and model_scope.lower() != "all":
        fm_text, _ = split_frontmatter(original)
        model_val = get_frontmatter_field(fm_text, "model")
        if model_val and not model_val.lower().startswith(model_scope.lower()):
            print(f"SKIP (model scope): {path}", file=sys.stderr)
            return False

    # Body line count filter
    _, body = split_frontmatter(original)
    if non_empty_line_count(body) < min_lines:
        print(f"SKIP (< {min_lines} body lines): {path}", file=sys.stderr)
        return False

    migrated = migrate_text(original, tag_map, MIN_BODY_LINES)

    if migrated == original:
        print(f"NO CHANGE: {path}")
        return False

    # Validate XML well-formedness of the migrated body (tag-balanced check)
    _, migrated_body = split_frontmatter(migrated)
    known_tags = set(tag_map.values())
    errors = validate_xml_wellformed(migrated_body, known_tags)
    if errors:
        print(
            f"ERROR: well-formedness failure in {path}:\n" + "\n".join(f"  {e}" for e in errors),
            file=sys.stderr,
        )
        return None

    if dry_run:
        original_lines = original.splitlines(keepends=True)
        migrated_lines = migrated.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            migrated_lines,
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
        )
        sys.stdout.writelines(diff)
        return True

    path.write_text(migrated, encoding="utf-8")
    print(f"MIGRATED: {path}")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate .agent.md body sections to hybrid Markdown + XML format.",
        epilog="Exit 0 = success. Exit 1 = error or no files matched.",
    )

    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--file",
        metavar="<path>",
        help="Single .agent.md file to migrate.",
    )
    target.add_argument(
        "--all",
        action="store_true",
        help="Migrate all *.agent.md files in .github/agents/.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print unified diff without writing changes.",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=30,
        metavar="N",
        help="Skip files with fewer than N non-empty body lines. (default: 30)",
    )
    parser.add_argument(
        "--model-scope",
        metavar="PREFIX",
        default=None,
        help=(
            "Only migrate files where the frontmatter 'model' field starts with "
            "PREFIX (e.g. 'Claude'). Files without a model field are always included."
        ),
    )
    parser.add_argument(
        "--tag-map",
        metavar="JSON",
        default=None,
        help=(
            "JSON object overriding or extending the default heading→tag map. "
            'Example: \'{"Philosophy": "context", "Mandate": "persona"}\''
        ),
    )

    args = parser.parse_args()

    # Build tag map
    tag_map = dict(DEFAULT_TAG_MAP)
    if args.tag_map:
        try:
            overrides = json.loads(args.tag_map)
            if not isinstance(overrides, dict):
                print("ERROR: --tag-map must be a JSON object.", file=sys.stderr)
                sys.exit(1)
            # Normalise keys to lowercase for matching
            tag_map.update({k.lower(): v for k, v in overrides.items()})
        except json.JSONDecodeError as exc:
            print(f"ERROR: invalid --tag-map JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    # Collect target files
    if args.all:
        files = sorted(AGENTS_DIR.glob("*.agent.md"))
        if not files:
            print(f"ERROR: no .agent.md files found in {AGENTS_DIR}", file=sys.stderr)
            sys.exit(1)
    else:
        files = [Path(args.file)]

    if args.dry_run:
        print("# DRY RUN — no files will be written\n")

    changed_count = 0
    error_count = 0
    for f in files:
        result = process_file(
            path=f,
            tag_map=tag_map,
            dry_run=args.dry_run,
            min_lines=args.min_lines,
            model_scope=args.model_scope,
        )
        if result is True:
            changed_count += 1
        elif result is None:
            error_count += 1

    noun = "file" if changed_count == 1 else "files"
    action = "would change" if args.dry_run else "changed"
    print(f"\n{changed_count} {noun} {action}.")
    if error_count:
        print(f"{error_count} file(s) had well-formedness errors — see stderr.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
