# Sprint Plan — W2 Product Reveal Repo Readiness (May 8, 2026)

**Sprint Scope**: Execute GitHub issues #561 (README.md refactor) and #562 (W2 Readiness Checklist) to prepare dogma repository for inbound developer traffic from the EndogenAI product reveal blog (publish: Fri May 8, 2026).

**Critical Deadline**: Thu May 7, 2026 (EOD) — all critical items must be merged before blog publish

**Effort Estimate**: 6–7 hours total
- **Critical items** (MUST complete by Thu EOD): 3–3.5 hours
- **Important items** (complete Fri May 1–Thu May 7): 3.5–4 hours  
- **Nice-to-have** (defer post-W2): TBD

---

## Phase 0 — Workplan Review Gate

**Agent**: Review  
**Deliverables**: Workplan validated against ordering constraints; `## Workplan Review Output` appended to scratchpad (verdict: APPROVED)  
**Depends on**: Nothing  
**Gate**: Phase 0.5 does not start until Review returns APPROVED  
**Status**: ⬜ Not started

**Workplan Review Criteria** (pass all 4):
1. Cross-cutting research items (if any) are in Phase 1, not marked "parallel with" dependent phases
2. Phase-specific research/docs precede implementation phases that depend on them
3. Critical path items (deadline Wed EOD) are in Phase 1
4. Phase dependencies are explicit (`Depends on:` annotations present)

---

## Phase 0.5 — Research & Recommendations (Best Practices Scout)

**Agents**: Research Scout → Biz Dev (review + recommendations) → Exec PM (workplan updates)  
**GitHub Issues**: Informing #561, #562  
**Deliverables**:
- `## Phase 0.5 Research Output` in scratchpad — Scout findings on 3 research questions
- `## Phase 0.5 Biz Dev Recommendations` in scratchpad — Biz Dev analysis + recommendations
- Updated workplan tasks (Exec PM applies recommendations to Phase 1/2)

**Depends on**: Phase 0 Review APPROVED  
**Gate**: Phase 1 does not start until recommendations applied to workplan  
**Status**: ⬜ Not started  
**Effort**: 45–60 minutes (15 min Scout, 15 min Biz Dev, 15 min Exec PM updates)

**Research Questions**:

### Q1: OSS Repository README Best Practices for Dashboard/Demo Visuals

**Context**: dogma has an MCP Dashboard (telemetry visualizer). Should visuals (screenshots, GIFs, live demo links) be:
- In main README.md (hero or dedicated section)?
- Only in mcp_server/README.md (sub-doc)?
- Both (brief screenshot in main, full docs in sub-doc)?

**Scout Task**: Survey 5–10 credible OSS repos with dashboards/demos (GitHub trending, high-star projects). Document patterns:
- Where do they place visuals?
- Screenshot vs GIF vs video?
- Live demo links included?

**Output**: Bullets in scratchpad under `## Phase 0.5 Research Output — Q1`.

### Q2: Adoption Flow Documentation Patterns

**Context**: dogma serves two use cases:
1. **Adopt dogma as a template** (new projects using cookiecutter or `adopt_wizard.py`)
2. **Contribute to dogma** (fork + feature branch + PR back to EndogenAI/dogma)

**Scout Task**: Survey 5–10 template repos or framework repos (e.g., cookiecutter projects, Next.js starter templates, design systems). Document:
- How do they separate "use this" vs "contribute to this"?
- Do they use separate docs/guides/ files, or inline in README Quick Start?
- Example commands included?

**Output**: Bullets in scratchpad under `## Phase 0.5 Research Output — Q2`.

### Q3: Repo Credibility Signals for Inbound Developers

**Context**: W2 blog will drive external developers to dogma repo for the first time. What signals establish credibility quickly?

**Scout Task**: Survey "first 30 seconds" of 5–10 high-credibility OSS repos (Apache, CNCF projects, popular frameworks). Document:
- What badges are present? (CI, coverage, version, license, downloads?)
- README structure patterns? (hero → quick start → architecture → community?)
- What's in the first fold? (tagline, value prop, installation?)

**Output**: Bullets in scratchpad under `## Phase 0.5 Research Output — Q3`.

---

**Biz Dev Review Task**:  
Read all 3 Scout outputs and synthesize recommendations for Phase 1/2:
- Q1 → Recommend dashboard visual strategy for Phase 1
- Q2 → Recommend adoption flow structure for Phase 1
- Q3 → Recommend credibility enhancements (badges, structure tweaks) for Phase 1

Write recommendations under `## Phase 0.5 Biz Dev Recommendations` in scratchpad (bullets, ≤500 tokens).

---

**Exec PM Update Task**:  
Read Biz Dev recommendations and update Phase 1/2 tasks in this workplan document:
- Adjust README refactor tasks to incorporate recommendations
- Flag any recommendations that belong in Phase 2 instead
- Commit updated workplan

