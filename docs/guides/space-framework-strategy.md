---
title: SPACE Framework Metrics for LLM Strategic Output
status: Active
---

# SPACE Framework Metrics for LLM Strategic Output

Evaluate strategic LLM outputs (research syntheses, architectural proposals, strategic advice) using the SPACE framework.

---

## SPACE Components

| Component | Definition | Measurement | Threshold |
|-----------|-----------|-------------|-----------|
| **S**ynthesis Quality | Depth of cross-source integration; novel connections vs. list of sources | Count cross-source citations + emergent patterns per page | High: ≥3 patterns per page; Low: citations only |
| **P**recision | Specificity of claims; avoid hedged generalities | Count statements with quantifiers (≥, specific %), check for "may/might/could" hedging | High: >70% specific claims; Low: >50% hedged |
| **A**ccuracy | Factual correctness; citations resolve and match | Spot-check 5 citations; verify claims against source text | High: 100% verified; Low: any unverified claim |
| **C**onvergence | Agreement with independent sources; not contrarian for novelty | Cross-check 3 major claims against recent research | High: convergent on 80%+; Low: outlier on >50% |
| **E**vidence Depth | Ratio of evidence to claims; not bare assertions | Count claims vs. citations supporting them | High: ≥1 cite per major claim; Low: >2 claims per cite |

---

## Decision Guidance

**Prefer high-S, low-P** (ambitious synthesis, but hedged language) over **high-P, low-S** (narrow, confident claims). 

Ambitious imprecision is correctable; narrow certitude is brittle.

For strategic decisions, set a minimum threshold of **S ≥ 3, P ≥ 60, A = 100, C ≥ 80, E ≥ 0.8**.
