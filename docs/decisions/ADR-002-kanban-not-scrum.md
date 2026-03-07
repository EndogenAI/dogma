# ADR-002: Kanban Over Scrum for Project Planning

**Date**: 2026-03-07
**Status**: Accepted
**Deciders**: EndogenAI core team

---

## Context

The project needs a planning methodology. The options are:
- **Scrum**: fixed sprints, retrospectives, velocity tracking
- **Kanban**: continuous flow, WIP limits, pull-based
- **Flow/ad-hoc**: no formal structure

The project has irregular contributor cadence — both human contributors and AI agent sessions arrive on-demand, not on a fixed schedule. Agent sessions can complete weeks of work in hours, and may be triggered by a single conversation.

## Decision

**Use Kanban.** Work flows continuously from `backlog → in-progress → review → done`. No fixed sprint cycles, no retrospectives. GitHub Projects v2 is the board. Issues are the primary unit of work.

Scrum's fixed sprint cycles are incompatible with on-demand agent architecture: agents don't attend retrospectives, and a single agent session may close an entire sprint's worth of issues.

## Consequences

- GitHub Projects v2 board should be configured as a Kanban board (not iteration-based).
- WIP limit on `in-progress`: max 3 issues at once for humans; agents may exceed this during a session.
- Milestone planning is used for longer-horizon goals (not sprint planning): each milestone maps to a release or a major phase.
- `docs/guides/workflows.md` PM section documents this decision.

## References

- [`docs/research/pm-and-team-structures.md`](../research/pm-and-team-structures.md) — RQ3: Sprint vs. Kanban vs. Flow
- [`docs/guides/workflows.md`](../guides/workflows.md) — Project Management Workflow section
