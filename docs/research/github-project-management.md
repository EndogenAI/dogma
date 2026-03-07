---
title: "GitHub Project Management & Automation"
research_issue: "TBD"
status: Final
date: 2026-03-07
sources:
  - .cache/sources/docs-github-com-en-issues-planning-and-tracking-with-project.md
  - .cache/sources/docs-github-com-en-issues-using-labels-and-milestones-to-tra.md
  - .cache/sources/docs-github-com-en-communities-using-templates-to-encourage-.md
  - .cache/sources/docs-github-com-en-discussions.md
  - .cache/sources/cli-github-com-manual-gh_project.md
  - .cache/sources/cli-github-com-manual-gh_issue.md
  - .cache/sources/docs-github-com-en-actions-writing-workflows-choosing-when-y.md
---

# GitHub Project Management & Automation

> **Status**: Final
> **Research Question**: How do we configure GitHub as the primary coordination interface for humans, Copilot agents, and automation in an open-source Python project?
> **Date**: 2026-03-07

---

## 1. Executive Summary

GitHub is the canonical coordination layer for this project — the surface where issues, pull requests, milestones, and labels create a machine-readable project model that humans, the `gh` CLI, GitHub Actions, and VS Code Copilot can all query. This synthesis establishes the setup pattern and command vocabulary to make that model effective.

Eight research questions were addressed across seven primary sources (all GitHub official documentation and the `gh` CLI manual). The most operationally dense finding is in H2 and the Pattern Catalog: the `gh` CLI covers approximately 95% of daily PM work non-interactively — agents can list, create, label, assign, and move issues entirely from the terminal. Projects v2 extends this model via a GraphQL API that has no equivalent REST endpoint, requiring `gh api graphql` for automation beyond simple item listing.

The highest-leverage setup actions for this repo are: (1) adopt a structured label taxonomy with `type:`, `area:`, and `priority:` prefixes; (2) migrate to YAML issue forms; and (3) wire a GitHub Project with auto-add and three built-in field types (Status, Priority, Iteration). These three changes transform GitHub from a passive issue tracker into an active coordination surface that agents can query and update deterministically.

---

## 2. Hypothesis Validation

### H1 — GitHub Projects v2: Field Types and Configuration

**Verdict**: CONFIRMED — richer than expected, with an important GraphQL-only constraint

**Field types** available in Projects v2:

| Field type | Description | Notes |
|---|---|---|
| **Status** | Single-select, built-in | Maps to Kanban columns on Board view |
| **Single select** | Custom enumeration | Use for Priority, Type |
| **Iteration** | Sprint-style cycles with break support | Built-in |
| **Text** | Free-form string | Use for notes, context links |
| **Number** | Numeric value | Use for story points, complexity |
| **Date** | Date picker | Use for target ship dates |

**Board layout**: A Board view is created by grouping on the Status field. GitHub does not enforce a specific status vocabulary; the default values are `Todo`, `In Progress`, `Done` but all are editable. You can save multiple views — Table (backlog triage), Board (sprint work), Roadmap (timeline) — each with independent filters.

**Built-in automation rules** (no Actions required):

- **Auto-archive**: Archive items when closed and not updated for N days (configurable per project).
- **Auto-add from repository**: When an issue/PR is opened in a linked repo and matches filter criteria, automatically add to the project.
- **Item status sync**: When a linked issue/PR closes, the project item status can be auto-set to `Done`.

**GraphQL vs REST**: Projects v2 has **no REST API**. All project creation, field management, and item manipulation requires `gh api graphql` or direct GraphQL queries. REST v3 only covers the legacy Projects v1 (deprecated). Key GraphQL types: `ProjectV2`, `ProjectV2Field`, `ProjectV2Item`. Setting a custom field value on an item requires the `updateProjectV2ItemFieldValue` mutation.

---

### H2 — `gh` CLI Patterns for Daily PM Work

**Verdict**: CONFIRMED — command vocabulary is complete; Projects scope must be authorized upfront

See Pattern Catalog §3.1 for the full quick-reference table.

**Critical prerequisite**: Projects scope requires explicit auth (run once per machine):