Write update summary under `## Phase 0.5 PM Workplan Updates` in scratchpad.

---

## Phase 1 — Critical Items: README.md Refactor + Metadata (3–3.5 hrs)

**Primary Agent**: Executive Docs (with Research Scout on call for any scouting gaps)  
**GitHub Issues**: #561, #562 (Critical section)  
**Deliverables**:
- `README.md` refactored with all sections from #561 spec (hero, architecture, MCP toolset, quick start, community, etc.)
- `CODE_OF_CONDUCT.md` created or updated
- GitHub repo metadata (description + topics) updated
- Community section added to README
- All changes committed to feat/w2-product-reveal-readiness-561-562

**Depends on**: Phase 0 Review APPROVED, Phase 0.5 recommendations applied to workplan  
**Gate**: Phase 1 Review does not start until all deliverables committed  
**Status**: ⬜ Not started

**Detailed Tasks**:

### 1.1 — README.md Refactor (2–3 hours)

**Context**: Current README needs significant expansion for product reveal readiness. Issue #561 specifies hero, architecture, MCP toolset, and quick start sections. **Phase 0.5 Biz Dev research identifies 5 must-have deliverables** for inbound developer credibility (from Q1–Q3 survey of high-credibility OSS repos).

**Must-Have Deliverables** (from Phase 0.5 research):
1. **Hero tagline**: "Values ingrained, sovereignty sustained" (user-confirmed final)
2. **License badge**: Apache 2.0 badge next to CI badge in hero section
3. **Community section**: GitHub Discussions link + CONTRIBUTING link + CODE_OF_CONDUCT reference (≤5 lines)
4. **Adoption flows**: Two clear paths with example commands:
   - "Adopt dogma in your project": `cookiecutter gh:EndogenAI/dogma` or `uv run python scripts/adopt_wizard.py`
   - "Contribute to dogma": One-line summary + link to CONTRIBUTING.md (≤3 lines)
5. **Dashboard visual**: 1 screenshot/GIF of MCP Dashboard in "MCP Dashboard" section + link to `mcp_server/README.md` immediately after

**Additional #561 Spec Items**:
- **Two-surface architecture explanation**: permanent substrate + MCP enforcement layer
- **MCP toolset overview table**: list of 13 MCP tools + brief descriptions
- **Repo metadata**: Updated description + topics in GitHub settings

**Success Criteria**:
- ✅ All 5 must-have deliverables from Phase 0.5 research present
- ✅ Hero section introduces tagline + license badge
- ✅ Two-surface architecture is clearly explained (substrate + MCP)
- ✅ MCP toolset table is present with 13 tools listed
- ✅ Community section has ≥2 actionable links (Discussions, CONTRIBUTING)
- ✅ Quick start has both adoption flows with example commands
- ✅ Dashboard visual (screenshot or GIF) present in MCP Dashboard section
- ✅ README passes the repository's configured documentation validation checks (link validation, docs build)

**Research Gap** (if needed): Scout existing README.md to understand current structure before refactor.

### 1.2 — CODE_OF_CONDUCT.md (15 minutes)

**Task**: Create or verify CODE_OF_CONDUCT.md exists and is welcoming.  
**Success Criteria**: File exists and references MANIFESTO.md ethical values.

### 1.3 — GitHub Repo Metadata (10 minutes)

**Task**: Update repository description and topic tags in GitHub settings (via API or web UI).  
**Target**:
- Description: "Values ingrained, sovereignty sustained — a governance framework and agent fleet for endogenous AI workflows"
- Topics: dogma, governance, agent, values-alignment, AI

**Success Criteria**: `gh repo view EndogenAI/dogma | grep -E "Description|topics"` shows updates.

### 1.4 — Community Section in README (15 minutes)

**Task**: Add section linking to GitHub Discussions, CONTRIBUTING guide, and community code of conduct.

**Success Criteria**: Section is present in README with ≥2 actionable community links.

---

## Phase 1 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 1 Review Output` in scratchpad; verdict: APPROVED or REQUEST CHANGES  
**Depends on**: Phase 1 (Critical Items) deliverables committed  
**Gate**: Phase 2 does not start until Review returns APPROVED  
**Status**: ⬜ Not started

**Review Criteria** (explicit):
1. **README.md Structure**: Does it have all 6 sections from #561 spec (hero, architecture, MCP table, quick start, community, metadata)?
2. **Tagline Presence**: Is "Values ingrained, sovereignty sustained" present in hero section?
3. **Code Quality**: Do `ruff check docs/ README.md` and linting pass?
4. **Linting**: Are there any `validate_synthesis.py` errors if any .md files were edited?
5. **Metadata**: Is GitHub repo description updated and visible?

