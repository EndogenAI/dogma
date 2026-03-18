---
title: Value Density as L3 Success Signal
status: Active
---

# Value Density as L3 Success Signal

## Definition

**Value Density (VD)** = (merged commits + closed issues) / (token spend this sprint × 10^-4)

Measured in commits/10-thousand-tokens. A sprint with 8 commits and 80K tokens = VD of 1.0.

---

## Why Token Spend Matters

Token spend is a proxy for efficiency. Lower token spend for the same deliverables means:
- Fewer agent handoffs (less context-loss overhead)
- Better pre-computation (algorithms before tokens, per MANIFESTO.md § 2)
- Denser orchestration (phases gate more tightly, less parallelization waste)

High VD = high-velocity sprint (high output per cognitive/computational resource).

---

## Decision Rule

**If VD < 0.5 commits/10k-tokens, next phase should focus on efficiency blocker research.**

Low VD signals:
- Context-heavy tasks consuming tokens without proportional output
- Insufficient pre-computation or phase gating
- Subagent hand-off cascade overhead

---

## Examples

| Sprint | Commits | Issues Closed | Token Spend | VD |
|--------|---------|---------------|-------------|-----|
| Sprint 15 (baseline) | 12 | 8 | 120K | 1.67 |
| Sprint 16 (parallel overload) | 6 | 2 | 180K | 0.44 |
| Sprint 17 (phase-gating fix) | 14 | 10 | 95K | 2.53 |

Sprint 16 exceeded decision threshold; Phase 1 (Sprint 17) focused on phase-gate optimization → VD recovered above baseline.
