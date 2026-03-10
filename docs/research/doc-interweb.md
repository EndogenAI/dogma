---
title: "Programmatic Documentation Interlinking"
status: Final
---

# Programmatic Documentation Interlinking

How can we programmatically weave bidirectional inline links across the doc corpus — a
citation interweb where every concept links to its canonical definition and every canonical
definition links back to its applications?

Related issue: #84

---

## 1. Executive Summary

The endogenic corpus currently has manually maintained cross-references: agent files cite
`../../AGENTS.md`, guides cite each other, and research docs cite MANIFESTO.md. This
interlinking is inconsistent — some docs are heavily cross-referenced, others (especially
mid-tier guides and older research docs) contain concept names that are never linked. The
result is a substrate that is structurally connected in principle but navigationally opaque
in practice: a reader cannot follow "Endogenous-First" from a research doc to its canonical
definition and back out to applications without knowing the corpus layout.

This synthesis validates three design decisions for a `scripts/weave_links.py` tool that
programmatically injects Markdown links for registered concept names across the corpus. All
three hypotheses are confirmed. The approach is grounded in the **Documentation-First**
principle from `../../AGENTS.md`: every change to a workflow, agent, or script must be
accompanied by clear documentation — a stronger requirement than documentation alone, it
implies the documentation itself is a first-class artifact that warrants the same tooling
investment as scripts.

The `data/` directory already contains `labels.yml` as a YAML-registry precedent. The weave
tool follows this pattern with `data/link_registry.yml`.

---

## 2. Hypothesis Validation

### Q1 — Is YAML-registry-driven weaving the right approach vs inline HTML annotations vs frontmatter?

**Candidate approaches**:
1. **YAML registry** (`data/link_registry.yml`) — central config mapping concept names to
   canonical source URLs; the script reads it and injects links wherever the concept name
   appears unlinked.
2. **Inline HTML annotations** — authors tag concept names with `<span data-concept="...">` or
   similar; the script reads these tags and injects links.
3. **Per-file frontmatter** — each doc declares its concept-to-link mapping in its own YAML
   frontmatter block.

**Endogenous evidence**:
- `data/labels.yml` establishes the pattern: a single YAML file at `data/` drives a script
  (`scripts/seed_labels.py`) that applies repo-wide configuration. YAML registry follows
  directly from this precedent without introducing a new pattern.
- Inline HTML annotations require authors to manually mark up every occurrence of a concept
  as they write. This front-loads cognitive overhead onto document authors and produces
  non-standard Markdown that breaks plain-text reading and GitHub rendering.
- Per-file frontmatter is per-document, not cross-document: it cannot express "whenever
  'Endogenous-First' appears anywhere in the corpus, link it to this target." It also
  duplicates the mapping across every file that mentions the concept — violating DRY and
  making registry updates an N-file operation.
- The `../../AGENTS.md` §Documentation-First principle requires every change to workflows
  be accompanied by documentation. A YAML registry makes the complete concept → canonical
  link graph inspectable, reviewable in PRs, and auditable by CI — consistent with the
  Documentation-First requirement applied to documentation tooling itself.
- `scripts/audit_provenance.py` already demonstrates that YAML-based configuration driving
  file-modification scripts is the repo's established pattern. `weave_links.py` will follow
  the same structure: read registry → scan corpus → apply changes.

> **Verdict Q1: CONFIRMED.** YAML registry at `data/link_registry.yml` is the correct
> approach. It matches the `data/labels.yml` precedent, is reviewable in PRs, and
> decouples concept-to-link mapping from document authoring.

---

### Q2 — Can idempotency be guaranteed by checking for existing Markdown links before injection?

**The idempotency risk**: Running `weave_links.py` twice should produce no diff on the second
run. Without a guard, repeated injection wraps already-linked text in additional link syntax,
producing `[[text](URL)](URL)` nesting.

**Proposed mechanism**: Before injecting a link for concept `C` pointing to target `T`,
scan the surrounding context for the regex pattern `\[([^\]]*)\]\([^)]*\)`. If the target
text is already wrapped in Markdown link syntax (any destination), skip injection.

**Endogenous evidence**:
- `scripts/audit_provenance.py` demonstrates precedent for regex-based text scanning:
  `_HEADING_RE = re.compile(r"^#{2,3}\s+(.+)$", re.MULTILINE)` — the same regex approach
  is appropriate for link-detection. No YAML parser or AST is needed.
