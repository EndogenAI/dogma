# `gh` CLI — Curated Agent Reference

> **Agent instruction**: use this file as your first lookup for `gh` command patterns on this repo.  
> For exhaustive flag reference, see `.cache/toolchain/gh/` (auto-generated; gitignored).

---

## Repo-Specific Conventions

| Convention | Value |
|---|---|
| Label namespaces | `type:`, `area:`, `priority:`, `status:` |
| Issue body | Always `--body-file <path>` — never `--body "..."` with multi-line text |
| Projects v2 API | GraphQL only (`gh api graphql`) — no REST for field values |
| Projects v2 auth | `gh auth refresh -s project` once per machine (not per session) |
| Verify-after-act | Every mutating command must be followed by a verification read |
| Priority encoding | Label **and** Projects v2 field — never only one location |

---

## Issues

```bash
gh issue list                                             # all open
gh issue list --label "type:research"                    # filter by label
gh issue list --milestone "Local Compute Foundation"     # filter by milestone
gh issue list --json number,title,labels,assignees       # structured JSON
gh issue view <num> --json title,body,labels,assignees,milestone
gh issue create --title "..." --label "type:research" --body-file /tmp/body.md
gh issue edit <num> --add-label "priority:high"
gh issue edit <num> --remove-label "status:stale"
gh issue edit <num> --milestone "Local Compute Foundation"
gh issue close <num>
```

**Safe body pattern** (avoids shell-quoting issues entirely):
```python
import subprocess, pathlib
body = pathlib.Path('/tmp/issue_body.md')
body.write_text('## Section\n\nContent here...\n')
subprocess.run(['gh', 'issue', 'create', '--title', 'My Issue',
                '--label', 'type:research', '--body-file', str(body)])
body.unlink()
```

### Known Failure Modes — Issues

| Mode | Symptom | Fix |
|------|---------|-----|
| `--body "..."` with multi-line text | `gh` hangs or silently corrupts; terminal freezes | Always use `--body-file <path>` |
| Copilot ignores priority | Priority set only in Projects v2 field, not as label | Add `priority:` label explicitly |
| Copilot misses context | Key facts in linked issues, not in body | Put key facts directly in issue body |

## Pre-Use Validation for Temp Files

Before passing a temporary file to any `gh` command with `--body-file`, validate file integrity:

### Quick Check (Recommended)

```bash
# Validate temp file before gh issue/pr edit or comment
test -s /tmp/body.md && file /tmp/body.md | grep -q "UTF-8\|ASCII" && \
  grep -q "^#" /tmp/body.md && \
  gh issue edit <num> --body-file /tmp/body.md || \
  echo "ERROR: file validation failed"
```

### Full Validation Checklist

| Check | Command | Why |
|-------|---------|-----|
| **Non-empty** | `test -s /tmp/file.md` | Catches silent truncation |
| **Valid UTF-8** | `file /tmp/file.md \| grep -q "UTF-8\|ASCII"` | Catches codec corruption |
| **Expected content** | `grep -q "^##" /tmp/file.md` | Catches incomplete writes |
| **Reasonable size** | `[ $(wc -c < /tmp/file.md) -lt 1000000 ]` | 1MB max for safety |

### Canonical Shell Wrapper

Save this as a local function or script:

```bash
validate_and_edit_issue() {
  local issue_num=$1
  local body_file=$2
  
  # Validation before use
  [[ -s "$body_file" ]] || { echo "ERROR: file empty or missing"; return 1; }
  file "$body_file" | grep -q "UTF-8\|ASCII" || { 
    echo "ERROR: file not valid UTF-8 text"; return 1; 
  }
  grep -q "## " "$body_file" || {
    echo "WARNING: no markdown headings found in $body_file";
  }
  
  # Safe to use now
  gh issue edit "$issue_num" --body-file "$body_file"
  
  # Post-use verification (Tier 3)
  gh issue view "$issue_num" --json body -q '.body' | diff -u "$body_file" - || {
    echo "WARNING: file content did not match after edit"
  }
}
```

### When Pre-Validation is Essential

