# `audit\_ai\_dependencies`

scripts/audit_ai_dependencies.py

Scan .github/agents and scripts/ for external AI API references and produce
a dependency inventory for the NIST AI RMF GOVERN 6.1 annual audit.

Purpose:
    Maps every external AI API call in dogma agent files and scripts to its
    provider, then outputs a structured inventory in YAML. The inventory is
    the input to the manual ENISA 8-dimension scoring step (recorded in
    data/enisa-lock-in-scoring.yml). This implements issue #381 and satisfies
    the NIST AI RMF GOVERN 6.1 control for third-party AI dependency tracking.

    Run annually (or when a new AI provider dependency is introduced) to
    produce an updated snapshot.

Inputs:
    .github/agents/*.agent.md   — fleet agent files (scanned for provider refs)
    scripts/*.py                — Python scripts (scanned for provider refs)
    --agents-dir DIR            — override agents directory (default: .github/agents)
    --scripts-dir DIR           — override scripts directory (default: scripts)
    --output FILE               — write YAML inventory to this file
                                  (default: stdout)
    --dry-run                   — print inventory to stdout without writing file

Outputs:
    YAML inventory with keys: scan_date, providers[], raw_references[]
    Each raw_reference: file, provider_id, line_number, evidence

Exit codes:
    0   Scan completed (even if no providers found)
    1   No input directories found or fatal error
    2   I/O error

Usage examples:
    # Print inventory to stdout
    uv run python scripts/audit_ai_dependencies.py --dry-run

    # Write to file for review
    uv run python scripts/audit_ai_dependencies.py --output /tmp/ai-deps.yml

    # Custom dirs
    uv run python scripts/audit_ai_dependencies.py \
        --agents-dir .github/agents \
        --scripts-dir scripts \
        --output /tmp/ai-deps.yml

## Usage

```bash
    # Print inventory to stdout
    uv run python scripts/audit_ai_dependencies.py --dry-run

    # Write to file for review
    uv run python scripts/audit_ai_dependencies.py --output /tmp/ai-deps.yml

    # Custom dirs
    uv run python scripts/audit_ai_dependencies.py \
        --agents-dir .github/agents \
        --scripts-dir scripts \
        --output /tmp/ai-deps.yml
```

<!-- hash:3fdecc6b5f97f9b9 -->