- The check is conservative by design: if a concept name is already linked to *any* URL
  (not just the registry target), skip injection. This prevents overriding intentional
  custom links — the "existing link wins" rule is safer than a URL-equality check.
- For concepts that appear multiple times in a document, inject the link only on the **first
  occurrence per section** (delimited by `##` headings). Subsequent occurrences in the same
  section are likely redundant. This is the same approach used in LaTeX `\autoref` and in
  Wikipedia's manual of style for inline links.
- Idempotency can be tested mechanically: run the script twice on a fixture file and
  assert `file_v2 == file_v3`. This test is required by `../../AGENTS.md` §Testing-First.

> **Verdict Q2: CONFIRMED.** Idempotency is guaranteed by: (a) existing-link regex check
> before injection, (b) first-occurrence-per-section rule, and (c) a mandatory idempotency
> test in the test suite. The "existing link wins" rule prevents interference with intentional
> custom cross-references.

---

### Q3 — What are the ≥5 seed concepts that bootstrap `link_registry.yml`?

The registry must start with concepts that appear frequently, are inconsistently linked
today, and have unambiguous canonical sources in the existing corpus.

**Proposed seed concepts**:

| ID | Concept name | Canonical target | Appears in |
|----|-------------|-----------------|------------|
| C1 | `Endogenous-First` | `../../MANIFESTO.md#endogenous-first` | Everywhere |
| C2 | `Algorithms Before Tokens` | `../../MANIFESTO.md#algorithms-before-tokens` | AGENTS.md, research docs |
| C3 | `Programmatic-First` | `../../AGENTS.md#programmatic-first-principle` | Guides, agent files |
| C4 | `D4 synthesis` | `../../docs/guides/deep-research.md` | Research docs, scratchpads |
| C5 | `Conventional Commits` | `../../CONTRIBUTING.md#commit-discipline` | Agent files, AGENTS.md |
| C6 | `Documentation-First` | `../../AGENTS.md#documentation-first` | Agent files, AGENTS.md |

C1 and C2 anchor the axiom layer — they are foundational concepts that appear in almost
every research doc but are rarely hyperlinked. C3 and C6 are operational principles in
`AGENTS.md` that are heavily referenced but inconsistently linked. C4 normalizes a term of
art ("D4 synthesis") that appears in scratchpads and agent files. C5 ensures Conventional
Commits references are consistently linked to the commit discipline guide.

> **Verdict Q3: CONFIRMED.** Six seed concepts (exceeding the ≥5 requirement) are
> identified, all with verifiable canonical targets in the existing corpus. Bootstrap
> `data/link_registry.yml` with these six; extend via PR as new concepts emerge.

---

## 3. Pattern Catalog

### Pattern 1 — YAML Registry as Single Source of Truth

Store all concept → canonical link mappings in `data/link_registry.yml`, formatted as:

```yaml
concepts:
  - concept: "Endogenous-First"
    aliases: ["endogenous-first", "Endogenous First"]
    canonical_source: "MANIFESTO.md#endogenous-first"
    scopes: ["docs/", ".github/agents/", "AGENTS.md"]
  - concept: "Algorithms Before Tokens"
    aliases: ["algorithms-before-tokens"]
    canonical_source: "MANIFESTO.md#algorithms-before-tokens"
    scopes: ["docs/", ".github/agents/"]
```

The `scopes` field restricts injection to relevant paths. Injecting "Endogenous-First" links
into MANIFESTO.md itself would be self-referential and wrong — scope filtering prevents this.

**Reuse anchor**: mirrors `data/labels.yml` consumed by `scripts/seed_labels.py`.

---

### Pattern 2 — Idempotency Guard (Existing Link Detection)

Before injecting a link, check whether the target text span is already wrapped in a Markdown
link using:

```python
import re
_LINK_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')

def is_already_linked(text: str, concept_start: int) -> bool:
    for m in _LINK_RE.finditer(text):
        if m.start() <= concept_start <= m.end():
            return True
    return False
```

This is the critical idempotency guard. It addresses the risk described in Q2: without this
check, repeated script runs produce nested link syntax. The guard must be the first check
in the injection pipeline, before any write operation.

---

### Pattern 3 — First-Occurrence-Per-Section Rule

For each `##` section, inject a link for a concept on its first occurrence only. Track
concept-name → last-injected-section-index during the scan:

```python
seen_in_section: dict[str, int] = {}  # concept_name -> section_index

if seen_in_section.get(concept_name) == current_section:
    continue  # already linked in this section
seen_in_section[concept_name] = current_section
```

