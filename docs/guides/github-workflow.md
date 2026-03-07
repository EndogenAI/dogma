# GitHub Workflow Guide

A concise, locally-queryable reference for GitHub operations on this repository — covering the `gh` CLI command vocabulary, label taxonomy, issue design conventions, milestone/project patterns, and Copilot-aware issue authoring.

This guide is derived from [`docs/research/github-project-management.md`](../research/github-project-management.md). Consult that document for hypothesis analysis, trade-off discussion, and the full setup reasoning.

---

## 1. Core Conventions

| Convention | Value |
|---|---|
| Label namespaces | `type:`, `area:`, `priority:`, `status:` |
| Milestone shape | Thematic (no due date unless a release is imminent) |
| Issue body format | YAML issue forms (not legacy Markdown templates) |
| Priority encoding | Label **and** Projects v2 field — never only one location |
| Project API | GraphQL only (no REST for Projects v2) |
| Discussions | Low-frequency community surface only; do not use as coordination layer |

---

## 2. `gh` CLI Quick Reference

```bash
# --- Issues ---
gh issue list                                    # all open issues
gh issue list --label "type:research"            # filter by label
gh issue list --milestone "Local Compute"        # filter by milestone
gh issue list --json number,title,labels,assignees  # structured JSON output
gh issue view <num> --json title,body,labels,assignees,milestone
gh issue create --title "..." --body "..." --label "type:research"
gh issue edit <num> --add-label "priority:high"
gh issue edit <num> --remove-label "status:stale"
gh issue edit <num> --milestone "Local Compute Foundation"
gh issue close <num>

# --- Labels ---
gh label list
gh label create "type:research" --color "e4e669" --description "Research task"

# --- Milestones (REST API) ---
gh api repos/:owner/:repo/milestones               # list
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Local Compute Foundation" -f description="..."   # create
gh issue list --milestone "Local Compute Foundation"

# --- Projects v2 ---
gh auth refresh -s project                         # REQUIRED once per machine
gh project list --owner EndogenAI
gh project create --owner EndogenAI --title "Backlog"
gh project item-list <num> --owner EndogenAI --format json
gh project item-add <num> --owner EndogenAI --url <issue-url>
gh project field-list <num> --owner EndogenAI

# --- PRs ---
gh pr list
gh pr view <num> --json title,body,labels,reviewRequests
gh pr create --fill
```

> **Projects v2 field values** (Priority, Iteration) require `gh api graphql` with the `updateProjectV2ItemFieldValue` mutation — there is no CLI flag for setting field values.

---

## 3. Label Taxonomy

This repo uses colon-prefixed label namespaces. All four namespaces are used together:

| Namespace | Purpose | Values |
|---|---|---|
| `type:` | Work category | `type:bug`, `type:feature`, `type:docs`, `type:research`, `type:chore` |
| `area:` | Codebase domain | `area:scripts`, `area:agents`, `area:docs`, `area:ci` |
| `priority:` | Urgency | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` |
| `status:` | Workflow state | `status:blocked`, `status:needs-review`, `status:stale` |

**Rule**: Every issue should have at minimum one `type:` label and one `priority:` label. `area:` labels are auto-applied via the labeler workflow. `status:` labels are applied manually as issues move through the workflow.

To seed the full label taxonomy, run `scripts/seed_labels.py` (creates all labels idempotently from `data/labels.yml`).

---

## 4. Issue Authoring for Copilot Readability

VS Code Copilot reads issue **title**, **body**, and **labels** when given `#<number>`. It does **not** read:
- Projects v2 field values (Priority, Iteration)
- Issue comments
- Cross-linked issues

**Implications**:

- **Encode priority as a label** (not only in project fields): `priority:high` appears in Copilot context; project field values do not.
- **Self-contained body**: Put key facts in the body directly. Do not rely on linked issues. Copilot does not traverse cross-references.
- **Structured headings**: YAML issue form output produces predictable heading anchors (`## Research Question`, `## Gate Deliverables`) that agents can grep.
- **Use the checklist items** in Gate Deliverables to signal progress; Copilot reads checked/unchecked markdown checkboxes.

