# `audit\_provenance`

audit_provenance.py
-------------------
Purpose:
    Audits the endogenic substrate for value signal provenance. Reads agent
    files and checks whether each file's instructions trace their signal
    provenance back to foundational MANIFESTO.md axioms via a 'x-governs:'
    frontmatter annotation.

    Provenance annotation format (in .agent.md YAML frontmatter):
        x-governs:
          - endogenous-first
          - programmatic-first

    Orphaned files: .agent.md files with no 'x-governs:' frontmatter field.
    Unverifiable citations: axiom names in 'x-governs:' not found in MANIFESTO.md.

Inputs:
    --agents-dir  PATH   Directory of .agent.md files (default: .github/agents/)
    --manifesto   PATH   Path to MANIFESTO.md for axiom name validation
                         (default: auto-resolved MANIFESTO.md at repo root)
    --output      FILE   Write JSON report to this file (default: stdout)
    --format      json|summary  Output format (default: json)

Outputs:
    JSON report:
    {
        "files": [
            {
                "path": str,
                "citations": [str],      # axiom names found in x-governs:
                "orphaned": bool,        # True if no x-governs: field at all
                "unverifiable": [str]    # axiom names not in MANIFESTO.md
            }
        ],
        "fleet_citation_coverage_pct": float,  # % of files with x-governs:
        "total_unverifiable": int
    }
    Exit code: 0 on success; non-zero on configuration or runtime errors.

Usage examples:
    uv run python scripts/audit_provenance.py
    uv run python scripts/audit_provenance.py --format summary
    uv run python scripts/audit_provenance.py --output /tmp/provenance.json

## Usage

```bash
    uv run python scripts/audit_provenance.py
    uv run python scripts/audit_provenance.py --format summary
    uv run python scripts/audit_provenance.py --output /tmp/provenance.json
```

<!-- hash:fcba3aa7f8dbaccf -->
