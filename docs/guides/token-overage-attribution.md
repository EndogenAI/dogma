---
governs: [local-compute-first, algorithms-before-tokens]
---

# Token Overage Attribution Protocol

> Governing axiom: [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — minimize token burn; attribute overages to phases before close so they can be encoded as fixes. See also [AGENTS.md § Pre-Delegation Rate-Limit Gate](../../AGENTS.md#pre-delegation-rate-limit-gate-sprint-18).

At session close, any session where token usage exceeded budget must go through this three-step attribution protocol before the scratchpad is archived. Skipping this protocol means the overage root cause is not encoded — the same waste recurs next session.

---

## Three-Step Protocol

### Step 1 — Identify the High-Burn Phase

Run the token spin detector to surface which session phase consumed the most tokens:

```bash
uv run python scripts/token_spin_detector.py
```

The script outputs a ranked list of phases by token consumption. Record the top entry (phase name + token count).

### Step 2 — Log Under `## Token Overage`

In the session scratchpad (`.tmp/<branch>/<date>.md`), append a `## Token Overage` section with:

```
## Token Overage

Phase: <phase name>
Tokens consumed: <count>
Budget: <target>
Root cause: <one sentence — e.g., "multi-pass re-read of docs/research/ without pre-caching">
Fix candidate: <one sentence — e.g., "pre-warm .cache/sources/ before delegation">
```

This creates a permanent record of the overage and its root cause. The [rate-limit gate pattern](../../AGENTS.md#pre-delegation-rate-limit-gate-sprint-18) is the upstream enforcement mechanism that prevents overages from reaching this step in the first place.

### Step 3 — Open a GitHub Issue for Overages > 20%

If token consumption exceeded the session budget by more than 20%, open a GitHub issue to encode a fix:

```bash
# Write body to temp file first (per AGENTS.md § File Writing Guardrails)
gh issue create \
  --title "chore: encode token-overage fix for <phase>" \
  --label "type:chore,area:ci" \
  --body-file /tmp/overage-issue.md
```

Tag with `type:chore` and `area:ci`. The issue body must include: phase name, root cause, and the fix candidate from Step 2.

---

## When This Protocol Applies

| Condition | Action |
|-----------|--------|
| Session ended within budget | Skip this protocol |
| Session exceeded budget by ≤ 20% | Steps 1–2 only (log; no issue) |
| Session exceeded budget by > 20% | Steps 1–3 (log + open issue) |
| Root cause is a repeatedly-seen pattern | Escalate to Executive Scripter to encode a pre-delegation gate |

---

## Governing References

- [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — minimize token burn; make each session measurably cheaper than the last
- [AGENTS.md § Pre-Delegation Rate-Limit Gate](../../AGENTS.md#pre-delegation-rate-limit-gate-sprint-18) — upstream gate that prevents rate-limits before they cause overages
- [AGENTS.md § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle) — if the same overage root cause is seen twice, encode a script-level fix before the third occurrence
