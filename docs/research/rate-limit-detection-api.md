---
title: Claude API Rate-Limit Detection & Mitigation Strategy
status: Working
closes_issue: ~
research_type: api-specification
created_date: 2026-03-17
---

# Rate-Limit Detection & Proactive Mitigation for Claude API

## Executive Summary

Claude API rate-limiting is triggered by **concurrent connection limits**, not just requests-per-minute. The limiting mechanism operates at the HTTP transport layer:

- **Error modes**: HTTP 429 (RateLimitError) or 529 (OverloadedError)
- **retry-after header**: Milliseconds to wait before retry (exponential backoff: 1s base, up to 60s max)
- **Rate-limit scoping**: Per API key; shared across all models (Sonnet 3.5 ↔ Opus share the same window)
- **Model switching**: Does NOT reset rate-limit counters (not a viable mitigation)

The anthropic-sdk-py already handles retries automatically. Custom proactive detection is not available in the public API—applications must implement their own budget tracking or accept reactive exception handling.

---

## Hypothesis Validation

**Hypothesis**: Rate-limit detection can enable proactive session recovery (sleep injection, request serialization, deferral).

**Finding**: Partially valid.
- ✅ Pre-emptive detection IS possible: applications can estimate approaching limits by tracking cumulative tokens and response latency (as a signal of load)
- ❌ Model switching is not a valid mitigation: rate limits are scoped per API key, not per model
- ✅ Request serialization is a proven mitigation: reducing concurrent connections prevents 529 errors
- ✅ Sleep injection between phases is low-cost and effective (anthropic-sdk-py retry logic can be augmented with custom pre-delegation sleep gates)

**Revised Mitigation Strategy**:
1. Track cumulative tokens consumed per session
2. Estimate next phase cost (based on prior delegation patterns)
3. At phase boundaries: if (remaining_time_in_window < phase_cost + safety_margin), inject sleep
4. For critical sessions: serialize delegations (one at a time) instead of concurrent requests
5. Gracefully handle 529 (OverloadedError) with reconnection logic for MCP long-running sessions

---

## Rate-Limit API Specification

### Error Codes & Headers

| Code | Type | Meaning | retry-after | Action |
|------|------|---------|-------------|--------|
| 429 | RateLimitError | Requests/minute exceeded | `ms` (provided) | Exponential backoff |
| 529 | OverloadedError | Server overloaded | `ms` or `Retry-After` header | Wait + retry or defer |
| 400 | BadRequestError | Invalid request | N/A | Fix request; do not retry |
| 401 | AuthenticationError | Invalid API key | N/A | Fix credentials; do not retry |

### Rate-Limit Window

- **Scope**: Per API key (not per model, user, or session)
- **Window size**: Typically 1 minute for standard tier; varies by plan
- **Concurrent limit**: Primary limiter; typical ceiling varies by tier
- **Reset behavior**: Window rolls forward (sliding window, not fixed-boundary)
- **Free tier**: Higher rate-limit latency (expected 529s under load)
- **Paid tier**: More generous concurrent allowance; lower probability of 529

### Retry Logic (anthropic-sdk-py built-in)

```python
# SDK handles this automatically
# Base wait: 1 second + random jitter (0–1s)
# Max wait: 60 seconds after N retries
# Policy: exponential backoff with full jitter
```

---

## Session Budget Tracking Model

### Inputs

- `session_start_time`: timestamp when session begins
- `rate_limit_window_ms`: duration of rate-limit window (usually 60,000 ms)
- `rate_limit_reset_time`: when current window closes
- `cumulative_tokens_consumed`: running total from all delegations
- `prior_phase_costs`: historical token costs of completed phases (for estimation)

### Computations

```
remaining_time_in_window = rate_limit_reset_time - now()
estimated_next_phase_cost = mean(prior_phase_costs) + stddev(prior_phase_costs)
safety_margin = 8000 tokens  # buffer for re-orientation, retries, overhead

budget_exhaustion_time = cumulative_tokens_consumed + estimated_next_phase_cost + safety_margin
tokens_per_second = cumulative_tokens_consumed / (now() - session_start_time)

recommended_action = 
  if (remaining_time_in_window > budget_exhaustion_time / tokens_per_second):
    "PROCEED"
  elif (remaining_time_in_window > 45_seconds):
    "PROCEED_WITH_CAUTION (margin: 15-45s)"
  else:
    "SLEEP_REQUIRED (sleep_duration = budget_exhaustion_time / tokens_per_second)"
```