```bash
gh auth refresh -s project
gh auth status  # verify "project" appears in scopes
```

**Key patterns for agents querying project state**:

```bash
# Structured JSON output — pipe to jq for scripting
gh issue list --label "type:bug" --json number,title,labels,assignees

# All items in a project with field values (requires project scope)
gh project item-list <project-num> --owner <owner> --format json

# View issue body + labels + assignees in terminal
gh issue view <num> --json title,body,labels,assignees,milestone
```

---

### H3 — Label Taxonomy

**Verdict**: CONFIRMED — colon-prefix convention is the OSS community standard; bulk creation via `gh` CLI is straightforward

GitHub's default labels (`bug`, `enhancement`, etc.) lack structure for agent querying. The canonical OSS pattern uses colon-prefixed namespaces that enable both human filtering and `gh issue list --label` queries:

| Namespace | Purpose | Examples |
|---|---|---|
| `type:` | Work category | `type:bug`, `type:feature`, `type:docs`, `type:research`, `type:chore` |
| `area:` | Codebase domain | `area:scripts`, `area:agents`, `area:docs`, `area:ci` |
| `priority:` | Urgency / importance | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` |
| `status:` | Workflow state (non-project) | `status:blocked`, `status:needs-review`, `status:stale` |

**Bulk create via `gh label create`** — see Pattern Catalog §3.3 for the full shell script block.

Encoding priority in labels (in addition to the Projects v2 Priority field) ensures it is visible to `gh issue list` queries and to Copilot's issue context — both of which do not read project field values directly.

---

### H4 — Issue Template Schema (YAML Issue Forms)

**Verdict**: CONFIRMED — YAML forms are the current standard; Markdown templates are legacy

**Top-level schema**:

| Key | Type | Required | Description |
|---|---|---|---|
| `name` | String | ✓ | Template picker display name |
| `description` | String | ✓ | Template picker subtitle |
| `body` | Array | ✓ | Input element definitions |
| `title` | String | optional | Pre-filled issue title |
| `labels` | Array or CSV | optional | Auto-applied labels |
| `assignees` | Array or CSV | optional | Auto-assigned users |
| `projects` | Array or CSV | optional | Auto-added to project (`owner/number`) |
| `type` | String | optional | Org-level issue type (if enabled) |

**Body field types**:

| type | Description | Key attributes |
|---|---|---|
| `input` | Single-line text | `label`, `placeholder`, `value` |
| `textarea` | Multi-line text | `label`, `value`, `render` (syntax highlight language) |
| `dropdown` | Single or multi-select | `options` (array), `multiple: true` |
| `checkboxes` | Boolean checklist | `options` list, each with `label` and optional `required: true` |
| `markdown` | Static display-only text | `value` (rendered read-only) |
| `upload` | File attachment | `label`, `description` |

**Wire `projects:` in the form** to ensure every issue created from the template is automatically tracked. This is more reliable than the Projects auto-add filter (which only runs on `opened` events and requires matching filter criteria).

---

### H5 — GitHub Discussions: Configuration and Agent Access

**Verdict**: PARTIALLY CONFIRMED — mostly browser/GraphQL API; `gh` CLI has no native Discussions subcommand

**Enabling**: Discussions are enabled per-repository via Settings → Features → Discussions.

**Default categories**: General, Ideas, Polls, Q&A. Announcements is auto-created for public repos. Custom categories can be added with the `Answer` format (enables marking replies as accepted answers).

**`gh` CLI status**: The standard `gh` CLI manual (March 2026) has no `gh discussion` top-level subcommand. Discussion reads and creates require the GraphQL API:

```bash
gh api graphql -f query='
  { repository(owner:"OWNER", name:"REPO") {
      discussions(first:10) { nodes { title number body } }
  } }'
