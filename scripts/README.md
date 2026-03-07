# scripts/

Reusable endogenous scripts for the EndogenAI Workflows repo. All scripts are first-class repo
artifacts: committed, documented, and runnable. Per `AGENTS.md` conventions, every script opens
with a docstring describing its purpose, inputs, outputs, and usage examples.

---

## Directory Layout

```
scripts/
  prune_scratchpad.py          # Cross-agent scratchpad session file manager (--init, --annotate, --force, --append-summary, --check-only)
  watch_scratchpad.py          # File watcher — auto-annotates .tmp/*.md on change (uses watchdog)
  scaffold_agent.py            # Scaffold a new .agent.md stub from a validated template
  scaffold_workplan.py         # Scaffold a docs/plans/YYYY-MM-DD-<slug>.md workplan from template
  generate_agent_manifest.py   # Emit a JSON or Markdown skills manifest of all .agent.md files
  fetch_source.py              # Fetch a URL into .cache/sources/ and maintain a manifest (no re-fetching)
  fetch_all_sources.py         # Batch-fetch all URLs from OPEN_RESEARCH.md + research doc frontmatter
  link_source_stubs.py         # Populate ## Referenced By sections in per-source stubs (bidirectional link graph)
  validate_synthesis.py        # Quality gate for D3/D4 synthesis documents — run before any Archivist commit (exit 0 = pass, 1 = fail)
  migrate_agent_xml.py         # Bulk-migrate .agent.md body sections to hybrid Markdown + XML format (--dry-run safe)
  pr_review_reply.py           # Post replies to PR inline review comments and resolve threads (--reply-to, --resolve, --batch)
  seed_labels.py               # Idempotent GitHub label seeder — reads data/labels.yml and syncs via gh label create --force (--dry-run, --delete-legacy)
```

---

## Testing Scripts

Every script in this directory has automated tests in `tests/`. Tests are a first-class artifact, not an afterthought.

**Run all tests**:
```bash
uv run pytest tests/ -v
```

**Run with coverage**:
```bash
uv run pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```

**Run only fast tests** (skip slow + integration):
```bash
uv run pytest tests/ -m "not slow and not integration" -v
```

**Run tests for a single script**:
```bash
uv run pytest tests/test_prune_scratchpad.py -v
```

**Run a specific test**:
```bash
uv run pytest tests/test_prune_scratchpad.py::TestPruneScrapbookAnnotation::test_annotate_is_idempotent -v
```

Tests enforce:
- **Happy path**: Script works with valid inputs
- **Error cases**: Invalid inputs produce clear errors (correct exit codes)
- **Idempotency**: Running a script twice doesn't break things
- **Exit codes**: Every code path has a documented exit code

Before committing any script changes, verify: `uv run pytest tests/test_<script_name>.py --cov=scripts`

For detailed testing guidance, see [`docs/guides/testing.md`](../docs/guides/testing.md).

---

## scripts/prune_scratchpad.py

**Purpose**: Manage cross-agent scratchpad session files in `.tmp/<branch>/<date>.md`.
Initialises today's session file, annotates H2 headings with line ranges, and prunes
completed sections to one-line archive stubs when needed.

**Tests**: [`tests/test_prune_scratchpad.py`](../tests/test_prune_scratchpad.py)

**Usage**:

```bash
# Initialise today's session file (creates .tmp/<branch>/<date>.md if absent)
uv run python scripts/prune_scratchpad.py --init

# Annotate H2 headings with line ranges [Lstart–Lend] (idempotent; run after writes)
uv run python scripts/prune_scratchpad.py --annotate
uv run python scripts/prune_scratchpad.py --annotate --file .tmp/my-branch/2026-03-05.md

# Dry-run prune — print result without writing
uv run python scripts/prune_scratchpad.py --dry-run

# Prune completed sections (only when file exceeds 2000 lines, or use --force)
uv run python scripts/prune_scratchpad.py --force

# Append a session summary block safely (no heredocs; safe for backtick content)
uv run python scripts/prune_scratchpad.py --append-summary "Session closed. Phases 1-3 complete. Open: issue #12."

# Corruption detection only — exits 0 if clean, 1 if corrupted lines found
uv run python scripts/prune_scratchpad.py --check-only
```

