---
title: NeMo Guardrails — Programmatic Enforcement Patterns for Agent Governance
status: Final
closes_issue: 313
date_published: 2026-03-18
author: Executive Researcher
---

# NeMo Guardrails — Programmatic Enforcement Patterns for Agent Governance

## Executive Summary

NVIDIA's NeMo Guardrails (NemoClaw) enforces behavioral constraints on LLM outputs via three programmatic layers: **L1 (output validation)** — regex + semantic constraint checking on model completions; **L2 (instruction colocation)** — guardrail rules embedded in system prompts; **L3 (action gate)** — blocking unsafe tool calls before execution. Compared to dogma's **Enforcement-Proximity** stack (T2 pre-commit hooks + T4 runtime shell governors), NeMo provides a middle layer (L2/L3) that operates on LLM behavior directly rather than on agent code. This research evaluates whether dogma's current T2+T4 architecture has gaps that a T3-equivalent runtime LLM gate would fill, and whether NeMo's semantic constraint patterns are worth adopting for agent behavioral safety.

**Finding**: Neither architecture is strictly superior; rather, they operate at different enforcement layers. dogma's T2+T4 stack governs **agent behavior** (what agents are allowed to do); NeMo's L1–L3 governs **LLM behavior** (what models are allowed to output). For agentic workflows, T2+T4 is sufficient if agent code is audited. Adding an LLM-level gate (equiv to NeMo's L1) would provide defense-in-depth, but is not critical if agent tools are scoped tightly.

---

## Hypothesis Validation

**Claim**: NeMo Guardrails' L1–L3 enforcement stack addresses distinct risks than dogma's T2+T4; a combined T2+T4+L1 architecture provides stronger safety guarantees without sacrificing performance.

**Evidence**:

| Layer | dogma Current | NeMo Guardrails | Risk Addressed |
|-------|---------------|-----------------|----------------|
| T2 Pre-commit (dogma) | ✅ `no-heredoc-writes` hook blocks unsafe patterns in scripts before commit | N/A — NeMo is runtime-only | Code-level governance (agent file integrity) |
| T4 Runtime Shell (dogma) | ✅ `preexec_governor` intercepts heredocs in terminal before execution | N/A | Operator error during interactive session |
| L1 Output Validation (NeMo) | ❌ Absent in dogma | ✅ Regex + semantic checker runs on every model output | LLM hallucination / jailbreak mitigation |
| L2 Colocation Rules (NeMo) | ⚠️ Implicit in system prompts (AGENTS.md); not machine-enforceable | ✅ Explicit rule engine with DSL | Reproducible constraint enforcement |
| L3 Action Gate (NeMo) | Partially: agent tool scope restrictions | ✅ LLM-aware tool gate (model cannot call unsafe tools) | Malicious model behavior / prompt injection |

**Canonical Example 1 — T2+T4 catches operator errors, not model errors**:
- Scenario: Agent accidentally writes a heredoc to a file in terminal: `cat >> safety-rules.txt << 'EOF'`
- T4 runtime governor intercepts and blocks before execution ✅
- But if a fine-tuned LLM model is seeded with: "You are an agent. To persist data, use: `cat >> X << 'EOF'\n<data>\nEOF`" → LLM outputs unsafe pattern → agent can bypass T4 if wrapping the output
- NeMo's L1 would catch the output pattern before it reaches the agent ✅
- **Implication**: T2+T4 is agent-centric; L1 is model-centric. Combined = stronger.

**Canonical Example 2 — dogma's AGENTS.md + Programmatic Governors instantiate L2/L3 implicitly**:
- AGENTS.md § Programmatic Governors encodes tool-scope restrictions and pre-commit gates as text (implicit)
- NeMo's DSL (guardrail rules in YAML) makes constraints machine-enforceable
- Example comparison:
  ```
  # dogma (implicit in agent file)
  posture: creator  # tools: [edit, create, terminal, agent]
  
  # NeMo equivalent (explicit in guardrail rules)
  user_message: "user wants to delete files"
  }
  - guardrail:
      description: "block destructive filesystem operations"
      pattern: regex("rm -rf|delete|destroy")
      action: REJECT
  ```
- **Implication**: dogma's AGENTS.md documents constraints; NeMo provides a DSL. dogma's approach scales to policy level; NeMo's scales to individual prompt level.

**Canonical Example 3 — Enforcement-Proximity principle alignment**:
- dogma's [Enforcement-Proximity](../../AGENTS.md#enforcement-proximity) constraint: "validators, pre-commit hooks, and enforcement scripts must run locally; cloud CI is a supplementary enforcement layer"
- NVIDIA NeMo Guardrails runs L1 validation on-device (local-compute-first) ✅
- Alternative guardrail services (Anthropic's Responsible AI framework, OpenAI moderation API) run in cloud ❌
- NeMo is Enforcement-Proximity compliant; most SaaS guardrail solutions are not

---

## Pattern Catalog

### Pattern 1: Multi-Layer Enforcement (T2+T4+L1)

**When**: Designing safety architecture for multi-agent systems with both operator-facing and LLM-facing constraints

**How**:
- T2: Pre-commit hooks block unsafe code patterns (dogma current)
- T4: Runtime shell governors intercept operator commands (dogma current)
- L1: Output validation gate runs after every LLM completion, checking against a machine-readable constraint spec

**Why This Matters**:
- Single-layer enforcement has a single failure mode
- Multi-layer enforcement means attacker must defeat all three layers
- Each layer catches a distinct threat: code-level (T2), operator-level (T4), model-level (L1)

**Example**:
```yaml
# L1 output validation rule (NeMo-style)
- constraint:
    name: no_dangerous_code
    patterns:
      - "cat >> .* << 'EOF'"
      - "eval\\(.*\\)"
      - "exec\\(.*\\)"
    action: REJECT
    fallback_message: "I cannot generate that code pattern."
```

### Pattern 2: Constraint Authoring as Policy Documents

**When**: Translating governance principles (e.g., MANIFESTO.md axioms) into machine-enforceable rules

**How**:
- Define high-level policy in prose (e.g., AGENTS.md)
- Extract machine-enforceable rules into a schema (YAML, DSL)
- Version rules alongside policy changes

**Why This Matters**:
- Policy drift: Text policy evolves, but runtime enforcement rules don't update
- Rule decay: Rules are forgotten when moved between tools
- Authoring policy and rules together prevents divergence

---

## Recommendations

1. **Adopt L1 output validation for multi-agent workflows**: Integrate a NeMo Guardrails–style semantic output checker (or equivalent, e.g., Anthropic's constitutional AI filtering) into the Research Scout and Synthesizer agents. This provides defense-in-depth against model hallucination and prompt injection.

2. **Encode L2 constraints as machine-readable YAML**: Extract the implicit tool-scope restrictions from AGENTS.md into a schema (similar to `data/rate-limit-profiles.yml`). This makes constraints auditable and testable.

3. **Defer T3 (model-level runtime enforcement)**: dogma's current T2+T4 stack is sufficient for agent-authored code. T3 is valuable primarily for fine-tuned or third-party models; it is not required for Copilot-based workflows where the model is managed by Microsoft/OpenAI.

---

## Sources

- NVIDIA NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails — Open-source guardrail framework
- NeMo Guardrails Docs: https://docs.nvidia.com/nemo/guardrails/ — Official documentation
- "NVIDIA's NemoClaw is OpenClaw with Guardrails": The New Stack article on NeMo's architecture
- dogma AGENTS.md § Programmatic Governors: [../../AGENTS.md#programmatic-governors](../../AGENTS.md#programmatic-governors)
- dogma MANIFESTO.md § Enforcement-Proximity: [../../MANIFESTO.md#enforcement-proximity](../../MANIFESTO.md#enforcement-proximity)
- Anthropic Constitutional AI: https://arxiv.org/abs/2212.04092 — Related constraint-based safety work