```

**Agent recommendation**: Treat Discussions as a low-frequency community surface. Issues and PR comments are the primary structured coordination layer. Reserve Discussions for announcements and community Q&A only, and do not depend on them for agent-readable project state.

---

### H6 — GitHub Actions for PM Automation

**Verdict**: CONFIRMED — trigger surface is rich; `issues`, `pull_request`, `label`, `milestone` cover all PM use cases

**Key webhook events for PM automation**:

| Event | Most useful activity types | PM use case |
|---|---|---|
| `issues` | `opened`, `labeled`, `milestoned`, `closed` | Auto-label on open, route to project |
| `pull_request` | `opened`, `ready_for_review`, `labeled` | PR size labeler, auto-assign reviewer |
| `label` | `created`, `deleted` | Label taxonomy drift detection |
| `milestone` | `created`, `closed` | Sprint boundary notifications |
| `schedule` | cron expression | Stale bot, weekly digest |

**High-value PM automation recipes**:

1. **Stale bot** (`on: schedule`) — Label issues `status:stale` after 30 days of inactivity; close after a 7-day warning. Use `actions/stale@v9`. Exempt `priority:critical` and `status:blocked`.
2. **Auto-label by path** (`on: pull_request: paths`) — Apply `area:scripts` when `scripts/**` changes. Use `actions/labeler@v5` with `.github/labeler.yml`.
3. **PR size labeler** (`on: pull_request`) — Apply `size:XS/S/M/L/XL` based on diff line count. Use `codelytv/pr-size-labeler@v1`.
4. **Auto-assign on ready** (`on: pull_request: types: [ready_for_review]`) — Assign reviewers when a draft PR transitions to ready.

---

### H7 — Milestones: CLI and REST API

**Verdict**: CONFIRMED — straightforward REST resource; `gh issue list --milestone` is the most practical filter

Milestones are a **REST API** resource (unlike Projects v2). Common CLI patterns:

```bash
# Create a milestone with a due date
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Sprint 3" -f due_on="2026-03-28T00:00:00Z"

# List open milestones
gh api repos/:owner/:repo/milestones

# List issues in a milestone (title accepted directly — no ID lookup needed)
gh issue list --milestone "Sprint 3"

# Close a milestone
gh api repos/:owner/:repo/milestones/<number> --method PATCH -f state="closed"
```

Milestones complement Projects v2: use milestones for time-bounded sprint containers and Projects v2 Iteration fields for sprint planning within the board.

---

### H8 — Copilot Context from Issues

**Verdict**: PARTIALLY CONFIRMED — Copilot reads title, body, and labels; project field values are NOT included

When a VS Code Copilot session references `#<issue-number>`, Copilot reads the issue **title**, **body**, and **labels** from the GitHub API. It does not automatically ingest linked PRs, comments, or Projects v2 field values (Priority, Iteration) unless explicitly pasted into the chat.

**Implications for agent-friendly issue design**:

- **Put context in the body**: Copilot does not traverse cross-reference links. Duplicate key facts in the body rather than pointing to other issues.
- **Use labels as structured metadata**: Labels appear in the Copilot context. `priority:high` and `type:bug` labels are readable by agents and can be used to filter `gh issue list --label` queries.
- **Structured YAML form bodies help agents parse**: YAML issue forms produce consistently-formatted markdown bodies. Field headings become predictable anchors for regex/grep extraction.
- **Encode priority twice**: Set it as a `priority:` label (queryable by `gh` and read by Copilot) AND as a Projects v2 custom field (visible in board views). Do not rely on only one location.

---

## 3. Pattern Catalog

### 3.1 `gh` CLI Quick-Reference Table

| Task | Command |
|---|---|
| List open issues | `gh issue list` |
| List by label | `gh issue list --label "type:bug"` |
| List as JSON | `gh issue list --json number,title,labels,assignees` |
| Create issue | `gh issue create --title "..." --body "..." --label "type:bug"` |
| Assign issue | `gh issue edit <num> --add-assignee @me` |
| Add label | `gh issue edit <num> --add-label "priority:high"` |
| Remove label | `gh issue edit <num> --remove-label "status:stale"` |
| Set milestone | `gh issue edit <num> --milestone "Sprint 3"` |
| Close issue | `gh issue close <num>` |
| View issue (JSON) | `gh issue view <num> --json title,body,labels,assignees,milestone` |
| Create label | `gh label create "type:bug" --color d73a4a --description "Defect"` |
| List labels | `gh label list` |
| List projects | `gh project list --owner <owner>` |
| Create project | `gh project create --owner <owner> --title "Backlog"` |
| View project | `gh project view <num> --owner <owner>` |
| List project items | `gh project item-list <num> --owner <owner> --format json` |
| Add issue to project | `gh project item-add <num> --owner <owner> --url <issue-url>` |
| List project fields | `gh project field-list <num> --owner <owner>` |
| Create project field | `gh project field-create <num> --owner <owner> --name "Priority" --data-type SINGLE_SELECT` |
| Create milestone | `gh api repos/:owner/:repo/milestones --method POST -f title="Sprint N"` |
| List milestones | `gh api repos/:owner/:repo/milestones` |
| List issues by milestone | `gh issue list --milestone "Sprint N"` |
| List open PRs | `gh pr list` |
| View PR (JSON) | `gh pr view <num> --json title,body,labels,reviewRequests` |
| Create PR | `gh pr create --fill` |

### 3.2 Projects v2 Field Types Reference

| Field type | Created via | Agent-queryable via CLI | Notes |
|---|---|---|---|
| Status | Built-in | ✓ `item-list` | Board grouping; default: Todo/In Progress/Done |
| Title | Built-in | ✓ | Mirrors issue/PR title |
| Assignees | Built-in | ✓ | Synced from issue |
| Labels | Built-in | ✓ | Synced from issue |
| Linked PR | Built-in | ✓ | Auto-linked |
| Single select | `field-create --data-type SINGLE_SELECT` | ✓ | Use for Priority, Type |
| Iteration | `field-create --data-type ITERATION` | ✓ | Sprint cycles with break support |
| Text | `field-create --data-type TEXT` | ✓ | Notes, context links |
| Number | `field-create --data-type NUMBER` | ✓ | Story points, complexity |
| Date | `field-create --data-type DATE` | ✓ | Ship dates |

Setting a field value on a project item requires the GraphQL `updateProjectV2ItemFieldValue` mutation — there is no `gh project item-edit` field-value CLI flag. Use `gh api graphql` with the mutation.

### 3.3 Canonical Label Taxonomy — Creation Script

```bash
#!/usr/bin/env bash
# type: namespace
gh label create "type:bug"       --color "d73a4a" --description "Defect in existing behavior"
gh label create "type:feature"   --color "0075ca" --description "New capability"
gh label create "type:docs"      --color "0075ca" --description "Documentation change"
gh label create "type:research"  --color "e4e669" --description "Research task"
gh label create "type:chore"     --color "cfd3d7" --description "Maintenance, dependency update"

# area: namespace
gh label create "area:scripts"   --color "bfd4f2" --description "scripts/ changes"
gh label create "area:agents"    --color "bfd4f2" --description ".github/agents/ changes"
gh label create "area:docs"      --color "bfd4f2" --description "docs/ changes"
gh label create "area:ci"        --color "bfd4f2" --description "CI/CD workflow changes"

# priority: namespace
gh label create "priority:critical" --color "b60205" --description "Blocker — must fix now"
gh label create "priority:high"     --color "e99695" --description "Next sprint"
gh label create "priority:medium"   --color "f9d0c4" --description "This quarter"
gh label create "priority:low"      --color "fef2c0" --description "Nice to have"

# status: namespace
gh label create "status:blocked"      --color "e4e669" --description "Waiting on external dependency"
gh label create "status:needs-review" --color "d4c5f9" --description "Awaiting reviewer"
gh label create "status:stale"        --color "cfd3d7" --description "No activity for 30+ days"
```

Encode this block as `scripts/seed_labels.py` reading from a YAML manifest so the taxonomy is version-controlled and reproducible.

### 3.4 Issue Form Field Types at a Glance

| `type` | Single-line | Multiline | Choices | Boolean | Static | File |
|---|---|---|---|---|---|---|
| `input` | ✓ | | | | | |
| `textarea` | | ✓ | | | | |
| `dropdown` | | | ✓ | | | |
| `checkboxes` | | | | ✓ | | |
| `markdown` | | | | | ✓ | |
| `upload` | | | | | | ✓ |

---

## 4. Recommendations for This Repo

Sequenced — each step is independently completable and the later steps build on the earlier ones.

**R1 — Seed the label taxonomy** (30 min)
Create `scripts/seed_labels.py` reading from a `data/labels.yml` manifest. Delete GitHub's flat default labels first (`gh label delete "bug" --yes`, etc.). Commit the manifest so the taxonomy is reproducible in any fork.

**R2 — Create a GitHub Project** (15 min)
`gh project create --owner <owner> --title "EndogenAI Backlog"`. Add a `Priority` single-select field (Critical/High/Medium/Low). Configure a Board view grouped by Status. Enable auto-add for issues with `type:bug` or `type:feature`. Enable auto-archive for closed items older than 14 days.

**R3 — Migrate issue templates to YAML forms** (45 min)
Replace `.github/ISSUE_TEMPLATE/*.md` with YAML forms. Wire `labels:` and `projects:` in each form's frontmatter. Minimum template set: `bug.yml`, `feature.yml`, `research.yml`. The existing `research.md` template is a candidate for conversion.

**R4 — Add `area:` auto-label workflow** (20 min)
Create `.github/labeler.yml` mapping `scripts/**` → `area:scripts`, `.github/agents/**` → `area:agents`, `docs/**` → `area:docs`. Add `.github/workflows/labeler.yml` using `actions/labeler@v5` on `pull_request`.

**R5 — Add stale bot** (15 min)
Add `.github/workflows/stale.yml` using `actions/stale@v9`. Mark stale after 30 days, close after 7-day warning. Exempt `priority:critical`, `priority:high`, and `status:blocked`.

**R6 — Document `gh auth refresh -s project` in `CONTRIBUTING.md`**
Any contributor or agent working with Projects v2 via CLI must run this once per machine. Add it to the new-contributor setup checklist so agents do not hit silent permission errors.

---

## 5. Open Questions

1. **Project field values in Copilot context**: Does VS Code Copilot read Projects v2 field values (Priority, Iteration) when given an issue number? Official docs are silent. Requires empirical testing — the conservative assumption (they are NOT included) should drive label taxonomy adoption.
2. **`gh discussion` CLI support**: No native `gh discussion` subcommand exists as of March 2026. Is this on the CLI roadmap? Monitoring required before encoding Discussion creation into agent workflows.
3. **Label manifest drift detection**: Should the label taxonomy be enforced in CI? The `label` Actions event could trigger a drift-detection workflow comparing `gh label list --json` against the committed manifest in `data/labels.yml`.
4. **Org-level issue types**: The `type:` top-level key in YAML issue forms requires org-level issue type configuration. This repo is under a personal account — verify whether issue types are available or fall back to using a `type:` label field within the form body.
5. **Bulk project field update via GraphQL**: Setting Priority/Iteration on project items programmatically requires `updateProjectV2ItemFieldValue` mutations. Document the pattern explicitly and consider a `scripts/update_project_item.py` helper.

---

## 6. Sources

| Source | URL | Cached path |
|---|---|---|
| GitHub Projects — About Projects | https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects | `.cache/sources/docs-github-com-en-issues-planning-and-tracking-with-project.md` |
| GitHub Projects — Using the API | https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects | `.cache/sources/docs-github-com-en-issues-planning-and-tracking-with-project.md` |
| Managing Labels | https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels | `.cache/sources/docs-github-com-en-issues-using-labels-and-milestones-to-tra.md` |
| Issue Form Syntax | https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms | `.cache/sources/docs-github-com-en-communities-using-templates-to-encourage-.md` |
| GitHub Discussions | https://docs.github.com/en/discussions | `.cache/sources/docs-github-com-en-discussions.md` |
| gh project CLI | https://cli.github.com/manual/gh_project | `.cache/sources/cli-github-com-manual-gh_project.md` |
| gh issue CLI | https://cli.github.com/manual/gh_issue | `.cache/sources/cli-github-com-manual-gh_issue.md` |
| GitHub Actions — Workflow Triggers | https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows | `.cache/sources/docs-github-com-en-actions-writing-workflows-choosing-when-y.md` |
