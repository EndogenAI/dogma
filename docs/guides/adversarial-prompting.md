---
title: Adversarial Prompting for Trend-Adjacent Strategy
status: Active
---

# Adversarial Prompting for Trend-Adjacent Strategy

## Pattern

**Trendslop**: LLM output that repackages existing trends without novel analysis, evidence, or surprising perspective. Surfaces polished but derivative conclusions.

Trendslop is a failure mode — it looks rigorous but collapses under adversarial pressure.

### Detection Prompt

After receiving strategic output from an LLM, embed this follow-up:

```
Identify the three most conventional claims in your response. 
For each claim, what evidence would overturn it? 
What would a rival researcher cite to argue against you?
```

Trendslop fails this test — it cannot produce falsifiable counter-positions because it rests on unstated conventional assumptions.

---

## When to Use

Use adversarial prompting when:

1. **Strategic LLM output is being evaluated for novelty** — e.g., LLM producing a proposal, research synthesis, or architectural recommendation
2. **Output is synthetic but potentially derivative** — synthesizes sources well but may repackage rather than advance
3. **Decision depends on novel insight** — if the output is a replay of available trends, it fails to meet the threshold

Do **not** use adversarial prompting for factual lookups, code generation, or routine formatting tasks.

---

## Integration

Embed adversarial prompts at the **Review gate** before approving strategic research or architectural recommendations. Log the results in the session scratchpad under `## Adversarial Review`.
