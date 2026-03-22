#!/usr/bin/env python3
"""
Substrate Distiller — audit the implementation state of accepted recommendations.

Scans the repository substrate (agents, skills, guides) to ensure that
recommendations marked as 'accepted' or 'accepted-for-adoption' in
data/recommendations-registry.yml are explicitly referenced by their ID.

Exit codes:
  0: All accepted recommendations are distilled/referenced.
  1: Found accepted recommendations missing from the substrate.
  2: I/O or configuration error.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_registry(registry_path: Path) -> List[Dict[str, Any]]:
    """Load the recommendations registry."""
    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("recommendations", [])
    except Exception as e:
        print(f"Error reading registry: {e}", file=sys.stderr)
        sys.exit(2)


def get_substrate_files(root: Path) -> List[Path]:
    """Find all substrate files (*.agent.md, SKILL.md, docs/guides/*.md)."""
    files = []

    # Agents
    files.extend(root.glob(".github/agents/**/*.agent.md"))

    # Skills
    files.extend(root.glob(".github/skills/**/SKILL.md"))

    # Guides
    files.extend(root.glob("docs/guides/**/*.md"))

    return [p for p in files if p.is_file()]


def main():
    parser = argparse.ArgumentParser(description="Audit recommendation distillation.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if any missing.")
    parser.add_argument("--dry_run", action="store_true", dest="dry_run", help="Preview without exit code 1.")
    parser.add_argument("--id", help="Filter for a specific recommendation ID.")
    parser.add_argument("--registry", default="data/recommendations-registry.yml", help="Registry path.")

    args = parser.parse_args()
    root = Path.cwd()
    registry_path = root / args.registry

    recommendations = load_registry(registry_path)

    accepted_statuses = {"accepted", "accepted-for-adoption"}
    targets = [r for r in recommendations if r.get("status") in accepted_statuses]

    if args.id:
        targets = [r for r in targets if r.get("id") == args.id]
        if not targets:
            print(f"No accepted recommendation found with ID: {args.id}")
            return

    if not targets:
        print("No accepted recommendations to audit.")
        return

    substrate_files = get_substrate_files(root)
    print(f"Scanning {len(substrate_files)} substrate files for {len(targets)} recommendations...")

    # Read all content once to avoid re-reading for every ID
    file_contents = {}
    for f in substrate_files:
        try:
            file_contents[f] = f.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not read {f}: {e}")

    missing = []
    for rec in targets:
        rec_id = rec["id"]
        found = False
        found_in = []
        for path, content in file_contents.items():
            if rec_id in content:
                found = True
                found_in.append(str(path.relative_to(root)))

        if not found:
            missing.append(rec)
            print(f"❌ MISSING: {rec_id} ({rec.get('title', 'No Title')[:50]}...)")
        else:
            print(f"✅ DISTILLED: {rec_id} (found in {len(found_in)} files)")

    if missing:
        print(f"\nFinal count: {len(missing)} missing / {len(targets)} total accepted.")
        if args.check and not args.dry_run:
            sys.exit(1)
    else:
        print("\nAll accepted recommendations are distilled into the substrate.")


if __name__ == "__main__":
    main()
