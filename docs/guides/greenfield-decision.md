---
governs: [endogenous-first, programmatic-first]
---

# Greenfield Decision Framework

> Governing axiom: [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — build from existing system knowledge before reaching for new components. See also [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle).

Before creating any new component from scratch, evaluate it against the five criteria below in order. The framework determines whether to **extend an existing component** or **build greenfield**. Apply each criterion in sequence and stop at the first decisive answer.

---

## Five-Criterion Framework

### Criterion 1 — Existing Coverage ≥ 60%

Does an existing script or agent cover ≥ 60% of the use case?

**Check**: Search `scripts/` and `.github/agents/` for overlap. Run `uv run python scripts/check_fleet_integration.py --dry-run` to surface existing fleet members with related scope.

**Decision**: If yes → **Extend** the existing component. Do not create a new file.

**Anti-pattern**: Creating a new `scripts/check_X.py` when `scripts/check_fleet_integration.py` already handles 70% of the logic. Two near-identical scripts accumulate independently, diverge on edge cases, and impose double the maintenance burden.

---

### Criterion 2 — Extension Line Count > 50

Would extending an existing file require adding more than 50 new lines to it?

**Decision**: If yes → Consider greenfield. A 50-line growth threshold is a signal that the existing abstraction boundary is wrong for this use case, not that the new use case is a natural extension.

**Exception**: If the added lines are primarily data (config values, mappings, lookup tables), they may be added to the existing file even above the threshold — data growth is not the same as logic growth.

---

### Criterion 3 — Fundamentally Different Posture

Does the component require a fundamentally different agent posture from existing fleet members?

**Check**: Consult the posture taxonomy in [AGENTS.md § Agent authoring conventions](../../AGENTS.md#agent-authoring-conventions). A new posture means a different tool scope (read-only vs. full execution) or a different decision authority (subagent vs. executive).

**Decision**: If yes → **Greenfield agent file** in `.github/agents/`, following [agent-file-authoring SKILL](../../.github/skills/agent-file-authoring/SKILL.md).

---

### Criterion 4 — Two Sessions Hit the Same Abstraction Boundary

Would two subsequent sessions both encounter the same abstraction boundary — the same place where the current fleet falls short?

**Decision**: If yes → **Encode as a shared `SKILL.md`** in `.github/skills/<name>/`. When a procedure appears in two agent bodies, extract it to a skill before writing a third copy (Programmatic-First applied to instruction prose).

---

### Criterion 5 — One-Off Task

Is this a genuinely non-recurring, one-off task?

**Decision**: If yes → **Interactive is acceptable**. Document the assumption inline (code comment or commit message body) so a future session can re-evaluate if the assumption turns out to be wrong.

**Caveat**: A task that appears one-off but recurrs unexpectedly triggers the Programmatic-First encoding obligation — at the second recurrence, script it before the third.

---

## Decision Summary Table

| Criterion | Outcome |
|-----------|---------|
| Existing coverage ≥ 60% | Extend existing |
| Extension > 50 lines | Consider greenfield |
| Different posture required | Greenfield agent file |
| Two sessions hit same boundary | Extract to SKILL.md |
| Genuine one-off | Interactive + document assumption |

---

## Governing References

- [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — build from existing system knowledge; greenfield is the expensive last resort
- [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle) — the third recurrence triggers a scripting obligation; this framework determines the correct encoding target
- [AGENTS.md § VS Code Customization Taxonomy](../../AGENTS.md#vs-code-customization-taxonomy) — boundary decision rule between agent files and SKILL.md files
