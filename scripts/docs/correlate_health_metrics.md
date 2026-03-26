# `correlate\_health\_metrics`

Measure health metric correlations with cross-reference density.

Health Proxies:
1. Task Velocity: GitHub issues closed while file was active (issues/month)
2. Test Coverage: % of referenced scripts with passing tests
3. Citation Coherence: Consistency of MANIFESTO.md axiom citations

Computes Pearson correlation coefficient (R) and significance test.

Usage:
    uv run python scripts/correlate_health_metrics.py [--crd-file FILE]

Output: JSON with per-file health metrics and correlation analysis

## Usage

```bash
    uv run python scripts/correlate_health_metrics.py [--crd-file FILE]
```

<!-- hash:904f31e76e85d1f6 -->