- ✅ Composing long-form issue bodies (> 500 chars)
- ✅ Multi-line markdown with backticks, code blocks, tables
- ✅ Issue/PR bodies that are critical paths (e.g., epic checklists)
- ✅ After any process that might corrupt file (terminal heredocs, large file writes)

### When Pre-Validation is Optional

- [ ] Simple one-line issue comments (< 100 chars)
- [ ] File is read directly from a committed file (git checkout)

---

## Pull Requests

```bash
gh pr list
gh pr view <num> --json title,body,labels,reviewRequests
gh pr create --fill
gh pr create --title "..." --body-file /tmp/pr_body.md --label "type:feature"
```

### Known Failure Modes — PRs

| Mode | Symptom | Fix |
|------|---------|-----|
| `--body "..."` multi-line | Same as issues — hang or corruption | Use `--body-file` |
| CI failing after push | PR review requested before CI passes | Check `gh run list --limit 3` first |

---

## Labels

```bash
gh label list
gh label create "type:research" --color "e4e669" --description "Research task"
uv run python scripts/seed_labels.py          # idempotent full sync from data/labels.yml
uv run python scripts/seed_labels.py --delete-legacy  # also remove GitHub default flat labels
```

> `seed_labels.py` uses `gh label create/delete` — does **not** require `project` scope.

### Known Failure Modes — Labels

| Mode | Symptom | Fix |
|------|---------|-----|
| Label creation fails silently | No error, but label missing | Run `gh label list` to verify |
| `project` scope used for labels | Auth error | Labels do not need project scope — omit it |

---

## Milestones

```bash
gh api repos/:owner/:repo/milestones                            # list
gh api repos/:owner/:repo/milestones --method POST \
  -f title="Local Compute Foundation" -f description="..."     # create
gh api repos/:owner/:repo/milestones/<num> \
  --method PATCH -f state="closed"                             # close
gh issue list --milestone "Local Compute Foundation"           # filter issues
```

> Milestones on this repo are **thematic**, not time-boxed. Every open issue must be assigned to one.

### Known Failure Modes — Milestones

| Mode | Symptom | Fix |
|------|---------|-----|
| Zero output after `gh api` create | Silent success or silent failure | Immediately run `gh api repos/:owner/:repo/milestones` to verify |
| Milestone name mismatch | `--milestone` filter returns empty | Check exact title with `gh api repos/:owner/:repo/milestones` |

---

## Projects v2

```bash
gh auth refresh -s project            # required once per machine
gh auth status                        # verify "project" scope present

gh project list --owner EndogenAI
gh project create --owner EndogenAI --title "Backlog"
gh project item-list <num> --owner EndogenAI --format json
gh project item-add <num> --owner EndogenAI --url <issue-url>
gh project field-list <num> --owner EndogenAI
```

> **Field values** (Priority, Iteration, Status) require GraphQL — there is no CLI flag:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "<project-id>"
      itemId: "<item-id>"
      fieldId: "<field-id>"
      value: { singleSelectOptionId: "<option-id>" }
    }) { projectV2Item { id } }
  }'
```

### Known Failure Modes — Projects v2

| Mode | Symptom | Fix |
|------|---------|-----|
| `project` scope missing | `gh project` commands return auth error | `gh auth refresh -s project` |
| Field value not set after `gh project item-add` | Item added but Priority/Status blank | Use `updateProjectV2ItemFieldValue` GraphQL mutation |
| Project IDs required for GraphQL | Mutation fails with missing ID args | Use `gh project field-list` and `gh project item-list` to get IDs first |
| Copilot does not see project field values | Agent ignores priority | Encode priority as `priority:` label too |

---

## REST API

```bash
gh api repos/:owner/:repo                    # repo metadata (`:owner/:repo` expands automatically)
gh api repos/:owner/:repo/milestones         # milestone list
gh api repos/:owner/:repo/labels             # label list
gh api repos/:owner/:repo/issues/<num>       # issue detail
```

### Known Failure Modes — REST API

| Mode | Symptom | Fix |
|------|---------|-----|
| Silent failure on POST/PATCH | Zero output, no error | Always follow with a GET to verify state |
| `:owner/:repo` not expanded | 404 | Use `gh api` (auto-expands) not raw `curl` |

---

## GraphQL API

```bash
gh api graphql -f query='{ viewer { login } }'    # verify auth
gh api graphql -f query='
  query {
    repository(owner: "EndogenAI", name: "Workflows") {
      projectsV2(first: 10) { nodes { id title } }
    }
  }'
