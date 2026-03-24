---
title: GitHub Engineering Blog Agent Patterns for Agentic Workflows
status: Final
closes_issue: 398
x-governs:
  - endogenous-first
  - algorithms-before-tokens
created: 2026-03-23
recommendations:
  - id: rec-github-blog-001
    title: "ADOPT Interrogative Pre-Delegation Gate (Phase 0)"
    status: accepted-for-adoption
    effort: Medium
    linked_issue: 427
    decision_ref: null
  - id: rec-github-blog-002
    title: "DOCUMENT GitHub-Dogma Alignment in Comparative Guide"
    status: accepted-for-adoption
    effort: Low
    linked_issue: 428
    decision_ref: null
  - id: rec-github-blog-003
    title: "EXTEND validate_synthesis.py to Check Pattern Catalog Canonical Example Count"
    status: accepted-for-adoption
    effort: Low
    linked_issue: 428
    decision_ref: null
  - id: rec-github-blog-004
    title: "CONSIDER Squad-Style Agent Charter Files"
    status: deferred
    effort: High
    linked_issue: 429
    decision_ref: null
---

# GitHub Engineering Blog Agent Patterns for Agentic Workflows

## 1. Executive Summary

GitHub Engineering has documented internal AI agent usage patterns across two blog articles (Jan 2026, Mar 2026) that reveal convergent design decisions with Dogma's endogenous methodologies. The research question — *How might GitHub's documented agent patterns inform or validate Dogma's methodologies?* — yields a **validates** verdict across all four investigation areas.

**Key findings**:
1. **Context window management as deliberate skill** — GitHub's "start fresh chats, preserve in custom instructions" pattern matches Dogma's per-day scratchpad + committed substrate (gitignored ephemeral vs. versioned persistent)
2. **Planning agent architecture** — GitHub Plan agent's interrogative clarification complements (not contradicts) Dogma's decompositive Executive Planner; we could adopt pre-delegation interrogation as Phase 0 gate
3. **TDD with AI** — Article 1 empirically validates Dogma's Testing-First Requirement (AGENTS.md § Testing-First Requirement): tests catch what AI gets wrong before users encounter it
4. **Multi-agent coordination** — GitHub Squad's independent-agent-review and explicit-written-memory patterns align with Dogma's Review-always-separate and substrate-versioned-with-code principles

**Verdict**: No contradictions discovered. GitHub patterns validate core Dogma axioms and offer one extension opportunity (interrogative pre-delegation gate). This convergence strengthens confidence that Dogma's endogenous constraints reflect broader industry best practices.

**Recommendation**: **ADOPT** interrogative pre-delegation gate (Rec 4.1); **DOCUMENT** alignment patterns in guides (Rec 4.2).

---

## 2. Hypothesis Validation

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| **H1**: GitHub's context window management strategies will align with Dogma's scratchpad-per-session approach | ✅ **STRONGLY SUPPORTED** | Article 1: "Context window is precious. Start new chat sessions when old context isn't needed." Maps directly to Dogma's per-day scratchpad files (.tmp/\<branch\>/\<YYYY-MM-DD\>.md) — both treat context as finite resource requiring deliberate pruning. |
| **H2**: GitHub Plan agent architecture will contradict Dogma's Executive Planner (decomposition vs. interrogation are competing strategies) | ❌ **REJECTED** | Article 1 Plan agent **interrogates** to clarify requirements; Dogma Planner **decomposes** known requirements into phases. These are complementary, not competing — interrogation refines input, decomposition structures output. No conflict. |
| **H3**: GitHub TDD patterns will validate Dogma's Testing-First Requirement as generalizable to AI-assisted development | ✅ **STRONGLY SUPPORTED** | Article 1: "Just like us developers, AI-assisted tools produce bugs. Tests help catch before users do." Year rollover edge case caught by test suite. Empirical validation that Testing-First (AGENTS.md § Testing-First Requirement) applies equally to AI-generated code. |
| **H4**: GitHub Squad multi-agent coordination will reveal centralized orchestration that contradicts Dogma's distributed handoff topology | ❌ **REJECTED** | Article 2 Squad uses thin coordinator routing to specialists (no heavy centralization), different-agent-review requirement, explicit written memory. These align with Dogma's Executive → Specialist → Takeback handoff and Review-always-separate patterns. Independent overlap validates both. |
| **H5**: GitHub patterns will reveal context-passing failures or lateral communication anti-patterns | ✅ **SUPPORTED** | Article 2: "Different agent must fix rejected work" — prevents same-agent revision loop. Maps to issue #397 finding that lateral agent communication produces 36-100% failure rates. GitHub discovered the same constraint. |

