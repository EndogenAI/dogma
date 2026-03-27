# `seed\_labels`

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

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:d9ecde1eadc80ccd -->