Return APPROVED or REQUEST CHANGES — [criterion number: one-line reason].

---

## Phase 2 — Important Items: MCP Docs + TODO Resolution + Security (3.5–4 hrs)

**Primary Agent**: Executive Docs (with Executive Scripter for TODO sweep)  
**GitHub Issues**: #562 (Important section)  
**Deliverables**:
- MCP server docs elevated in prominence (mcp_server/README.md reviewed + linked from main README)
- Adoption path clarity improved (docs/guides/adoption.md or section in README)
- TODO/FIXME placeholders resolved or tracked as new issues
- SECURITY.md created or updated
- MCP Dashboard documentation complete (in mcp_server/README.md or dedicated doc)
- All changes committed

**Depends on**: Phase 1 Review APPROVED  
**Gate**: Phase 2 Review does not start until all deliverables committed  
**Status**: ⬜ Not started

**Detailed Tasks**:

### 2.1 — MCP Server Docs Prominence (30 minutes)

**Task**: Review `mcp_server/README.md` and ensure it's linked prominently from main README (Phase 1 MCP table can link here).

**Note**: Phase 1 already adds dashboard visual + link to `mcp_server/README.md` per Phase 0.5 research. This task verifies completeness and enhances if needed.

**Success Criteria**: mcp_server/README.md exists and is linked from main README MCP toolset section.

### 2.2 — Optional Enhancements (Version Badge, Dashboard GIF) (45 minutes)

**Task** (Phase 0.5 research — "Important" tier):
1. **Version badge**: Add version/release badge if dogma has versioned releases (check `CHANGELOG.md` or git tags)
2. **Dashboard GIF**: If Phase 1 used static screenshot, upgrade to animated GIF showing real telemetry/interaction (≤2MB)
3. **Quick Start mobile optimization**: Verify Quick Start visible within 3 scrolls on mobile viewport

**Note**: Phase 1 already handles adoption flow clarity per research (two flows with example commands). This task is for enhancement polish.

**Success Criteria**: Version badge present (if applicable), dashboard visual optimized, mobile Quick Start validated.

### 2.3 — TODO/FIXME Sweep (1.5 hours)

**Task**: Run `grep -r "TODO\|FIXME" docs/ scripts/ .github/ --include="*.py" --include="*.md"` and either:
- Resolve (implement the TODO)
- Create a tracked GitHub issue (add to backlog for post-W2)
- Leave with clear justification documented inline

**Success Criteria**: All TODOs are either resolved, tracked, or justified. No orphaned placeholders.

**Research Gap** (if needed): Scout codebase for TODO locations before deciding on resolution strategy.

### 2.4 — SECURITY.md (20 minutes)

**Task**: Create or update SECURITY.md with vulnerability reporting guidance.

**Success Criteria**: File exists with clear instructions for reporting security issues (email, private advisory, etc.).

### 2.5 — MCP Dashboard Documentation (30–60 minutes)

**Task**: Ensure MCP Dashboard is documented (setup, running, troubleshooting).

**Success Criteria**: mcp_server/README.md includes dashboard setup instructions; OR dedicated doc exists with link from main README.

---

## Phase 2 Review — Review Gate

**Agent**: Review  
**Deliverables**: `## Phase 2 Review Output` in scratchpad; verdict: APPROVED or REQUEST CHANGES  
**Depends on**: Phase 2 (Important Items) deliverables committed  
**Gate**: Phase 3 (Finalize + Merge) does not start until Review returns APPROVED  
**Status**: ⬜ Not started

**Review Criteria**:
1. **TODO Resolution**: Are there any remaining untracked TODOs/FIXMEs?
2. **MCP Prominence**: Is mcp_server/README.md linked from main README?
3. **Adoption Clarity**: Do both adoption flows have clear documentation?
4. **SECURITY.md**: Does it exist and have reporting guidance?
5. **Docs Linting**: Pass `validate_synthesis.py` for all touched .md files

Return APPROVED or REQUEST CHANGES — [criterion number: one-line reason].

---

## Phase 3 — Finalize + Merge

**Agent**: GitHub Agent  
**Deliverables**: PR opened, Review gate triaged, PR merged to main  
**Depends on**: Phase 2 Review APPROVED  
**Gate**: None (final phase)  
**Status**: ⬜ Not started

**Steps**:
1. Create PR with title: `feat(product-reveal): W2 repo readiness — README refactor + critical docs (#561, #562)`
2. Link to issues #561 and #562 in PR body
3. Wait for CI to pass
4. Triage Copilot PR review comments (blocking vs suggestion vs nit)
5. Fix any blocking issues; post batch reply using `scripts/pr_review_reply.py`
6. Merge when all blockers resolved and Review gate APPROVED

---

## Nice-to-Have Items (Defer Post-W2)

These are tracked for future sprints; do NOT block W2 publish:

