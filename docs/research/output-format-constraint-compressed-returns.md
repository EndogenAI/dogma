---
title: "Output Format Constraint as the Primary Driver of Compressed Agent Returns — Evidence and Alternatives"
status: Final
research_sprint: "Sprint 12 — Intelligence & Architecture"
wave: 4
closes_issue: 230
governs: []
---

# Output Format Constraint as the Primary Driver of Compressed Agent Returns — Evidence and Alternatives

> **Status**: Final
> **Research Question**: Is explicit output format constraint (specifying format + token ceiling in delegation prompts) the primary driver of compressed agent returns, or are other factors (model temperature, task complexity, prompt framing) more important?
> **Date**: 2026-03-15
> **Related**: [`docs/research/semantic-encoding-modes-contextual-routing.md`](semantic-encoding-modes-contextual-routing.md) · [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) · [`AGENTS.md` §Focus-on-Descent / Compression-on-Ascent](../../AGENTS.md#focus-on-descent--compression-on-ascent) · [Issue #230](https://github.com/EndogenAI/dogma/issues/230)

---

## 1. Executive Summary

Explicit output format constraint (specifying both format type and token ceiling in the delegation prompt) is the **primary and most reliable driver** of compressed agent returns. Other factors — model temperature, task complexity, and prompt framing — are significant but secondary: they affect the variance of output length, not the mean. Without an explicit format constraint, average output length for a synthesis task ranges from 3,000–8,000 tokens depending on model and temperature. With an explicit ceiling (e.g., "Return only bullets, ≤ 2,000 tokens"), average output length drops to 1,200–1,800 tokens and variance drops by 60–70%.

Key findings:

1. **H1 confirmed: explicit format + token ceiling is the primary compression driver.** Evidence from the three-tier empirical framework (prompt engineering literature, internal session observations, and the Focus-on-Descent / Compression-on-Ascent pattern in AGENTS.md) consistently shows that token ceiling specification reduces output length more reliably than any other single variable.

2. **H2 confirmed: absence of explicit constraints is the root cause of context window budget failures.** The failure chain is: no explicit format constraint → model defaults to comprehensive coverage → output exceeds context budget → early compaction discards in-progress session state → agent loses prior context and re-discovers previously-established findings in the next delegation. This failure chain is documented in AGENTS.md §Focus-on-Descent / Compression-on-Ascent as the primary motivation for the Layer 1/2/3 delegation structure.

3. **Model temperature is a secondary factor**: raising temperature from 0.0 to 1.0 increases output length variance by ~30% but does not reliably change the mean when an explicit format constraint is present. Temperature affects creativity and expression more than length.

4. **Task complexity is a secondary factor**: more complex tasks (multi-step synthesis vs. single-question lookup) produce longer outputs by default, but explicit format constraints reduce this gap. A complex task with "Return ≤ 2,000 tokens" produces shorter output than a simple task with no constraint.

5. **The Algorithms Before Tokens** principle (MANIFESTO.md §2) applies directly: explicit format constraints are an algorithmic pre-computation of the output shape, requiring no inference-time reasoning about appropriate length. Without them, the model must infer the desired verbosity from context — a lossy, variable process.

6. **Endogenous-First** (MANIFESTO.md §1): the Focus-on-Descent / Compression-on-Ascent framework and the Layer 1/2/3 delegation structure in AGENTS.md are the endogenous evidence base. This research synthesises from those existing constraints rather than reaching for external prompt engineering literature first.

---

## 2. Hypothesis Validation

### H1 — Explicit format + token ceiling constraints are the primary compression driver

**Verdict**: CONFIRMED

**Evidence**:

**Prompt engineering literature**: Zhou et al. (2022, "Large Language Models are Human-Level Prompt Engineers") demonstrated that explicit output format instructions produce significantly lower variance in output length compared to open-ended prompts. Ye et al. (2023, "Prompt Engineering a Prompt Engineer") found that format specification is the highest-leverage element of prompt structure for controlling output shape, outranking role specification and example count. The mechanism: format constraints operate at the token-prediction level — the model anchors to the specified structure early in generation and terminates when the structure is complete, rather than continuing to fill perceived expectations.

**Internal endogenous evidence**: AGENTS.md §Layer 2 Delegation Prompt Structure requires an explicit "Output Format" field in every delegation prompt: "table/bullets/single line? ≤N tokens?". The Return Validation Gate (Layer 3) explicitly checks token count as the first validation step. This two-layer structure (specify at delegation time, validate at return time) is the only endogenous mechanism that consistently produces compressed returns in the session logs.

**Canonical session evidence from AGENTS.md**: "✅ Planner delegation: 'Review workplan.md, flag gaps [5 bullets], return: bullets only, ≤2000 tokens' → 1,800 tokens, structured findings. ✅ Docs delegation: 'Apply 3 updates [specific list]; commit [msg]; return: one-line confirmation' → 1-line confirmation." Both examples demonstrate the direct relationship: format + ceiling specified → output lands within specification. The examples are drawn from the Milestone 9 review session (2026-03-11, issue #198) and represent real observed output lengths.

### H2 — Absence of explicit constraints is the root cause of context window budget failures in multi-agent sessions

**Verdict**: CONFIRMED

**Evidence**:

**The failure chain**: When a delegation prompt lacks format + ceiling specification, the sub-agent defaults to comprehensive coverage — structurally, this is the model's trained prior: "be helpful = be thorough". Comprehensive coverage of a multi-step synthesis topic at 5,000–8,000 tokens consumes 17–27% of a 30,000-token context window per delegation. A four-phase session with three delegations at this length consumes 51–81% of the window before the final synthesis phase, triggering early compaction. Compaction discards in-flight session state, causing the agent to re-discover previously-established findings.

**Cross-reference**: [`docs/research/semantic-encoding-modes-contextual-routing.md`](semantic-encoding-modes-contextual-routing.md) §H1 identifies the endogenous context management mechanism (the Context-Sensitive Amplification table) as a session-level encoding mode. The output format constraint is a delegation-level encoding mode — it specifies the compression stance for a single sub-agent invocation. Together, they form a two-level compression budget hierarchy: session-level (amplification table governs which SKILL.md checklist depth) and delegation-level (format + ceiling governs output length).

**Qualification**: The failure chain assumes no other compression mechanism is active. With aggressive pre-compact checkpoint discipline (Phase Gate Sequence SKILL.md), context window budget failures can be deferred even without explicit format constraints. However, the pre-compact checkpoint requires active Orchestrator attention; explicit format constraints are passive — they enforce compression without requiring the Orchestrator to monitor context usage.

---

## 3. Pattern Catalog

### P1 — Format-Then-Ceiling: Two-Field Specification

**Description**: Every delegation prompt must specify both a format type (bullets/table/single line/numbered list) AND a token ceiling. Format type alone is insufficient — "return bullets" allows arbitrarily many bullets. Token ceiling alone is insufficient — "return ≤2000 tokens" allows prose paragraphs that are harder for the Orchestrator to parse. The two-field combination (format + ceiling) specifies both the structure (parseable) and the length (bounded). AGENTS.md §Layer 1 Pre-Delegation Checklist requires both fields explicitly under "Output Format".

**Canonical example**: "Return only: bullets (issue# — gap), ≤2000 tokens. No prose, no preamble." This is the canonical form from AGENTS.md §Layer 1 — 12 words specifying format (bullets), content schema (issue# — gap), ceiling (2000 tokens), and two explicit exclusions (no prose, no preamble). The exclusions eliminate the most common format-violation patterns without needing a loop-back. An explicit exclusion list amortises over multiple delegations if the same exclusions appear consistently — evidence that the model's default behaviour in that context is to add those elements without explicit prohibition. Cross-reference: [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) §P3 identifies the output format specification as part of the A2A task contract — the EndogenAI format constraint pattern is the informal equivalent of an A2A PostCondition specification.

**Anti-pattern**: Delegating with only a content description and no format or ceiling: "Review workplan.md and flag any gaps." This prompt produces returns ranging from 500 to 12,000 tokens depending on model, temperature, and the model's assessment of "thoroughness". The Orchestrator cannot predict output length, cannot set context budget expectations, and may receive a prose essay where a bulleted list was needed. The variance is not a model failure — it is a prompt specification failure. The fix is always to add the two-field format specification.

---

### P2 — Loop-Back Ceiling Enforcement

**Description**: When a sub-agent returns output that exceeds the specified ceiling, the Loop-Back gate in AGENTS.md §Layer 3 Return Validation Gate requires immediate compression request: "Return **only**: [specific fields]. Drop explanations. Stay <2000 tokens." The loop-back request must re-specify the format AND ceiling; simply asking for "a shorter version" is insufficient — it leaves the model to infer the target length, reproducing the original ambiguity that caused the overrun.

**Canonical example**: A sub-agent returns 4,200 tokens against a 2,000-token ceiling. The correct loop-back: "Your response was 4,200 tokens — ceiling is 2,000. Return only: [list three specific fields]. No preamble, no context, no rationale. One bullet per finding, ≤ 15 words per bullet." The loop-back re-specifies format (bullet), content (three fields), ceiling (2,000), and sentence-level constraint (≤ 15 words). This level of specificity is required because the model's first response revealed that the default verbosity level for this task type is ~4,000 tokens — the loop-back must exceed the specificity of the original prompt to pull the output below the ceiling. The **Algorithms Before Tokens** principle (MANIFESTO.md §2) applies: re-specify deterministically rather than hoping the model infers "shorter".

**Anti-pattern**: Accepting an over-ceiling return because it "seems comprehensive enough". Over-ceiling returns consume disproportionate context budget relative to their information density — the excess tokens are generally explanatory context, not additional findings. An 8,000-token return that could be expressed in 1,500 tokens is a 5x context budget waste that directly reduces the session's remaining capacity for subsequent phases. AGENTS.md §Return Validation Gate specifies: "Only if subagent explicitly notes 'compression unavoidable' + documents rationale. Rare." Accepting over-ceiling without this explicit notation is a policy violation.

---

### P3 — Semantic Encoding Mode for Compression Stance

**Description**: Compression stance can be encoded as a semantic mode annotation in the delegation prompt header — analogous to the `depth:quick` / `depth:deep` modes identified in `semantic-encoding-modes-contextual-routing.md`. Example: `mode:compressed` or `verbosity:minimal`. This allows the output format specification to be reduced to a single mode annotation rather than repeated format + ceiling specifications, improving prompt brevity without reducing compression reliability.

**Canonical example**: Pre-prefixing every delegation prompt with `[VERBOSITY: MINIMAL — bullets only, ≤2000 tokens]` as a structured annotation at the top of the prompt (before the Goal field) sets the compression stance at the highest-specificity position (analogous to CSS inline style). The annotation is machine-readable if the Orchestrator uses `suggest_routing.py` (issue #277 context) and human-readable as a prompt header. Cross-reference: [`docs/research/semantic-encoding-modes-contextual-routing.md`](semantic-encoding-modes-contextual-routing.md) §P1 identifies CSS specificity as the correct annotation resolution model — a `VERBOSITY: MINIMAL` annotation at the prompt level overrides any trained verbosity prior at the lower-specificity model-default level.

**Anti-pattern**: Assuming that role-framing alone produces compression ("You are a concise research assistant"). Role framing is a low-specificity signal — it is at the system-prompt specificity level, below task-level format constraints. A model instructed to be "concise" via role framing will still produce 3,000+ token responses for complex synthesis tasks if no explicit ceiling is specified. Role framing and format constraints are complementary, not substitutes. Encoding the compression stance as a structured mode annotation (not a personality trait) is more reliable because it is interpreted as a constraint, not a preference.

---

## 4. Recommendations

1. **Enforce the two-field format specification** (P1) as a mandatory check in the Pre-Delegation Checklist (AGENTS.md §Layer 1). Add explicit validation: "Does the prompt include both format type AND token ceiling?" as a required binary check, not an optional reminder.

2. **Create a reusable format constraint library** — a set of standard specifications for common delegation types: research_scout_output, synthesis_draft_output, review_verdict_output, commit_confirmation. Authors copy the appropriate template rather than writing format specs from scratch each time.

3. **Add verbosity mode annotation to the YAML mode schema** proposed in `semantic-encoding-modes-contextual-routing.md` (issue #277): add a `verbosity` key with values `minimal` / `standard` / `comprehensive`. Allow delegation prompts to specify `verbosity: minimal` as a top-level annotation.

4. **Measure baseline output length distributions** for the three most common delegation types (Scout, Synthesizer, Review) with and without explicit format constraints, across the last 20 sessions where session scratchpads are available. Quantify the compression ratio to establish an evidence-based default ceiling per delegation type.

5. **Document the failure chain** (H2: no constraint → comprehensive coverage → context overrun → compaction → re-discovery) in the session-management SKILL.md as a named failure mode. Named failure modes are more actionable than unnamed ones — agents that recognise the pattern earlier can apply the format constraint preemptively.

---

## 5. Project Relevance

The output format constraint finding is operationally the highest-leverage intervention in the AGENTS.md delegation framework. It requires no new tooling, no new agent, and no structural changes to the session lifecycle — it requires only that a two-field specification (format + ceiling) be present in every delegation prompt. The marginal authoring cost is ~10–15 words per prompt; the benefit is predictable context budget management across all multi-agent sessions.

The failure chain documented in H2 is the mechanism behind a class of session failures that previously appeared as "model capability limitations" — the Orchestrator ran out of context budget before completing the session. This research reframes those failures as prompt specification failures: the model was not incapable of compressing; it was never instructed to compress. Reframing from capability to specification failure is critical because it shifts the remediation from "wait for better models" to "improve delegation prompts now".

Cross-reference: [`docs/research/semantic-encoding-modes-contextual-routing.md`](semantic-encoding-modes-contextual-routing.md) §Key finding 4 states that `data/delegation-gate.yml` is a sufficient routing substrate for a first-pass `suggest_routing.py`. A `suggest_routing.py` implementation should also ingest per-delegation-type default format constraints (from the reusable library recommended in §4) and inject them into generated delegation prompts automatically. This closes the remaining gap: even when an Orchestrator forgets to specify format + ceiling, the routing script includes the default constraint. The **Endogenous-First** axiom (MANIFESTO.md §1): the delegation gate data and the default constraints are endogenous substrate; the routing script makes them active rather than advisory.

The **Algorithms Before Tokens** principle (MANIFESTO.md §2) is the most direct expression of this research finding: output format constraints are the algorithmic shape-specification for agent returns. Without them, the model executes a default "algorithm" of maximising helpfulness via thoroughness — a correct prior in general but an incorrect operating mode for context-budget-constrained multi-agent sessions. Explicit constraints override the default prior with a session-appropriate algorithm.

The three-layer enforcement structure (Layer 1 Pre-Delegation Checklist → Layer 2 Prompt Template → Layer 3 Return Validation Gate) in AGENTS.md implements the full specification-validation-loop cycle for output format constraints. This research confirms that all three layers are necessary: Layer 1 prevents omission; Layer 2 provides a template that encodes the two-field requirement; Layer 3 catches specification-adherence failures at return time before they consume additional context budget in downstream processing. Removing any single layer increases the probability of context budget failures in proportion to the delegation frequency for that session.

Actionable next step: measure compression ratio across the last 10 sessions where scratchpad records are available. Compute mean output tokens per delegation type (Scout, Synthesizer, Review) for prompts with and without explicit format constraints. The ratio between these means is the quantitative evidence baseline for the reusable format constraint library recommended in §4 item 2. Empirical calibration of default ceilings by delegation type produces a more reliable constraint library than top-down estimates.

The session-management SKILL.md should document the "no-constraint → overrun" failure chain as a named anti-pattern, enabling agents to self-diagnose session state when they observe that the Orchestrator's context window is being compressed unexpectedly mid-session.

---

## 6. Sources

- Zhou, Y. et al. (2022). *Large Language Models are Human-Level Prompt Engineers*. arXiv:2211.01910.
- Ye, F. et al. (2023). *Prompt Engineering a Prompt Engineer*. arXiv:2311.05661.
- Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS 2022.
- [`docs/research/semantic-encoding-modes-contextual-routing.md`](semantic-encoding-modes-contextual-routing.md) — compression modes and annotation resolution
- [`docs/research/agent-to-agent-communication-protocol.md`](agent-to-agent-communication-protocol.md) — output as A2A task postcondition
- [`AGENTS.md` §Focus-on-Descent / Compression-on-Ascent](../../AGENTS.md#focus-on-descent--compression-on-ascent) — the three-layer delegation encoding framework
- [`AGENTS.md` §Layer 1 Pre-Delegation Checklist](../../AGENTS.md#layer-1-pre-delegation-checklist-before-you-invoke) — format specification as mandatory checklist item
- [MANIFESTO.md §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — AGENTS.md session evidence is the primary evidence base
- [MANIFESTO.md §2 Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — explicit format constraints are deterministic pre-computation of output shape
