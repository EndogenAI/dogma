"""scripts/scaffold_agent.py

Scaffold a new VS Code Copilot .agent.md file from a minimal template.

Purpose:
    Generate a well-formed .agent.md stub in .github/agents/ with correct
    frontmatter, body structure, and placeholder sections ready to be filled in.
    Enforces the naming conventions and frontmatter schema defined in
    .github/agents/AGENTS.md.

Inputs:
    --name         Display name for the agent, e.g. "Research Foo"  (required)
    --description  One-line summary ≤ 200 characters               (required)
    --posture      readonly | creator | full                        (default: creator)
    --area         Area prefix for fleet sub-agents, e.g. "research"
                   If omitted, the agent is treated as a standalone workflow agent.
    --dry-run      Print the generated file without writing it

Outputs:
    .github/agents/<slugified-name>.agent.md

Usage examples:
    uv run python scripts/scaffold_agent.py \
        --name "Research Foo" \
        --description "Surveys sources on foo topics and catalogues findings." \
        --posture creator \
        --area research

    uv run python scripts/scaffold_agent.py \
        --name "Research Foo" \
        --description "Surveys sources on foo topics and catalogues findings." \
        --dry-run

Exit codes:
    0  Success
    1  Validation error (name conflict, description too long, missing required arg)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).parent.parent / ".github" / "agents"

POSTURE_TOOLS: dict[str, list[str]] = {
    "readonly": ["search", "read", "changes", "usages"],
    "creator": ["search", "read", "edit", "web", "changes", "usages"],
    "full": [
        "search",
        "read",
        "edit",
        "write",
        "execute",
        "terminal",
        "usages",
        "changes",
        "agent",
    ],
}

TEMPLATE = """\
---
name: {name}
description: {description}
tools:
{tools_yaml}
handoffs:
  - label: Hand off to Review
    agent: Review
    prompt: "Work is complete. Please review the changed files against AGENTS.md constraints before committing."
    send: false
  - label: Return to Executive
    agent: {executive_hint}
    prompt: "Results are ready. Please review and decide on the next step."
    send: false
---

## Persona

<persona>
You are the **{name}** for the EndogenAI Workflows project.

<!-- TODO: Write a one-sentence mandate for this agent. -->
</persona>

---

## Endogenous Sources — Read Before Acting

<context>
1. [`AGENTS.md`](../../AGENTS.md) — guiding constraints.
2. [`docs/guides/`](../../docs/guides/) — existing formalized guides.
3. The active session scratchpad (`.tmp/<branch>/<date>.md`) — read before acting to avoid re-discovering context.

<!-- TODO: Add any additional files this agent must read before acting. -->
</context>

---

## Workflow

<instructions>
<!-- TODO: Enumerate the numbered steps or role-specific checklist for this agent. -->

1. Read endogenous sources listed above.
2. <!-- Step 2 -->
3. <!-- Step 3 -->
4. Hand off to **Review** when work is complete.
</instructions>

---

## Guardrails

<constraints>
<!-- Explicit list of what this agent must NOT do. -->

- Do not commit directly — always hand off to **Review** first.
- Do not modify files outside the scope of this agent's stated role.
- Do not install packages or modify lockfiles without explicit instruction.
</constraints>

---

## Completion Criteria

<output>
<!-- TODO: Define the deliverables and success conditions for this agent. -->

- [ ] All required files created or updated.
- [ ] Changes reviewed (handed off to Review) before committing.
</output>
"""


def slugify(name: str) -> str:
    """Convert a display name to a lowercase-kebab-case file slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def validate_name_unique(name: str) -> None:
    existing = {}
    for f in AGENTS_DIR.glob("*.agent.md"):
        content = f.read_text()
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if match and match.group(1).strip() == name:
            print(f"ERROR: An agent named '{name}' already exists in {f.name}", file=sys.stderr)
            sys.exit(1)
    return existing


def build_tools_yaml(posture: str) -> str:
    tools = POSTURE_TOOLS.get(posture)
    if tools is None:
        print(
            f"ERROR: Unknown posture '{posture}'. Choose one of: readonly, creator, full",
            file=sys.stderr,
        )
        sys.exit(1)
    return "\n".join(f"  - {t}" for t in tools)


def infer_executive(name: str, area: str | None) -> str:
    """Best-guess executive name for the return handoff hint."""
    if area:
        return f"Executive {area.title()}"
    # Fall back to a generic placeholder
    return "<!-- target executive agent name -->"


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new .agent.md file in .github/agents/.")
    parser.add_argument("--name", required=True, help="Display name for the agent")
    parser.add_argument("--description", required=True, help="One-line summary ≤ 200 chars")
    parser.add_argument(
        "--posture",
        choices=["readonly", "creator", "full"],
        default="creator",
        help="Tool posture (default: creator)",
    )
    parser.add_argument("--area", default=None, help="Area prefix, e.g. 'research'")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing")
    args = parser.parse_args()

    # Validate description length
    if len(args.description) > 200:
        print(
            f"ERROR: description is {len(args.description)} characters; max is 200.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate name uniqueness
    if not args.dry_run:
        validate_name_unique(args.name)

    tools_yaml = build_tools_yaml(args.posture)
    executive_hint = infer_executive(args.name, args.area)

    content = TEMPLATE.format(
        name=args.name,
        description=args.description,
        tools_yaml=tools_yaml,
        executive_hint=executive_hint,
    )

    slug = slugify(args.name)
    out_path = AGENTS_DIR / f"{slug}.agent.md"

    if args.dry_run:
        print(f"# DRY RUN — would write: {out_path}\n")
        print(content)
        return

    if out_path.exists():
        print(f"ERROR: File already exists: {out_path}", file=sys.stderr)
        sys.exit(1)

    out_path.write_text(content)
    print(f"Created: {out_path}")
    print("Next steps:")
    print("  1. Fill in the TODO sections in the generated file.")
    print("  2. Update .github/agents/README.md with the new agent entry.")
    print("  3. Verify handoff targets: grep -h '^name:' .github/agents/*.agent.md | sort | uniq -d")
    print("  4. Commit: feat(agents): add <name> agent")


if __name__ == "__main__":
    main()