```

### Known Failure Modes — GraphQL

| Mode | Symptom | Fix |
|------|---------|-----|
| Node IDs differ from REST IDs | Mutation fails with "not found" | GraphQL uses global node IDs (`PVT_...`), not integer IDs |
| Long GraphQL string via `--field query='...'` | Shell quoting corruption | Use `-f query=@/tmp/query.graphql` file form for complex queries |

---

## Verify-After-Act Reference

| Command | Verification |
|---|---|
| `gh issue create` | `gh issue list --state open --limit 3` |
| `gh issue close <num>` | `gh issue view <num> --json state` |
| `gh issue edit <num>` | `gh issue view <num> --json labels,milestone` |
| `gh pr create` | `gh pr view` |
| `git push` | `git log --oneline -1`, then `gh run list --limit 3` |
| milestone create via API | `gh api repos/:owner/:repo/milestones` |
| `gh project item-add` | `gh project item-list <num> --owner EndogenAI --format json` |

---

## GitHub Actions Runs

For agents waiting on CI completion after a `git push` or similar, use the dedicated polling script instead of manual bash loops:

```bash
# Simple case: wait for most recent run on current branch
uv run python scripts/wait_for_github_run.py $(gh run list --limit 1 -q '.[0].databaseId')

# With explicit timeout (default: 150s = 2.5 minutes)
uv run python scripts/wait_for_github_run.py 22890618155 --timeout-secs 300

# Custom repo
uv run python scripts/wait_for_github_run.py 12345 --repo other/repo
```

**Exit codes**:
- `0` — Run completed with conclusion="success"
- `1` — Run completed with conclusion="failure" or timeout reached
- `2` — Run not found or invalid run ID

**Why the script?** Manual polling via shell loops is error-prone (exit code capture, JSON parsing, timeout handling). The [`scripts/wait_for_github_run.py`](../../scripts/wait_for_github_run.py) script encodes:
- Robust JSON parsing via `gh run view --json`
- Configurable timeout and polling interval
- Clear progress reporting
- Correct exit code semantics (success=0, failure=1, not found=2)

**Polling internals** (for debugging):

```bash
# Get run status directly
gh run view <run-id> --json status,conclusion

# Watch logs in real-time (alternative to scripting)
gh run view <run-id> --log

# List runs on a branch
gh run list --branch <branch-name> --limit 5
```

### Known Failure Modes — Runs

| Mode | Symptom | Fix |
|------|---------|-----|
| `databaseId` vs `number` confusion | Script returns "not found" | Use `databaseId` (internal GitHub ID) not `number` (user-facing ID) |
| Timeout too short for cold starts | Timeout reached before run completes | Increase `--timeout-secs` (default 150s safe for most tests) |
| Manual polling loses progress | No record of poll attempts | Use the script to get timestamped progress output |
| Zero exit code implies success | Script exited cleanly but run failed | Always check `gh run view` conclusion after script returns |

---

## Setup Checklist (New Contributor / New Machine)

- [ ] `gh auth login`
- [ ] `gh auth refresh -s project` — add Projects v2 scope
- [ ] `gh auth status` — verify `project` scope present
- [ ] `uv run python scripts/seed_labels.py` — sync labels from `data/labels.yml`
- [ ] `gh api repos/:owner/:repo/milestones` — confirm milestone list

---

## Further Reading

- Full `gh` flag inventory: `.cache/toolchain/gh/` (run `uv run python scripts/fetch_toolchain_docs.py gh` to populate)
- Full synthesis and hypothesis analysis: [`docs/research/github-project-management.md`](../research/github-project-management.md)
- Actionable workflow guide: [`docs/guides/github-workflow.md`](../guides/github-workflow.md)