**Flags**:

| Flag | Description |
|------|-------------|
| `--init` | Create today's session file if absent; exits 0 |
| `--annotate` | Annotate H2 headings with `[Lstart–Lend]` ranges; idempotent |
| `--dry-run` | Print pruned output without writing |
| `--force` | Prune regardless of line count; also updates `_index.md` |
| `--append-summary TEXT` | Append a `## Session Summary — YYYY-MM-DD` block using Python file I/O (no heredocs) |
| `--check-only` | Scan for corruption (repeated heading patterns); exits 0 if clean, 1 if found |
| `--file PATH` | Override path resolution; target a specific scratchpad file |

**When to run**: at session start (`--init`), after agent writes to check line count,
at session end (`--force` + `--append-summary`) to archive cleanly and update `_index.md`.

---

## scripts/scaffold_workplan.py

**Purpose**: Scaffold a new `docs/plans/YYYY-MM-DD-<slug>.md` workplan file from a standard
template, with today's date and the current git branch pre-filled. Prints the created path to
stdout. Exits 1 without overwriting if the target file already exists.

Per `AGENTS.md`: for any session with ≥ 3 phases or ≥ 2 agent delegations, a workplan must be
created and committed *before* execution starts. This script makes that step one command.

**Usage**:

```bash
# Create a workplan for today
uv run python scripts/scaffold_workplan.py <slug>

# Example
uv run python scripts/scaffold_workplan.py formalize-workflows
# Creates: docs/plans/2026-03-06-formalize-workflows.md
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `slug` | yes | Dash-separated slug, e.g. `fix-session-management`. Converted to title-case for the workplan heading. |

**Exit codes**: `0` file created; `1` missing slug, file already exists, or write error.

**After running**: fill in the `## Objective` section and at least one `## Phase Plan` entry,
then commit with `docs(plans): add workplan for <slug>`.

---

## scripts/watch_scratchpad.py

**Purpose**: File watcher (uses Python `watchdog`) that auto-annotates `.tmp/*.md` session
files on every change. Keeps H2 heading line-range annotations current without any manual
agent step. Includes a cooldown guard to prevent the annotator's own writes from re-triggering
a loop.

**Usage**:

```bash
# Start the watcher (Ctrl-C to stop)
uv run python scripts/watch_scratchpad.py

# Watch a custom directory
uv run python scripts/watch_scratchpad.py --tmp-dir .tmp
```

**Requirement**: `watchdog >= 4.0`. Install with:

```bash
uv add --group dev watchdog
uv sync
```

**VS Code task**: add a background task to `.vscode/tasks.json` to auto-start this watcher
when the workspace opens. Example:

```json
{
  "label": "Watch Scratchpad",
  "type": "shell",
  "command": "uv run python scripts/watch_scratchpad.py",
  "isBackground": true,
  "runOptions": { "runOn": "folderOpen" },
  "presentation": { "reveal": "silent", "panel": "dedicated" }
}
```

---

## scripts/scaffold_agent.py

**Purpose**: Scaffold a new VS Code Copilot `.agent.md` file in `.github/agents/` from a
validated template. Enforces the frontmatter schema and naming conventions defined in
`.github/agents/AGENTS.md`. Validates name uniqueness and description length before writing.

**Usage**:

```bash
# Scaffold a new research sub-agent (dry run first)
uv run python scripts/scaffold_agent.py \
    --name "Research Foo" \
    --description "Surveys sources on foo topics and catalogues findings." \
    --posture creator \
    --area research \
    --dry-run

# Write the file for real
uv run python scripts/scaffold_agent.py \
    --name "Research Foo" \
    --description "Surveys sources on foo topics and catalogues findings." \
    --posture creator \
    --area research
```

**Arguments**:

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | yes | Display name for the agent (must be unique) |
| `--description` | yes | One-line summary ≤ 200 characters |
| `--posture` | no | `readonly` \| `creator` \| `full` (default: `creator`) |
| `--area` | no | Area prefix for fleet sub-agents, e.g. `research` |
| `--dry-run` | no | Print output without writing |

**After running**: fill in the TODO sections in the generated file, add it to
`.github/agents/README.md`, run the name-uniqueness check, and commit.

---

## scripts/generate_agent_manifest.py

