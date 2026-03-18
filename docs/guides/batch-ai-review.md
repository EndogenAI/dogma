---
title: Batch AI Output Review Strategy
status: Active
---

# Batch AI Output Review Strategy

## 30-Min Deep-Work Window Protocol

Do not review LLM outputs serially (one at a time, as they arrive). Instead, cluster outputs of the same type from the same session into a single 30-minute deep-work block.

### Rationale

- **Context preservation**: Clustering outputs lets you hold shared context (session goals, session scratchpad, evaluation criteria) in working memory across reviews
- **Signal spotting**: Comparing multiple outputs from the same phase in sequence reveals patterns (e.g., "all three proposals hedged on security — recurring gap")
- **Batch efficiency**: Review velocity 2–3× higher than serial reviews due to reduced context-switching overhead

### Preparation Checklist

Before starting the 30-min window:

1. Stage outputs in a single folder or document
2. Write success criteria (what makes an output "approved" or "send-back") as a bullet list
3. Set a timer for 30 min; aim to review 3–5 outputs in this window
4. Write findings to scratchpad under `## Review Session Output` (not scattered in comments)

### When to Stage Outputs

Batch **only** outputs that:
- Same agent produced them (or same agent type — e.g., multiple Research Scout passes)
- Same phase or workflow (don't batch Phase 2 outputs with Phase 5 outputs)
- Same evaluation criteria apply
- Produced within 24 hours

Do **not** batch outputs from different agents or phases — context divergence defeats the benefit.

---

## Velocity Improvement

A 30-min batch review session typically processes 12–15K tokens of output with higher precision than serial reviewing of the same set over 90 minutes. Result: 2–3× higher signal-to-time ratio.
