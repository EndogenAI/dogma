# Context Budget Policy — Per-Tier Allocation Targets

**Status**: Draft
**Governs**: All Executive fleet agents
**Review cycle**: After each Value Encoding milestone phase
**Source research**: [docs/research/context-budget-balance.md](research/context-budget-balance.md) (issue #85)

---

## Tiers

| Tier | Description | Budget Ceiling | Notes |
|------|-------------|----------------|-------|
| T1 Instruction | AGENTS.md + agent file + mode instructions + memory | ≤ 25% | D1 baseline: ~14,375 tokens fixed. Trigger R1/R2 when T1 > 20K tokens |
| T2 Session | Active scratchpad + task context + issue bodies + file reads | ≤ 55% | Reserve for task content; prune when scratchpad ≥ 2,000 lines |
| T3 Output | Response buffer | ≤ 15% | Hard floor; never sacrifice to gain T1/T2 headroom |
| T4 Reserve | Available for retrieval injection (RAG governance) | ≥ 5% | Required once R3 retrieval layer is implemented (#80) |

> **Derivation**: T1 ceiling (25%) is set at 1.25× the D1 baseline fraction at 50K effective context (28.7%). This provides a 25% growth buffer before enforcement triggers while keeping T1 well below the Q2 degradation threshold of 30-45%. T2 (55%) + T3 (15%) + T4 (5%) = 75%. T1 (25%) + 75% = 100%. At 128K context, T1=25% = 32K tokens — enough headroom for current substrate plus one phase of R1 extraction growth.

---

## Intervention Triggers

| Condition | Recommended Intervention |
|-----------|--------------------------|
| T1 > 20,000 tokens | Audit agent file for extractable decision logic — run R1 (skills extraction, #79) |
| T1 > 25,000 tokens | Hard trigger: R2 pruning audit required before next sprint commit |
| T2 > ceiling (scratchpad ≥ 2,000 lines) | `uv run python scripts/prune_scratchpad.py --force` |
| T2 context accumulation visible mid-session | Enable compaction; write session summary to scratchpad immediately |
| T4 < 5% (retrieval layer active) | Skip RAG injection this session; note gap in scratchpad |
| Instruction adherence shortcutting observed | Mid-session signal: re-read relevant AGENTS.md section explicitly; schedule T1 audit |

---

## Measurement Methodology

### Token count (character proxy)

Until a dedicated `scripts/count_instruction_tokens.py` exists, use the character/4 proxy:

```bash
# T1 measurement
total_chars=$(wc -c < AGENTS.md)
agent_chars=$(wc -c < .github/agents/<agent-name>.agent.md)
echo "T1 estimate: $(( (total_chars + agent_chars) / 4 )) tokens (+ ~1,900 for mode/memory)"
```

Exact tiktoken measurement (requires `tiktoken` package):

```bash
uv run python -c "
import tiktoken
enc = tiktoken.encoding_for_model('gpt-4')
with open('AGENTS.md') as f: agents = len(enc.encode(f.read()))
print(f'AGENTS.md: {agents} tokens')
"
```

### D1 Baseline (2026-03-08 measurement)

| Layer | Characters | Tokens (÷4) |
|-------|-----------|-------------|
| AGENTS.md | 28,361 | ~7,090 |
| executive-orchestrator.agent.md | 19,141 | ~4,785 |
| Mode instructions (Executive Researcher) | ~5,500 | ~1,375 |
| User + repo memory | ~4,500 | ~1,125 |
| **Total T1** | **~57,500** | **~14,375** |

At current size: T1 consumes 44.9% at 32K context, 28.7% at 50K, 11.2% at 128K.  
**Risk zone threshold**: T1 > 25% of effective working context per turn.

---

## Growth Forecast

If the substrate grows at the observed rate (~5K chars per milestone phase):

| Milestone Phase | Projected T1 Chars | T1 Tokens | T1% at 50K |
|----------------|-------------------|-----------|-----------|
| Current (baseline) | 57,500 | 14,375 | 28.7% |
| +1 phase | 62,500 | 15,625 | 31.3% — RISK ZONE |
| +2 phases | 67,500 | 16,875 | 33.8% — TRIGGER R1 |
| Post-R1 extraction | ~47,500 | ~11,875 | 23.8% — SAFE |

R1 (skill extraction) must be executed before the +2 phase forecast is reached to stay below the 30% risk threshold at 50K effective context.

---

## Derivation

Numeric targets X, Y, Z, W are derived from the D1 and D2 findings in [docs/research/context-budget-balance.md](research/context-budget-balance.md):

- **X = 25%** (T1 ceiling): 1.25× the measured D1 fraction at 50K context (28.7%). Provides a managed growth buffer while staying below the Q2 degradation threshold (30–45% at 32K; 15–20% of in-flight context mid-session). Aligns with Anthropic guidance: fixed system prompt should be minimal given finite attention budget.
- **Y = 55%** (T2 ceiling): Derived as the complement of T1 + T3 + T4 floors (25% + 15% + 5%). Consistent with the scratchpad compaction trigger at 2,000 lines (`prune_scratchpad.py`).
- **Z = 15%** (T3 output floor): Derived from observed output size distribution in research sessions (typical synthesis section: 500–2,000 tokens; full response: 1,000–4,000 tokens at 32K context = 3–12%). 15% provides a 25% safety buffer over observed maximums.
- **W = 5%** (T4 RAG reserve floor): Minimal reserve for a single targeted governance query (~500 tokens for BM25 query result). Increase to 10% once R3 retrieval layer is active.

---

## Related Issues

- [#85](https://github.com/EndogenAI/Workflows/issues/85) — Source research (this document derives from its D1/D2 findings)
- [#80](https://github.com/EndogenAI/Workflows/issues/80) — Queryable docs substrate — T4 implementation
- [#79](https://github.com/EndogenAI/Workflows/issues/79) — Skills as decision codifiers — T1 reduction via extraction (R1)
- [#82](https://github.com/EndogenAI/Workflows/issues/82) — Dogma neuroplasticity — T1 reduction via pruning (R2)
- [#13](https://github.com/EndogenAI/Workflows/issues/13) — Episodic memory — T2 management (history queryable on demand)
- [#14](https://github.com/EndogenAI/Workflows/issues/14) — AIGNE AFS governance — pipeline-level context compress/select/isolate