---

## 3. Pattern Catalog

### Pattern 3.1: Context Window as Finite Precious Resource

**Source**: Article 1 (Chris Reddington, Jan 2026)  
**Governor**: [MANIFESTO.md § Agent Communication](../../AGENTS.md#agent-communication)

**Problem**: Long-lived chat sessions accumulate irrelevant history that dilutes focus and wastes context window capacity.

**Solution**: Start new chat sessions when previous context no longer serves current task. Preserve reusable context in custom instructions/prompt files, not in ephemeral chat history.

**Canonical example**:
> Before implementing time zones, I deliberately started a new chat session. The context from our previous conversation (workspace creation, basic countdown logic) wasn't needed anymore. And any context that might have been useful was now included in our custom instructions file. When working with AI tools, that context window is precious. Bringing in irrelevant history clutters the conversation and dilutes focus.

**Dogma alignment**: Scratchpad per-day file structure (.tmp/\<branch\>/\<YYYY-MM-DD\>.md) materializes the same principle — each day is fresh context, essential findings preserved in session summary. Committed substrate (AGENTS.md, guides, research docs) serves as "custom instructions" that persist across sessions.

**Adoption status**: Already implemented (session-management skill § 5.1).

---

### Pattern 3.2: Interrogative Pre-Delegation Gate

**Source**: Article 1 (Plan agent, Jan 2026)  
**Governor**: [MANIFESTO.md § Endogenous-First](../../MANIFESTO.md#1-endogenous-first)

**Problem**: Vague requirements lead to AI making reasonable but wrong assumptions. Developer doesn't discover gaps until implementation reveals them.

**Solution**: Insert interrogative agent **before** decomposition/execution agents. Plan agent asks clarifying questions that reveal edge cases and unstated assumptions.

**Canonical example**:
> I gave it my rough idea: interactive time zone selector, time travel theme, animate between zones, maybe a world map. The Plan agent came back with questions that made me think:
> - Should the circular dial be primary with the world map as secondary, or vice versa?
> - What happens on mobile: dropdown fallback or touch-friendly scroll?
> - When a time zone passes midnight, show "already celebrating" with confetti, or a timer showing how long since midnight?
>
> This is the beauty of working with AI in this way. The Plan agent makes you think, potentially asking a clarifying question and offering options A or B. But as you reflect, you realize the answer is somewhere in between.

**Dogma gap**: Executive Planner decomposes known requirements but doesn't interrogate vague ones. We lack a pre-delegation interrogation gate.

**Adoption opportunity**: Add "Frame + Interrogate" Phase 0 before Planner delegation when requirements are < 50% specified (heuristic: ≥3 "maybe" or "could" phrases in user request).

**Adoption status**: Not implemented (see Recommendation 4.1).

---

### Pattern 3.3: Test-Driven Development Catches AI Bugs

**Source**: Article 1 (TDD with Copilot, Jan 2026)  
**Governor**: [AGENTS.md § Testing-First Requirement](../../AGENTS.md#testing-first-requirement)

**Problem**: AI-generated code can pass syntax checks and even appear correct but fail on edge cases (e.g., year rollover logic, timezone transitions).

**Solution**: Write tests first (expected behavior), let them fail (red), implement to pass (green). AI executes tests, catches failures, adjusts implementation. Human reviews final green state.

**Canonical example**:
> Copilot created test files for time zone utilities, city state management, and countdown logic. All failing tests in a red state. Good!
>
> Then it implemented [...] With access to tools, the custom agent also executed tests in the terminal. Two test cases failed: the logic that determined whether the celebration was being triggered correctly between year rollovers.
>
> Since Copilot had access to the output, the custom agent caught the test failures, adjusted the timezone implementation, and the tests went green.
>
> This is exactly why TDD and thinking about code quality matters. Just like us developers, AI-assisted development can get things wrong. Tests help us catch bugs before users do. The year rollover edge case would have been embarrassing to discover on December 31, given that it was the core capability of the app!

**Dogma alignment**: AGENTS.md § Testing-First Requirement mandates tests before commit for all scripts. Article 1 empirically validates this extends to AI-generated code (not just human-authored scripts).

**Adoption status**: Already implemented for scripts; could extend to agent-generated synthesis docs via validate_synthesis.py (already exists as structural validation).

---

### Pattern 3.4: Drop-Box Shared Memory (Asynchronous > Real-Time)

**Source**: Article 2 (Squad, Mar 2026)  
**Governor**: [AGENTS.md § Agent Communication](../../AGENTS.md#agent-communication)

**Problem**: Real-time synchronization across multiple agents is fragile. Live chat state or vector database lookups introduce coordination failures.

**Solution**: Use versioned file as "drop-box" for shared memory. Agents append decisions asynchronously. No live sync required — file is single source of truth.

**Canonical example**:
> Most AI orchestration relies on real-time chat or complex vector database lookups to keep agents in sync. We've found that this is often too fragile; synchronizing state across live agents is a fool's errand.
>
> Instead, Squad uses a "drop-box" pattern. Every architectural choice, like choosing a specific library or a naming convention, is appended as a structured block to a versioned `decisions.md` file in the repository. This is a bet that asynchronous knowledge sharing inside the repository scales better than real-time synchronization.

**Dogma alignment**: .tmp/\<branch\>/\<date\>.md scratchpad serves identical function — agents append under named sections, Executive integrates. AGENTS.md + committed docs serve as persistent equivalent to Squad's decisions.md.

**Key difference**: Squad's decisions.md is agent-authored; Dogma's scratchpad is human-reviewed before commit (Review gate prevents direct agent commits to authoritative docs).

**Adoption status**: Already implemented (session-management skill § 3).

---

### Pattern 3.5: Different Agent Must Fix Rejected Work

**Source**: Article 2 (Squad, Mar 2026)  
**Governor**: [MANIFESTO.md § Augmentive Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership)

**Problem**: Single agent reviewing its own work produces rubber-stamp approval. Same context window = same blind spots.

**Solution**: Orchestration layer prevents original agent from self-revising. Rejection routes to **different agent** with fresh context window and independent perspective.

**Canonical example**:
> Once the backend specialist drafts the initial implementation, the tester runs their test suite against it. If those tests fail, the tester rejects the code. Crucially, the orchestration layer prevents the original agent from revising its own work. Squad's reviewer protocol can prevent the original author from revising rejected work, and a different agent must step in to fix it. This forces genuine independent review with a separate context window and a fresh perspective, rather than asking a single AI to review its own mistakes.

**Dogma alignment**: Review agent is always separate from implementing agent (Research Scout ≠ Research Reviewer; Executive Docs ≠ Review). Takeback handoff topology enforces this — specialist returns to Executive, Review reads output, sends back for revision if needed.

**Cross-validation**: Issue #397 research found McEntire's empirical data: single-agent 100% success vs. 36-100% multi-agent lateral failure. GitHub Squad independently discovered same constraint ("different agent must fix").

**Adoption status**: Already implemented (Executive Fleet Privileges § Subagent Commit Authority).

---

### Pattern 3.6: Explicit Memory in Prompts > Implicit in Weights

**Source**: Article 2 (Squad, Mar 2026)  
**Governor**: [MANIFESTO.md § Documentation-First](../../MANIFESTO.md#guiding-constraints)

**Problem**: AI's "memory" of project decisions is opaque when embedded in model weights or live session state. Team members can't audit what the AI "knows."

**Solution**: Agent identity built from versioned repository files (charter, history, decisions). These are plain text committed alongside code. Cloning repo = onboarded team.

**Canonical example**:
> We believe an AI team's memory should be legible and versioned. You shouldn't have to wonder what an agent "knows" about your project.
>
> In Squad, an agent's identity is built primarily on two repository files: a charter (who they are) and a history (what they've done), alongside shared team decisions. These are plain text. Because these live in your `.squad/` folder, the AI's memory is versioned right alongside your code. When you clone a repo, you aren't just getting the code; you are getting an already "onboarded" AI team because their memory lives alongside the code directly in the repository.

**Dogma alignment**: AGENTS.md, .agent.md files, SKILL.md files, committed research docs — all serve as explicit agent memory. Agent file frontmatter encodes role, tools, handoffs. Documentation-First principle (AGENTS.md § Guiding Constraints) mandates every workflow/agent/script change must have accompanying docs.

**Key difference**: Squad's memory is per-agent (charter + history); Dogma's is fleet-wide (AGENTS.md governs all agents, individual .agent.md specializes).

**Adoption status**: Already implemented (agent-file-authoring skill, Documentation-First constraint).

---

## 4. Recommendations

### Recommendation 4.1: ADOPT Interrogative Pre-Delegation Gate (Phase 0)

**Action**: Add "Frame + Interrogate" Phase 0 workflow for any session where user request contains ≥3 vague signals ("maybe," "could," "possibly," ambiguous scope).

**Rationale**: Pattern 3.2 (Interrogative Pre-Delegation Gate) shows GitHub Plan agent catches unstated assumptions through clarifying questions. Dogma Executive Planner decomposes known requirements but doesn't interrogate vague ones. Adding Phase 0 interrogation before Planner delegation would surface edge cases **before** phasing/dependencies are locked in.

**Acceptance criteria**:
- [ ] Phase 0 gate added to phase-gate-sequence skill
- [ ] Interrogation prompt template created (stores in data/ or .github/skills/)
- [ ] Executive Planner reads Phase 0 output before decomposition
- [ ] Session scratchpad records interrogation Q&A under `## Phase 0 — Interrogation`
- [ ] Vague-signal heuristic (≥3 "maybe"/"could") encoded as gate trigger

**Effort**: Medium (3-4 hours) — skill update, prompt template, phase-gate-fsm.yml entry

**Status**: Proposed (issue #398 recommendation)

---

### Recommendation 4.2: DOCUMENT GitHub-Dogma Alignment in Comparative Guide

**Action**: Create `docs/guides/github-copilot-patterns-alignment.md` documenting the 6 patterns from this research and their Dogma equivalents.

**Rationale**: Pattern convergence (5/6 patterns already implemented, 1/6 extension opportunity) validates Dogma's endogenous constraints reflect broader industry best practices. Documenting alignment helps onboard contributors who arrive from GitHub Copilot ecosystem.

**Acceptance criteria**:
- [ ] Guide created at `docs/guides/github-copilot-patterns-alignment.md`
- [ ] 6-row table: Pattern | GitHub Source | Dogma Equivalent | Status
- [ ] Cross-references to relevant AGENTS.md sections + skills
- [ ] Link added to docs/guides/README.md catalog

**Effort**: Low (1-2 hours) — documentation-only, no code changes

**Status**: Proposed (issue #398 recommendation)

---

### Recommendation 4.3: EXTEND validate_synthesis.py to Check Pattern Catalog Canonical Example Count

**Action**: Add validation rule to `scripts/validate_synthesis.py`: Pattern Catalog section must contain ≥2 `**Canonical example**:` subheadings.

**Rationale**: Pattern 3.3 (TDD Catches AI Bugs) and Pattern 3.5 (Different Agent Must Fix) both rely on preserved canonical examples for signal fidelity. Current validator checks section presence but not canonical example count. Low-effort enforcement that prevents pattern drift.

**Acceptance criteria**:
- [ ] New validation rule added to validate_synthesis.py
- [ ] Test case added to tests/test_validate_synthesis.py
- [ ] Rule enforced in CI (already runs on every PR touching docs/research/)
- [ ] Error message: "Pattern Catalog must have ≥2 canonical examples (found N)"

**Effort**: Low (30-45 min) — single function, single test case, pre-commit hook already exists

**Status**: Proposed (issue #398 recommendation)

---

### Recommendation 4.4: CONSIDER Squad-Style Agent Charter Files (Deferred)

**Action**: Investigate whether .agent.md files should include explicit "history" section (precedent decisions this agent has made in prior sessions).

**Rationale**: Pattern 3.6 (Explicit Memory in Prompts) shows Squad encodes per-agent history in versioned files. Dogma .agent.md files encode role/tools/constraints but not session history. Could agent charter files benefit from "Prior Decisions" section?

**Tradeoff**: Increases .agent.md file size; introduces maintenance burden (who updates history section?); unclear whether cross-session agent memory improves quality (no empirical data yet).

**Acceptance criteria** (if pursued):
- [ ] Prototype "Prior Decisions" section in 2-3 .agent.md files
- [ ] Run A/B test: sessions with/without history section, measure output quality
- [ ] If quality improves >10%, extend to full fleet; otherwise reject

**Effort**: High (6-8 hours) — prototype, A/B test design, measurement tooling

**Status**: Deferred (insufficient evidence that benefit outweighs cost)

---

## 5. Sources

### Primary Sources

1. **Reddington, Chris** (2026-01-20). "Context windows, Plan agent, and TDD: What I learned building a countdown app with GitHub Copilot." *GitHub Engineering Blog*. Retrieved 2026-03-24. https://github.blog/developer-skills/application-development/context-windows-plan-agent-and-tdd-what-i-learned-building-a-countdown-app-with-github-copilot/  
   Cached: `.cache/sources/github-blog-developer-skills-application-development-context.md`

2. **Gaster, Brady** (2026-03-19). "How Squad runs coordinated AI agents inside your repository." *GitHub Engineering Blog*. Retrieved 2026-03-24. https://github.blog/ai-and-ml/github-copilot/how-squad-runs-coordinated-ai-agents-inside-your-repository/  
   Cached: `.cache/sources/github-blog-ai-and-ml-github-copilot-how-squad-runs-coordina.md`

### Endogenous Cross-References

- [AGENTS.md § Agent Communication](../../AGENTS.md#agent-communication) — Scratchpad protocol, handoff topology
- [AGENTS.md § Testing-First Requirement](../../AGENTS.md#testing-first-requirement) — Scripts must have tests before commit
- [AGENTS.md § Executive Fleet Privileges](../../AGENTS.md#executive-fleet-privileges) — Handoff topology, Review separation
- [MANIFESTO.md § Endogenous-First](../../MANIFESTO.md#1-endogenous-first) — Scaffold from existing knowledge
- [MANIFESTO.md § Augmentive Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership) — Agents surface options, humans decide
- [.github/skills/session-management/SKILL.md](../../.github/skills/session-management/SKILL.md) — Scratchpad lifecycle, per-day files
- [.github/skills/phase-gate-sequence/SKILL.md](../../.github/skills/phase-gate-sequence/SKILL.md) — Inter-phase checkpoint workflow
- [docs/research/multi-agent-collaboration-failure-modes.md](./multi-agent-collaboration-failure-modes.md) (Issue #397) — McEntire's 36-100% lateral communication failure rates
