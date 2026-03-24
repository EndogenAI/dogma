# Recommendations Provenance Schema

**Version**: 1.0  
**Governs**: All `status: Final` D4 synthesis documents in `docs/research/`  
**Validated by**: `scripts/validate_synthesis.py`

---

## Purpose

The `recommendations:` frontmatter block links each recommendation in a synthesis
document's `## Recommendations` section to its corresponding GitHub issue and records
the current implementation status. This enables provenance tracing: for any
recommendation, you can answer "was this adopted?", "which issue tracks it?", and
"why was it rejected or deferred?" without reading through issue threads manually.

This schema is part of the Recommendations Provenance system introduced in Sprint 23
(issue #406), implementing the [Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle)
from `AGENTS.md`: provenance data that was previously inferred interactively from
issue comments is now encoded as structured frontmatter and enforced by CI.

---

## Schema

Each entry in the `recommendations:` list maps to one recommendation in the
`## Recommendations` section of the same document.

```yaml
recommendations:
  - id: rec-<doc-slug>-001          # unique, stable ID — never change after first commit
    title: "Short recommendation title"  # human-readable label; should match the ## Recommendations entry
    status: adopted                  # see Status Taxonomy below
    linked_issue: 401                # GitHub issue number (integer); strongly preferred, warning-only if absent for non-deferred entries
    decision_ref: ""                 # optional URL to issue comment where a rejection/deferral was logged
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **Always** | Stable unique identifier. Format: `rec-<doc-slug>-NNN` (three-digit zero-padded integer). Never rename after first commit — it is used as a stable reference in cross-doc links. |
| `title` | string | **Always** | Human-readable label matching the corresponding `## Recommendations` section entry. Keep it under 80 characters. |
| `status` | string | **Always** | One of the 7 status values defined below. |
| `linked_issue` | integer | **Strongly preferred** | GitHub issue number (not URL). Missing values produce a warning for non-`deferred` entries; `deferred` entries may omit it when no issue exists yet. |
| `decision_ref` | string | **Conditional** | URL to the issue comment or discussion thread where a rejection or deferral was logged. Required when `status` is `rejected` or `not-accepted`. |

---

## Status Taxonomy

Seven valid status values, ordered from open to closed:

| Status | Meaning | `decision_ref` required? |
|--------|---------|--------------------------|
| `accepted` | Recommendation accepted as stated; implementation not yet started. | No |
| `accepted-for-adoption` | Accepted with planned customization; work in progress. | No |
| `adopted` | A customized version of the recommendation is encoded in project practices. | No |
| `completed` | Recommended action was fully implemented and verified against acceptance criteria. | No |
| `rejected` | Decision made not to implement; `decision_ref` must point to the issue comment logging that decision. | **Yes** |
| `not-accepted` | Softer rejection — often "not now" or "not in this form"; `decision_ref` required. | **Yes** |
| `deferred` | Acknowledged but parked; `linked_issue` is strongly preferred so it is not lost. | No |

### Status Progression

A typical recommendation moves through statuses like this:

```
accepted → accepted-for-adoption → adopted / completed
         ↘ not-accepted / rejected / deferred
```

Once a recommendation reaches `completed`, `rejected`, or `not-accepted`, its status
should not change (these are terminal states). `adopted` is semi-terminal — it may be
revisited if the practice is later superseded.

---

## Placement

The `recommendations:` block goes in the YAML frontmatter of the synthesis document,
alongside existing keys (`title`, `status`, `date`, etc.).

```yaml
---
title: "Agent Fleet Design Patterns — Research Synthesis"
status: Final
date: 2026-03-15
closes_issue: 289
recommendations:
  - id: rec-agent-fleet-design-patterns-001
    title: "Adopt L0–L3 maturity model for fleet progression"
    status: adopted
    linked_issue: 291
    decision_ref: ""
  - id: rec-agent-fleet-design-patterns-002
    title: "Encode phase-gate sequence in AGENTS.md"
    status: completed
    linked_issue: 292
    decision_ref: ""
  - id: rec-agent-fleet-design-patterns-003
    title: "Reject agent-per-task spawning in favor of role-reuse"
    status: rejected
    linked_issue: 293
    decision_ref: "https://github.com/EndogenAI/dogma/issues/293#issuecomment-1234567890"
---
```

---

## Validation Rules

`validate_synthesis.py` enforces the following rules at the recommendations
provenance check. That check hard-enforces only for D4 synthesis docs under
`docs/research/`, excluding `docs/research/sources/**` and `OPEN_RESEARCH.md`:

### Hard Failures (exit code 1)

1. The YAML frontmatter is malformed in a way that prevents parsing the
  `recommendations:` block.
2. A `status: Final` **synthesis doc** is missing the `recommendations:` key entirely.
3. The `recommendations:` value exists but is not a YAML list.
4. Any `recommendations:` item is not a mapping (dict).
5. Any entry is missing or has an empty `id`, `status`, or `title` field.
6. Any entry has a `status` value outside the validator's canonical set:
  `accepted`, `accepted-for-adoption`, `adopted`, `completed`, `rejected`,
  `not-accepted`, `deferred`.
7. Any entry with `status: rejected` or `status: not-accepted` has no
  `decision_ref` (absent or empty string).

### Warnings (non-blocking, exit code 0)

8. Any non-`deferred` entry has no `linked_issue` — the recommendation may be lost
   without an issue to track it.
9. A `status: Final` file outside that D4 set (for example `OPEN_RESEARCH.md`) is
  missing `recommendations:` — logged as a warning but does not fail validation.

### How Synthesis Docs Are Identified

D4 synthesis docs for this check are files under `docs/research/` whose relative path
does not begin with `sources/` and whose filename is not `OPEN_RESEARCH.md`.

D3 per-source synthesis documents under `docs/research/sources/` are still validated
by `validate_synthesis.py` generally; they only bypass the `recommendations:` check,
because D3 docs describe individual external sources rather than project-level
recommendations.

---

## Adding Recommendations to an Existing Doc

1. Open the synthesis doc.
2. Count recommendation items in the `## Recommendations` section.
3. For each item, add an entry to the `recommendations:` list in frontmatter.
4. Assign a stable `id` using the doc slug + three-digit counter.
5. Look up the corresponding GitHub issue and set `linked_issue`.
6. Set the current `status` honestly — don't guess.
7. Run `uv run python scripts/validate_synthesis.py <doc>` to confirm the block is valid.
8. Commit with `docs(research): add recommendations provenance to <doc-slug>`.

---

## Related

- [`AGENTS.md` § Programmatic-First Principle](../../AGENTS.md#programmatic-first-principle)
- [`scripts/validate_synthesis.py`](../../scripts/validate_synthesis.py) — CI enforcement
- [Issue #406 — Recommendation Provenance](https://github.com/EndogenAI/dogma/issues/406)
