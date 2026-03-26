# `substrate\_distiller`

Substrate Distiller — audit the implementation state of accepted recommendations.

Scans the repository substrate (agents, skills, guides) to ensure that
recommendations marked as 'accepted' or 'accepted-for-adoption' in
data/recommendations-registry.yml are explicitly referenced by their ID.

Exit codes:
  0: All accepted recommendations are distilled/referenced.
  1: Found accepted recommendations missing from the substrate.
  2: I/O or configuration error.

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:20320caedae0ab35 -->
