# `git` — Curated Agent Reference

> **Agent instruction**: use this file as your first lookup for `git` command patterns on this repo.
> For exhaustive flag reference, see `.cache/toolchain/git/` or `git <subcommand> --help`.

---

## Repo-Specific Conventions

| Convention | Value |
|---|---|
| Commit format | [Conventional Commits](https://www.conventionalcommits.org/) — `type(scope): message` |
| Default branch | `main` |
| Force-push to `main` | **Prohibited** — never `git push --force` to `main` |
| Branch naming | `feat/slug`, `fix/slug`, `chore/slug`, `docs/slug` |
| Pre-commit hooks | `.pre-commit-config.yaml` — ruff check/format run on commit |
| Commit scope | Small, incremental commits — one logical change per commit |
| PR merge strategy | **Rebase and merge** — preserves full Conventional Commits history on `main`; squash merge is disabled |

---

## Conventional Commit Types

| Type | Use for |
|------|---------|
| `feat` | New features or capabilities |
| `fix` | Bug fixes |
| `docs` | Documentation changes only |
| `chore` | Maintenance (deps, config, tooling) |
| `refactor` | Code restructuring without behaviour change |
| `test` | Adding or fixing tests |
| `ci` | CI/CD workflow changes |

---

## Status & Inspection

```bash
git status                          # working tree state
git status --short                  # compact summary
git log --oneline -10               # recent commits, one per line
git log --oneline -5 --graph        # branch graph
git diff                            # unstaged changes
git diff --staged                   # staged changes
git diff HEAD~1                     # diff against previous commit
git show <sha>                      # inspect a specific commit
```

---

## Branching

```bash
git checkout -b feat/my-feature     # create + switch to new branch
git switch -c feat/my-feature       # modern equivalent
git branch                          # list local branches
git branch -d feat/done             # delete merged branch
git checkout main && git pull       # update main before branching
```

---

## Staging & Committing

```bash
git add <file>                      # stage specific file
git add scripts/ tests/             # stage a directory
git add -p                          # interactive staging (hunks)
git commit -m "feat(scripts): add X" # commit with message
git commit --amend --no-edit        # amend last commit (local only)
```

---

## Remote Operations

```bash
git push origin <branch>            # push branch
git push --set-upstream origin <branch>  # push + set tracking
git pull                            # pull current branch
git fetch --prune                   # fetch all, prune deleted remotes
```

**Verify-after-push**: after `git push`, always run `git log --oneline -1` to confirm the push succeeded, then `gh run list --limit 3` to monitor CI.

---

## Undoing Changes

```bash
git restore <file>                  # discard unstaged changes
git restore --staged <file>         # unstage a file
git reset --soft HEAD~1             # undo last commit, keep changes staged
git reset --hard HEAD~1             # undo last commit, discard changes
git stash                           # stash dirty state
git stash pop                       # restore stash
git revert <sha>                    # safe undo via new commit (shareable branches)
```

---

## Tags

```bash
git tag v1.2.3                      # lightweight tag
git tag -a v1.2.3 -m "Release 1.2.3"  # annotated tag
git push origin v1.2.3              # push a tag
git push origin --tags              # push all tags
```

---

## PR Merge Strategy

This repo uses **rebase and merge** for all PRs. Squash merge is disabled.

| Strategy | Effect on `main` |
|---|---|
| **Rebase and merge** ✓ | All branch commits land linearly on `main`; full `git log` / `git bisect` / `git blame` granularity preserved |
| Merge commit | Full history preserved but adds a merge commit to `main` |
| Squash merge ✗ | Collapses N commits into one; destroys per-commit Conventional Commits encoding in the git DAG |

Squash merge is specifically harmful here because this repo treats commit messages as a documentation encoding layer — each `fix(scope):` or `feat(scope):` commit is a discrete durable record of agent decisions.

---

## Known Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| `git push` rejected on `main` | Branch protection or diverged history | Create a PR branch; never force-push main |
| Pre-commit hook blocks commit | ruff check/format failing | Run `uv run ruff check --fix && uv run ruff format` before committing |
| `git commit --amend` causes diverged remote | Amending a pushed commit | Only amend unpushed commits; use `git revert` for pushed commits |
| Merge conflict on `uv.lock` | Two branches updated deps | Run `uv lock` after resolving `pyproject.toml` conflicts |
| CI fails after push | Lint or test failure | Check `gh run list --limit 3`; fix locally, push again — do not re-push without fixing |
