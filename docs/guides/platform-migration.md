---
governs: [local-compute-first, endogenous-first]
---

# Platform Migration Guide

> Governing axiom: [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — platforms are infrastructure, not identity. The project must remain portable across providers by design. See also [`docs/research/ai-platform-lock-in-risks.md`](../research/ai-platform-lock-in-risks.md).

This guide specifies the five-step process for migrating the project between AI platforms (model provider, hosting environment, or API). Follow the steps in order; do not skip to Step 3 before Step 1 is complete.

---

## Five-Step Migration Process

### Step 1 — Check Provider Profiles

Before any migration work begins, review `data/rate-limit-profiles.yml` to confirm whether a profile for the new provider already exists:

```bash
cat data/rate-limit-profiles.yml
```

If a profile exists, use it directly in Step 3. If no profile exists, add one following the schema in the file (fields: `provider`, `delegation_sleep_sec`, `circuit_breaker_threshold`, `budget_floor_tokens`). Commit the new profile before proceeding.

### Step 2 — Validate with `local-localhost` Profile First

Before connecting to the new external provider, run all integration tests against the `local-localhost` profile to establish a baseline:

```bash
uv run python scripts/rate_limit_gate.py 100000 delegation --provider local-localhost --audit-log
```

A pass here confirms the gate infrastructure is functioning before adding the complexity of a new external endpoint.

### Step 3 — Run Rate-Limit Gate with New Provider

Run the rate-limit gate script configured for the new provider to confirm budget and circuit-breaker behaviour:

```bash
BUDGET=<token_budget>
uv run python scripts/rate_limit_gate.py "$BUDGET" delegation --provider <new-provider> --audit-log
```

If the gate returns `safe: false`, do not proceed. Diagnose using `.cache/rate-limit-audit.log` before retrying.

### Step 4 — Update Toolchain Reference

Update the toolchain reference file for the new provider in `docs/toolchain/`. If no reference file exists, create one following the format of an existing toolchain doc (e.g., `docs/toolchain/gh.md`). The file must include:

- Provider name and API endpoint pattern
- Known failure modes and workarounds
- Rate-limit tier details (requests/min, tokens/min)
- Any provider-specific authentication setup

### Step 5 — Full Test Suite + Agent File Validation

Run the full validation stack before declaring the migration complete:

```bash
# Full test suite (skip long-running integration tests for speed)
uv run pytest tests/ -x -m "not slow" -q

# Agent file compliance
uv run python scripts/validate_agent_files.py --all

# Confirm rate-limit gate writes cleanly to audit log
tail -20 .cache/rate-limit-audit.log
```

All checks must pass. Any failure is a blocking issue; do not start using the new provider in production sessions until the test suite is green.

---

## Migration Checklist

- [ ] Step 1: Provider profile exists in `data/rate-limit-profiles.yml`
- [ ] Step 2: `local-localhost` baseline passed
- [ ] Step 3: New provider gate returns `safe: true`
- [ ] Step 4: Toolchain reference updated in `docs/toolchain/`
- [ ] Step 5: Full test suite and agent file validation passed
- [ ] Commit migration changes following [Conventional Commits](../../CONTRIBUTING.md#commit-discipline)

---

## Governing References

- [MANIFESTO.md § 3 Local-Compute-First](../../MANIFESTO.md#3-local-compute-first) — platforms are infrastructure; portability is a structural requirement, not a nice-to-have
- [docs/research/ai-platform-lock-in-risks.md](../research/ai-platform-lock-in-risks.md) — research synthesis on vendor ToS volatility and lock-in mitigation
- [AGENTS.md § Pre-Delegation Rate-Limit Gate](../../AGENTS.md#pre-delegation-rate-limit-gate-sprint-18) — rate-limit gate infrastructure used in Steps 2 and 3
- [data/rate-limit-profiles.yml](../../data/rate-limit-profiles.yml) — provider profile registry
