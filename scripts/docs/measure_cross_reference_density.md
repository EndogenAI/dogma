# `measure\_cross\_reference\_density`

Measure cross-reference density (CRD) in agent and skill files.

CRD = intra-subsystem references / total references

Intra-subsystem: references to MANIFESTO.md, AGENTS.md, CONTRIBUTING.md, or same-layer files
Cross-subsystem: references outside the layer (e.g., agent → docs/guides, agent → scripts)

Usage:
    uv run python scripts/measure_cross_reference_density.py [--output FILE]

Output: JSON with per-file metrics and fleet statistics

## Usage

```bash
    uv run python scripts/measure_cross_reference_density.py [--output FILE]
```

<!-- hash:c1adecd37ec7e6f3 -->
