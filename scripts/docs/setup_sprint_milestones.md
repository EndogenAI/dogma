# `setup\_sprint\_milestones`

Setup sprint milestones and assign issues to them.

Based on docs/plans/2026-03-25-next-sprint-recommendation.md, this script:
1. Defines Q2 Governance Wave milestones with phase-based issue assignments
2. Provides --dry-run preview of all assignments
3. Executes assignments with --apply flag via gh milestone API
4. Returns: 0 on success, 1 on API error, 2 on usage error

Usage:
    uv run python scripts/setup_sprint_milestones.py --dry-run
    uv run python scripts/setup_sprint_milestones.py --apply

Pre-populated from: docs/plans/2026-03-25-next-sprint-recommendation.md
Sprint Structure:
  - Q2 Governance Wave 1 (Apr 1–8): Phases 0–2
  - Q2 Governance Wave 2 (Apr 8–22): Phases 3–4 (future sprint)
  - Backlog — Research & Secondary: Bare-bones research + long-tail

## Usage

```bash

    uv run python scripts/setup_sprint_milestones.py --dry-run
    uv run python scripts/setup_sprint_milestones.py --apply

Pre-populated from: docs/plans/2026-03-25-next-sprint-recommendation.md
```

<!-- hash:ce63db6328bee93e -->
