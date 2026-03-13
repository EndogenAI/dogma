"""
scripts/seed_labels.py — Idempotent GitHub label seeder for EndogenAI/dogma.

Purpose
-------
Reads a YAML label manifest (data/labels.yml by default) and creates or updates
every label in the ``labels`` section using ``gh label create --force``. Optionally
deletes legacy GitHub default labels listed in the ``legacy_labels`` section.

Run this script whenever the label manifest changes or when bootstrapping a fresh
fork of the repository.

In production, label enforcement is handled automatically by `.github/workflows/label-sync.yml`
(runs on every push to `main` when `data/labels.yml` changes). This script serves as the
bootstrap tool for fresh forks or for manual ad-hoc enforcement when the CI workflow is
not yet active.

Inputs
------
- data/labels.yml (or path supplied via --labels-file)

Outputs
-------
- stdout: one line per label action (CREATE, DELETE, skipped in dry-run)
- stderr: warnings and errors

Flags
-----
--labels-file PATH   Path to the labels YAML manifest. Default: data/labels.yml
--delete-legacy      Also delete labels listed in the legacy_labels section.
                     Default: False. Use with caution — irreversible on live repos.
--dry-run            Print what would happen without making any API calls. Exit 0.
--repo OWNER/REPO    Target repository. Default: current repo from ``gh repo view``.

Exit codes
----------
0  All operations succeeded (or --dry-run completed).
1  Validation error: YAML invalid, required keys missing, or gh auth failure.
2  File not found: the labels YAML file does not exist.

Usage examples
--------------
# Preview all changes without making API calls
uv run python scripts/seed_labels.py --dry-run

# Create/update all namespace labels in the current repo
uv run python scripts/seed_labels.py

# Create/update labels AND delete legacy GitHub defaults
uv run python scripts/seed_labels.py --delete-legacy

# Target a specific repo and manifest file
uv run python scripts/seed_labels.py --repo myorg/myrepo --labels-file data/labels.yml

# Dry-run with legacy deletion included
uv run python scripts/seed_labels.py --dry-run --delete-legacy
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Idempotent GitHub label seeder — reads data/labels.yml and syncs via gh CLI.",
    )
    parser.add_argument(
        "--labels-file",
        default="data/labels.yml",
        metavar="PATH",
        help="Path to the labels YAML manifest (default: data/labels.yml).",
    )
    parser.add_argument(
        "--delete-legacy",
        action="store_true",
        default=False,
        help="Delete labels listed in the legacy_labels section of the manifest.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print planned actions without making any gh API calls.",
    )
    parser.add_argument(
        "--repo",
        default=None,
        metavar="OWNER/REPO",
        help="Target repository (owner/repo). Defaults to current repo from gh repo view.",
    )
    return parser


# ---------------------------------------------------------------------------
# YAML loading and validation
# ---------------------------------------------------------------------------


def load_manifest(path: Path) -> dict[str, Any]:
    """Load and minimally validate the labels YAML manifest.

    Returns the parsed dict. Exits 2 if the file is missing, 1 if invalid.
    """
    if not path.exists():
        print(f"ERROR: labels file not found: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"ERROR: failed to parse YAML in {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print(f"ERROR: {path} must contain a YAML mapping at the top level.", file=sys.stderr)
        sys.exit(1)

    if "labels" not in data or not isinstance(data["labels"], list):
        print(f"ERROR: {path} must contain a 'labels' list.", file=sys.stderr)
        sys.exit(1)

    for i, entry in enumerate(data["labels"]):
        for required_key in ("name", "color", "description"):
            if required_key not in entry:
                print(
                    f"ERROR: labels[{i}] is missing required key '{required_key}'.",
                    file=sys.stderr,
                )
                sys.exit(1)

    return data


# ---------------------------------------------------------------------------
# gh CLI helpers
# ---------------------------------------------------------------------------


def _gh_repo_flag(repo: str | None) -> list[str]:
    """Return ['-R', 'owner/repo'] if repo is set, else []."""
    return ["-R", repo] if repo else []


def _verify_gh_auth(repo: str | None, dry_run: bool) -> None:
    """Check that `gh auth status` succeeds; exit 1 on failure."""
    if dry_run:
        return
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            "ERROR: gh auth check failed. Run `gh auth login` first.\n" + result.stderr.strip(),
            file=sys.stderr,
        )
        sys.exit(1)


def create_or_update_label(
    name: str,
    color: str,
    description: str,
    repo: str | None,
    *,
    dry_run: bool,
) -> None:
    """Create or update a single label via gh label create --force."""
    cmd = [
        "gh",
        "label",
        "create",
        name,
        "--color",
        color,
        "--description",
        description,
        "--force",
    ] + _gh_repo_flag(repo)

    if dry_run:
        print(f'[DRY RUN] WOULD CREATE/UPDATE  {name!r}  #{color}  "{description}"')
        return

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"ERROR: failed to create/update label {name!r}: {result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK  CREATE/UPDATE  {name!r}")


def delete_label(name: str, repo: str | None, *, dry_run: bool) -> None:
    """Delete a single label via gh label delete --yes."""
    cmd = ["gh", "label", "delete", name, "--yes"] + _gh_repo_flag(repo)

    if dry_run:
        print(f"[DRY RUN] WOULD DELETE          {name!r}")
        return

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Treat "label not found" as a non-fatal warning (already gone).
        stderr = result.stderr.strip()
        if "not found" in stderr.lower() or "could not find" in stderr.lower():
            print(f"SKIP  DELETE  {name!r}  (not found — already removed)")
        else:
            print(
                f"ERROR: failed to delete label {name!r}: {stderr}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print(f"OK  DELETE  {name!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    labels_path = Path(args.labels_file)
    manifest = load_manifest(labels_path)

    _verify_gh_auth(args.repo, dry_run=args.dry_run)

    namespace_labels: list[dict[str, str]] = manifest["labels"]
    legacy_labels: list[str] = manifest.get("legacy_labels", [])

    if args.dry_run:
        print(f"[DRY RUN] Loaded {len(namespace_labels)} namespace labels from {labels_path}")
        if args.delete_legacy:
            print(f"[DRY RUN] Will delete {len(legacy_labels)} legacy labels")
        print()

    errors = 0

    # Create / update namespace labels
    for label in namespace_labels:
        try:
            create_or_update_label(
                name=label["name"],
                color=label["color"],
                description=label["description"],
                repo=args.repo,
                dry_run=args.dry_run,
            )
        except SystemExit:
            errors += 1

    # Delete legacy labels (only if --delete-legacy passed)
    if args.delete_legacy:
        if not args.dry_run:
            print()
        for name in legacy_labels:
            try:
                delete_label(name, args.repo, dry_run=args.dry_run)
            except SystemExit:
                errors += 1

    if errors:
        print(f"\n{errors} error(s) encountered.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")
    else:
        print("\nDone.")


if __name__ == "__main__":
    main()
