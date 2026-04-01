# Deprecated Scripts

This file tracks scripts that have been deprecated and replaced. Deprecated scripts remain in place with a deprecation warning to avoid breaking existing workflows, but should not be used in new work.

## Format

Each entry specifies:
- **Script**: The deprecated script name
- **Status**: DEPRECATED
- **Reason**: Why it was deprecated
- **Replacement**: The new script or approach to use
- **Deprecated on**: Date (YYYY-MM-DD)

---

## emit_otel_genai_spans.py

- **Status**: DEPRECATED
- **Reason**: Violated `action_target` naming convention (issue #529) — had "genai" qualifier between action and target
- **Replacement**: `emit_genai_spans.py`
- **Migration**: All imports and references updated in Sprint 22
- **Deprecated on**: 2026-04-01