**Purpose**: Enumerate all `.agent.md` files in `.github/agents/`, extract `name`, `description`,
`tools`, `posture`, `capabilities`, and `handoffs` from their YAML frontmatter, and emit a
structured skills manifest. Enables orchestrators and sessions to load ~100-token agent stubs
rather than paying the full ~5K-token cost per agent body (lazy-loading pattern; see
`docs/research/agentic-research-flows.md`).

**Output fields per agent**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Agent display name from frontmatter |
| `description` | `str` | One-line summary from frontmatter |
| `tools` | `list[str]` | Tool names declared in frontmatter |
| `posture` | `str` | Derived from tools: `readonly` \| `creator` \| `full` |
| `capabilities` | `list[str]` | 2–5 lowercase-hyphenated tags extracted from description |
| `handoffs` | `list[str]` | Agent names this agent can delegate to (from `handoffs[].agent`) |
| `file` | `str` | Repo-relative path to the `.agent.md` file |

**Posture derivation rules**:
- `full` — tools include any of: `execute`, `terminal`, `agent`, `run`, `browser`
- `creator` — tools include any of: `edit`, `write`, `create`, `notebook` (but not full)
- `readonly` — tools are read/search only, or the list is empty

**Usage**:

```bash
# Print JSON manifest to stdout
uv run python scripts/generate_agent_manifest.py

# Write manifest to a file
uv run python scripts/generate_agent_manifest.py --output .github/agents/manifest.json

# Emit a Markdown table (includes posture, capabilities, handoffs columns)
uv run python scripts/generate_agent_manifest.py --format markdown

# Dry-run: list files that would be processed without generating output
uv run python scripts/generate_agent_manifest.py --dry-run

# Use a custom agents directory
uv run python scripts/generate_agent_manifest.py --agents-dir path/to/agents/
```

**Arguments**:

| Flag | Required | Description |
|------|----------|-------------|
| `--agents-dir` | no | Path to directory containing `.agent.md` files (default: `.github/agents/`) |
| `--output` | no | Write output to this file instead of stdout |
| `--dry-run` | no | Print files that would be processed; do not generate output |
| `--format` | no | `json` (default) or `markdown` |

**Exit codes**: `0` success; `1` agents directory not found or any file fails to parse.

**Dependencies**: stdlib only — no third-party packages required.

---

## scripts/fetch_source.py

**Purpose**: Fetch a URL, distil the HTML into clean Markdown (headings, bold, links, code
blocks, lists — noise stripped), save the result to `.cache/sources/<slug>.md`, and maintain
`.cache/sources/manifest.json`. Agents use `read_file` on cached paths instead of re-fetching
the same pages across sessions, saving tokens and avoiding repeated network round-trips.
Per the programmatic-first principle: fetch once, read many times.

**Usage**:

```bash
# Fetch and cache a URL (prints local path to stdout)
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470

# Fetch with an explicit human-readable slug
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --slug aigne-afs-paper

# Dry run — show what would be fetched/cached without doing it
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --dry-run

# Check if a URL is cached (exit 0 = cached, exit 2 = not cached)
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --check

# Print local path of a cached URL without re-fetching
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --path

# Re-fetch even if already cached
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --force

# List all cached sources (slug, URL, date fetched, file size)
uv run python scripts/fetch_source.py --list
```

**Cache layout**:

```
.cache/
  sources/
    manifest.json          # index: slug → url, title, fetched_at, path, size_bytes
    <slug>.md              # distilled Markdown (HTML→Markdown conversion, noise stripped)
```

**Markdown distillation**: HTML is converted to Markdown — `h1–h6` → `# through ######`,
`strong/em` → `**/**`, `a` → `[text](href)`, `pre/code` → fenced blocks, `ul/ol/li` → `-/1.`,
`blockquote` → `>`. Non-content blocks (`script`, `style`, `nav`, `footer`, `header`, `aside`)
are stripped entirely. Whitespace is normalised. The result is clean, agent-readable Markdown.

**Slug generation**: if `--slug` is not provided, derived from the URL by stripping scheme
and `www.`, replacing `/?.=&` with `-`, collapsing adjacent dashes, and truncating to 60 chars.
Example: `https://arxiv.org/abs/2512.05470` → `arxiv-org-abs-2512-05470`.

