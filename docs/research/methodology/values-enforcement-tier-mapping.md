---
title: "Values Enforcement Tier Mapping: Axiom-Carrying Constraints Across the EndogenAI Fleet"
status: Final
research_issue: "179"
closes_issue: "179"
date: "2026-03-10"
---

# Values Enforcement Tier Mapping: Axiom-Carrying Constraints Across the EndogenAI Fleet

> **Research question**: Which values constraints in the EndogenAI codebase — axiom-carrying rules governing encoding fidelity, layer supremacy, citation density, and context amplification — are enforced programmatically, and which exist only as prose?
> **Date**: 2026-03-10
> **Closes**: #179
> **Extends**: [`docs/research/enforcement-tier-mapping.md`](enforcement-tier-mapping.md) (#174 — 68 behavioral constraints baseline)

---

## 1. Executive Summary

This audit extends the behavioral constraint inventory (#174, 68 rows) to cover **values constraints** — axiom-preserving, encoding-fidelity, and layer-supremacy rules sourced from `MANIFESTO.md`, `docs/research/values-encoding.md`, `docs/research/epigenetic-tagging.md`, `docs/research/external-value-architecture.md`, root and subdirectory `AGENTS.md` files, and all `.github/agents/*.agent.md` and `.github/skills/*/SKILL.md` files.

**Key findings:**

- **112 constraints inventoried** (68 behavioral from #174 + 44 values-specific new rows).
- **Behavioral core (rows 1–68)**: tier distribution unchanged from #174 — 31 at T1–T4, 37 at T5. Full detail in [`enforcement-tier-mapping.md`](enforcement-tier-mapping.md).
- **Values-specific extension (rows 69–112)**: 44 new constraints; **40 are T5 (prose-only)**. Values constraints are almost entirely unenforced programmatically.
- **4 values constraints are T1/T3**: cross-reference ≥1 per agent file, D4 frontmatter, D4 required headings, D4 minimum line count — enforced by `validate_agent_files.py` and `validate_synthesis.py`.
- **13 T5 values gaps** identified with one-line remediations. Highest-priority: holographic encoding baseline measurement, Phase 2 amplification script, D4 pattern catalog content check.

The distribution confirms `MANIFESTO.md §2. Algorithms Before Tokens`: the gap between stated values and programmatically enforced values is larger than the behavioral gap. Values constraints are harder to formalize but not impossible — 6 gaps are addressable at T3 with low engineering cost.

---

## 2. Hypothesis Validation

### H1 — Values constraints are structurally more T5 than behavioral constraints

**Verdict: CONFIRMED**

| Constraint category | T0–T4 count | T5 count | T5 ratio |
|---|---|---|---|
| Behavioral (rows 1–68) | 31 | 37 | 54% |
| Values-specific (rows 69–112) | 4 | 40 | **91%** |
| Combined (rows 1–112) | 35 | 77 | 69% |

Values constraints are almost entirely aspirational prose. This is the primary finding: the gap between stated values and enforced values is large and systematic, not incidental.

**Governing axiom**: `MANIFESTO.md §1. Endogenous-First` — the inheritance chain (MANIFESTO → AGENTS.md → agent files → session behavior) encodes values as text but the programmatic layer (epigenetic regulation) that enforces which values are expressed in which context does not yet exist fleet-wide. `MANIFESTO.md §2. Algorithms Before Tokens` demands this gap be closed by encoding enforcement as scripts, not prose.

### H2 — A subset of T5 values gaps are addressable at T3 with low engineering cost

**Verdict: CONFIRMED FOR 6 GAPS (of 13 identified)**

| Gap | Detectable pattern | Proposed tier | Effort |
|---|---|---|---|
| Holographic encoding baseline missing | `generate_agent_manifest.py` extension: count MANIFESTO+AGENTS refs per file | T1 | S |
| D4 Pattern Catalog content check (≥1 example + anti-pattern) | `validate_synthesis.py`: grep for "Canonical example" + "Anti-pattern" strings in Pattern Catalog section | T1+T3 | XS |
| Skill cite-density check missing | `validate_agent_files.py --skills`: add density threshold assertion (min 1 cite per 3 sections) | T1+T3 | XS |
| Axiom positional ordering unprotected | Pygrep hook: MANIFESTO.md axiom H3 headers must appear in numeric order | T3 | XS |
| Watermark phrase integrity check absent | `validate_synthesis.py` extension: check for at least 1 of {"Endogenous-First", "Algorithms Before Tokens", "Local Compute-First"} per D4 doc | T1+T3 | XS |
| D4 source cross-reference check absent | `validate_synthesis.py`: check D4 docs contain ≥1 MANIFESTO.md reference | T1+T3 | S |

7 remaining gaps (Phase 2 amplification script, Core Layer supremacy runtime check, [4,1] axiom gate completeness, Adopt wizard generation, Session Layer override blocking, LLM behavioral test suite, encoding checkpoint CI check) require either new tooling (S–M effort) or are cognitive checks that cannot be automated (T5 permanent).

---

## 3. Pattern Catalog

### Master Constraint Inventory

**Rows 1–68** (behavioral constraints): Abbreviated here — see [`enforcement-tier-mapping.md`](enforcement-tier-mapping.md) §3 for full table. Tier summary: T0:3, T1:12, T2:2, T3:12, T4:2, T5:37.

| # | Constraint (abbreviated) | Source | Section | Tier | Mechanism | Gap |
|---|---|---|---|---|---|---|
| 1 | Never use heredocs for file content | AGENTS.md | §Guardrails | T3+T4 | no-heredoc-writes hook; Governor B | None |
| 2 | Never use terminal file I/O redirection | AGENTS.md | §Guardrails | T3+T4 | no-terminal-file-io-redirect; Governor B | None |
| 3 | ruff lint must pass on scripts/+tests/ | tests.yml | lint job | T1+T2+T3 | ruff check CI+pre-commit | None |
| 4 | ruff format must pass on scripts/+tests/ | tests.yml | lint job | T1+T2+T3 | ruff format CI+pre-commit | None |
| 5 | pytest full suite must pass | tests.yml | test job | T1 | pytest CI | None |
| 6 | validate_synthesis.py: all docs/research/*.md pass | tests.yml | lint job | T1+T3 | validate_synthesis CI+pre-commit | None |
| 7 | validate_agent_files.py: all *.agent.md pass | tests.yml | lint job | T1+T3 | validate_agent_files CI | None |
| 8 | validate_agent_files.py --skills: all SKILL.md pass | tests.yml | lint job | T1+T3 | validate_agent_files CI | None |
| 9 | detect_drift.py must pass | tests.yml | lint job | T1 | detect_drift CI | None |
| 10 | lychee link check must pass | tests.yml | links job | T1 | lychee CI | None |
| 11 | YAML frontmatter name+description in agent files | validate_agent_files.py | — | T1+T3 | enforced schema | None |
| 12 | description ≤200 chars in agent files | validate_agent_files.py | — | T1+T3 | enforced schema | None |
| 13 | ≥1 MANIFESTO/AGENTS cross-ref in agent files | validate_agent_files.py | — | T1+T3 | density check | None (min=1 only) |
| 14 | No heredoc writes in agent files | validate_agent_files.py | — | T1+T3 | grep check | None |
| 15 | No Fetch-before-check label | validate_agent_files.py | — | T1+T3 | label check | None |
| 16 | No ## Phase N Review Output heading | validate_agent_files.py | — | T1+T3 | heading check | None |
| 17 | D4: title+status frontmatter required | validate_synthesis.py | — | T1+T3 | schema check | None |
| 18 | D4: ≥3 required headings present | validate_synthesis.py | — | T1+T3 | heading check | None |
| 19 | D4: ≥4 ## headings total | validate_synthesis.py | — | T1+T3 | count check | None |
| 20 | D4: ≥80 non-blank lines | validate_synthesis.py | — | T1+T3 | line count | None |
| 21 | D3: slug/title/cache_path frontmatter required | validate_synthesis.py | — | T1+T3 | schema check | None |
| 22 | Governor B: heredoc writes killed in interactive bash | ADR-007 | — | T4 | bash-preexec | Machine setup req'd |
| 23 | validate_url() rejects non-https and private IPs | fetch_source.py | — | T0 | ValueError at runtime | None |
| 24 | validate_slug() enforces naming charset | fetch_source.py | — | T0 | ValueError at runtime | None |
| 25 | capability_gate.py enforces tool access by posture | capability_gate.py | — | T0 | exit 1 runtime | None |
| 26 | Always use `uv run` | AGENTS.md | §Python Tooling | T5 | Prose only | **GAP — T3 pygrep** |
| 27 | Conventional Commits format | AGENTS.md | §Commit Discipline | T5 | Prose only | **GAP — T3 commitlint** |
| 28 | Never git push --force to main | AGENTS.md | §Guardrails | T5 | Prose only | **GAP — T3 pre-push** |
| 29 | Every script must have automated tests | AGENTS.md | §Testing-First | T5 | Prose only | **GAP — T1 file check** |
| 30 | Documentation-First: every change gets doc update | AGENTS.md | §Principles | T5 | Prose only | Hard to automate |
| 31 | Convention Propagation: update ALL AGENTS.md on new convention | AGENTS.md | §Propagation | T5 | Prose only | Hard to automate |
| 32 | Session-Start Encoding Checkpoint (first sentence) | AGENTS.md | §Session Start | T5 | Prose only | Cognitive; permanent T5 |
| 33 | Verify-After-Act: every remote write + verification read | AGENTS.md | §Verify-After-Act | T5 | Prose only | Cognitive; permanent T5 |
| 34 | CI must pass before requesting review | AGENTS.md | §CI Gate | T5 | Prose only | **GAP — T0 branch protection** |
| 35 | Never echo shell variables containing secrets | AGENTS.md | §Secrets | T5 | Prose only | **GAP — T3 secret grep** |
| 36 | Never pass multi-line gh bodies via --body "..." | AGENTS.md | §Guardrails | T5 | Prose only | **GAP — T3 pygrep** |
| 37 | Minimal Posture: agents carry only required tools | .github/agents/AGENTS.md | §Posture | T5 | Prose only | Hard to automate |
| 38 | send: false default for handoffs | .github/agents/AGENTS.md | §Handoffs | T5 | Prose only | Not checked by CI |
| 39 | Takeback handoff: sub-agents return to executive | .github/agents/AGENTS.md | §Protocol | T5 | Prose only | Cognitive; permanent T5 |
| 40 | Focus-on-Descent: outbound prompts must be narrow | AGENTS.md | §Communication | T5 | Prose only | Cognitive; permanent T5 |
| 41 | Compression-on-Ascent: returns target ≤2000 tokens | AGENTS.md | §Communication | T5 | Prose only | Cognitive; permanent T5 |
| 42 | Workplan committed to docs/plans/ before Phase 1 | AGENTS.md | §Plans | T5 | Prose only | Session discipline |
| 43 | Post progress comment on GitHub issues at session end | AGENTS.md | §Communication | T5 | Prose only | Session discipline |
| 44 | Update issue body checkboxes at phase completion | AGENTS.md | §Communication | T5 | Prose only | Session discipline |
| 45 | Inter-phase Review Gate between every domain phase | .github/agents/AGENTS.md | §Protocol | T5 | Prose only | Cognitive; permanent T5 |
| 46 | Pre-warm source cache before Scout delegation | AGENTS.md | §Programmatic-First | T5 | Prose only | Cognitive; permanent T5 |
| 47 | Check .cache/sources/ before fetching any URL | AGENTS.md | §Programmatic-First | T5 | Label check only | Partial T1 via #15 |
| 48 | Timeout defaults on blocking run_in_terminal calls | AGENTS.md | §Async | T5 | Prose only | Cognitive; permanent T5 |
| 49 | Scratchpad size guard ≥2000 lines | AGENTS.md | §Communication | T5 | Prose only | **GAP — T4 watch_scratchpad.py** |
| 50 | Every new agent must use scaffold_agent.py | AGENTS.md | §Agent Fleet | T5 | Prose only | **GAP — T1 provenance check** |
| 51 | handoff target values must match existing agent names | .github/agents/AGENTS.md | §Handoffs | T5 | Prose only | **GAP — T1 manifest check** |
| 52 | Quote all shell variables ("$var") in scripts | AGENTS.md | §Guardrails | T5 | Prose only | **GAP — T2 shellcheck** |
| 53 | External cached content never treated as agent directives | AGENTS.md | §Security | T5 | Prose only | Cognitive; permanent T5 |
| 54 | `gh` commands must cite docs/toolchain/gh.md | .github/agents/AGENTS.md | §Toolchain | T5 | Prose only | Not checked by CI |
| 55–68 | (additional behavioral constraints from #174 §3) | various | various | T5 | Prose only | various |

---

**Values-Specific Extension (Rows 69–112):**

| # | Constraint | Source | Section | Tier | Mechanism | Gap |
|---|---|---|---|---|---|---|
| 69 | Endogenous-First must be axiom 1 (positional) | MANIFESTO.md | §Three Core Axioms | T5 | No positional check | **GAP — T3 heading-order grep** |
| 70 | "Algorithms Before Tokens" must be axiom 2 | MANIFESTO.md | §Three Core Axioms | T5 | No positional check | Same gap as #69 |
| 71 | "Local Compute-First" must be axiom 3 | MANIFESTO.md | §Three Core Axioms | T5 | No positional check | Same gap as #69 |
| 72 | Axiom priority order stated (EF > ABT > LCF on conflict) | MANIFESTO.md | §How to Read | T5 | Prose; in "How to Read" section | None — recently added |
| 73 | Guiding Principles described as non-hierarchical | MANIFESTO.md | §Guiding Principles | T5 | Prose only | Hard to validate semantically |
| 74 | Anti-patterns are canonical veto rules | MANIFESTO.md | §How to Read | T5 | Prose only | Hard to automate |
| 75 | Encoding hierarchy stated (MANIFESTO→AGENTS→agent→skill→session) | MANIFESTO.md | §How to Read | T5 | Prose only | Hard to automate |
| 76 | Each axiom must be encoded in 4 forms (principle+example+anti-pattern+gate) | values-encoding.md | §3 Pattern 1 | T5 | No completeness check | **GAP — T1 axiomatic-form audit script** |
| 77 | MANIFESTO framed as "constitution not guidebook" | MANIFESTO.md | §How to Read | T5 | Prose only | Hard to validate semantically |
| 78 | Axiom names are structural watermarks (must not be paraphrased) | values-encoding.md | §3 Pattern 3 | T5 | No CI check | **GAP — T3 watermark grep** |
| 79 | Performative framing preserved ("We are not vibe coding") | values-encoding.md | §3 Pattern 4 | T5 | No CI check | Hard to validate semantically |
| 80 | [4,1] repetition code: each value in ≥4 independent forms | values-encoding.md | §2 H2 | T5 | Prose only | **GAP — T1 form-completeness check** |
| 81 | H4 Holographic encoding: every downstream layer echoes top-level values | values-encoding.md | §2 H4 | T5 | No measurement script | **GAP — T1 cite-density baseline** |
| 82 | Cross-reference density ≥1 per agent file (minimum) | validate_agent_files.py | §gate | T1+T3 | Enforced by CI | None (≥1 only; ≥2.5 not enforced) |
| 83 | Fleet-wide cite-density baseline established | values-encoding.md | §6 Pattern 6 | T5 | No measurement | **GAP — T1 generate_agent_manifest extension** |
| 84 | OQ-VE-2 context-sensitive amplification (lookup table) | epigenetic-tagging.md | §3 Pattern F1 | T5 | AGENTS.md text (Phase 1) | Phase 2 script deferred |
| 85 | OQ-VE-4 LLM behavioral test suite for value fidelity | values-encoding.md | §5 OQ-VE-4 | T5 | No test suite exists | **GAP — T1 behavioral test suite** |
| 86 | Hermeneutical frame present as separate section in MANIFESTO | values-encoding.md | §3 Pattern 2 | T5 | No CI check (implemented manually) | None — added 2026-03-09 |
| 87 | Programmatic governance layer (CI gates) must exist per constraint category | values-encoding.md | §2 H3 | T5 | Prose principle; CI partially covers | Ongoing gap closure per #174 R1–R3 |
| 88 | D4 Pattern Catalog must contain ≥1 canonical example | AGENTS.md | §Agent Communication | T5 | validate_synthesis checks heading not content | **GAP — T1+T3 content check** |
| 89 | D4 Pattern Catalog must contain ≥1 anti-pattern | AGENTS.md | §Agent Communication | T5 | validate_synthesis checks heading not content | Same gap as #88 |
| 90 | D4 documents must cite ≥1 MANIFESTO.md reference | values-encoding.md | §6 Pattern 6 | T5 | No CI check | **GAP — T1+T3 ref check** |
| 91 | Session-start encoding checkpoint names governing axiom by task type | AGENTS.md | §Context-Sensitive Amplification | T5 | Prose only; lookup table guidance | Cognitive; permanent T5 |
| 92 | Encoding checkpoint names primary endogenous source explicitly | AGENTS.md | §Context-Sensitive Amplification | T5 | Prose only | Cognitive; permanent T5 |
| 93 | research/survey/scout/synthesize → amplify Endogenous-First | epigenetic-tagging.md | §3 Pattern F1 | T5 | Lookup table (AGENTS.md text) | Phase 2 script deferred |
| 94 | commit/push/review/merge/PR → amplify Documentation-First | epigenetic-tagging.md | §3 Pattern F1 | T5 | Lookup table (AGENTS.md text) | Phase 2 script deferred |
| 95 | script/automate/encode/CI → amplify Programmatic-First | epigenetic-tagging.md | §3 Pattern F1 | T5 | Lookup table (AGENTS.md text) | Phase 2 script deferred |
| 96 | agent/skill/authoring/fleet → amplify Endogenous-First + Minimal Posture | epigenetic-tagging.md | §3 Pattern F1 | T5 | Lookup table (AGENTS.md text) | Phase 2 script deferred |
| 97 | local/inference/model/cost → amplify Local Compute-First | epigenetic-tagging.md | §3 Pattern F1 | T5 | Lookup table (AGENTS.md text) | Phase 2 script deferred |
| 98 | Phase 2 amplify_context.py must prepend axiom verbatim (not paraphrased) | epigenetic-tagging.md | §3 Pattern F2 | T5 | Script not yet built | **GAP — T1 when script built** |
| 99 | Context Window Checkpoint written before context compaction | .github/agents/executive-orchestrator.agent.md | §Protocol | T5 | Prose only in agent file | Cognitive; permanent T5 |
| 100 | Core Layer (MANIFESTO+AGENTS) > Deployment Layer supremacy | external-value-architecture.md | §3 Pattern E1 | T5 | Prose only; no runtime guard | **GAP — T0 Adopt wizard validation** |
| 101 | Deployment Layer constraints additive only (no Core override) | external-value-architecture.md | §3 Pattern E1 | T5 | Prose only; conflict_resolution field informational | Hard to enforce programmatically |
| 102 | client-values.yml conflict_resolution field must be pre-populated | external-value-architecture.md | §2 H4 | T5 | No Adopt wizard exists yet | **GAP — T0 Adopt wizard script** |
| 103 | Session Layer (task overrides) has lowest priority | external-value-architecture.md | §3 Pattern E1 | T5 | Prose only | Cognitive; permanent T5 |
| 104 | Adopt wizard generates client-values.yml stub as scripted step | external-value-architecture.md | §2 H3 | T5 | No script | **GAP — T0 script adoption** |
| 105 | Agent reads AGENTS.md before client-values.yml (Core Layer read-first) | external-value-architecture.md | §2 H1 | T5 | Prose / session ritual only | Cognitive; permanent T5 |
| 106 | Multi-principal hierarchy declared in each client deployment | external-value-architecture.md | §3 Pattern E1 | T5 | Prose + conflict_resolution field | Not CI-enforced |
| 107 | Every SKILL.md must reference AGENTS.md as governing constraint in first section | AGENTS.md | §Agent Skills | T5 | validate_agent_files --skills checks section but not first-section cite | **GAP — T1+T3 first-section grep** |
| 108 | Skill cite density ≥0.5 per section (minimum threshold) | values-encoding.md | §6 Pattern 6 | T5 | No threshold check | **GAP — T1+T3 density threshold** |
| 109 | Agent file Action section must reference its Quality-gate | .github/agents/AGENTS.md | §Structure | T1+T3 | validate_agent_files checks section presence | None (section check only) |
| 110 | Encoding inheritance chain consistent across fleet generations | AGENTS.md | §Guiding Constraints | T5 | No lineage check | Hard to automate |
| 111 | MANIFESTO.md axiom names must not be renamed without ADR | MANIFESTO.md | §How to Read | T5 | No rename protection | Hard to enforce; convention only |
| 112 | Pre-compact checkpoint protocol: commit uncomm. changes before compaction | .github/agents/executive-orchestrator.agent.md | §Protocol | T5 | Prose only | Cognitive; permanent T5 |

### Tier Distribution Summary

| Tier | Behavioral (#174) | Values-Specific (new) | Combined |
|---|---|---|---|
| T0 | 3 | 0 | 3 |
| T1 | 12 | 2 | 14 |
| T2 | 2 | 0 | 2 |
| T3 | 12 | 0 | 12 |
| T4 | 2 | 0 | 2 |
| T5 | 37 | 40 | **77** |
| **Total** | **68** | **44** | **112** |

### T5 Values Gaps with Remediations

| # | Gap | Proposed tier | One-line remediation |
|---|---|---|---|
| G1 | Fleet-wide holographic encoding baseline absent | T1 | Extend `generate_agent_manifest.py` to output cite-density per file and fleet mean |
| G2 | D4 Pattern Catalog content check absent (example + anti-pattern strings) | T1+T3 | Extend `validate_synthesis.py` to grep for "Canonical example" + "Anti-pattern" strings in `## Pattern Catalog` section |
| G3 | D4 documents do not require ≥1 MANIFESTO.md reference | T1+T3 | Extend `validate_synthesis.py` to assert `MANIFESTO` appears ≥1 in D4 doc body |
| G4 | axiom positional ordering unprotected | T3 | Add pygrep hook: axiom H3 headers in MANIFESTO.md must appear with numeric prefix 1/2/3 in order |
| G5 | Watermark phrase integrity check absent in D4 docs | T1+T3 | Extend `validate_synthesis.py` to check ≥1 of {"Endogenous-First", "Algorithms Before Tokens", "Local Compute-First"} appears in D4 body |
| G6 | SKILL.md cite density threshold unenforced | T1+T3 | Extend `validate_agent_files.py --skills` to assert (MANIFESTO + AGENTS cites) / sections ≥ 0.33 |
| G7 | SKILL.md governing constraint citation not in first section | T1+T3 | Extend `validate_agent_files.py --skills` to grep first `##` section for AGENTS.md reference |
| G8 | Phase 2 amplify_context.py not built | T1 | Build `scripts/amplify_context.py` per `epigenetic-tagging.md §3 Pattern F2` spec |
| G9 | Core Layer supremacy not validated at adoption | T0 | Add validation step to Adopt wizard script: check `client-values.yml` conflict_resolution field exists and contains "EndogenAI Core Layer" string |
| G10 | [4,1] axiom encoding incomplete (ABT and LCF gates missing) | T5→T3 | Audit MANIFESTO.md; add programmatic gate descriptions for Algorithms Before Tokens and Local Compute-First axioms |
| G11 | LLM behavioral test suite for value fidelity absent | T1 | Implement OQ-VE-4 test suite per `docs/research/llm-behavioral-testing.md` spec |
| G12 | No handoff target validation against agent manifest | T1 | Extend `validate_agent_files.py`: cross-reference `handoffs[].agent` values against `scripts/agent_capabilities.yaml` |
| G13 | No encoding checkpoint CI validation | T5 | Cognitive check; cannot be automated at T1/T3 — deferred; document as permanent T5 |

**Canonical example**: The cross-reference density constraint (row 82) exemplifies a partial T3 uplift: `validate_agent_files.py` enforces ≥1 MANIFESTO/AGENTS reference per agent file, blocking the zero-density case. However, the target threshold from holographic encoding theory (≥2.5 per section) remains unenforced. Partial enforcement is better than none — it eliminated the zero-density fleet state — but the gap between minimum and target is not closed.

**Anti-pattern**: Row 88–89 (D4 Pattern Catalog content check): `validate_synthesis.py` verifies that the heading `## Pattern Catalog` is present in D4 documents but does not verify that the section contains a canonical example and anti-pattern. A document with an empty Pattern Catalog section passes CI. This is the Goodhart's Law encoding failure: the metric (heading presence) is validated without validating the value it proxies (knowledge encoded as concrete examples).

---

## 4. Recommendations

### R1 — D4 Pattern Catalog content gate (T5→T1+T3) — Priority: High

**Action**: Extend `validate_synthesis.py` to assert that any D4 document with a `## Pattern Catalog` heading also contains:
- The substring `Canonical example` (case-insensitive) somewhere in the section body
- The substring `Anti-pattern` (case-insensitive) somewhere in the section body

**Rationale**: `MANIFESTO.md §1. Endogenous-First` and `values-encoding.md §3 Pattern 1` both specify that each value must be encoded with a concrete example and a named anti-pattern. These are the prototype anchors that make values resilient to semantic drift. Without a CI gate, this constraint exists only as prose.

**Effort**: XS — `validate_synthesis.py` already parses section bodies. **Expected effect**: every committed D4 document is guaranteed to provide at least minimal prototype anchoring for the values it encodes.

### R2 — Fleet-wide holographic encoding measurement (T5→T1) — Priority: High

**Action**: Extend `generate_agent_manifest.py` to compute per-file cite density score `(MANIFESTO_cites + AGENTS_cites) / section_count` and fleet-wide mean/median. Add a CI assert that fleet mean density ≥ 0.50.

**Rationale**: `values-encoding.md §6 Pattern 6` designates cross-reference density as the primary measurable proxy for holographic encoding fidelity. Without a baseline and CI gate, the fleet density can erode silently as new agents are added. `MANIFESTO.md §2. Algorithms Before Tokens` requires encoding rather than ad-hoc measurement.

**Effort**: S. **Expected effect**: establishes the empirical baseline required by #169 and prevents density erosion in future fleet additions.

### R3 — MANIFESTO axiom watermark check (T5→T3) — Priority: Medium

**Action**: Add pygrep hook: every D4 docs/research/*.md file must contain at least one axiom name string.

**Effort**: XS. **Expected effect**: all D4 research documents maintain traceable echo of foundational values.

---

## 5. Sources

- [`docs/research/enforcement-tier-mapping.md`](enforcement-tier-mapping.md) — behavioral constraint baseline (#174)
- `MANIFESTO.md §1. Endogenous-First`, `§2. Algorithms Before Tokens`, `§How to Read This Document`
- [`docs/research/values-encoding.md`](values-encoding.md) §2 H2–H4, §3 Patterns 1–7, §6
- [`docs/research/epigenetic-tagging.md`](epigenetic-tagging.md) §2 H1–H4, §3 Patterns F1–F2
- [`docs/research/external-value-architecture.md`](external-value-architecture.md) §2 H1–H4, §3 Pattern E1
- `scripts/validate_agent_files.py`, `scripts/validate_synthesis.py` — current CI gate implementations
- `.github/agents/AGENTS.md` — agent-file structural constraints
- Root `AGENTS.md` §Guiding Constraints, §Context-Sensitive Amplification
