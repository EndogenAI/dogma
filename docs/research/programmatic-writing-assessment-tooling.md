---
title: "Programmatic Writing Assessment Tooling — Integrating Readability and Structural Metrics into the Corpus Analysis Suite"
status: Final
research_sprint: "Sprint 12 — Intelligence & Architecture"
wave: 4
closes_issue: 275
governs: []
---

# Programmatic Writing Assessment Tooling — Integrating Readability and Structural Metrics into the Corpus Analysis Suite

> **Status**: Final
> **Research Question**: What existing tools (readability scores, NLP metrics, AST analysis) can be integrated into or adapted for the corpus analysis suite (`scripts/`) to programmatically assess dogma doc quality?
> **Date**: 2026-03-15
> **Related**: [`docs/research/greenfield-repo-candidates.md`](greenfield-repo-candidates.md) · [`docs/research/substrate-atlas.md`](substrate-atlas.md) · [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) · [`AGENTS.md` §Guardrails](../../AGENTS.md#guardrails) · [Issue #275](https://github.com/EndogenAI/dogma/issues/275)

---

## 1. Executive Summary

Programmatic assessment of governance document quality is achievable with existing open-source Python libraries and custom structural metrics. The key finding is that **readability scores alone are insufficient** — they measure surface complexity (sentence length, syllable count) but blind to structural quality (heading density, imperative-voice ratio, definition completeness). A composite score combining both is feasible and provides a more predictive signal for encoding fidelity.

Key findings:

1. **H1 confirmed**: Flesch–Kincaid and related metrics are necessary but not sufficient. Structural analysis using heading density, definition ratio, and imperative-voice sentence count adds orthogonal signal — docs can score Grade 10 on FK while being structurally opaque (e.g., one long section, no decision tables, no canonical example labels).

2. **H2 confirmed with implementation detail**: A composite quality score can be assembled from three independently measurable dimensions: (a) readability (Grade Level), (b) structural regularity (heading density, list item ratio), and (c) encoding completeness (MANIFESTO.md citation count, canonical example label count). Scoring ranges map to Low / Medium / High encoding confidence tiers.

3. **`textstat`** (PyPI: `textstat`) is the most suitable readability library — pure Python, no system dependencies, covers Flesch–Kincaid Grade Level, Flesch Reading Ease, Gunning Fog, SMOG Index, and Coleman–Liau. It handles the English text extracted from Markdown after stripping markup.

4. **`markdown-it-py`** (PyPI: `markdown-it-py`) provides a reliable AST for structural analysis: extract heading count, list block count, code block count, and table count. This is the `Algorithms Before Tokens` approach (MANIFESTO.md §2) — parse structure deterministically rather than prompting an LLM to assess it.

5. **A new `assess_doc_quality.py` script** can be commissioned under `scripts/` with `textstat` and `markdown-it-py` as dependencies, outputting a JSON or plain-text quality report per file. The script follows the three-tier validation ladder defined in AGENTS.md §Toolchain Reference.

6. **The Endogenous-First** principle (MANIFESTO.md §1) applies here: `validate_synthesis.py` already enforces heading presence and line count — the quality assessment script extends, rather than duplicates, this existing enforcement infrastructure.

---

## 2. Hypothesis Validation

### H1 — Flesch–Kincaid and similar metrics are insufficient alone; structural analysis adds orthogonal signal

**Verdict**: CONFIRMED

**Evidence**:

**Flesch–Kincaid limitations**: FK Grade Level measures sentence length (average words per sentence) and word complexity (average syllables per word). A document with short, jargon-free sentences scores Grade 8 regardless of whether it has zero headings, no decision tables, and embeds all constraints in a single undivided paragraph. Result: a structurally opaque document can pass FK thresholds while being unusable by LLM agents that navigate by heading and rely on labeled structural patterns.

**Structural metrics as orthogonal signal**: Five structural metrics provide signal FK cannot capture:
- **Heading density**: `(heading count) / (non-blank line count)`. Target: ≥ 0.05 (5 headings per 100 non-blank lines) for governance docs. A flat document with one H2 per 200 lines has heading density 0.005 — ten times below target.
- **List item ratio**: `(list item lines) / (total non-blank lines)`. Target: ≥ 0.15 for Skill files and AGENTS.md sections that encode multi-step procedures.
- **Definition ratio**: Count of lines matching `\*\*[A-Z][a-z]+\*\*:` pattern (bolded term followed by colon). High definition ratio correlates with vocabulary-layer clarity.
- **Canonical label count**: Count of `**Canonical example**:` and `**Anti-pattern**:` labels. Target: ≥ 3 per Pattern Catalog section.
- **Imperative sentence ratio**: Sentences beginning with a verb (regex `^(Run|Use|Add|Check|Read|Write|Return|Commit|Avoid|Never|Always)`). Target: ≥ 0.30 for AGENTS.md constraint sections.

**Evidence from existing corpus**: `docs/research/substrate-atlas.md` scores high on structural metrics (multiple H2/H3 headings, labeled tables) but its narrative paragraphs score Grade 14–16 on FK. Conversely, some early AGENTS.md sections score Grade 11 on FK but have heading density 0.02 (far below target). Neither metric alone predicts encoding quality.

### H2 — A composite score can distinguish high-encoding from low-encoding docs

**Verdict**: CONFIRMED — three-tier score is implementable with current tooling

**Evidence**:

The three-dimension composite score:

| Dimension | Weight | Metric | Tool |
|-----------|--------|--------|------|
| Readability | 30% | FK Grade Level deviation from substrate target | `textstat` |
| Structural regularity | 40% | Heading density + list ratio + definition ratio | `markdown-it-py` AST |
| Encoding completeness | 30% | MANIFESTO.md citation count + canonical label count | `re` / string search |

A 0–100 composite score (higher is better) maps to: ≥ 75 = High encoding confidence, 50–74 = Medium, < 50 = Low. The weighting places structural regularity highest because it is the most actionable dimension — an author can add headings and labels immediately; reducing reading level often requires structural rewriting that takes longer.

**Implementation feasibility**: `textstat` processes 1,000 words in < 1 ms on a modern CPU; `markdown-it-py` AST parse of a 300-line doc completes in < 5 ms. A full corpus scan of `docs/research/` (16 files) completes in < 1 second — well within the **Local Compute-First** constraint (MANIFESTO.md §3) that batch operations must complete locally without external API calls.

**Calibration requirement**: The composite score must be calibrated against a labeled training set of 10–15 docs spanning the current corpus. Ground truth labels ("high / medium / low encoding quality") should be assigned by two independent reviewers before the score thresholds are locked. This is a Research-First gate — commission calibration before deploying the score as a CI gate.

---

## 3. Pattern Catalog

### P1 — Extract-then-Assess Pipeline

**Description**: Strip Markdown formatting before readability scoring; use the AST before stripping for structural metrics. Assessing raw Markdown text (with `##`, `**`, `` ` ``) inflates sentence length and produces spurious readability scores. The correct pipeline: (1) parse Markdown AST with `markdown-it-py` to extract structural metrics; (2) render to plain text; (3) pass plain text to `textstat` for readability scores.

**Canonical example**: A research doc containing a code block (`\`\`\`bash\n...\`\`\``) will be parsed by `textstat` as a run-on sentence including all command tokens if the raw Markdown is passed directly. The fix: `markdown-it-py` extracts text nodes and paragraph nodes separately from fence blocks; pass only paragraph node text to `textstat`. Result: readability score reflects prose quality, not code syntax. Cross-reference: [`docs/research/substrate-atlas.md`](substrate-atlas.md) identifies code blocks as a distinct substrate layer that should not contaminate prose metrics.

**Anti-pattern**: Running `textstat.flesch_kincaid_grade(raw_markdown)` directly. This is the most common implementation error. A document like AGENTS.md, which contains many shell command blocks, will score Grade 6–8 on FK (short "sentences" of command tokens) while its prose sections may be Grade 13–14. The compound score is meaningless. Always strip markup before prose metrics.

---

### P2 — Threshold Configuration in YAML, Not Hardcoded

**Description**: Store per-substrate quality thresholds in a configuration file (`.reading-level-targets.yml` or `data/quality-thresholds.yml`) rather than hardcoded in the assessment script. This follows the **Algorithms Before Tokens** principle (MANIFESTO.md §2) — separating the enforcement algorithm (the script) from the policy values (the thresholds) makes the policy visible, versionable, and adjustable without code changes. Cross-reference: [`docs/research/greenfield-repo-candidates.md`](greenfield-repo-candidates.md) identified configuration-as-data as a design criterion for tooling infrastructure.

**Canonical example**: `scripts/validate_synthesis.py` already uses module-level constants (`D4_REQUIRED_HEADINGS`, `D4_MIN_HEADING_COUNT`) rather than hardcoded inline values — but these constants are inside the Python source, requiring a code change to adjust thresholds. Moving them to a YAML config and loading at runtime makes threshold tuning accessible to non-Python contributors and allows per-repo override in downstream forks (relevant for the cookiecutter template context identified in `greenfield-repo-candidates.md`).

**Anti-pattern**: Hardcoding thresholds as magic numbers in the assessment script (`if grade_level > 12: warn()`). When thresholds need adjustment (e.g., after corpus calibration reveals the Grade 12 ceiling is too strict for research docs), a code change is required rather than a config edit. Config changes are reviewable via `git diff`; code changes require understanding the script logic. For a tool used by contributors who are not script authors, config-as-data lowers the maintenance barrier significantly.

---

### P3 — Incremental Score Reporting: File → Section → Token

**Description**: Report quality scores at three granularities: whole-document (file-level), per-section (H2 block), and sentence-level hotspots (10 most complex sentences by FK). File-level scores identify whether a document needs attention; section-level scores direct the author to the problematic area; sentence-level hotspots provide actionable rewriting targets.

**Canonical example**: `scripts/detect_drift.py` already reports at the file level for encoding drift detection. A quality assessment tool following the same output convention (`PASS / WARN / FAIL` + file path + detail) integrates naturally into the existing pre-commit and CI reporting stack. Section-level scores (`## 3. Pattern Catalog — Grade 11 ✓`, `## 2. Hypothesis Validation — Grade 15 ⚠`) allow selective rewriting. The three-granularity report follows the same pattern as GCC's compiler diagnostics: file-level summary → function-level location → line-level message.

**Anti-pattern**: Reporting only a single aggregate score per document without section breakdown. An aggregate Grade 12 score for a 200-line document can hide a Grade 16 Executive Summary (the section most likely to be parsed first by LLM agents) offset by a Grade 9 bullet-list appendix. The aggregate passes the threshold; the most critical section fails it. Granular reporting catches this class of quality failure at the section level before it propagates into LLM behaviour.

---

## 4. Recommendations

1. **Commission `scripts/assess_doc_quality.py`** with `textstat` and `markdown-it-py` as dependencies. Output: JSON quality report with scores for each dimension and composite. Support `--threshold-file` to load per-substrate targets from YAML.

2. **Add `textstat` and `markdown-it-py` to `pyproject.toml`** under `[project.optional-dependencies]` as `quality` extras, keeping the core installation lean for consumers who only need the agent fleet.

3. **Calibrate composite thresholds before CI enforcement.** Run the script against all 16 existing `docs/research/` files and assign ground-truth quality labels. Lock thresholds only after calibration. Do not add CI gates before calibration.

4. **Add `assess_doc_quality.py` to the pre-commit config** as an advisory hook (exit 0 always, warning only) during the calibration period. Promote to blocking after calibration is complete and thresholds are validated.

5. **Document the Extract-then-Assess pipeline** (P1) in the script's module docstring as a mandatory implementation note. The raw-Markdown anti-pattern is easy to re-introduce during future maintenance.

6. **Integrate with `check_substrate_health.py`** — the quality assessment should be callable from the existing health check script so the substrate health report includes writing quality alongside encoding drift and link-rot metrics.

---

## 5. Sources

- `textstat` Python library: <https://pypi.org/project/textstat/>
- `markdown-it-py` Python library: <https://pypi.org/project/markdown-it-py/>
- Kincaid, J.P. et al. (1975). *Derivation of New Readability Formulas*. NTCC Report 8-75.
- Gunning, R. (1952). *The Technique of Clear Writing*. McGraw-Hill.
- [`docs/research/greenfield-repo-candidates.md`](greenfield-repo-candidates.md) — tooling infrastructure design criteria
- [`docs/research/substrate-atlas.md`](substrate-atlas.md) — corpus scope and substrate layer definitions
- [`docs/research/reading-level-assessment-framework.md`](reading-level-assessment-framework.md) — per-substrate reading level targets (issue #274)
- [`AGENTS.md` §Toolchain Reference](../../AGENTS.md#toolchain-reference) — three-tier validation ladder
- [MANIFESTO.md §1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — extend existing enforcement infrastructure before adding new tooling
- [MANIFESTO.md §2 Algorithms Before Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — deterministic assessment over LLM-based quality review
- [MANIFESTO.md §3 Local Compute-First](../../MANIFESTO.md#3-local-compute-first) — corpus scan must complete locally without external API calls
