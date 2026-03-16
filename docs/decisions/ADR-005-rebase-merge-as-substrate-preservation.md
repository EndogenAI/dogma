---
Status: Accepted
Date: 2026-03-07
Deciders: EndogenAI core team
---

# ADR-005: Rebase-and-Merge as the Canonical PR Merge Strategy

---

## Context

This project treats the git commit graph and GitHub's application layer as **a multi-layered immutable substrate** — a passive side-effect of using GitHub that encodes every decision, correction, and agent action in a cryptographically addressed, content-immutable record.

The three substrate layers, from most durable to least:

| Layer | Durability | What it records |
|---|---|---|
| **git object store** | Cryptographic — content-addressed by SHA; objects persist unless garbage-collected | Every file state ever committed; every commit ever made on any branch |
| **GitHub PR + review layer** | Application-level immutable — PR pages survive merges; reviews/comments are permanent | Intent, reasoning, inline corrections, agent decisions at review time |
| **`main` commit log** | Durable but shaped by merge strategy — the traversable history of the project | Agent decisions encoded as Conventional Commit messages; the "tree rings" of the project |

The **merge strategy** directly governs the quality of Layer 3. Squash-merging collapses N branch commits into one new SHA on `main`. The original commits become **dangling git objects** — preserved in the git object store (Layer 1) but unreachable from `main` via `git log`, `git bisect`, or `git blame`. They are also visible on the GitHub PR page (Layer 2) but not as first-class traversable history.

This repo uses [Conventional Commits](https://www.conventionalcommits.org/) as a deliberate encoding convention — each `type(scope): message` commit is a discrete, dated record of an agent or human decision. Squash-merging degrades this encoding: instead of 5 granular fix commits tracing a debugging sequence, `main` shows one aggregate entry. The density of the tree rings is reduced.

Three merge strategies were evaluated:

| Strategy | Layer 3 quality | Notes |
|---|---|---|
| **Squash merge** | Degraded — N commits → 1 per PR | History readable but encoding granularity lost |
| **Merge commit** | Full — all commits + merge commit | Merges add noise to `main`; non-linear history |
| **Rebase and merge** | Full — all commits, linear | No merge commit noise; linear `git log`; ideal for Conventional Commits |

## Decision Drivers

- Preserve full Conventional Commits granularity on `main` for `git log`, `git bisect`, and `git blame` precision
- Avoid squash-merge degradation of the "tree rings" encoding principle (MANIFESTO.md)
- Linear history without merge-commit noise; rebase-and-merge is the only strategy that achieves both

## Considered Options

See the strategy comparison table in the Context section above. Short summary:

1. **Squash merge** — degrades Layer 3 history; N commits collapsed to 1 per PR; encoding granularity lost
2. **Merge commit** — preserves all commits but adds non-linear merge noise to `main`
3. **Rebase and merge** — full granular history, linear log, no merge commits (**chosen**)

## Decision

**Use rebase-and-merge exclusively. Disable squash merge and merge commit in repository settings.**

All PRs must be merged via "Rebase and merge" in the GitHub UI. This ensures:
- Every commit on every PR branch lands on `main` individually, in chronological order
- `git log --oneline main` reads as a coherent, granular Conventional Commits history
- `git bisect` has maximum precision — bugs can be isolated to a single commit
- `git blame` traces each line to the specific agent decision that introduced it
- The tree rings of the project are dense and readable

## Consequences

- **Contributors must keep PR commits clean**: since every commit lands on `main`, each should be a valid Conventional Commit. Fix-up commits (`fixup!`) should be squashed before PR review, not via GitHub's squash option.
- **`AGENTS.md` guardrail**: agents making commits on PR branches must follow Conventional Commits format, because those commits will be `main` history.
- **Documented in**: `docs/toolchain/git.md` (PR merge strategy row), `docs/guides/github-workflow.md` (section 9), `CONTRIBUTING.md` (Pull Request section).
- **Repository setting**: Settings → General → Pull Requests → uncheck "Allow squash merging" and "Allow merge commits"; check "Allow rebase merging".
- **Existing history**: Prior to 2026-03-07, squash merge was the default. All PR35 and earlier merges are single squash commits on `main`. This is noted for archaeology but does not invalidate the decision going forward.

## Connection to Endogenic Values

This decision is an instance of the **tree rings principle** from `docs/guides/mental-models.md`:

> *"Commit incrementally — each commit is a dated, complete unit of work. Future sessions can see what changed, why, and when."*

It is also an instance of the **Endogenous-First axiom**: the git commit log is part of the system's inherited knowledge. Degrading that record with squash merges reduces what agents can learn from the project's history.

## References

- [`docs/guides/mental-models.md`](../guides/mental-models.md) — Tree Rings metaphor
- [`docs/research/github-as-memory-substrate.md`](../research/infrastructure/github-as-memory-substrate.md) — P4: Commit archaeology, Layer architecture
- [`docs/guides/github-workflow.md`](../guides/github-workflow.md) — Section 9: PR Merge Strategy
- [`docs/toolchain/git.md`](../toolchain/git.md) — PR Merge Strategy section
- Issue [#36](https://github.com/EndogenAI/dogma/issues/36) — decision trigger
- PR [#37](https://github.com/EndogenAI/dogma/pull/37) — initial documentation