This prevents repeated links for concepts mentioned multiple times in one section (e.g.,
"Endogenous-First" in a section that opens with the principle and re-references it later).
It also keeps the output readable and avoids over-linking, which degrades the reading
experience.

---

### Pattern 4 — Dry-Run Mode with Diff Output

Every write operation in `weave_links.py` must be guarded by a `--dry-run / -n` flag that
prints a unified diff of what would change without modifying any file. The diff surface area
should be printed to stdout for review. This satisfies the `../../AGENTS.md` guidance that
scripts with `--dry-run` guards are appropriate for tasks that "could break something if done
wrong." Interlinking is such a task — a registry misconfiguration could inject wrong links
across hundreds of files.

**Acceptance test**: `uv run python scripts/weave_links.py --dry-run` exits 0 and produces
identical output on two consecutive runs (pure read, no writes).

---

### Pattern 5 — Audit Integration for Broken Links

After `weave_links.py` injects links, `scripts/check_doc_links.py` (already in `scripts/`)
should be run to verify no injected links are broken. This closes the feedback loop:
weave → audit → report. The sequence should be encoded as a CI step so link injection
regressions are caught automatically, not manually.

**Reuse anchor**: `scripts/check_doc_links.py` already exists — no new script needed for
the audit step. Wire it as a post-weave CI check.

---

## 4. Recommendations

### R1 — Create `data/link_registry.yml` with 6 seed concepts

**Rationale**: `../../AGENTS.md` §Documentation-First states "every change to a workflow,
agent, or script must be accompanied by clear documentation." The inverse is equally true:
documentation tooling should meet the same quality bar as scripts. A YAML registry is the
documentation substrate equivalent of a migration schema: it is the single authoritative
record of cross-reference intent, reviewable in PRs and auditable by CI.

Bootstrap with the 6 seed concepts from Q3. Use `scopes` filtering to prevent self-referential
injection. Commit alongside the first `weave_links.py` implementation.

---

### R2 — Implement `scripts/weave_links.py` with `--dry-run`, idempotency guard, and `--scope`

**Rationale**: `../../AGENTS.md` §Programmatic-First Principle requires scripting any task
performed more than twice interactively. Manual cross-reference maintenance in a 157-file
corpus is already a repeated task — the third time anyone adds a link to "Endogenous-First"
across docs should be the script, not a human. The `--dry-run` flag is non-negotiable for
a file-modifying script with broad corpus scope.

**Minimum viable CLI**:
```bash
uv run python scripts/weave_links.py [--dry-run] [--scope <glob>] [--registry data/link_registry.yml]
```

Extend `audit_provenance.py`'s `Path.glob` + `read_text` corpus-read pattern as the
implementation foundation.

---

### R3 — Tests must cover idempotency, scope filtering, and alias matching

**Rationale**: `../../AGENTS.md` §Testing-First Requirement mandates tests for every
committed script. Three non-negotiable test cases:

1. **Idempotency test**: apply weaving to a fixture file twice; assert `run1_output == run2_output`.
2. **Scope filter test**: a concept with `scopes: ["docs/"]` must not inject into `AGENTS.md`
   even if the concept name appears there.
3. **Alias test**: a concept with `aliases: ["endogenous-first"]` must match both
   `Endogenous-First` and `endogenous-first` in documents.

Mark all file-modification tests with `@pytest.mark.io` per `pyproject.toml` conventions.

---

## 5. Sources

- `../../AGENTS.md` — §Documentation-First (governing principle for this work),
  §Programmatic-First Principle, §Testing-First Requirement
- `../../MANIFESTO.md` — core axioms: Endogenous-First, Algorithms Before Tokens,
  Local Compute-First
- `../../data/labels.yml` — YAML registry pattern precedent (consumed by `seed_labels.py`)
- `../../scripts/audit_provenance.py` — corpus-read pattern, regex-based text scanning,
  YAML frontmatter extraction (all reusable in `weave_links.py`)
- `../../scripts/check_doc_links.py` — existing link audit script; wired as post-weave CI check
- `../../docs/guides/agents.md` — example doc with inconsistent cross-referencing; primary
  beneficiary of interlinking (manually references AGENTS.md conventions but rarely hyperlinks)
- Wikipedia Manual of Style — "first occurrence per section" inline linking convention
- Corpus size: 124 `docs/**/*.md` + 33 `.github/agents/*.agent.md` = ≈157 text files
  (verified via `find` on 2026-03-08)
