# Workplan: Sprint Planning — Production Hardening & Adoption Sprint

**Branch**: `feat/sprint-production-hardening-adoption`
**Date**: 2026-03-14
**Orchestrator**: Executive Orchestrator

---

## Objective

Produce a fully sequenced, phase-gated execution plan for the **Production Hardening & Adoption Sprint**. The sprint addresses one critical back-propagation issue (#212), a security fix (#106), documentation convention debt from the prior sprint, four high-priority scripts features, two major adoption deliverables, and a re-queued fleet audit (#152). Sprint scope is capped at 18 issues; 20 additional open issues are explicitly deferred. A housekeeping phase precedes execution to close 7 milestone #11 issues that were completed on-branch but never auto-closed.

---

## Milestone #11 Open-Issue Audit

The following issues appear open on GitHub despite the prior workplan marking them complete. Assessment is based on commit evidence in `docs/plans/2026-03-13-sprint-planning-self-improvement.md`.

| # | Claimed Close Commit | Assessment | Action |
|---|---------------------|------------|--------|
| #245 | `c1996af` + `ee4bb8a` | Complete — `Closes #245` not in PR body | `gh issue close 245` |
| #246 | `cc42e08` + `d0a67c9` | Complete — same cause | `gh issue close 246` |
| #247 | `cc42e08` + `d0a67c9` | Complete — same cause | `gh issue close 247` |
| #248 | `8203208` | Complete — same cause | `gh issue close 248` |
| #107 | `8203208` | Complete — same cause | `gh issue close 107` |
| #227 | `0bc63b4` | Complete — same cause | `gh issue close 227` |
| #203 | `af49037` + `d091a73` | Complete — same cause | `gh issue close 203` |
| #152 | — | **Genuinely deferred** — M-effort audit; re-queued to this sprint | Include in Phase 5 |

---

## Issue Inventory (18 sprint-scoped)

| # | Title | Type | Priority |
|---|-------|------|----------|
| #212 | Back-propagation: MANIFESTO §3 LCF structural-enabler framing → endogenic design paper → full dogma propagation | research | critical |
| #106 | fix(security): block IPv6 link-local addresses (fe80::/10) in fetch_source.py validate_url() | security | high |
| #257 | validate_agent_files.py — add specificity metrics and MANIFESTO section-anchored citation check | feature | high |
| #254 | prune_scratchpad.py phase 2 — docs/sessions/ archive + session-hash frontmatter | feature | high |
| #255 | generate_script_docs.py — pydoc-markdown wrapper for scripts/docs/ generation and staleness check | feature | high |
| #225 | docs(guides): encode doc type taxonomy + programmatic sweep table pattern in workflows.md | docs | medium |
| #226 | docs(agents): encode explicit binary acceptance criteria requirement in Review delegation guidance | docs | medium |
| #222 | chore: encode back-propagation weave/link/consolidate discipline in deep-research-sprint skill and executive-docs agent | chore | medium |
| #224 | feat: specify and optionally enforce manual stop gate for edits to final-status research docs | feature | medium |
| #152 | Audit fleet guardrails for programmatic enforcement opportunities (re-queued) | chore | medium |
| #237 | chore: [4,1] encoding coverage audit — script-driven baseline of MANIFESTO principle F1-F4 forms | chore | medium |
| #256 | feat(scripts): extract_action_items.py — D4 research doc action item extraction with BM25 dedup | feature | medium |
| #238 | feat: Implement constitutional AI post-session value fidelity hook in validate_session.py (OQ-4) | feature | medium |
| #214 | feat(ci): issue-metrics action — scheduled committed issue/PR health snapshot for agent orientation | feature | medium |
| #205 | feat(adoption): AccessiTech LLC — first dogma adoption use case, informs onboarding playbook | feature | high |
| #56 | feat: implement Adopt onboarding wizard (scripts/adopt_wizard.py) | feature | high |
| #125 | Adopt Wizard Integration with client-values.yml | feature | medium |
| #241 | Agent Orientation Efficiency — Streamline Session Startup Without Adding Tokens | feature | high |

---

## Phase Plan

### Phase 0 — Workplan Review Gate ⬜

**Agent**: Review
**Deliverables**: Verdict logged under `## Workplan Review Output` in session scratchpad — must return APPROVED before Phase 1 begins
**Depends on**: this workplan committed
**Gate**: Phase 1 does not begin until Review returns APPROVED
**Status**: ⬜ Not started

---

### Phase 1 — Sprint Housekeeping ⬜

**Agent**: Executive PM
**Deliverables**:
- D1: Seven M#11 issues closed on GitHub (#245, #246, #247, #248, #107, #227, #203) — confirmed via `gh issue view <num> --json state`
- D2: Closure log appended to session scratchpad (each `gh issue close` command + state result)
- D3: #152 confirmed open and re-labelled for this sprint

**Depends on**: nothing
**Gate**: All seven closures verified; #152 confirmed open before Phase 2 begins
**Script opportunity**: `for n in 245 246 247 248 107 227 203; do gh issue close $n; done` + verify loop
**Status**: ⬜ Not started

---

### Phase 2 — LCF Structural-Enabler Back-Propagation Research & Apply ⬜

**Agent**: Executive Researcher → Executive Docs (Scout → Synthesizer → Reviewer → propagation apply)
**Issues**:
- #212 `Back-propagation: MANIFESTO §3 LCF structural-enabler framing → endogenic design paper → full dogma propagation round` — effort: XL — critical-path issue; Scout reads prior LCF research (#245 synthesis, MANIFESTO §3 current text, endogenic design paper); Synthesizer produces amendment proposals; Docs applies propagation commits to MANIFESTO §3, endogenic design paper, and any AGENTS.md sections that reference LCF framing

**Depends on**: Phase 1
**Gates**: Phase 4 for #226 and #224 (AGENTS.md must stabilise after propagation before review-guidance edits proceed); Phase 5 (encoding coverage scope confirmed by LCF framing decision)
**Note**: Do not begin any MANIFESTO.md or AGENTS.md edits in other phases until Phase 2 propagation commits land
**Status**: ⬜ Not started

---

### Phase 3 — Security Hardening & Core Script Features ⬜

**Agent**: Executive Scripter
**Parallel with**: Phase 2 (scripts/fetch_source.py, prune_scratchpad.py, validate_agent_files.py — no MANIFESTO or AGENTS.md overlap)
**Issues**:
- #106 `fix(security): block IPv6 link-local addresses (fe80::/10) in fetch_source.py validate_url()` — effort: S — highest-urgency non-research item; add regex/socket guard for `fe80::/10` range; update tests
- #254 `prune_scratchpad.py phase 2 — docs/sessions/ archive + session-hash frontmatter` — effort: M — extends existing script with archive-to-docs/sessions/ and frontmatter hash; test coverage required
- #257 `validate_agent_files.py — add specificity metrics and MANIFESTO section-anchored citation check` — effort: M — adds two new CI gate checks; natural batch with #106 for single Scripter pass

**Effort total**: S + M + M ≈ 2 dev-days
**Depends on**: Phase 1
**Gates**: Phase 7 (adoption wizard and validate tooling must be hardened before first external adoption run)
**Status**: ⬜ Not started

---

### Phase 4 — Documentation Conventions ⬜

**Agent**: Executive Docs
**Issues**:
- #225 `docs(guides): encode doc type taxonomy + programmatic sweep table pattern in workflows.md` — effort: S — `docs/guides/workflows.md` only; safe to start post-Phase 1
- #222 `chore: encode back-propagation weave/link/consolidate discipline in deep-research-sprint skill and executive-docs agent` — effort: S — `.github/skills/deep-research-sprint/SKILL.md` + `executive-docs.agent.md`; safe to start post-Phase 1
- #226 `docs(agents): encode explicit binary acceptance criteria requirement in Review delegation guidance` — effort: S — touches AGENTS.md review section; **gates on Phase 2 AGENTS.md propagation completing**
- #224 `feat: specify and optionally enforce manual stop gate for edits to final-status research docs` — effort: M — spec in docs + optional validate_synthesis.py CI enforcement; **gates on Phase 2 settling final-status doc conventions**

**Effort total**: S + S + S + M ≈ 2 dev-days
**Sub-phase ordering within Phase 4**:
  - #225 and #222 require Phase 1 only (separate file domains: `workflows.md`, skill + agent files — no MANIFESTO or AGENTS.md overlap with Phase 2)
  - #226 and #224 require Phase 2 complete — these touch AGENTS.md and final-status doc conventions that Phase 2 LCF propagation may modify
**Depends on**: Phase 1 (for #225, #222); Phase 2 (for #226, #224) — the full Phase 4 gate is Phase 2 complete
**Gates**: Phase 7 (adoption onboarding references these conventions)
**Status**: ⬜ Not started

---

### Phase 5 — Fleet Audit & Encoding Coverage Baseline ⬜

**Agent**: Executive Scripter
**Parallel with**: Phase 4 (audit scripts vs. docs edits — distinct domains)
**Issues**:
- #152 `Audit fleet guardrails for programmatic enforcement opportunities` — effort: M — re-queued from prior sprint; read-analysis pass across fleet; produces scripting-gap report; prior blocker (#151) confirmed closed
- #237 `chore: [4,1] encoding coverage audit — script-driven baseline of which MANIFESTO principles have all F1-F4 encoding forms` — effort: M — produces quantitative coverage baseline; LCF framing from Phase 2 must be settled before running audit

**Effort total**: M + M ≈ 2 dev-days
**Depends on**: Phase 2 (LCF framing from #212 confirms audit scope); Phase 1 for baseline sprint state
**Note**: #152 gap report feeds informally into Phase 6 scripting priorities but does not hard-gate it
**Status**: ⬜ Not started

---

### Phase 6 — Scripts Tooling Features ⬜

**Agent**: Executive Scripter
**Parallel with**: Phase 4 (script features vs. docs edits — distinct file domains)
**Issues**:
- #256 `feat(scripts): extract_action_items.py — D4 research doc action item extraction with BM25 dedup` — effort: M — upstream research #247 complete (✓ `d0a67c9`); new script; requires tests
- #255 `feat(scripts): generate_script_docs.py — pydoc-markdown wrapper for scripts/docs/ generation and staleness check` — effort: M — upstream research #246 complete (✓ `cc42e08`); new script; requires tests
- #238 `feat: Implement constitutional AI post-session value fidelity hook in validate_session.py (OQ-4)` — effort: M — extends validate_session.py; no intra-sprint upstream gate
- #214 `feat(ci): issue-metrics action — scheduled committed issue/PR health snapshot for agent orientation` — effort: S — new CI workflow; standalone

**Effort total**: M + M + M + S ≈ 3 dev-days
**Depends on**: Phase 1; prior sprint research for #255 (#246 ✓) and #256 (#247 ✓)
**Status**: ⬜ Not started

---

### Phase 7 — Adoption Work ⬜

**Agent**: Executive Orchestrator (coordinates Executive Docs + Executive Scripter sub-delegations)
**Issues**:
- #205 `feat(adoption): AccessiTech LLC — first dogma adoption use case, informs onboarding playbook` — effort: L — documents first external adoption; drives wizard acceptance criteria; must precede #56 within the phase
- #56 `feat: implement Adopt onboarding wizard (scripts/adopt_wizard.py)` — effort: L — first-time adopter CLI; requires hardened tooling from Phase 3 and stable doc conventions from Phase 4
- #125 `Adopt Wizard Integration with client-values.yml` — effort: M — connects wizard with Deployment Layer values file; natural batch follow-on to #56 within the phase
- #241 `Agent Orientation Efficiency — Streamline Session Startup Without Adding Tokens` — effort: M — **blocked: dependency-decision gate required before implementation begins** — do not start until user confirms the mechanism in response to the blocking question below

**Effort total**: L + L + M + M (conditional) ≈ 4 dev-days
**Depends on**: Phase 3 (hardened tooling); Phase 4 full (doc conventions stable); Phase 2 (dogma propagation complete — ensures onboarding reflects final LCF framing)
**Blocking question for #241**: Before delegating #241 implementation, the Orchestrator must surface this decision: *"Issue #241 (Agent Orientation Efficiency) is currently blocked. The mechanism proposed is [TBD from issue body]. Do you want to unblock it in this sprint, and if so, which approach should be used?"*
**Status**: ⬜ Not started

---

### Phase 8 — Review & Commit ⬜

**Agent**: Review → GitHub
**Deliverables**:
- D1: All changed files validated — Review agent returns APPROVED verdict logged in scratchpad under `## Review Output`
- D2: All changes committed with Conventional Commit messages; `Closes #NNN` lines in PR body for all 18 sprint issues
- D3: CI passes — `gh run list --limit 3` green before requesting review

**Depends on**: All preceding phases complete
**Gate**: CI must pass before review is requested; close issues via `Closes #NNN` in PR body — not manually
**Status**: ⬜ Not started

---

## Dependency Graph

```
Phase 1 (Housekeeping)
├── Phase 2 (LCF Research + Propagation) ────────── hard-gates Phase 4 (#226, #224); hard-gates Phase 5
├── Phase 3 (Security + Core Scripts) ───────────── hard-gates Phase 7; parallel with Phase 2
├── Phase 4 (Docs Conventions) ──────────────────── hard-gates Phase 7
│   ├── #225, #222: start after Phase 1 (parallel with Phase 2)
│   └── #226, #224: start after Phase 2
├── Phase 5 (Fleet Audit + Coverage) ────────────── after Phase 2; soft-informs Phase 6
├── Phase 6 (Scripts Tooling Features) ──────────── parallel with Phase 4 and 5
└── Phase 7 (Adoption) ──────────────────────────── gates Phase 8
    └── #241: blocked — awaiting unblocking decision
        └── Phase 8 (Review + Commit)
```

**Sequencing layers**:
- **Layer 1 (parallel, after Phase 1)**: Phase 2 ‖ Phase 3 ‖ Phase 4 (#225, #222 only) ‖ Phase 6
- **Layer 2 (after Phase 2)**: Phase 4 (#226, #224) ‖ Phase 5
- **Layer 3 (after Phase 2 + Phase 3 + Phase 4 full)**: Phase 7
- **Layer 4**: Phase 8

---

## Deferred Issues

| # | Title | Reason for Deferral |
|---|-------|---------------------|
| #221 | GitHub Actions marketplace caching patterns research | effort:XL; no immediate unblocking gate this sprint |
| #197 | Programmatic Governance Coverage Asymmetry — Semantic Drift Detection | milestone:#10 ordering constraint |
| #196 | Topological-Temporal Coherence Joint Specification — Phase 10 Research | milestone:#10 ordering constraint |
| #231 | research: H1 empirical baseline — encode-before-act vs reactive reconstruction A/B | standalone XL research; post-hardening sprint |
| #158 | feat(agents): capability-aware agent registry design | milestone:#9; deferred pending capability-gate script stabilisation |
| #157 | chore(scripts): subshell audit logging in PREEXEC governor | milestone:#9; fits dedicated governor sprint |
| #156 | chore(scripts): token-spinning detection and rate-limiting | milestone:#9; pairs with #157 |
| #113 | Tier 2 Behavioral Testing — Drift Detection | milestone:#9; deferred |
| #105 | feat(scripts): implement scripts/amplify_context.py | milestone:#9; deferred |
| #253 | feat(scripts): parse_fsm_to_graph.py — FSM-to-NetworkX path analysis | low priority; fits alongside #237 in future audit sprint |
| #57 | feat: implement Greenfield onboarding wizard | milestone:#5; after Adopt wizard (#56) ships |
| #206 | feat(adoption): FrankenBrAIn — greenfield benchmark | low priority; after AccessiTech (#205) |
| #207 | research(adoption): product-fork-initialization guide | unclassified; defer pending triage |
| #204 | docs: add product fork initialization guide | unclassified; defer pending triage |
| #202 | Add MkDocs Material docsite | milestone:#5; effort:L; defer |
| #234 | research: Empirical session studies (Q2 + Q4) | low priority; ongoing background research |
| #232 | research: H2 NK model formalization — Kauffman K-coupling graph | low priority; standalone research |
| #230 | Validate explicit output format constraint as primary driver of compressed returns | low priority research |
| #131 | Cognee Library Adoption (After Local Compute Baseline) | blocked; milestone:#11 |
| #128 | Phase 1 AFS Integration — Index Session to AFS on Session Close | low priority; AFS dependency unresolved |
| #129 | SQLite-only Pattern A1 for AFS — FTS5 Keyword Index | low priority; milestone:#9 |

---

## Acceptance Criteria

- [ ] Phase 0 complete — Workplan Review APPROVED logged in scratchpad under `## Workplan Review Output`
- [ ] Phase 1 complete — 7 M#11 issues confirmed closed on GitHub; #152 confirmed open
- [ ] #212 research synthesis committed; full propagation round applied to MANIFESTO §3, endogenic design paper, and AGENTS.md
- [ ] #106 IPv6 security fix committed with tests passing
- [ ] All 18 sprint issues assigned to a named execution phase with effort label (XS/S/M/L/XL)
- [ ] Phase dependencies explicit — no phase begins before its prerequisite phase
- [ ] #226 and #224 start only after Phase 2 AGENTS.md propagation commits land
- [ ] #241 blocking gate documented — unblocking decision received from user before implementation
- [ ] Parallelisable phases explicitly annotated
- [ ] Review agent APPROVED verdict logged in scratchpad under `## Review Output`
- [ ] CI passes before review is requested (`gh run list --limit 3` green)
- [ ] All 18 sprint issues closed via `Closes #NNN` in PR body — no manual closes
