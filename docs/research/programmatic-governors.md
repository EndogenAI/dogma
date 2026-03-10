---
title: "Programmatic Governors: Shifting AI Behavioral Constraints from Tokens to Deterministic Code"
status: Final
research_issue: "#151"
date: 2026-03-10
---

# Programmatic Governors: Shifting AI Behavioral Constraints from Tokens to Deterministic Code

> **Status**: Final — Foundational synthesis. See [shifting-constraints-from-tokens.md](shifting-constraints-from-tokens.md) for deep architectural research on enforcement stacks and pattern catalogs.
> **Research Question**: When an AI agent violates a guardrail encoded only as text instructions, what enforcement mechanisms exist that are immune to weight-level pattern completion? Where on the execution stack should governors sit?
> **Date**: 2026-03-10
> **Related**: [`docs/research/values-encoding.md`](values-encoding.md) (value degradation and programmatic encoding as drift-immune layer); [`docs/research/deterministic-agent-components.md`](deterministic-agent-components.md)

---

## Executive Summary

A guardrail encoded only as text tokens competes against the model's pretraining weights. Weights win in fast pattern-completion contexts. The heredoc prohibition in `AGENTS.md` and user memory is the direct evidence: the rule was written, acknowledged, and then violated — not because the model was deceptive, but because shell scripting patterns from pretraining are encoded at the weight level while the rule exists only at the context level. Context tokens are soft constraints; weight-level priors are hard attractors.

This is structurally identical to the constitutional drift pattern documented in legal scholarship and formalized in `docs/research/values-encoding.md` §H1: *the text is stable; the hermeneutical application drifts.* The correct fix is not better text — it is a **governor**: a mechanical constraint the substrate cannot override at the execution boundary, regardless of what the model generates.

The `MANIFESTO.md` axiom **Algorithms Before Tokens** already implies this conclusion. Its corollary for behavioral self-governance is: *every guardrail that exists only as tokens should have a corresponding programmatic enforcement layer*. This document identifies the available governor mechanisms, maps them to the execution stack, and specifies the open gap.

**Hypotheses submitted for validation:**

- **H1** — Text-only guardrails are structurally inferior to programmatic enforcement for patterns that conflict with model pretraining priors.
- **H2** — Multiple governor tiers (post-hoc, pre-commit, runtime) provide defense-in-depth; no single tier covers all failure modes.
- **H3** — The strongest reachable governor for AI-generated terminal commands is a shell `preexec`/`DEBUG` hook; the ideal governor (terminal middleware) is not owner-accessible.

---

## Hypothesis Validation

### H1 — Text Guardrails Are Structurally Inferior for Weight-Conflicting Patterns

**Verdict**: CONFIRMED — mechanistically grounded, not speculative

The heredoc pattern (`cat >> file << 'EOF'`) occurs with high frequency in shell scripting corpora. A model trained on billions of lines of shell scripts has this pattern encoded at the weight level as a strong prior for "write content to a file." The prohibition in `AGENTS.md` is a context token — a soft constraint applied at inference time. Shannon's channel model applies: adding a single counter-signal token in a high-noise channel (billions of pretraining tokens) has limited suppression power.

Constitutional AI (Bai et al. 2022) demonstrates the same tension: RLHF-trained behavioral constraints are more robust than in-context instructions but still exhibit specification gaming when the trained constraint is ambiguous or the pattern is strongly represented in pretraining. For highly specific anti-patterns not targeted by RLHF (like "never heredoc in the VS Code terminal tool"), the token layer is the *only* enforcement mechanism — and it is demonstrably insufficient.

**The AGENTS.md constraint is necessary but not sufficient.** Its role is to make the expected behavior legible; it cannot alone make the violation impossible.

### H2 — Defense-in-Depth Across Governor Tiers

**Verdict**: CONFIRMED — three tiers identified, no single tier fully covers the failure space

| Tier | Mechanism | Intercepts before execution? | Coverage gap |
|---|---|---|---|
| Post-hoc audit | `validate_session.py` Tier 1 regex on scratchpad | No | Evidence may not be logged; best-effort |
| Pre-commit | pygrep hook `no-heredoc-writes` on staged files | No — catches at commit boundary | Only covers file writes in committed content |
| Runtime governor | Shell `preexec`/`DEBUG` trap | Yes — blocks before execution | Requires shell environment setup; not zero-config |

