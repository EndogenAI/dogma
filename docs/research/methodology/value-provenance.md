---
title: "Value Signal Provenance — Research Synthesis"
status: Final
governs: [endogenous-first, provenance-tracking]
---

# Value Signal Provenance — Research Synthesis

## 1. Executive Summary

Provenance tracing extends the existing value-encoding substrate in two ways:
where cross-reference density (#54) counts how many lines reference foundational
documents, and drift detection (#71) measures phrasal alignment with canonical
watermarks, provenance tracing establishes a chain-of-custody link between each
agent file and the specific MANIFESTO.md axioms that govern its instructions.

The chosen implementation — a `governs:` YAML frontmatter field validated against
MANIFESTO.md H2/H3 headings — is feasible with zero external dependencies and
reuses the existing frontmatter-parsing pattern from `generate_agent_manifest.py`.
Three candidate formats were evaluated (inline HTML comment, YAML frontmatter, external
JSON manifest); file-level frontmatter annotation was selected because it reuses
existing infrastructure, is invisible in rendered output, and is compatible with
the existing `validate_agent_files.py` CI gate.

The primary actionable output of `audit_provenance.py` is orphaned-file detection:
at baseline, every agent in the fleet lacks a `governs:` annotation, making the
fleet 100% orphaned. The follow-up task — adding `governs:` to the authoring
standard and running the audit in CI — is a single xs-effort sprint item. The
broader value of this work is closing the chain-of-custody gap: knowing that an
agent file references MANIFESTO.md (#54: cross-reference density) and uses the
correct phrases (#71: drift score) is necessary but not sufficient evidence that
it was actually derived from foundational axioms. The `governs:` annotation makes
the derivation relationship explicit and machine-checkable.

## 2. Hypothesis Validation

### H1 — Provenance tracing at instruction granularity is feasible without external dependencies

**Verdict: REFUTED (refined)** — instruction-level tracing would require embedding
each instruction block to a specific axiom, which in turn requires either semantic
analysis (Approach B from #71, deferred) or manual annotation of every instruction
paragraph. This is out of scope for the current sprint. File-level tracing via
`governs:` frontmatter is feasible with pure stdlib: extract frontmatter, parse the
`governs:` list, normalise to lowercase-hyphenated names, and compare against the
set of MANIFESTO.md H2/H3 headings — the entire check fits in ≤50 lines of Python.
The distinction between H4 "holographic encoding" (Pattern 6 in values-encoding.md)
and practical provenance tracking is the actionable divide: holographic encoding
means every file re-encodes all values, while provenance tracing means each file
declares which axioms it was derived from. Both are useful; only the latter is
automatable without NLP at the current toolchain level.

### H2 — Frontmatter annotation is the lowest-overhead viable format

**Verdict: CONFIRMED** — Format B (YAML frontmatter `governs:`) requires zero infrastructure changes, reuses existing frontmatter parsing, works with the existing CI gate in `validate_agent_files.py`, and produces a file-level provenance record that can be automatically audited. Format A (inline HTML comment) requires parsing comment syntax and placement discipline near each instruction block — higher authoring cost for equivalent file-level coverage. Format C (external JSON manifest) requires manual maintenance and drifts out of sync with file changes. Format B is strictly dominated on the overhead dimension.

### H3 — Most current agent files are provenance-orphaned

**Verdict: CONFIRMED** — No agent files in the fleet currently carry a `governs:`
frontmatter field. The fleet is 100% orphaned at baseline. This was verified by
running `uv run python scripts/audit_provenance.py --format summary` against
`.github/agents/`. The result: `fleet_citation_coverage_pct = 0.0`.
This is the highest-priority follow-up action: add `governs:` to the agent file
authoring standard in `docs/guides/agents.md` and make it a required frontmatter
key in `validate_agent_files.py` (Check 5, alongside the existing four checks).
The editing pass itself is xs-effort — one `governs:` block per agent file, each
containing axiom names from the MANIFESTO.md vocabulary.

## 3. Pattern Catalog

### Pattern P1 — File-Level Provenance via governs: Annotation

**Evidence**: Cross-domain precedent in legal citators (Shepard's Citations,
LexisNexis), package dependency graphs (`pyproject.toml` `dependencies:` field),
and the RDF/PROV-O ontology (`prov:wasDerivedFrom` predicate). Each system encodes
a "this was derived from" relationship at the artifact level without requiring
inline annotation of every sentence. The `prov:wasDerivedFrom` triple, for example,
links a derived dataset to its source dataset — the equivalent in this system is
a `governs:` field linking an agent file to the MANIFESTO.md axioms that justified
its behavioral constraints. YAML frontmatter is the idiomatic analog: structured,
machine-readable, invisible to rendered output, and already parsed by
`validate_agent_files.py`.

**Endogenous applicability**: Add `governs:` to `.agent.md` frontmatter as a
required field. Run `audit_provenance.py` to surface orphaned files and flag
unverifiable citations. The controlled vocabulary (MANIFESTO.md H2/H3 headings)
prevents citation drift to non-existent axioms — a hard constraint enforced at
audit time rather than relying on author discipline.

### Pattern P2 — Orphan Detection as First CI Gate

**Evidence**: Static analysis tools (mypy, ruff, eslint) all begin with
"is this referenced / typed / declared?" checks before deeper semantic analysis.
Orphan detection is O(N) over the file system — no semantic analysis required.
It is the least expensive and most actionable provenance check, analogous to
ruff's F821 undefined-name check: it catches the most obvious failure mode
(missing annotation entirely) with minimal false-positive risk.

**Endogenous applicability**: `audit_provenance.py --format summary` as a CI
report step; orphan count is reported but not a hard-fail at this stage. This
follows the same calibration posture as `detect_drift.py` — advisory first,
blocking only after a fleet baseline is established and the authoring standard
has been updated. Premature hard-fail gates create friction without improving
quality when the source-of-truth (the authoring standard) is still catching up.

### Pattern P3 — Vocabulary-Constrained Citations Prevent Citation Drift

**Evidence**: Legal citation systems require citations to use canonical identifiers
(case names, statute sections, reporter volumes) — free-text citations drift to
ambiguous or non-existent references. The Blue Book enforces this via a controlled
vocabulary of reporter abbreviations; Shepard's enforces it by only accepting
filed case citations, not informal summaries. The MANIFESTO.md H2/H3 heading set
as a controlled vocabulary for `governs:` values replicates this discipline at the
agent-file level: agents cannot cite invented axiom names without the audit script
flagging them as unverifiable.

**Endogenous applicability**: `audit_provenance.py` validates `governs:` values
against the normalised set of MANIFESTO.md headings and emits an `unverifiable`
list for any citation that does not match a known axiom name. This closes the loop
between authoring (add `governs:`) and validation (audit rejects unknowns) — the
same feedback loop that ruff provides for Python imports and mypy provides for
type annotations.

## 4. Recommendations

Refs: [../../AGENTS.md](../../AGENTS.md) (Endogenous-First, Documentation-First). [../../MANIFESTO.md](../../../MANIFESTO.md) (inheritance chain axiom).

**R1 (Immediate)**: Add `governs:` field to the `.agent.md` authoring standard in `docs/guides/agents.md` and make it a required frontmatter key in `validate_agent_files.py`. Effort: xs. Impact: transforms 100% orphan fleet to 0% orphan with one editing pass. This is the single highest-leverage follow-up from this synthesis.

**R2 (Sprint 2)**: Run `audit_provenance.py` as a CI report step (non-blocking) after every PR that touches `.github/agents/`. Report `fleet_citation_coverage_pct` as a trend metric alongside `avg_cross_ref_density` (from `generate_agent_manifest.py`). Effort: xs. Impact: creates visibility without blocking velocity.

**R3 (Sprint 3+)**: Add `unverifiable_count > 0` as a soft warning in CI (exit 0, print to PR summary). Push toward `fleet_citation_coverage_pct = 100%` as a sprint-quality metric. Treating this as a hard-fail gate is premature until R1 is complete.

**R4 (Post-baseline)**: When #71 Approach B (embedding-similarity drift detection) is implemented, combine `governs:` annotations with embedding similarity to produce instruction-level provenance traces — the full chain-of-custody vision where each instruction paragraph is linked to its governing axiom with a confidence score.

## 5. Sources

- `docs/research/values-encoding.md` — Pattern 6 (holographic encoding, H4), Pattern 3 (watermark phrases); OQ-VE-1
- `scripts/audit_provenance.py` — implementation; run `--format summary` for current fleet baseline
- `scripts/detect_drift.py` — complementary drift signal (phrasal alignment); see §7 of values-encoding.md
- `scripts/generate_agent_manifest.py` — cross-reference density (#54); `avg_cross_ref_density` for fleet comparison
- Bray et al. (2014) RDF 1.1 Concepts — PROV-O provenance ontology as cross-domain precedent
- Legal citator precedent: Shepard's Citations (LexisNexis) — chain-of-authority tracing model