**Arguments**:

| Flag | Required | Description |
|------|----------|-------------|
| `url` | conditionally | URL to fetch (not required for `--list`) |
| `--slug` | no | Explicit filename slug |
| `--check` | no | Cache-check only; exit 0 = cached, 2 = miss |
| `--path` | no | Print cached path; exit 2 if not cached |
| `--force` | no | Re-fetch even if cached |
| `--list` | no | Print table of all cached sources |
| `--dry-run` | no | Show what would happen without writing |

**Exit codes**: `0` success; `1` fetch error or usage error; `2` cache miss (`--check`/`--path`).

**Dependencies**: stdlib only — `urllib.request`, `html.parser`, `json`, `pathlib`, `re`.

**Note**: `.cache/` is gitignored. The cache directory is auto-created on first use.

---

## scripts/fetch_all_sources.py

**Purpose**: Batch-fetch and cache all research source URLs referenced across the repo — from
`docs/research/OPEN_RESEARCH.md` "Resources to Survey" bullets and `docs/research/*.md` YAML
frontmatter `sources:` lists. Run this at the start of every research session to pre-warm the
cache so scouts use `read_file` on local `.md` paths instead of re-fetching through the context
window. Implements the **fetch-before-act** posture: populate the cache first, then research.

**Usage**:

```bash
# Dry run — show what URLs would be fetched without fetching
uv run python scripts/fetch_all_sources.py --dry-run

# Fetch everything not yet cached (safe to run repeatedly — skips cached URLs)
uv run python scripts/fetch_all_sources.py

# Force re-fetch all (refresh stale cache)
uv run python scripts/fetch_all_sources.py --force

# Only process OPEN_RESEARCH.md
uv run python scripts/fetch_all_sources.py --open-research-only

# Only process docs/research/*.md frontmatter
uv run python scripts/fetch_all_sources.py --research-docs-only
```

**Sources scanned**:
- `docs/research/OPEN_RESEARCH.md` — lines matching `- [ ] https://...` in "Resources to Survey" sections
- `docs/research/*.md` YAML frontmatter — `sources:` list entries

**Output**: Fetched `.md` files in `.cache/sources/`, manifest updated. Prints a summary:
`N already cached, M newly fetched, P failed`.

**Arguments**:

| Flag | Description |
|------|-------------|
| `--dry-run` | Show what would be fetched; no writes |
| `--force` | Re-fetch even if cached |
| `--open-research-only` | Only scan OPEN_RESEARCH.md |
| `--research-docs-only` | Only scan docs/research/*.md frontmatter |

**Exit codes**: `0` all fetches succeeded; `1` one or more failed.

**Dependencies**: stdlib only. Delegates to `fetch_source.py` per URL.

---

## scripts/link_source_stubs.py

**Purpose**: Maintain the bidirectional link graph between issue syntheses and per-source stubs.
Scans `docs/research/*.md` (issue syntheses) and `docs/research/sources/*.md` (stubs) for
markdown links to stubs, then writes `## Referenced By` entries back into each target stub.
This is the scripted Pass 2 in the three-pass synthesis workflow — never edit `## Referenced By`
sections manually.

**Usage**:

```bash
# Dry-run — show what would change without writing
uv run python scripts/link_source_stubs.py --dry-run

# Apply changes (idempotent — safe to run repeatedly)
uv run python scripts/link_source_stubs.py

# Verbose output
uv run python scripts/link_source_stubs.py --verbose
```

**When to run**: after Pass 1 (per-source stubs) is complete and before Pass 3 (issue synthesis).
Also run after adding new links to any issue synthesis or stub.

**Exit codes**: `0` completed (even if 0 stubs updated); `1` `docs/research/sources/` not found.

**Dependencies**: stdlib only.

---

## scripts/validate_synthesis.py

**Purpose**: Programmatic quality gate for D3 per-source synthesis reports and D4 issue
synthesis documents. Run before any Research Archivist commit to enforce a minimum quality
bar — equivalent to Claude Code's `TaskCompleted` hook.

Auto-detects document type:
- **D3** (file path contains `/sources/`): checks 8 required section headings, URL/cache_path frontmatter
- **D4** (all other paths under `docs/research/`): checks executive summary, status frontmatter

**Usage**:

```bash
# Validate a D3 per-source synthesis report
uv run python scripts/validate_synthesis.py docs/research/sources/<slug>.md

# Validate a D4 issue synthesis
uv run python scripts/validate_synthesis.py docs/research/<slug>.md

# Use a higher minimum line count
uv run python scripts/validate_synthesis.py <file> --min-lines 150

# In Archivist workflow — block commit on failure
uv run python scripts/validate_synthesis.py "$FILE" || exit 1
```

**Checks (D3)**:
1. File exists
2. ≥ 100 non-blank lines (configurable with `--min-lines`)
3. All 8 required section headings present (Citation, Research Question, Theoretical Framework, Methodology, Key Claims, Critical Assessment, Cross-Source Connections, Project Relevance) — accepts both numbered and unnumbered heading formats
4. Frontmatter has `slug`, `title`, `url` (or `source_url`), `cache_path`

**Checks (D4)**:
1. File exists
2. ≥ 100 non-blank lines
3. ≥ 4 `##` headings, including Executive Summary and Hypothesis Validation sections
4. Frontmatter has `title`, `status`

**Exit codes**: `0` = all checks passed; `1` = one or more checks failed (specific gaps listed to stdout).

**Dependencies**: stdlib only.

---

## scripts/migrate_agent_xml.py

**Purpose**: Bulk-migrate `.github/agents/*.agent.md` body sections from plain Markdown prose
to hybrid Markdown + XML format. Implements the migration spec from
`docs/research/xml-agent-instruction-format.md` §8.

Maps `## SectionName` headings to canonical XML tag wrappers per the §4 tag inventory:
`<persona>`, `<instructions>`, `<context>`, `<examples>`, `<tools>`, `<constraints>`, `<output>`.
YAML frontmatter is never touched.

**Usage**:

```bash
# Dry-run a single file (prints diff to stdout, no writes)
uv run python scripts/migrate_agent_xml.py --file .github/agents/executive-researcher.agent.md --dry-run

# Migrate a single file in-place
uv run python scripts/migrate_agent_xml.py --file .github/agents/executive-researcher.agent.md

# Dry-run all files in .github/agents/
uv run python scripts/migrate_agent_xml.py --all --dry-run

# Migrate all files (with min-line threshold — skip short agents)
uv run python scripts/migrate_agent_xml.py --all --min-lines 30
```

**Flags**:

| Flag | Description |
|------|-------------|
| `--file <path>` | Single file to migrate |
| `--all` | Migrate all `*.agent.md` files in `.github/agents/` |
| `--dry-run` | Print diff without writing |
| `--min-lines <int>` | Skip files with fewer instruction lines (default: 30) |
| `--model-scope <prefix>` | Only migrate files where `model` field begins with given prefix (default: disabled — all files processed) |

**Exit codes**: `0` = success; `1` = parse error or well-formedness failure.

**Dependencies**: stdlib only.

---

## scripts/pr_review_reply.py

**Purpose**: Post replies to GitHub PR inline review comments and resolve review threads.
Automates the post-review response loop — after fixing issues, post a reply on each inline
comment (referencing the fix commit) and mark the thread as resolved, without the manual
click-through on GitHub's UI.

Three modes:
- **Single reply**: `--reply-to <comment-id> --body <text>`
- **Single resolve**: `--resolve <thread-node-id>`
- **Batch**: `--batch <json-file>` — reply + resolve in one pass from a JSON array

**Usage**:

```bash
# Reply to a single comment
uv run python scripts/pr_review_reply.py --reply-to 2899252947 --body "Fixed in abc1234."

# Resolve a single thread
uv run python scripts/pr_review_reply.py --resolve PRRT_kwDORfkAR85yvrwz

# Batch from a JSON file (reply + resolve in one pass)
uv run python scripts/pr_review_reply.py --batch .tmp/review-replies.json

# Explicit repo and PR number (defaults auto-detect from gh CLI)
uv run python scripts/pr_review_reply.py --pr 15 --repo EndogenAI/Workflows --batch .tmp/review-replies.json
```

**Batch JSON format**:

```json
[
  {"reply_to": 2899252947, "body": "Fixed in abc1234.", "resolve": "PRRT_kwDORfkAR85yvrwz"},
  {"resolve": "PRRT_kwDORfkAR85yvrw6"},
  {"reply_to": 2899252960, "body": "Removed dead variable."}
]
```

Each entry may have any combination of `reply_to`+`body` (post a reply) and `resolve` (resolve the thread).

**Getting comment IDs and thread node IDs**:

```bash
# Comment database IDs
gh api repos/<owner>/<repo>/pulls/<num>/comments --jq '.[] | {id: .id, path: .path, line: .line}'

# Thread node IDs
gh api graphql -f query='{
  repository(owner:"<owner>",name:"<repo>") {
    pullRequest(number:<num>) {
      reviewThreads(first:20) {
        nodes { id isResolved comments(first:1) { nodes { databaseId } } }
      }
    }
  }
}'
```

**Flags**:

| Flag | Description |
|------|-------------|
| `--pr <num>` | PR number (default: auto-detect from `gh pr view`) |
| `--repo <owner/repo>` | Repository (default: auto-detect from `gh repo view`) |
| `--reply-to <id>` | Comment database ID to reply to |
| `--body <text>` | Reply body text (required with `--reply-to`) |
| `--resolve <id>` | GraphQL node ID of the thread to resolve |
| `--batch <file>` | JSON file with array of reply/resolve operations |

**Exit codes**: `0` = all operations succeeded; `1` = one or more failures.

**Dependencies**: stdlib only; requires `gh` CLI authenticated.

---

## scripts/seed_labels.py

**Purpose**: Idempotent GitHub label seeder. Reads `data/labels.yml` (or a custom path) and
creates or updates every label via `gh label create --force`. Optionally deletes the legacy
GitHub default labels (`bug`, `documentation`, etc.) listed in the `legacy_labels` section.
Designed to bootstrap a fresh fork or keep namespace labels in sync whenever the manifest
changes.

**Tests**: [`tests/test_seed_labels.py`](../tests/test_seed_labels.py)

**Usage**:

```bash
# Preview all actions without making API calls
uv run python scripts/seed_labels.py --dry-run

# Create/update all namespace labels in the current repo
uv run python scripts/seed_labels.py

# Create/update labels AND delete legacy GitHub defaults
uv run python scripts/seed_labels.py --delete-legacy

# Dry-run including legacy deletion
uv run python scripts/seed_labels.py --dry-run --delete-legacy

# Target a specific repo
uv run python scripts/seed_labels.py --repo myorg/myrepo

# Use a custom manifest path
uv run python scripts/seed_labels.py --labels-file path/to/labels.yml
```

**Flags**:

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--labels-file PATH` | no | `data/labels.yml` | Path to the labels YAML manifest |
| `--delete-legacy` | no | `False` | Delete labels listed in `legacy_labels` section |
| `--dry-run` | no | `False` | Print planned actions without making gh API calls |
| `--repo OWNER/REPO` | no | current repo | Target repository |

**YAML manifest format** (`data/labels.yml`):

```yaml
labels:
  - name: "effort:xs"
    color: "c2e0c6"          # 6-digit hex without leading #
    description: "< 30 min"

legacy_labels:
  - "bug"
  - "documentation"
```

**Exit codes**: `0` success; `1` validation/auth error; `2` labels file not found.

**Dependencies**: stdlib + `pyyaml`; requires `gh` CLI authenticated (`gh auth login`).

---

## Script Conventions

All scripts in this repo must follow these conventions (enforced by `Executive Scripter`):

1. **Module docstring** — purpose, inputs, outputs, usage examples, exit codes
2. **`--dry-run` flag** — any script that writes or deletes files must support it
3. **`uv run` invocation** — always invoke via `uv run python scripts/<name>.py`
4. **Committed** — scripts are first-class artifacts, committed with `chore(scripts): ...`
5. **Listed here** — every script must appear in this catalog

When adopting an external tool, document it here with usage notes and the rationale for adoption.

---

## References

- [`AGENTS.md` — Programmatic-First Principle](../AGENTS.md#programmatic-first-principle) — when and how to write scripts
- [`docs/guides/programmatic-first.md`](../docs/guides/programmatic-first.md) — extended guide
- [`docs/guides/session-management.md`](../docs/guides/session-management.md) — scratchpad and session protocols