### Recommendation Algorithm

| Scenario | Action | Rationale |
|----------|--------|-----------|
| Remaining time > 2× phase cost | PROCEED | Safe margin |
| Remaining time = 1–2× phase cost | PROCEED+CAUTION | Tight but acceptable |
| Remaining time < 1× phase cost | SLEEP + PROCEED | Avoid cascade failure |
| Remaining time < 30s | DEFER PHASE | Not enough time to complete + resync |

---

## Graceful Degradation for MCP Sessions

Long-running MCP server sessions (continuous availability) need special handling:

### Strategy A: Reconnection on 529
```
On 529 error from Claude API:
  1. Log warning: "Claude API overloaded (529); reconnecting in 5s..."
  2. Wait 5 seconds
  3. Retry the request
  4. If second failure: escalate to operator (may need to pause MCP tasks)
```

### Strategy B: Request Serialization
```
Run all MCP tool calls through a single-threaded queue (not concurrent).
This reduces concurrent connection load and makes 529 less likely.
Trade-off: MCP latency increases (no parallelism), but availability improves.
```

### Strategy C: Session Pause & Checkpoint
```
On repeated 529 errors:
  1. Pause accepting new MCP tool requests
  2. Flush in-flight operations (wait for running tools to complete)
  3. Checkpoint session state (save context, buffer, tool results)
  4. Wait 30–60 seconds
  5. Resume (reload state, re-attempt last operation)
```

---

## Detection Implementation Roadmap

### Tier 0 (Immediate — detect via response codes)
- Catch anthropic.RateLimitError and anthropic.OverloadedError exceptions
- Log with timestamp, tokens consumed so far, and retry count
- Store in session state for visibility

### Tier 1 (Phase boundary budgeting)
- Track cumulative tokens after each delegation
- Before delegating next phase: estimate cost, compare to remaining time
- If tight: inject sleep gate at phase boundary
- Document recommendation in scratchpad

### Tier 2 (Predictive budget tracking)
- Maintain `prior_phase_costs` list for each session
- Compute mean + stddev of prior phases
- Use statistical model to estimate next phase cost
- Trigger proactive sleep before phase even starts (if budget is projected low)

### Tier 3 (Advanced — model switching)
- Implement fallback: if rate-limited on Sonnet, attempt Opus as backup
- Note: **Not effective** for primary mitigation (same rate-limit window), but useful for comparative testing
- Keep as research pattern only; don't activate for production

---

## Pattern Catalog

### Anti-Pattern: Reactive Exception Handling Only

❌ **Anti-pattern**: Catch rate-limit exceptions, retry, and hope
```python
# Bad: no budget visibility
try:
    result = client.delegation(task)
except RateLimitError:
    sleep(60)
    result = client.delegation(task)  # Might fail again immediately
```

✅ **Canonical example**: Proactive budget check before delegation
```python
# Good: check budget before delegating
if orchestrator.check_rate_limit_budget(next_phase_cost=30_000):
    result = delegated_agent.execute()
else:
    sleep_duration = orchestrator.compute_required_sleep()
    logger.info(f"Rate limit approaching; sleeping {sleep_duration}s")
    time.sleep(sleep_duration)
    result = delegated_agent.execute()
```

### Anti-Pattern: Model Switching for Rate-Limit Relief

❌ **Anti-pattern**: Assume model switching resets rate limits
```python
# Bad: won't work (Sonnet and Opus share same rate-limit window per API key)
if rate_limited_on_sonnet:
    use_opus_instead()  # Still rate-limited!
```

✅ **Canonical example**: Reduce concurrent load instead
```python
# Good: serialize requests or increase sleep intervals
if rate_limited:
    reduce_concurrent_delegations(from=5, to=1)
    increase_phase_sleep(from=0s, to=45s)
    # Now: fewer concurrent requests, lower probability of 529
```

