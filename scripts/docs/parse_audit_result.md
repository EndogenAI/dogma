# `parse\_audit\_result`

parse_audit_result.py
---------------------

Purpose:
    Converts JSON provenance audit output (from audit_provenance.py) into human-readable
    Markdown reports and risk assessment tables suitable for PR comments and CI logs.

    Implements provenance risk assessment per docs/research/enforcement-tier-mapping.md
    and docs/research/bubble-clusters-substrate.md § Pattern B4 — Provenance Transparency.

    Risk levels are computed based on:
    - axiom_cite_count: Number of MANIFESTO.md citations in agent governing: field
    - test_coverage: Code coverage % of agent-associated test files
    - Activity level: Age since last modification over 90 days

    Thresholds (configurable, default baseline in gap-analysis-bubble-clusters.md § R8):
    - Green (Low risk): cite_count > threshold × 0.8 AND coverage > 80%
    - Yellow (Medium risk): cite_count between threshold × 0.5 and 0.8, OR coverage 60–80%
    - Red (High risk): cite_count < threshold × 0.5 AND coverage < 60%

Inputs:
    --audit-report FILE   Path to JSON report from audit_provenance.py
    --threshold FLOAT     Baseline citation threshold (default: 0.5; see docs/research/gap-analysis...)
    --pr-comment          Generate PR comment file at /tmp/audit-comment.md
    --output FILE         Write JSON risk assessment to file (default: stdout if --pr-comment)

Outputs:
    JSON risk assessment:
    {
        "status": "green" | "yellow" | "red",
        "summary": {
            "agents_analyzed": int,
            "green_count": int,
            "yellow_count": int,
            "red_count": int,
            "avg_cite_intensity": float,  # average cites per agent
            "overall_risk": str
        },
        "agents": [
            {
                "name": str,
                "status": str,
                "risk_level": str,
                "axiom_cites": int,
                "test_coverage": float | null,
                "notes": str
            },
            ...
        ],
        "recommendations": [str],
        "markdown_report": str
    }
    Exit code: 0 on success; 1 on error.

Usage examples:
    uv run python scripts/audit_provenance.py --output /tmp/audit.json
    uv run python scripts/parse_audit_result.py /tmp/audit.json --threshold 0.5

    # For PR commenting:
    uv run python scripts/parse_audit_result.py /tmp/audit.json --pr-comment
    gh pr comment --body-file /tmp/audit-comment.md

## Usage

```bash
    uv run python scripts/audit_provenance.py --output /tmp/audit.json
    uv run python scripts/parse_audit_result.py /tmp/audit.json --threshold 0.5

    # For PR commenting:
    uv run python scripts/parse_audit_result.py /tmp/audit.json --pr-comment
    gh pr comment --body-file /tmp/audit-comment.md
```

<!-- hash:227dc442cbac61f7 -->