---

## 5. Milestone Conventions

Milestones on this repo are **thematic** (not time-boxed sprints unless a release is imminent):

| Milestone | Scope |
|---|---|
| **Local Compute Foundation** | Research and implementation for local model inference and MCP distribution |
| **Session & Agent Efficiency** | Async handling, LLM tier strategy, agent format, context management |
| **Long-Horizon Research** | Foundational methodology, episodic memory, AIGNE evaluation |

Rules:
- Every open issue must be assigned to a milestone.
- Milestone closure: when all issues are closed/resolved, the milestone is closed via `gh api repos/:owner/:repo/milestones/<num> --method PATCH -f state="closed"`.
- New milestones require a scratchpad or workplan entry explaining the scope.

---

## 6. GitHub Actions PM Automation

Recommended workflows (see R4 and R5 in the synthesis):

| Workflow | File | Trigger | Action |
|---|---|---|---|
| Auto-label by path | `.github/workflows/labeler.yml` | `pull_request` | Apply `area:` labels from `.github/labeler.yml` |
| Stale bot | `.github/workflows/stale.yml` | `schedule` (daily) | Label stale after 30 days; close after 7-day warning |
| PR size labeler | `.github/workflows/pr-size.yml` | `pull_request` | Apply `size:XS/S/M/L/XL` |

Exempt from stale bot: issues with `priority:critical`, `priority:high`, or `status:blocked`.

---

## 7. `gh issue create` Body Safety

Passing multi-line bodies via `--body "..."` on the command line causes `gh` to hang or silently corrupt content when the body contains backticks, newlines, or special characters. This is the most common source of frozen terminal sessions.

**Always use `--body-file`** or Python `subprocess` with a list of args:

```python
# Safe pattern — avoids shell-quoting completely
import subprocess, pathlib
body = pathlib.Path('/tmp/issue_body.md')
body.write_text('## Section\\n\\nContent here...\\n')
subprocess.run(['gh', 'issue', 'create', '--title', 'My Issue',
                '--label', 'type:research', '--body-file', str(body)])
body.unlink()
```

Or with a temp file in bash (only for short, backtick-free bodies):
```bash
printf '%s' "$BODY" > /tmp/body.md
gh issue create --title "..." --body-file /tmp/body.md
```

---

## 8. Verify-After-Act Protocol

Any `gh` command that creates or modifies remote state **must be immediately followed** by a verification read:

| Command | Verification |
|---|---|
| `gh issue create` | `gh issue list --state open --limit 3` |
| `gh issue close <num>` | `gh issue view <num> --json state` |
| `gh issue edit <num>` | `gh issue view <num> --json labels,milestone` |
| `gh pr create` | `gh pr view` |
| `git push` | `git log --oneline -1` |
| milestone create via API | `gh api repos/:owner/:repo/milestones` |

Zero error output is **not** confirmation of success. Always verify.

---

## 9. Setup Checklist (New Contributor / New Machine)

- [ ] `gh auth login` — authenticate with GitHub
- [ ] `gh auth refresh -s project` — add Projects v2 scope (required once per machine)
- [ ] `gh auth status` — verify `project` scope is present
- [ ] Run `python scripts/seed_labels.py` (once labels are seeded — idempotent)
- [ ] Confirm milestone list: `gh api repos/:owner/:repo/milestones`

---

## 10. Further Reading

- Full synthesis with hypothesis analysis: [`docs/research/github-project-management.md`](../research/github-project-management.md)
- OSS documentation patterns: [`docs/research/oss-documentation-best-practices.md`](../research/oss-documentation-best-practices.md)
- PM and team structures: [`docs/research/pm-and-team-structures.md`](../research/pm-and-team-structures.md)