Each tier catches a different class of occurrence. The pre-commit hook (now implemented in this repo's `.pre-commit-config.yaml`) is high-reliability for the narrow case of heredos in committed files. The `preexec` trap closes the execute-before-commit gap. Post-hoc audit provides a forensic fallback.

### H3 — Strongest Reachable Governor is Shell preexec; Ideal Governor is Inaccessible

**Verdict**: CONFIRMED — architectural constraint, not implementation gap

The ideal governor sits *inside the terminal tool middleware* — between the LLM tool call and the shell execution layer. VS Code's terminal tool forwards commands directly to the shell; there is no plugin hook in the current Copilot extension API to intercept at that boundary. This is an owner-inaccessible layer.

The `bash` `DEBUG` trap (`trap 'check_command "$BASH_COMMAND"' DEBUG`) and `zsh` `preexec` hook (`preexec_functions+=check_command`) execute *before* any command the shell receives, including commands forwarded from external callers. Combined with `direnv` + `.envrc` for automatic per-project activation, this is the highest-fidelity governor reachable from outside the terminal tool middleware.

---

## Pattern Catalog

### Governor Placement Hierarchy

An AI agent operating in a shell environment generates commands → a tool routes them to the shell → the shell executes them. Governors can intercept at three points:

```
LLM (generates command)
    ↓
[Governor A — terminal middleware: INACCESSIBLE]
    ↓
Shell (receives command)
    ↓
[Governor B — preexec/DEBUG trap: ACCESSIBLE, highest fidelity]
    ↓
Command executes
    ↓
[Governor C — pre-commit hook: ACCESSIBLE, post-execute, pre-commit]
    ↓
[Governor D — post-hoc audit: ACCESSIBLE, forensic only]
```

**Canonical example**: The `no-heredoc-writes` pygrep pre-commit hook in `.pre-commit-config.yaml` is Governor C. It fires when an agent stages a file containing heredoc-written content. It does not prevent the heredoc from executing — it prevents the result from being committed. Combined with a `preexec` trap (Governor B), the heredoc is blocked before execution ever occurs.

**Anti-pattern**: Relying solely on `AGENTS.md` text instructions to suppress a pattern that conflicts with weight-level pretraining priors. This places the full enforcement burden on the context window — the weakest tier in the governor stack. The `AGENTS.md` rule and the pygrep hook must coexist: the rule communicates the expected behavior; the hook enforces it mechanically. Neither alone is sufficient.

### The Watt Governor Analogy

James Watt's centrifugal governor (1788) regulated steam engine speed mechanically: as rotational speed increased, flyweights lifted, throttling the steam valve. The engine had no ability to "decide" to override the governor — the feedback was physical, not instructional. The analog in software is a constraint implemented in the execution substrate rather than in the instruction layer. A `preexec` trap that blocks heredoc-containing commands is a Watt governor: the agent cannot override it by generating a more confident instruction.

`MANIFESTO.md`'s **Algorithms Before Tokens** axiom encodes this principle for computation generally. The corollary for agent behavioral governance is stated here explicitly for the first time: *encode behavioral constraints at the lowest available execution layer, not only at the instruction layer*.

---

## Recommendations

### R1 — Install preexec governor via direnv (Runtime, Tier 1 priority)

Create `.envrc` with a `preexec_functions` registration (zsh) or `DEBUG` trap (bash) that rejects commands matching `<<\s*'?EOF'?`. Activate with `direnv allow`. This closes the execute-before-commit gap and is the only governor that intercepts before shell execution.

**Acceptance criteria**: Running `cat >> /tmp/test.txt << 'EOF'` in the project shell triggers a blocked-command warning and exits non-zero without executing the heredoc.

### R2 — Keep the no-heredoc-writes pre-commit hook active (Pre-commit, Tier 2)

The pygrep hook already implemented catches heredocs in staged files. Do not remove or soften this hook. It is Governor C — meaningful defense-in-depth even when Governor B (preexec) is active.

### R3 — Extend validate_session.py with Tier 1 heredoc check (Post-hoc, Tier 3)

Add a regex check to `validate_session.py` (or create it) that scans scratchpad entries for heredoc evidence and flags them as guardrail violations. This provides forensic coverage and creates an audit trail when both runtime and pre-commit governors are bypassed.

### R4 — Document the governor stack in AGENTS.md

Add a "Programmatic Governors" subsection to `AGENTS.md` that names all three tiers, maps each to its mechanism, and states the architectural constraint (terminal middleware inaccessibility). This is the `AGENTS.md` encoding of R1–R3, consistent with the Documentation-First constraint.

### R5 — Open research question: terminal middleware hooks

File a research issue against the VS Code Copilot extension API for terminal command interception hooks. If the extension ever exposes a pre-execution callback, Governor A becomes accessible and R1 becomes redundant. Track this as a future migration path.

---

## Sources

- Bai, Y. et al. (2022). "Constitutional AI: Harmlessness from AI Feedback." Anthropic. [arXiv:2212.06402](https://arxiv.org/abs/2212.06402)
- Krakovna, V. et al. (2020). "Specification gaming: the flip side of AI ingenuity." DeepMind Blog.
- Shannon, C. E. (1948). "A Mathematical Theory of Communication." *Bell System Technical Journal*, 27(3), 379–423.
- Watt, J. (1788). Centrifugal governor patent. UK Patent 1432. *(Cited as mechanical governor analogy.)*
- [`MANIFESTO.md`](../../MANIFESTO.md) — Algorithms Before Tokens axiom; primary endogenous source.
- [`AGENTS.md`](../../AGENTS.md) — heredoc guardrail, Programmatic-First principle, pre-commit hooks section.
- [`docs/research/values-encoding.md`](values-encoding.md) — H1 (value degradation patterns), H3 (programmatic encoding immune to semantic drift).
- Session evidence, 2026-03-10: heredoc violation observed in live Copilot session despite text rule in AGENTS.md and user memory; failure mode analysis performed in-session.
