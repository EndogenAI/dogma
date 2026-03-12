---
title: "LCF Programmatic Enforcement: Closing the F4 Gap"
status: "Final"
research_issue: "#211"
date: "2026-03-12"
---

# LCF Programmatic Enforcement: Closing the F4 Gap

> **Research question**: Is the Local-Compute-First (LCF) human-judgment gate the correct
> long-term enforcement design, or do static observable proxies exist that make a partial
> programmatic gate tractable? If a `scripts/check_model_usage.py` gate is viable, what
> is its interface and enforcement surface?
> **Date**: 2026-03-12
> **Research Issue**: #211
> **Related**: [`docs/research/values-encoding.md`](values-encoding.md) (F4 gap origin);
> [`docs/research/programmatic-governors.md`](programmatic-governors.md) (governor tier taxonomy);
> [`docs/research/enforcement-tier-mapping.md`](enforcement-tier-mapping.md) (T0–T5 audit);
> Issue #131 (Cognee/Local Compute Baseline); Issue #152 (Fleet Guardrails Audit)

---

## 1. Executive Summary

The F4 gap — identified in `docs/research/values-encoding.md` — is the weakest encoding
point in the EndogenAI Workflows codebase's programmatic governance stack. The Local-Compute-First
(LCF) axiom (`MANIFESTO.md §3`: "Minimize token burn. Run locally whenever possible.") is
currently enforced only through two soft mechanisms: a documentation guide
(`docs/guides/local-compute.md`) and the `LLM Cost Optimizer` agent. No CI gate, no pre-commit
hook, and no static validator blocks cloud-model usage. `MANIFESTO.md §3` itself explicitly
names this as an intentional design choice — "the absence of a CI gate is intentional" — citing
the infeasibility of static semantic inference over model-usage intent.

This research validates that the intentional framing is *partially* correct but *overstated*.
Static linting cannot detect the *intent* behind a cloud-model API call. It can, however,
detect *observable proxies* — model name strings in configuration files, API endpoint
declarations, environment variable keys — that serve as tier-0 pre-commit signals. These
proxies do not replace human semantic judgment; they surface the cases where judgment is
most needed fastest.

The central conclusion is that a tiered enforcement surface is warranted: a WARN-only
`scripts/check_model_usage.py` pre-commit gate for tier-0 observable proxies, combined with
the existing human-judgment gate retained as the tier-1 semantic arbiter. This design does
not contradict `MANIFESTO.md §3`'s intentional framing — it narrows its scope. The no-CI-gate
rationale remains valid for *semantic intent*; it no longer holds for *observable surface
signals*. Implementation should defer to issue #131 (Cognee/Local Compute Baseline) for
baseline data that will calibrate the signal-to-noise ratio before enforcement blocking.

---

## 2. Hypothesis Validation

### H1 — The LCF Human-Judgment Gate Is the Correct Design

**Claim**: `MANIFESTO.md §3`'s rationale — "semantic context no static linter can evaluate"
— is a sound architectural argument for deferring LCF enforcement to human review.

**Evidence in favour**:

- The distinction between *what cannot be automated* (intent, context) and *what can*
  (observable output patterns, dependency declarations) is well-established in secure
  software development practice (NIST SP 800-218, PW.1.1). The SSDF explicitly reserves
  human review for the category of defects where intent cannot be inferred from static
  artifacts alone. Using a frontier model for a "simple transformation because it is faster
  to prompt than to script" is a judgment call that depends on the agent's prior actions,
  the task complexity assessment, and the available local model capabilities — none of which
  are present in any static artifact.

- The Anthropic Responsible Scaling Policy (2023) architecture directly parallels this
  reasoning: the RSP defines capability thresholds that *trigger* human review, rather than
  attempting to automate the full safety judgment at the model level. The RSP does not
  eliminate human review; it narrows the scope of what goes to human review by using
  automated tier-0 signals to route cases. The H1 argument that human judgment is the
  *primary* defense is consistent with this architecture.