**From Phase 0.5 Research (Q3 — Defer tier)**:
- [ ] Coverage badge (requires coverage reporting setup; not critical for W2)
- [ ] Download/install count badge (PyPI or npm stats if applicable)
- [ ] Live demo link for MCP Dashboard (if dashboard can be hosted publicly)
- [ ] Sponsor section (if fundraising active)

**From Original #562 Nice-to-Have**:
- [ ] Concrete examples/demos section in README
- [ ] AccessiTech/EndogenAI relationship clarification
- [ ] Test coverage + pre-commit.ci badges
- [ ] Adopt-test* folder explanation (docs/adopt-test-migration.md)
- [ ] External resources links (academic papers, talks, etc.)
- [ ] Video walkthrough or live demo links

---

## Success Metrics

**Blocking Success Criteria** (W2 publish must have these):
- ✅ README.md refactored per #561 spec (6 sections complete)
- ✅ MCP toolset overview table present
- ✅ Quick Start adoption paths documented (both flows clear)
- ✅ Community/discussions section linked
- ✅ GitHub repo metadata updated
- ✅ All changes merged to main by Wed EOD

**Important Success Criteria** (Thu May 1–7):
- ✅ TODO/FIXME resolution complete or tracked
- ✅ MCP docs prominent and linked
- ✅ SECURITY.md in place
- ✅ Dashboard docs complete

**Nice-to-Have** (post-W2):
- Demos / concrete examples
- Adopt-test folder explanation
- Badges + coverage links

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| README changes conflict with recent commits | Branch synced on Apr 30; low risk if Phase 1 completed by EOD Thu May 1 |
| MCP toolset table outdated | Scout mcp_server/ to verify tool list before writing table (Phase 1 task) |
| TODO resolution discovers major refactoring needs | Create tracked GitHub issue instead of implementing; prioritize post-W2 |
| Copilot PR review requests major structural changes | Triage early; break large feedback into manageable fixes; re-request review for each batch |
| Blog publish delayed past May 8 | Nice-to-have items can follow the blog; critical items MUST land before |

---

## Timeline

| Deadline | Items | Owner |
|----------|-------|-------|
| **Today (Thu Apr 30)** | Phase 0 Review + Phase 1 planning | Executive Orchestrator + Review |
| **Fri May 1–2** | Phase 1 (Critical Items) complete | Executive Docs + Research Scout |
| **Sat May 3** | Phase 1 Review + Phase 2 start | Review + Executive Docs |
| **Sun May 4–6** | Phase 2 (Important Items) continue | Executive Docs + Executive Scripter |
| **Thu May 7 (EOD)** | Phase 2 Review + PR merge complete | Review + GitHub Agent |
| **Fri May 8** | Blog publishes; repo ready for traffic | N/A |

---

## Issues & Questions for W2 Sprint

**Open Questions to Surface**:
1. Should adopt-test* folders be documented in main README, or deferred to CONTRIBUTING guide?
2. Is the "Values ingrained, sovereignty sustained" tagline final, or subject to brand review?
3. Are there specific AccessiTech/EndogenAI relationship clarifications needed for the blog audience?
4. Dashboard screenshots/GIF: should they be in the README, or only in mcp_server/README.md?

---

## Dependency Graph

```
Phase 0 Review (GATE)
    ↓
Phase 1: Critical Items (README, CODE_OF_CONDUCT, metadata, community)
    ↓
Phase 1 Review (GATE) ← MUST PASS before blog launch
    ↓
Phase 2: Important Items (MCP docs, adoption clarity, TODO sweep, SECURITY)
    ↓
Phase 2 Review (GATE)
    ↓
Phase 3: Finalize + Merge PR
    ↓
✅ W2 Product Reveal (May 8) — Blog drives traffic to polished repo
```

---

## Commit Discipline

All commits follow [Conventional Commits](../../CONTRIBUTING.md#commit-discipline):

- **Format**: `type(scope): description — closes #NNN` (e.g., `docs(readme): add hero section and MCP toolset table — closes #561`)
- **Types**: `docs`, `fix`, `feat`, `chore`
- **Scope**: `readme`, `mcp`, `adopt`, `security`, `community`, etc.
- **Issue References**: Include `Closes #561` and `Closes #562` in PR body to auto-close on merge

---

## Key Resources

- **Issue #561**: README.md refactor spec — full acceptance criteria
- **Issue #562**: W2 Readiness Checklist — critical/important/nice-to-have breakdown
- **Blog Publish**: Thu May 8, 2026 — accessi.tech/blog/why-we-built-endogenai
- **Previous Session Context**: Comms schedule + dev.to policy available in consulting repo
- **AGENTS.md**: Governance constraints for all agent behavior in this repo
- **mcp_server/README.md**: Existing MCP documentation to review

---