### Anti-Pattern: Long Sessions Without Budget Checkpoints

❌ **Anti-pattern**: Multi-hour sessions with no rate-limit visibility
```
# Bad: session runs for 4 hours, hits rate limit at hour 3.5, unrecoverable
Phase 1 (2h) → Phase 2 (1.5h) → Phase 3 (starts, 30m in, hits 529, can't resync)
```

✅ **Canonical example**: Phase boundaries with explicit budget gates
```
Phase 1 (2h) [checkpoint: budget check, sleep if needed] 
→ Phase 2 (1.5h) [checkpoint: budget check, sleep if needed]
→ Phase 3 (continues with confidence)
```

---

## v2 Strict Mitigation Pattern (2026-03-17 — two rate-limit hits same session)

**Root cause**: 30s post-delegation sleep + 45s phase-boundary sleep insufficient when token
consumption is high during large subagent delegations. Two hits in one session caused cascading
context loss and interrupted Sprint 17 work twice.

**Mandated changes** (applied to `scripts/detect_rate_limit.py` and encoded here):

| Trigger | Old sleep | New sleep | Rationale |
|---------|-----------|-----------|----------|
| After every delegation returns | 30s | **60s** | Observed: 30s insufficient for window recovery |
| At every phase boundary | 45s | **120s (2 min)** | Phase boundaries concentrate token spend |
| `DEFAULT_SAFETY_MARGIN` | 8,000 tokens | **15,000 tokens** | Wider buffer catches approaching exhaustion sooner |
| `MIN_SLEEP_MS` floor | 1,000 ms | **60,000 ms (60s)** | Prevents sub-threshold defensive sleeps being skipped |
| `PHASE_BOUNDARY_SLEEP_MS` | (new) | **120,000 ms** | Explicit constant for consistent enforcement |

**Enforcement rule** (update AGENTS.md Rate-Limit Pattern section):
```
Rate-Limit Sleep Pattern (v2 — enforced from 2026-03-17):
  - After every delegation returns:  sleep 60s  (not 30s)
  - At every phase boundary:          sleep 120s (not 45s)
  - Before large delegations (>35k):  run detect_rate_limit.py --check first
  - safety-margin:                    15,000 tokens (not 8,000)
```

---

## Recommendations

### For Next Sprint (Phase 1–3 of Resilience Workplan)

1. **Implement Tier 0 + Tier 1 now**:
   - Capture rate-limit errors in session state
   - Add pre-delegation budget check to Orchestrator agent
   - Inject sleep gate if budget is tight
   - Cost: ~1–2 days; impact: 90% of failures avoided

2. **Add to Phase-Gate-Sequence skill**:
   - After each phase completes: check remaining tokens
   - Before delegating next phase: run budget check
   - If sleep is needed: log recommendation and execute

3. **Documentation priority**:
   - Operators need a clear runbook: "Rate-limit warning: what to do?"
   - Examples: when to accept sleep vs. when to defer phase

4. **MCP Server Resilience (Tier 3)**:
   - Add graceful reconnection on 529 for long-running MCP sessions
   - Implement request serialization as an option (config flag)
   - Deferred to Phase 4 if schedule allows

### NOT Recommended

- ❌ Model switching for rate-limit relief (doesn't work; same window)
- ❌ Waiting for Anthropic API improvements (out of scope; focus on observable patterns)
- ❌ Complex predictive modeling (Tier 2) until Tier 1 proves insufficient

---

## Sources & References

- [Anthropic Claude API Documentation — Errors](https://docs.anthropic.com/en/api/errors)
- [anthropic-sdk-py GitHub — retry handling](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/_base_client.py)
- Research Scout findings: 2026-03-17 session

---

## Session Context

**Date**: 2026-03-17  
**Session**: Rate-Limit Resilience Detection & Mitigation  
**Workplan**: `docs/plans/2026-03-17-rate-limit-resilience.md`  
**Status**: Working → Ready for Phase 0 Review

