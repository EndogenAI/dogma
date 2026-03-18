---
governs: [endogenous-first, documentation-first]
---

# Quarterly Values Alignment Review

> Governing axiom: [MANIFESTO.md § Ethical Values](../../MANIFESTO.md#ethical-values) — values must be actively maintained; drift is not a failure of design but of ongoing encoding discipline. See also [AGENTS.md § Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy).

At the end of every quarter, the Executive Orchestrator runs a three-step values alignment review. This is not discretionary — it is a required phase-gate before the quarter's sprint retrospective is closed.

---

## Three-Step Review

### Step 1 — Encoding Coverage Check

Run the encoding coverage script to identify MANIFESTO.md axioms and AGENTS.md constraints with low cross-reference density:

```bash
uv run python scripts/encoding_coverage.py
```

The script outputs a table of axioms and constraints with their cross-reference counts. Any entry with fewer than 2 cross-references is flagged as `LOW_DENSITY`.

Record the top 3 `LOW_DENSITY` entries in the session scratchpad under `## Values Alignment Verdict`.

### Step 2 — Axiom Drift Detection

Run the cross-reference density measurement to surface any axioms that have drifted from the encoding substrate:

```bash
uv run python scripts/measure_cross_reference_density.py
```

The script compares cross-reference density between the current and prior quarter snapshots. A density decrease of > 15% on any axiom is flagged as `DRIFT`.

Append the output to the `## Values Alignment Verdict` section in the scratchpad.

### Step 3 — Produce Verdict and Act

Based on the outputs from Steps 1 and 2, produce a `## Values Alignment Verdict` block in the session scratchpad:

**If no LOW_DENSITY or DRIFT flags**:
```
## Values Alignment Verdict

Status: ALIGNED
Date: <YYYY-MM-DD>
Encoding coverage: all axioms ≥ 2 cross-references
Drift: none detected
```

**If LOW_DENSITY or DRIFT flags are present**:
```
## Values Alignment Verdict

Status: DRIFT DETECTED
Date: <YYYY-MM-DD>
Items:
- <axiom/constraint>: <density count> cross-references (LOW_DENSITY)
- <axiom/constraint>: <density delta> (DRIFT)
```

Then open a GitHub issue for each DRIFT item:

```bash
gh issue create \
  --title "chore: re-encode <axiom> — drift detected in Q<N> values review" \
  --label "type:chore,priority:high" \
  --body-file /tmp/drift-issue.md
```

---

## Schedule

| Quarter End | Review Due |
|-------------|------------|
| Q1 (March 31) | First session in April |
| Q2 (June 30) | First session in July |
| Q3 (September 30) | First session in October |
| Q4 (December 31) | First session in January |

The review must be completed and the `## Values Alignment Verdict` section written before any sprint planning for the new quarter begins.

---

## Governing References

- [MANIFESTO.md § Ethical Values](../../MANIFESTO.md#ethical-values) — values must be actively maintained, not declared once and assumed stable
- [AGENTS.md § Value Fidelity Test Taxonomy](../../AGENTS.md#value-fidelity-test-taxonomy) — four-layer encoding signal taxonomy this review operationalizes at the quarterly cadence
- [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle) — drift detection is a repeated task; `encoding_coverage.py` and `measure_cross_reference_density.py` are its encoded forms
