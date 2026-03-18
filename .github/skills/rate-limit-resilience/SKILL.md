---
name: rate-limit-resilience
description: |
  Pre-delegation rate-limit gate workflow with circuit-breaker, provider-aware policies,
  and audit logging. Implements safe budget checks before orchestration phases.
effort: M
languages: [python, yaml]
related-docs:
  - docs/research/rate-limit-detection-api.md
  - AGENTS.md  
related-issues:
  - "#322"
  - "#323"
  - "#324"
  - "#325"
depends-on:
  - rate_limit_config.py
  - rate_limit_gate.py
  - detect_rate_limit.py
  - data/rate-limit-profiles.yml
---

# Rate-Limit Resilience — Pre-Delegation Gate Workflow

## Beliefs & Context

**Governing Axiom** (from [`MANIFESTO.md#3-local-compute-first`](../../../MANIFESTO.md#3-local-compute-first)):
Rate-limit constraints are structural constraints on token usage, not optional optimizations.
Treating them as a first-class system property (not a post-hoc scaling concern) enables
reliable multi-phase sessions without token exhaustion.

**Integration Points**:
- [`AGENTS.md#programmatic-first-principle`](../../../AGENTS.md#programmatic-first-principle) — Phase 0 ships four scripts instead of interactive workarounds
- [`AGENTS.md#executive-fleet-privileges`](../../../AGENTS.md#executive-fleet-privileges) — Orchestrator holds rate-limit gate logic
- [`phase-gate-sequence` SKILL.md](../phase-gate-sequence/SKILL.md) — Pre-phase checkpoint integrates gate at step 2

**Related Research**:
- [`docs/research/rate-limit-detection-api.md`](../../../docs/research/rate-limit-detection-api.md) — Tier 1 budget tracking, Tier 2 circuit-breaker

---

## Workflow & Intentions

### 1. Load Provider Policies

At the start of a delegation, the orchestrator loads provider-specific rate-limit policies:

```python
from rate_limit_config import get_policy

policy = get_policy(provider='claude', operation='delegation')
# Returns: {'sleep_sec': 60, 'retry_limit': 1, 'circuit_breaker_threshold': 3}
```

**Available Providers**:
- `claude` — Anthropic Claude API (conservative: 60s minimum sleep)
- `gpt-4` — OpenAI GPT-4 (moderate: 30s minimum sleep)
- `gpt-3.5` — OpenAI GPT-3.5 (permissive: 20s minimum sleep)
- `local-localhost` — Local inference (no rate limit: 0s sleep)
- `fallback` — Unknown providers (conservative fallback)

**Available Operations**:
- `fetch_source` — Source fetching during research
- `delegation` — Agent delegation phase
- `phase_boundary` — Phase transitions
- `review_gate` — Review agent invocations
- `commit` — GitHub commits/API calls

### 2. Pre-Delegation Budget Check

Before delegating a phase, call `rate_limit_gate.py`:

```bash
uv run python scripts/rate_limit_gate.py 50000 delegation \
  --provider claude \
  --audit-log
```

**Inputs**:
- `current_token_budget` — tokens remaining in rate-limit window
- `operation_type` — one of the operations above
- `--provider` — provider name (default: `claude`)
- `--audit-log` — log decision to `.cache/rate-limit-audit.log`

**Output** (JSON):
```json
{
  "safe": true,
  "recommended_sleep_sec": 0,
  "reason": "Safe: 50000 tokens available, 1 retries allowed",
  "provider": "claude",
  "operation": "delegation",
  "consecutive_failures": 0
}
```

**Decision Logic**:
1. **Circuit-Breaker Check**: If N consecutive failures in last M minutes, return `safe: false`
   - N (threshold) varies by operation (e.g., 3 for delegation)
   - M (window) = 5 minutes
2. **Budget Check**: If current_token_budget < `MIN_BUDGET_SAFETY_MARGIN` (5k tokens), return `safe: false`
3. **Otherwise**: `safe: true`

### 3. Orchestrator Decision Flow

```python
import json
import subprocess

# Check gate before delegating
result = subprocess.run(
    ['uv', 'run', 'python', 'scripts/rate_limit_gate.py',
     str(current_budget), 'delegation',
     '--provider', provider_name,
     '--audit-log'],
    capture_output=True,
    text=True,
)

gate_decision = json.loads(result.stdout)

if gate_decision['safe']:
    # Proceed with delegation
    delegate_to_agent(...)
else:
    # Sleep + retry or defer phase
    sleep_sec = gate_decision['recommended_sleep_sec']
    print(f"Rate-limited. Sleeping {sleep_sec}s: {gate_decision['reason']}")
    time.sleep(sleep_sec)
    # Retry or escalate (e.g., defer phase to next session)
```

### 4. Circuit-Breaker Semantics

A **circuit-breaker threshold** is the number of consecutive rate-limit failures
that triggers the breaker.

**Per-provider thresholds** (from `data/rate-limit-profiles.yml`):
- Claude delegation: threshold=3 → if 3+ consecutive delegations rate-limited, block
- GPT-4 delegation: threshold=4 → more tolerance
- Phase boundaries: threshold=2 → stricter (fewer failures tolerated)

**Audit Log Format** (JSONL, one entry per line):
```json
{"timestamp": "2026-03-17T15:30:45.123456", "decision": "rate_limit_safe", "provider": "claude", "operation": "delegation", "consecutive_failures": 0, "reason": "..."}
{"timestamp": "2026-03-17T15:30:46.654321", "decision": "rate_limit_blocked", "provider": "claude", "operation": "delegation", "consecutive_failures": 1, "reason": "Circuit breaker..."}
```

### 5. Budget Detection (Tier 1)

`scripts/detect_rate_limit.py` provides simpler budget classification for initial checks:

```bash
# Check if 50k tokens can support a 30k phase
uv run python scripts/detect_rate_limit.py --check 50000 30000 --provider claude
# Output: OK
```

**Status Values**:
- `OK` — Abundant budget (remaining > 2× total_needed)
- `WARN` — Tight budget (1× < remaining ≤ 2× total_needed)
- `CRITICAL` — Low budget (0 < remaining ≤ 1× total_needed)
- `SLEEP_REQUIRED_NNN` — Budget exhausted; must sleep NNN milliseconds

**Issue #322 Fix**: Cap/floor logic corrected:
- Floor (minimum): `MIN_SLEEP_MS` = 60 seconds
- Cap (maximum): `PHASE_BOUNDARY_SLEEP_MS` = 120 seconds
- Previous bug: strict `max()` over all three values ignored floor/cap separation
- New logic: `min( max(computed, floor), cap )`

---

## Integration Points & Examples

### In AGENTS.md § Executive Orchestrator

**Before every delegation**, check the budget gate:

```yaml
Pre-Delegation Rate-Limit Check:
  - Run: uv run python scripts/rate_limit_gate.py $(current_budget) $(operation_type) --provider $(provider) --audit-log
  - If result.safe == false: defer phase or sleep
  - Log decision to scratchpad under "## Rate-Limit Gate Output"
```

### In phase-gate-sequence SKILL.md § Step 2

**Pre-phase checkpoint now includes**:
```bash
# Before delegating next phase
uv run python scripts/rate_limit_gate.py "$CURRENT_BUDGET" "$PHASE_TYPE" --provider "$PROVIDER" --audit-log
# If blocked: log, sleep, or defer
```

### Canonical Example — Research Scout Delegation

```bash
# Executive Orchestrator about to delegate research
BUDGET=75000  # tokens remaining
PHASE=delegation
PROVIDER=claude

if uv run python scripts/rate_limit_gate.py "$BUDGET" "$PHASE" --provider "$PROVIDER" --audit-log | grep -q '"safe": true'; then
    # Safe: delegate now
    delegate_to_research_scout(...)
else
    # Blocked: log and defer
    echo "Rate-limited. Deferring to next session." >> .tmp/branch/date.md
fi
```

---

## Testing & Validation

**Unit Tests**:
- `tests/test_rate_limit_config.py` — Policy loading, fallback behavior
- `tests/test_rate_limit_gate.py` — Gate logic, circuit-breaker, audit logging
- `tests/test_detect_rate_limit.py` — Budget detection, cap/floor fix (issue #322), provider parameter

**Test Coverage Target**: ≥80%

**Pre-Commit Validation**:
```bash
uv run ruff check scripts/rate_limit_*.py
uv run python -m pytest tests/test_rate_limit_*.py -q
```

**Integration Test** (manual, per-session):
1. Run a phase that consumes tokens (e.g., research delegation)
2. Check `.cache/rate-limit-audit.log` for gate decisions
3. Verify circuit-breaker triggers after 3+ consecutive failures (for Claude delegation)

---

## Guardrails & Constraints

**From [`AGENTS.md`](../../../AGENTS.md)**:
- All scripts carry `--dry-run` flag for safe preview (on scripts that mutate state)
- Python toolchain: always `uv run python`, never direct invocation
- No heredocs for content writes (use `create_file` / `replace_string_in_file`)

**Provider Policy Constraints**:
- Policies are **immutable** at runtime (loaded once, not refreshed during execution)
- To update policies, edit `data/rate-limit-profiles.yml` and restart the orchestrator session
- Fallback policy applies to unknown providers (conservative defaults)

**Audit Log Constraints**:
- Append-only (never truncate mid-session)
- JSONL format (one JSON object per line)
- Path: `.cache/rate-limit-audit.log` (gitignored; local to clone)

---

## Anti-Patterns & Known Issues

**Anti-Pattern**: Ignoring `safe: false` and delegating anyway
→ Will likely hit rate-limit mid-phase, causing cascading retries and session failure

**Anti-Pattern**: Clearing the audit log between retries
→ Circuit-breaker loses state; consecutive failures not counted

**Known Limitation**: Circuit-breaker window is fixed at 5 minutes
→ Future: make configurable per provider (GitHub issue TBD)

---

## Troubleshooting

**Q: Gate returns `safe: false` but budget looks high?**  
A: Check circuit-breaker: `grep "decision.*rate_limit" .cache/rate-limit-audit.log | tail -3`
If 3+ recent failures for that provider/operation, circuit-breaker is active.

**Q: Policy not loaded for new provider?**  
A: Verify entry in `data/rate-limit-profiles.yml` and restart session. Falls back to `fallback` policy if missing.

**Q: Audit log is empty?**  
A: Confirm `--audit-log` flag was used. Without it, no writes occur (intentional for testing).

---

## References

- **MANIFESTO.md** § [Local Compute-First](../../../MANIFESTO.md#3-local-compute-first)
- **AGENTS.md** § [Programmatic-First](../../../AGENTS.md#programmatic-first-principle)
- **Research**: [rate-limit-detection-api.md](../../../docs/research/rate-limit-detection-api.md)
- **Related Skills**: [phase-gate-sequence](./phase-gate-sequence/SKILL.md)
- **Related Issues**: #322 (cap/floor fix), #323 (provider policies), #324 (circuit-breaker), #325 (audit logging)