- Continuous Delivery pipeline theory (Fowler & Humble 2010) acknowledges that fast-feedback
  automated gates are appropriate for what can be deterministically evaluated, and that some
  quality dimensions are appropriately gated at the manual inspection stage — specifically
  when the gate condition requires broader context than can be embedded in a static rule.

**Evidence against**:

- The H1 claim, as currently instantiated in the codebase, goes beyond the SSDF and RSP
  precedents by *omitting entirely* the tier-0 automated signal layer. Both the SSDF and
  the RSP assume that observable proxies are being surfaced automatically *before* the
  human review gate. Placing human judgment as the *only* gate — without any automated
  handoff signal — means the human reviewer must discover the cases requiring review through
  context reading alone. This is a late-stage gate design.

- DORA *Accelerate* (2018) data on high-performing teams shows that human review as
  a *primary* (not late-stage) defense produces the slowest feedback loops and the highest
  rate of defect escape. The risk for LCF violations is the reverse: without early signal,
  cloud-model usage accumulates quietly until a cost or policy audit surfaces it.

**Verdict**: H1 is **partially confirmed, but overstated as implemented**. The human-judgment
gate is the correct *final arbiter* for semantic LCF intent. It is not a complete enforcement
design when no automated tier-0 signal exists to feed it. The intentional framing in
`MANIFESTO.md §3` remains defensible as a statement about *semantic* enforcement infeasibility,
but requires a narrowing amendment to acknowledge that observable-proxy enforcement is
tractable and deferred, not impossible.

---

### H2 — Static Observable Proxies Make a Partial Programmatic Gate Tractable

**Claim**: Even without semantic context, static-checkable signals exist in codebase artifacts
that correlate with cloud-model usage and can serve as tier-0 pre-commit WARN signals.

**Evidence**:

The existing enforcement patterns in this codebase establish a direct precedent:

- `validate_agent_files.py`: detects heredoc patterns via regex on file content. The
  linter has no semantic context — it cannot determine *why* a heredoc is present. It
  detects the observable pattern and surfaces a warning. This is structurally identical
  to what LCF detection would do: detect the observable pattern (model name string, API
  endpoint) and surface it for human review.

- `capability_gate.py`: validates agent capability declarations against a YAML manifest.
  This is manifest-based assertion — static checkable because the *declaration* is in
  a file, even if the *runtime behaviour* is not.

Applying the same two patterns to LCF detection:

**Observable proxy class 1 — Model name strings**: Configuration files, `.env` templates,
`pyproject.toml` extras, and agent YAML files may contain strings like `gpt-4`, `claude-3`,
`anthropic`, `openai`, `azure-openai` as declared model targets. These are statically
checkable. A regex scan on committed config files can surface these with zero false negatives
for the declared-in-config case.

**Observable proxy class 2 — API endpoint declarations**: Hardcoded strings such as
`api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com` in Python source
files and config templates are statically detectable. These are rare in this codebase
(most model invocations go through abstraction layers), so false positive rate would be low.

**Observable proxy class 3 — Python import declarations**: `import openai`, `import anthropic`,
`from langchain.llms import OpenAI` are detectable via AST analysis or simple module-name
grep. Import presence does not prove execution (the module may be conditionally imported for
local fallback), but constitutes a surface-level signal warranting WARN.

**Limitations**: None of these proxies can detect the case where a cloud model is invoked
dynamically through a variable-resolved model name, through an agent that already has the
SDK imported, or through an intermediate abstraction layer. The false-negative rate for
intent-driven cases is high. This confirms the need for the human-judgment tier to remain
as the semantic gate.

**Verdict**: H2 is **confirmed with bounded scope**. Static observable proxies are tractable
for tier-0 pre-commit WARN signals covering declared configurations, hardcoded endpoints, and
direct SDK imports. They do not cover dynamic invocation, abstraction-layer usage, or
intent-based assessment. A WARN-only gate with this scope is implementable and would not
produce prohibitive false positives on the current codebase.

---

## 3. Pattern Catalog

