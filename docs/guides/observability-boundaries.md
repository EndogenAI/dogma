# Observability Boundaries for Session Cost Tracking

## Purpose

Define what token usage is observable from this repository's local substrate and what remains unobservable when model execution happens in managed external layers.

## Boundary Matrix

| Layer | Observable locally | Not observable locally | Why |
|---|---|---|---|
| Script runtime (repo-controlled) | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, model id, phase context when emitted by local instrumentation | Provider-internal retry behavior or hidden server-side token adjustments | We control span attributes and session-cost append path in local scripts |
| Local telemetry/logging substrate | `session_cost_log.json` rows, synthetic markers, read-time filtering (`exclude_synthetic`) | Data never emitted by scripts (for example editor-hosted requests) | Local file substrate only captures what local code writes |
| CLI orchestration layer | Command status, stderr warnings, CI/test outcomes | Per-request Copilot token counters from editor extension traffic | CLI has no per-request Copilot token metadata surface |
| VS Code Copilot Chat / editor extension layer | User-visible responses, coarse usage/limit signals exposed by product UI | Structured per-request token usage export usable by local scripts | Managed service boundary; no local API contract for per-request token export |
| GitHub Copilot SaaS/admin analytics | Entitlement and usage counters at account/org level (where provided by GitHub) | Local span parity for each editor request | Product analytics are aggregate/control-plane oriented, not local span telemetry |

## Runbook by Symptom

| Symptom | Likely boundary class | Next action |
|---|---|---|
| Expected script invocation produced no session-cost row | Observable | Check `scripts/emit_otel_genai_spans.py` warning logs; verify span has non-zero numeric `gen_ai.usage.*` attrs; rerun tests for bridge path |
| Warning: zero-token record skipped | Observable | Confirm whether this was a placeholder event; if intentional, log with explicit synthetic marker via `--synthetic` in `session_cost_log.py` |
| Copilot Chat usage appears in UI but no local token rows exist | Unobservable (managed layer) | Do not treat as logging failure; annotate as boundary limitation in session notes and use synthetic marker only if explicitly desired |
| Billing/entitlement dashboard differs from local totals | Cross-boundary | Compare local log scope (script-only) against managed scope (product-wide), then document scope mismatch in reporting |

## Synthetic Record Convention

Use synthetic rows only for explicit placeholders or boundary annotations. Zero-token rows without `synthetic=true` are rejected by design.

Example:

```bash
uv run python scripts/session_cost_log.py \
  --session main/example/2026-03-27 \
  --model gpt-5.3-codex \
  --tokens-in 0 \
  --tokens-out 0 \
  --phase "Boundary annotation" \
  --timestamp 2026-03-27T20:00:00Z \
  --synthetic
```

## References

- [scripts/session_cost_log.py](../../scripts/session_cost_log.py)
- [scripts/emit_otel_genai_spans.py](../../scripts/emit_otel_genai_spans.py)
- [scripts/instrument_agent_calls.py](../../scripts/instrument_agent_calls.py)
- [docs/guides/copilot-ecosystem-limits.md](copilot-ecosystem-limits.md)
- [GitHub Copilot usage and entitlements](https://docs.github.com/en/copilot/managing-copilot/monitoring-usage-and-entitlements/monitoring-your-copilot-usage-and-entitlements)
- [GitHub Copilot rate limits](https://docs.github.com/en/copilot/troubleshooting-github-copilot/rate-limits-for-github-copilot)
