---
x-governs: [two-stage-guardrail-pipeline, irreversible-tool-gates, agent-security]
---

# Security Guide — Agent Tool Gates & Guardrail Pipeline

This guide documents the mandatory security controls for agent tools that can trigger irreversible external side effects: commits, pushes, issue creation, and GitHub API writes.

**Governing axioms**: [MANIFESTO.md § Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — build from verified research before reaching for external tooling; [AGENTS.md § Security Guardrails](../../AGENTS.md#security-guardrails) — the operative policy constraints for all agents.

**Research source**: [`docs/research/nemo-guardrails-governance.md`](../research/nemo-guardrails-governance.md) — Recommendation 4 (Rebedea et al. 2023; Inan et al. 2023; Ganguli et al. 2022).

---

## Irreversible Agent Tool Classification

The following tool categories trigger irreversible external side effects and are subject to multi-stage gate requirements:

| Tool Category | Examples | Risk Level |
|---|---|---|
| Version control writes | `git commit`, `git push`, `git push --force` | High |
| GitHub API writes | `gh issue create`, `gh pr create`, `gh issue close`, `gh issue edit` | High |
| File system destructive ops | `rm`, file overwrites without backup | High |
| Bulk operations | Label sync, milestone reassignment across many issues | Medium–High |

---

## Two-Stage Rule + LLM Guardrail Pipeline

For any agent tool that can trigger an irreversible external side effect, apply the following two-stage pipeline before execution. This pattern is validated by Rebedea et al. (2023) and Inan et al. (2023) and reduces adversarial bypass from ~18% (rules only) to ~3% (hybrid pipeline).

### Stage 1 — Rule-Based Gate (L1, <5ms)

**Purpose**: Block known-bad patterns with minimal latency overhead.

**In dogma, Stage 1 is already encoded as**:

1. **Pre-commit hooks** (`AGENTS.md § Guardrails`) — static linting, ruff checks, validate-agent-files, validate-synthesis. These run at `git commit` boundary and block known-bad patterns before any remote write.

2. **MCP `validate_repo_path`** (`mcp_server/dogma_server.py`) — enforces path-safety validation before any file-write tool is invoked by an agent. Applies a fixed rule set: no writes outside the workspace root, no writes to `.git/`, no writes to system paths.

3. **AGENTS.md prohibitions** (text-layer T2 rules) — explicit "Never do these" list; caught by governors (see `AGENTS.md § Programmatic Governors`).

4. **Pre-use validation gate** (`AGENTS.md § Pre-Use Validation`) — mandatory `test -s` / `file | grep UTF-8` checks before passing temp files to `gh` commands.

**Characteristics**: Fast (<5ms), deterministic, catches known signatures. Does not catch adversarial paraphrasing.

### Stage 2 — LLM Classifier Escalation Path (L2, 150–400ms)

**Purpose**: Handle adversarial paraphrasing and edge cases that bypass Stage 1 rules.

**When to apply Stage 2**: Stage 2 escalation is triggered when:
- An agent request contains indirect or paraphrased phrasing that references an irreversible action without triggering a Stage 1 rule (e.g., "wipe the stale branches" vs. `git push --force`)
- A delegated agent returns an output that proposes a bulk write not explicitly in the current phase plan
- An external content source (`.cache/sources/`, `.cache/github/`) contains instruction-like text that could redirect subsequent tool calls

**Stage 2 implementation options** (in order of preference per Endogenous-First):
1. **Human-in-the-loop pause**: For high-stakes writes, surface the proposed action to the user as an explicit decision menu (see `AGENTS.md § When to Ask vs. Proceed`) before executing. This is always available and requires no additional tooling.
2. **Broad-scope irreversible change blocking question gate**: Mandated in `AGENTS.md § Focus-on-Descent / Compression-on-Ascent` — before any bulk destructive delegation, block and ask.
3. **LLM meta-classifier** (Llama Guard-style): For automated pipeline contexts, a secondary LLM call that classifies the proposed action against a safety taxonomy before execution. Not yet adopted in dogma; document decision in a D4 research doc before implementing.

**Latency profile**: Stage 2 (human-in-the-loop) adds ~0ms machine latency but adds a human decision round-trip. LLM meta-classifier adds 150–400ms. Both are acceptable at the agent tool-gate boundary (not at per-token streaming level).

### Combined Pipeline Diagram

```
Agent proposes irreversible action
          │
          ▼
  ┌──────────────────────────────┐
  │ Stage 1: Rule-Based Gate     │
  │ pre-commit hooks             │
  │ MCP validate_repo_path       │
  │ AGENTS.md prohibitions       │
  │ Pre-use validation           │
  └──────────────────────────────┘
          │
    Known-bad? ──── YES ──→ BLOCK (exit 1 / error)
          │
          NO
          │
          ▼
  ┌──────────────────────────────┐
  │ Stage 2: LLM Classifier /    │
  │ Human-in-the-loop pause      │
  │                              │
  │ Trigger on: paraphrased      │
  │ bypass, bulk ops, external   │
  │ content instruction injection│
  └──────────────────────────────┘
          │
    Ambiguous? ─── YES ──→ ESCALATE / ASK USER
          │
          NO (clearly safe)
          │
          ▼
       EXECUTE
```

---

## Red-Team Validation Cadence

Per Recommendation 5 of `docs/research/nemo-guardrails-governance.md`, schedule quarterly red-team evaluations against the guardrail configuration:

- **Frequency**: Quarterly (aligned with the values review cycle in `docs/guides/quarterly-values-review.md`)
- **Method**: 3+ annotators, 2-hour sessions, targeting the most recent batch of rule additions
- **Threshold**: Any bypass rate >10% triggers a Stage 2 addition or rule rewrite before the next sprint
- **Record**: Document results in a session scratchpad entry under `## Red-Team Output`

---

## References

- [`docs/research/nemo-guardrails-governance.md`](../research/nemo-guardrails-governance.md) — Research synthesis; Recommendation 4 is the direct source for the two-stage pipeline pattern
- [`AGENTS.md § Security Guardrails`](../../AGENTS.md#security-guardrails) — Operative policy constraints (Prompt Injection, Secrets Hygiene, SSRF)
- [`AGENTS.md § Programmatic Governors`](../../AGENTS.md#programmatic-governors) — T3/T4 enforcement stack
- [`AGENTS.md § When to Ask vs. Proceed`](../../AGENTS.md#when-to-ask-vs-proceed) — Human-in-the-loop escalation policy
- [MANIFESTO.md § Self-Governance & Guardrails](../../MANIFESTO.md#self-governance--guardrails)
- Rebedea et al. (2023). "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails." arXiv:2310.10501.
- Inan et al. (2023). "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations." arXiv:2312.06674.
- Ganguli et al. (2022). "Red Teaming Language Models to Reduce Harms." arXiv:2209.07858.