### P1 — Observable LCF Violation Signals

**Canonical example**: `validate_agent_files.py` detects the string pattern
`cat.*<<.*'?EOF'?` in committed Python and shell files without any semantic context — just
regex on file content. The same mechanism applies to cloud-model strings.

Statically detectable signals, ordered by false-positive risk (lowest first):

| Signal | Detection method | FP risk | Notes |
|--------|-----------------|---------|-------|
| Config key `model: gpt-*` or `model: claude-*` | YAML key scan | Very low | Declared model target in agent config |
| Hardcoded API endpoint string (`api.openai.com`) | Regex on `.py`/`.yaml`/`.env` | Very low | Explicit endpoint declaration |
| SDK import (`import openai`, `import anthropic`) | AST / grep on `.py` | Low | Import presence ≠ execution but is a surface signal |
| Environment variable `OPENAI_API_KEY` declared in `.env.example` | Grep on `.env*` | Low | Signals anticipated cloud usage |
| Model name string in prompt template files | Regex on `.md`/`.txt` prompt files | Medium | Legitimate local model references may match |

A `check_model_usage.py` implementation covering the first three signal classes would
produce a high-signal, low-noise scan on this codebase. The fourth class should be
scoped to `.env.example` only (not `.env`, which is gitignored) to avoid false positives
from local developer environment files.

---

### P2 — Tiered Enforcement Surface Design

**Canonical example**: The Anthropic RSP (2023) routes above-threshold capability cases
to mandatory human review without attempting to automate the full safety judgment. The
automated tier serves as a *routing signal*, not a *verdict*.

The correct enforcement surface for LCF has two tiers:

**Tier 0 — Static observable proxy gate (pre-commit or CI WARN)**

- Mechanism: `scripts/check_model_usage.py` scans committed files for observable proxy
  signals (P1 above).
- Output: `PASS` (no signals), `WARN` (signals found — surfaces for review), `FAIL`
  (reserved for a future blocking-quality threshold, not recommended currently).
- Enforcement point: pre-commit hook (fast local feedback) or CI step (auditable).
- Human action required: WARN output routes to the human-judgment gate (tier 1) for
  semantic assessment.

**Tier 1 — Human-judgment semantic gate (existing, retained)**

- Mechanism: Augmentive Partnership review step (`docs/guides/local-compute.md`,
  `LLM Cost Optimizer` agent).
- Scope: Intent assessment — was the cloud model used because a local alternative was
  genuinely infeasible, or as a convenience shortcut? Is the usage documented with
  justification?
- No automated replacement exists or is proposed. This tier is the final arbiter.

**Anti-pattern**: Collapsing both tiers into a single human-review-only gate, with no
automated routing signal, forces the human reviewer to discover cloud-model usage through
full context reading. This is the current state.

---

### P3 — `scripts/check_model_usage.py` Design Specification

**Canonical example**: `scripts/capability_gate.py` — a manifest-driven static validator
that takes a file path, checks declarations against a YAML spec, and returns a structured
exit code. `check_model_usage.py` follows the same interface pattern.

**Interface**:

```python
# Usage:
#   uv run python scripts/check_model_usage.py [paths...] [--format text|json] [--level warn|fail]
#
# Inputs:
#   paths     — one or more file paths or directories to scan (default: repo root)
#   --format  — output format: 'text' (human-readable) or 'json' (CI-parseable)
#   --level   — enforcement level: 'warn' exits 0 with findings listed; 'fail' exits 1 on any finding
#
# Outputs:
#   PASS  — no observable cloud-model signals found; exit 0
#   WARN  — one or more signals found; human review recommended; exit 0 (default level)
#   FAIL  — one or more signals found; exit 1 (only when --level fail is passed)
#
# Signal description format:
#   [SIGNAL_TYPE] path/to/file.ext:LINE — "matched text" — [rationale for flag]
#
# Example output (WARN level):
#   check_model_usage: WARN — 2 cloud-model signals found
#   [MODEL_NAME]  .github/agents/llm-cost-optimizer.agent.md:14 — "model: gpt-4o" — declared model target
#   [SDK_IMPORT]  scripts/fetch_source.py:12 — "import openai" — direct SDK import
#   Action: Review flagged usages for LCF compliance. See docs/guides/local-compute.md.
```

