# W2 README Enhancement Sprint — Workplan

**Branch**: `feat/w2-readme-enhancements-567-568-569-570`  
**Date**: 2026-05-01  
**Issues**: #567, #568, #569, #570

---

## Sprint Overview

This sprint enhances the W2 README with four targeted improvements: establishing the four-substrate model as a conceptual foundation (#568), enriching the AccessiTech case study with substrate-level detail (#569), auditing and expanding the glossary (#567), and conducting independent research on governance-failure examples (#570). The four-substrate model is the foundational dependency: both the case study and glossary will reference it. Research is independent and can run in parallel with foundational work.

---

## Clarifying Questions — ANSWERED

User responses received 2026-05-01:

1. **#569 (Case Study)**: The acceptance criteria mention Conor's personal AccessiTech adoption experience (11-point narrative from PR #564 review comment 3171557785). Should this be written in first-person (Conor's voice), third-person narrative, or distilled into general principles? (Requires human sign-off on tone/voice.)  
   **ANSWER**: Distilled into general principles with collective "we" language (open and inclusive, no personal attribution)

2. **#570 (Research)**: If the primary Maven Smart System / Iran incident cannot be verified, should the research phase pivot to alternative governance-failure examples, mark the finding as "inconclusive," or defer the issue? (Requires human decision gate.)  
   **ANSWER**: Deep dive research phase — plenty of information available on governance failures; pivoting won't be needed. Conduct thorough research.

3. **#567 (Glossary)**: The glossary work includes adding entries and improving README linking. Should new glossary entries be added to the existing `docs/glossary.md` file, or should a mini-glossary section be added directly to README? (Affects placement strategy.)  
   **ANSWER**: Use existing `docs/glossary.md` file. README should have inline links pointing to glossary terms.

4. **Scope Boundary**: Are all four issues scoped to `README.md` and `docs/glossary.md` only, or do any require changes to other docs (e.g., `MANIFESTO.md`, guides, or research docs)? (Confirms file scope.)  
   **ANSWER**: Expanded scope — include MANIFESTO.md audit phase (near end of sprint) to check for backpropagation needs from README.md and product reveal readiness; include mkdocs audit phase (near end of sprint) to verify docs build configuration and integration. New research docs under `docs/research/` are acceptable.

---

## Phase Structure

### Phase 0 — Workplan Review Gate

**Agent**: Review  
**Description**: Validate phase ordering, research-first compliance for #570, and dependency annotations. Confirm #568 gates #569 and #567; confirm #570 research is independent.  
**Deliverables**:  
- D1: Review verdict (`APPROVED` or `REQUEST CHANGES — [reason]`)  
**Depends on**: nothing  
**Gate**: No domain phase begins until Phase 0 returns `APPROVED`  
**Status**: ⬜ Pending

---

### Phase 1A — Four-Substrate Model (Foundation)

**Agent**: Executive Docs  
**Description**: Draft and commit the four-substrate model section in `README.md` (#568). This is the foundational conceptual content that both #569 (case study) and #567 (glossary) will reference.  
**Deliverables**:  
- D1: Four-substrate model section added to `README.md` (What Is This Repo or Architecture section)
- D2: Section includes: Policy Docs, Design/Technical Docs, Agent Files, Enforcement Scripts
- D3: Distinction between EndogenAI (social endeavor) and dogmaMCP (technical harness) articulated
- D4: Committed with message `docs(readme): expand README with four-substrate architecture (#568)`  
**Depends on**: Phase 0 (Review APPROVED)  
**Gate**: Phase 2 (case study) and Phase 3 (glossary) do not start until D4 is committed  
**Status**: ⬜ Pending

---

### Phase 1B — Governance-Failure Research (Parallel)

**Agent**: Executive Researcher (delegates to Research Scout)  
**Description**: Conduct research per #570 acceptance criteria. Verify the Maven Smart System / Iran incident or identify alternative verified governance-failure examples. Research-first gate applies: no link added to README until verified source found.  
**Deliverables**:  
- D1: Research findings documented in `.tmp/<branch>/<date>.md` under `## Research Scout Output`  
- D2: Source cached in `.cache/sources/` if verified URL found
- D3: If primary incident cannot be verified, surface alternative options to human for decision
**Depends on**: Phase 0 (Review APPROVED)  
**Gate**: If research findings affect README claims, surface to Orchestrator before Phase 4 (final review)  
**Parallelization**: Runs concurrently with Phase 1A (no shared file paths, no output dependency)  
**Status**: ⬜ Pending

---

### Phase 2 — AccessiTech Case Study Enrichment

**Agent**: Executive Docs  
**Description**: Add AccessiTech case study to README Use Cases (or dedicated section) per #569 acceptance criteria. Distill the 11-point narrative from PR #564 review into a clean, accessible narrative using collective "we" language (open and inclusive, no personal attribution). References the four-substrate model from Phase 1A.  
**Deliverables**:  
- D1: Case study section drafted in README (readable for laypeople per comment 3171395840)
- D2: `dA11y` defined or linked
- D3: Narrative connects to four-substrate model if applicable
- D4: Written with collective "we" voice, distilled into general principles (no personal attribution)
- D5: Committed with message `docs(readme): add AccessiTech case study (#569)`  
**Depends on**: Phase 1A (four-substrate model must exist to reference)  
**Gate**: Phase 3 does not start until D5 is committed  
**Status**: ⬜ Pending

---

### Phase 3 — Glossary Audit and Enhancement

**Agent**: Executive Docs  
**Description**: Audit `docs/glossary.md` per #567 acceptance criteria. Add `Sovereignty` entry, review `Endogenous-First` and `Endogenic Development` entries, add missing README terms, improve README→glossary inline linking. May reference four-substrate model concepts from Phase 1A.  
**Deliverables**:  
- D1: `Sovereignty` entry added to glossary with definition, source, related terms
- D2: Existing entries reviewed and updated as needed
- D3: Glossary audit complete (all prominent README terms covered)
- D4: README contains inline links to `docs/glossary.md` for key terms
- D5: All glossary internal cross-references validated (no broken links)
- D6: Committed with message `docs(glossary): audit and enhance glossary + improve README linking (#567)`  
**Depends on**: Phase 1A (glossary may reference substrate model); Phase 2 (avoid merge conflicts in README)  
**Gate**: Phase 4 does not start until D6 is committed  
**Status**: ⬜ Pending

---

### Phase 4 — MANIFESTO.md Audit

**Agent**: Executive Docs  
**Description**: Audit `MANIFESTO.md` for backpropagation needs based on README.md enhancements from Phases 1-3. Check whether foundational principles in MANIFESTO need updates to align with the four-substrate model, case study, or glossary additions. Verify product reveal readiness (W2 launch alignment).  
**Deliverables**:  
- D1: MANIFESTO.md audit complete — findings documented in scratchpad
- D2: List of backpropagation updates needed (if any) with justification
- D3: W2 product reveal readiness confirmation (does MANIFESTO support README positioning?)
- D4: If updates needed: committed with message `docs(manifesto): backpropagate W2 README enhancements`; else: no-op confirmed in scratchpad  
**Depends on**: Phase 3 (all README/glossary changes complete)  
**Gate**: Phase 5 does not start until D1-D3 are documented  
**Status**: ⬜ Pending

---

### Phase 5 — mkdocs Audit

**Agent**: Executive Docs  
**Description**: Audit `mkdocs.yml` and GitHub "Docs Build" workflow (ID: 247040819) to ensure documentation build configuration is correct and site deploys properly. Verify navigation structure includes new glossary entries and README changes will be visible on https://endogenai.github.io/dogma/  
**Deliverables**:  
- D1: mkdocs.yml audit complete — navigation structure validated
- D2: GitHub "Docs Build" workflow verified active and passing
- D3: Docs site URL confirmed accessible (https://endogenai.github.io/dogma/)
- D4: Navigation includes `docs/glossary.md` and new entries are reachable
- D5: Findings documented in scratchpad; if fixes needed: committed with message `docs(mkdocs): update config for W2 enhancements`  
**Depends on**: Phase 4 (all doc changes complete before build audit)  
**Gate**: Phase 6 does not start until D1-D4 are confirmed  
**Status**: ⬜ Pending

---

### Phase 6 — Final Review & PR Open

**Agent**: Review → GitHub  
**Description**: Validate all changes against AGENTS.md constraints, synthesis quality, and acceptance criteria for all four issues. Commit final state, push, and open PR.  
**Deliverables**:  
- D1: Review verdict (`APPROVED` or `REQUEST CHANGES`)  
- D2: All changes committed and pushed to `feat/w2-readme-enhancements-567-568-569-570`  
- D3: PR opened with description listing all 4 issues and key changes
- D4: CI passing (link check, lint, tests)  
**Depends on**: Phases 1A, 1B, 2, 3, 4, 5 (all domain work complete)  
**Gate**: Sprint is not complete until D4 is confirmed (CI green)  
**Status**: ⬜ Pending

---

## Success Criteria

Sprint is complete when:

- [ ] All four issues (#567, #568, #569, #570) have acceptance criteria satisfied
- [ ] `README.md` contains four-substrate model section, AccessiTech case study (with collective "we" voice), and improved glossary links
- [ ] `docs/glossary.md` has Sovereignty entry and audit complete
- [ ] Research findings from #570 are documented (verified link added or alternatives surfaced)
- [ ] MANIFESTO.md audit complete — backpropagation needs addressed or confirmed none
- [ ] mkdocs.yml and Docs Build workflow verified and navigation structure validated
- [ ] All clarifying questions answered and documented in scratchpad
- [ ] Review gate (Phase 6) returns `APPROVED` verdict
- [ ] All commits follow Conventional Commits format
- [ ] CI passes on branch
- [ ] PR is ready for merge

---

## Parallelization Notes

**Phase 1A and Phase 1B** can run concurrently:
- No shared file paths (`README.md` vs. research docs/scratchpad)
- No output dependency (research findings from 1B do not inform 1A content directly)
- Both gate subsequent phases independently (1A gates 2 and 3; 1B surfaces findings for Phase 6 if needed)

**Phases 2 and 3 are sequential**:
- Both modify `README.md` (Phase 2) and may reference each other
- Running in parallel risks merge conflicts
- Phase 3 (glossary) may reference Phase 2 content (case study terms)

**Phases 4 and 5 are sequential**:
- Both are audit phases that depend on all prior content changes (Phases 1-3)
- Phase 4 (MANIFESTO audit) checks backpropagation needs from README changes
- Phase 5 (mkdocs audit) validates documentation build after all changes
- Both must complete before Phase 6 (Final Review)

---

## Commit Convention

All commits follow [Conventional Commits](../../CONTRIBUTING.md#commit-discipline):
- `docs(readme): <description> (#issue)`
- `docs(glossary): <description> (#issue)`
- `chore: <description>` for workplan updates

---

## References

- **Issue #567**: [docs(glossary): audit glossary for completeness](https://github.com/EndogenAI/dogma/issues/567)
- **Issue #568**: [docs(readme): expand README with four-substrate architecture](https://github.com/EndogenAI/dogma/issues/568)
- **Issue #569**: [docs(readme): add AccessiTech case study](https://github.com/EndogenAI/dogma/issues/569)
- **Issue #570**: [docs(readme): research governance-failure article link](https://github.com/EndogenAI/dogma/issues/570)
- **PR #564 Review Comments**: Source of all 4 issues (comments 3171219472, 3171363709, 3171557785, 3171377485)
- **AGENTS.md**: Governance constraints for all agent behavior
