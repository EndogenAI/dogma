import argparse
import json
import re
import sys
from pathlib import Path
from typing import List


def find_repo_root() -> Path:
    """Walk up from this file until pyproject.toml is found."""
    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


# Mapping of mandatory tags to their expected Markdown headings
MANDATORY_MAPPINGS = {
    "context": r"## Beliefs & Context",
    "instructions": r"## Workflow & Intentions",
    "constraints": r"## (Guardrails|Constraints|Philosophy)",
    "output": r"## Desired Outcomes & Acceptance",
}


def audit_agent_file(file_path: Path) -> List[str]:
    """Check an agent file for mandatory XML tags and heading alignment."""
    content = file_path.read_text(encoding="utf-8")
    missing_tags = []

    for tag, heading_pattern in MANDATORY_MAPPINGS.items():
        # Tag existence check
        opening_tag = f"<{tag}>"
        closing_tag = f"</{tag}>"

        has_opening = opening_tag in content
        has_closing = closing_tag in content

        if not has_opening or not has_closing:
            missing_tags.append(tag)
            continue

        # Alignment check: heading should follow opening tag soon after
        # Non-greedy match or just line-by-line check would be safer, but
        # for a quick audit, we use a simpler pattern to avoid catastrophic backtracking.
        # Check if the heading exists anywhere after the opening tag.
        tag_index = content.find(opening_tag)
        heading_match = re.search(heading_pattern, content[tag_index:], re.IGNORECASE | re.MULTILINE)
        if not heading_match:
            missing_tags.append(f"{tag} (alignment)")

    return missing_tags


def main():
    parser = argparse.ArgumentParser(description="Audit agent fleet for structural compliance.")
    parser.add_argument(
        "--target-dir",
        type=str,
        default=".github/agents/",
        help="Directory to audit (default: .github/agents/)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    target_path = repo_root / args.target_dir

    if not target_path.exists() or not target_path.is_dir():
        print(f"Error: Target directory not found: {target_path}")
        sys.exit(1)

    agent_files = list(target_path.glob("*.agent.md"))
    gap_report = {}

    for agent_file in agent_files:
        missing = audit_agent_file(agent_file)
        if missing:
            gap_report[agent_file.name] = missing

    if args.format == "json":
        print(json.dumps(gap_report, indent=2))
    else:
        if not gap_report:
            print("Structural Audit: 100% compliant. No gaps found.")
        else:
            print(f"Structural Audit: {len(gap_report)}/{len(agent_files)} agents have gaps.")
            print("-" * 40)
            for agent, gaps in gap_report.items():
                print(f"{agent}: {', '.join(gaps)}")

    sys.exit(0)


if __name__ == "__main__":
    main()