**Signal classes scanned** (initial implementation):
1. YAML/TOML keys with cloud model values (`model: gpt-*`, `model: claude-*`, `model: gemini-*`)
2. Hardcoded API endpoint strings in `.py`, `.yaml`, `.toml`, `.env.example`
3. Direct SDK imports (`import openai`, `import anthropic`, `from openai`, `from anthropic`)

**Enforcement point recommendation**: Pre-commit hook (WARN level only). CI can mirror
as an audit step. Do not use `--level fail` until baseline data from #131 confirms
signal quality.

**Dependency**: Issue #131 (Cognee/Local Compute Baseline) should provide telemetry
data on actual local vs. cloud usage patterns before this script's signal classes are
calibrated. Without baseline data, the false-positive rate for SDK imports is unknowable
on a per-project basis.

---

### AP1 — Anti-Pattern: Treating Absence of a CI Gate as Meaning "Nothing Can Be Automated"

**Description**: The current `MANIFESTO.md §3` note reads: "The absence of a CI gate is
intentional: cloud-model usage detection requires semantic context no static linter can
evaluate." Read literally, this statement is correct. Read operationally, it has produced
an absence of observable-proxy enforcement that goes beyond what the rationale warrants.

**The conflation**: The claim that *full semantic intent inference* is infeasible for
static analysis does not imply that *no static signal* is available. `validate_agent_files.py`
detects heredoc patterns without semantic context; `capability_gate.py` validates capability
declarations without executing any agent. Both produce useful signals within their bounded
scope.

**Why this matters**: When the rationale for non-enforcement is stated as "static linters
cannot evaluate semantic context," the operational reading becomes "do not build any static
gate." This is a scope conflation that eliminates the tier-0 layer entirely. The correct
reading is narrower: "do not attempt to automate the *semantic intent* tier; do automate
the *observable proxy* tier."

**Contrast with P1**: Observable signals (P1 above) are checkable without semantic context.
The anti-pattern forecloses them by using a semantic-tier argument as a blanket exclusion.

---

### AP2 — Anti-Pattern: Full Semantic Enforcement of Cloud-Model Intent

**Description**: Attempting to build a gate that detects *intent* to use a cloud model —
e.g., detecting that an agent *chose* a cloud model when a local alternative was feasible —
would require the gate to assess task complexity, available local model capabilities, and
agent decision rationale. No static analyzer can evaluate this. An attempt to do so would
produce a gate with:

- **High false-positive rate**: any cloud-model import flagged as a violation, even when
  usage is genuinely justified (e.g., capability genuinely exceeds local models).
- **Low specificity**: the gate would not distinguish between `gpt-4o` invoked for a
  150-token classification task (clear LCF violation) and `gpt-4o` invoked for a frontier
  reasoning task with no local equivalent (justified use).
- **Gaming surface**: agents could trivially pass the gate by wrapping the cloud invocation
  in an abstraction layer with a neutral name.

**Correct scope boundary**: Static enforcement belongs at the tier-0 observable-proxy level
(P1, P2, P3). Semantic enforcement belongs at the tier-1 human-judgment gate (retained as
per H1 verdict). Attempting to collapse tier 1 into tier 0 produces a useless gate and
a false sense of automated coverage.

---

## 4. Recommendations

- **(a) Formalise the human-judgment gate as intentional T2+ design with explicit rationale.**
  The current `MANIFESTO.md §3` gate note is accurate but under-specified. It should be
  amended to distinguish: (i) static observable-proxy enforcement is *deferred* pending
  `check_model_usage.py` implementation; (ii) semantic intent enforcement is *intentionally*
  delegated to human review. This prevents the AP1 conflation from recurring and aligns with
  the T0–T5 tier taxonomy in `docs/research/enforcement-tier-mapping.md`. This is a
  documentation-only amendment; it does not change existing behaviour.

- **(b) Implement `check_model_usage.py` as a WARN-only soft gate (not FAIL-blocking).**
  Initial implementation should target signal classes 1–3 from P3 above. WARN-only exit code
  ensures no false positives block developer workflow while surfacing signals for the tier-1
  human review gate. The gate should be added as a pre-commit hook and as a non-blocking CI
  audit step. Test coverage must meet the 80% minimum per `AGENTS.md` Testing-First Requirement:
  happy path, zero-signal repos, each signal class independently, and `--level fail` behaviour.

- **(c) Assess #131 dependency before enabling blocking enforcement.**
  Issue #131 (Cognee/Local Compute Baseline) will provide empirical usage data on cloud vs.
  local model invocations in real sessions. This data is needed to calibrate signal classes,
  quantify the false-positive rate for SDK imports, and determine whether `--level fail`
  is appropriate. `check_model_usage.py` should be implemented in WARN mode; the decision
  to elevate to FAIL mode should be deferred to the #131 closure sprint.

- **(d) Re-assess enforcement tier after #131 is closed.**
  Once baseline telemetry is available, run a signal-quality audit: what fraction of WARN
  signals produced by `check_model_usage.py` correspond to genuine LCF violations vs.
  justified uses? If precision is above 80%, upgrade the pre-commit hook to `--level fail`.
  If precision is below 50%, narrow signal class 3 (SDK imports) to only top-level imports
  in agent-facing scripts (excluding tests and optional dependency blocks).

- **(e) Document the `check_model_usage.py` script in `docs/guides/local-compute.md`.**
  Every added enforcement surface must be documented with its rationale, scope, and
  human-action expectations (`docs/AGENTS.md` Documentation-First requirement). The guide
  should explain: what the script checks, what WARN output means, how to respond to a
  flagged signal, and where the tier-1 semantic review gate sits.

---

## 5. Sources

**Fowler, M. & Humble, J. (2010)**. *Continuous Delivery: Reliable Software Releases through
Build, Test, and Deployment Automation*. Addison-Wesley. — Deployment pipeline quality gate
theory; fast-feedback at earliest feasible stage; manual inspection appropriate only where
automated detection is genuinely infeasible.

**Forsgren, N., Humble, J. & Kim, G. (2018)**. *Accelerate: The Science of Lean Software and
DevOps*. IT Revolution Press. — DORA metrics; high-performing teams use automated commit-level
quality gates; human review as late-stage gate is highest-latency design.

**NIST (2022)**. *Secure Software Development Framework (SSDF) v1.1*, SP 800-218.
National Institute of Standards and Technology. PW.1.1: automated defect detection in source
code; SSDF distinction between automatable (observable output patterns, dependency declarations)
and non-automatable (intent, context) defect categories.

**Anthropic (2023)**. *Responsible Scaling Policy v1.0*. Anthropic PBC. — Capability-threshold
triggered enforcement; tiered gate design (automated routing signal → mandatory human review);
pattern mapped onto LCF tiered enforcement surface in P2.

**EndogenAI Workflows — `MANIFESTO.md §3`** (2026). Local Compute-First axiom; canonical
example (ollama pull); anti-pattern (convenience cloud use); intentional no-CI-gate rationale;
`check_model_usage.py` as named deferred candidate.

**EndogenAI Workflows — `docs/research/values-encoding.md`** (2026). F4 gap: LCF soft gate
characterisation; T1–T5 encoding weakness analysis; remediation options.

**EndogenAI Workflows — `docs/research/enforcement-tier-mapping.md`** (2026). T0–T5
distribution audit; 37 T5-prose-only constraints; high-priority T5→T3 uplift candidates.

**EndogenAI Workflows — `docs/research/programmatic-governors.md`** (2026). Governor tier
taxonomy; pre-commit pygrep pattern as established enforcement mechanism; precedent for
analogous `check_model_usage.py` design.
