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
  validate_agent_files.py      # Encoding fidelity gate for .agent.md AND SKILL.md files — agent (4 checks) + skill (7 checks); --skills flag; run in CI
  migrate_agent_xml.py         # Bulk-migrate .agent.md body sections to hybrid Markdown + XML format (--dry-run safe)
  pr_review_reply.py           # Post replies to PR inline review comments and resolve threads (--reply-to, --resolve, --batch)
  seed_labels.py               # Idempotent GitHub label seeder — reads data/labels.yml and syncs via gh label create --force (--dry-run, --delete-legacy)
  fetch_toolchain_docs.py      # Cache gh CLI help output as structured Markdown under .cache/toolchain/ (--check, --force, --dry-run)
  wait_for_unblock.py          # Poll a GitHub issue until status:blocked is removed; writes trigger file on exit 0 (--issue, --interval, --timeout, --dry-run)
  detect_drift.py              # Detect value-encoding drift in .agent.md files via watermark-phrase analysis (--agents-dir, --threshold, --fail-below, --format, --output)
  audit_provenance.py          # Audit .agent.md files for governs: provenance annotations; report orphaned files and unverifiable axiom citations (--agents-dir, --manifesto, --format, --output)
  propose_dogma_edit.py        # Programmatic enforcer of the back-propagation protocol — generate ADR-style dogma edit proposals from session evidence (--input, --tier, --affected-axiom, --proposed-delta, --output)
  query_docs.py                # BM25 query CLI over the documentation corpus — scoped retrieval without bulk context loading (query, --scope, --top-n, --output text|json)
  weave_links.py               # Inject Markdown cross-reference links across the corpus via a YAML concept registry (--scope, --dry-run, --registry); idempotent
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
| `cross_ref_density` | `int` | Count of lines referencing `MANIFESTO.md`, `AGENTS.md`, or `docs/guides/` |

**Manifest-level fields** also include `avg_cross_ref_density` (fleet average, `float`). Agents with `cross_ref_density < 1` emit a `WARNING` to stderr.

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

## scripts/fetch_toolchain_docs.py

**Purpose**: Run `gh help` and `gh <subcommand> --help` for every top-level subcommand, convert
the output to structured Markdown, and write it to `.cache/toolchain/`. Agents can look up `gh`
CLI syntax locally without burning tokens or network round-trips.

Per the programmatic-first principle: agents repeatedly look up `gh` CLI flags interactively
(e.g. `gh issue create`, `gh pr merge`, `gh api` pagination). This script encodes that lookup.

**Tests**: [`tests/test_fetch_toolchain_docs.py`](../tests/test_fetch_toolchain_docs.py)

**Usage**:

```bash
# Fetch and cache all gh CLI docs (writes to .cache/toolchain/)
uv run python scripts/fetch_toolchain_docs.py

# Cache a specific tool
uv run python scripts/fetch_toolchain_docs.py --tool uv

# Refresh all tools  
uv run python scripts/fetch_toolchain_docs.py --tool all

# Check freshness for all tools (skip refresh if < 24 hours old)
uv run python scripts/fetch_toolchain_docs.py --tool all --check

# Force re-fetch even if recently cached
uv run python scripts/fetch_toolchain_docs.py --tool all --force

# Dry run — print what would be written without touching the filesystem
uv run python scripts/fetch_toolchain_docs.py --dry-run

# Custom output directory
uv run python scripts/fetch_toolchain_docs.py --output-dir /tmp/toolchain-cache
```

**Outputs**:

| File | Contents |
|------|----------|
| `.cache/toolchain/gh/<subcommand>.md` | Per-subcommand structured Markdown (Usage, Flags table, Examples) |
| `.cache/toolchain/gh/index.md` | All subcommands with one-line descriptions and links |
| `.cache/toolchain/gh.md` | Single aggregate file, all subcommands concatenated |

**Arguments**:

| Flag | Description |
|------|-------------|
| `--tool gh` | CLI tool to document. Currently only `gh` is supported. Default: `gh`. |
| `--output-dir PATH` | Root directory for cache output. Default: `.cache/toolchain/`. |
| `--check` | Skip refresh if cache files are < 24 hours old. |
| `--force` | Always re-fetch, ignoring cache age. |
| `--dry-run` | Print what would be written without touching the filesystem. |

**Exit codes**: `0` success; `1` `gh` not on PATH, no subcommands found, or usage error.

**When to run**: at the start of any session that will issue `gh` CLI commands — especially
before writing new scripts that use the `gh` API, to verify flag names without re-running
interactive lookups.

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

## scripts/validate_agent_files.py

**Purpose**: Programmatic encoding-fidelity gate for `.agent.md` files in `.github/agents/`
and `SKILL.md` files in `.github/skills/`. Prevents encoding drift in the
MANIFESTO → AGENTS.md → agent files / skill files → session prompts inheritance chain.

**Agent file checks (4)**:
1. Valid YAML frontmatter with required fields: `name`, `description`
2. Required section headings present: Endogenous Sources, an Action section (Workflow/Checklist/Scope/Methodology), and a Quality-gate section (Completion Criteria or Guardrails)
3. At least one back-reference to `MANIFESTO.md` or `AGENTS.md` (cross-reference density ≥ 1)
4. No heredoc file writes (`cat >> ... << 'EOF'` patterns) outside negation context

**SKILL.md checks (7)**:
1. Valid YAML frontmatter present
2. Required fields: `name`, `description`
3. Name format: `^[a-z][a-z0-9-]*[a-z0-9]$`, max 64 chars, no consecutive hyphens
4. `name` matches parent directory name
5. Description length: ≥10 and ≤1024 chars (block scalars handled automatically)
6. At least one back-reference to `AGENTS.md` or `MANIFESTO.md` in body
7. Minimum body length: ≥100 chars after frontmatter

**Usage**:

```bash
# Validate a single agent file
uv run python scripts/validate_agent_files.py .github/agents/executive-orchestrator.agent.md

# Validate a single SKILL.md file
uv run python scripts/validate_agent_files.py .github/skills/session-management/SKILL.md

# Validate all agent files in .github/agents/
uv run python scripts/validate_agent_files.py --all

# Validate all SKILL.md files in .github/skills/
uv run python scripts/validate_agent_files.py --skills

# Validate both agent files AND SKILL.md files
uv run python scripts/validate_agent_files.py --all

# In CI (non-zero exit blocks the job)
for f in .github/agents/*.agent.md; do
    uv run python scripts/validate_agent_files.py "$f"
done
```

**Exit codes**: `0` = all checked files pass; `1` = one or more checks failed (specific gaps listed to stdout).

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

## scripts/wait_for_unblock.py

Poll a GitHub issue on an interval until `status:blocked` is removed from its
labels. Designed for two integration patterns:

**Tier 1 — in-session block** (requires an open VS Code session):
Run as a background terminal; the agent session blocks on it with `await_terminal`.
When the label is removed (e.g. by the `unblock-issues.yml` Actions workflow on
PR merge), the terminal exits 0 and the agent auto-continues orchestration.

**Tier 2 — cross-session trigger file**:
Run as a `launchd` / `cron` daemon. On exit 0, writes
`.tmp/triggers/<repo>-issue-<N>.unblocked` — a session-start check discovers it
and presents the ready-to-run orchestration prompt. Works even when VS Code is
closed.

```bash
# In-session: poll every 60s with a 2-hour timeout
uv run python scripts/wait_for_unblock.py --issue 60 --interval 60 --timeout 7200

# Dry-run to verify config
uv run python scripts/wait_for_unblock.py --issue 60 --dry-run

# Explicit repo
uv run python scripts/wait_for_unblock.py --issue 60 --repo EndogenAI/Workflows

# Session-start trigger check
ls .tmp/triggers/*.unblocked 2>/dev/null && cat .tmp/triggers/*.unblocked
```

**Exit codes**: `0` unblocked; `1` timeout; `2` error (bad issue, gh CLI failure).

**Trigger file location**: `.tmp/triggers/<owner>-<repo>-issue-<N>.unblocked`
(gitignored). Contains: issue, repo, title, url, unblocked_at (ISO 8601 UTC).

**Publisher side**: `.github/workflows/unblock-issues.yml` removes `status:blocked`
automatically when a PR containing `Unblocks #N` in its body is merged to `main`.

---

## scripts/audit_provenance.py

**Purpose**: Audit `.agent.md` files in `.github/agents/` for `governs:` frontmatter annotations that trace each file's instructions back to foundational MANIFESTO.md axioms. Extends `detect_drift.py` (phrasal watermark alignment) and `generate_agent_manifest.py` (cross-reference density) with chain-of-custody tracing at the file level.

**Output fields per file**:

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | Filesystem path to the `.agent.md` file (typically an absolute path under `.github/agents/`) |
| `citations` | `list[str]` | Normalised axiom names found in `governs:` |
| `orphaned` | `bool` | `True` if no `governs:` key in frontmatter |
| `unverifiable` | `list[str]` | Axiom names not found as H2/H3 headings in MANIFESTO.md |

**Report-level fields**: `fleet_citation_coverage_pct` (% of files with `governs:`), `total_unverifiable`.

**Axiom vocabulary** (validated against MANIFESTO.md H2/H3 headings):
`endogenous-first`, `algorithms-before-tokens`, `local-compute-first`,
`programmatic-first`, `documentation-first`, `minimal-posture`

**Usage**:

```bash
# Print JSON report to stdout
uv run python scripts/audit_provenance.py

# Human-readable summary (one line per file with ✓/⚠️/✗ status)
uv run python scripts/audit_provenance.py --format summary

# Write report to a file
uv run python scripts/audit_provenance.py --output /tmp/provenance.json

# Use a custom agents directory or MANIFESTO.md path
uv run python scripts/audit_provenance.py --agents-dir path/to/agents/ --manifesto path/to/MANIFESTO.md
```

**Arguments**:

| Flag | Required | Description |
|------|----------|-------------|
| `--agents-dir` | no | Path to `.agent.md` directory (default: `.github/agents/`) |
| `--manifesto` | no | Path to `MANIFESTO.md` (default: repo root) |
| `--output` | no | Write output to this file instead of stdout |
| `--format` | no | `json` (default) or `summary` |

**Exit codes**: `0` on success; `1` on configuration or usage errors (for example, when `--agents-dir` or `--manifesto` point to missing paths).

**Dependencies**: stdlib only — no third-party packages required.

**Tests**: [`tests/test_audit_provenance.py`](../tests/test_audit_provenance.py)

**Related**: `scripts/detect_drift.py` (watermark phrases), `scripts/generate_agent_manifest.py` (cross-reference density), `docs/research/value-provenance.md` (synthesis).

---

## scripts/propose_dogma_edit.py

**Purpose**: Programmatic enforcer of the back-propagation protocol from `docs/research/dogma-neuroplasticity.md`. Reads a scratchpad session file, extracts watermark-phrase evidence lines, runs the coherence check (does the proposed delta remove a watermark phrase?), and emits an ADR-style Markdown proposal. Implements **Algorithms Before Tokens** (`MANIFESTO.md §2`) by encoding the evidence threshold check and coherence validation as a deterministic CLI.

**Imports**: `WATERMARK_PHRASES` from `detect_drift.py`; `extract_manifesto_axioms` from `audit_provenance.py` — does not reimplement either.

**Tests**: [`tests/test_propose_dogma_edit.py`](../tests/test_propose_dogma_edit.py)

**Usage**:

```bash
# Generate a T3 proposal from today's session file
uv run python scripts/propose_dogma_edit.py \
  --input .tmp/feat-value-encoding-fidelity/2026-03-09.md \
  --tier T3 \
  --affected-axiom "Focus-on-Descent" \
  --proposed-delta "Add signal-preservation rules for canonical examples" \
  --output /tmp/proposal.md

# T1 proposal — exits 1 if coherence check fails (blocking)
uv run python scripts/propose_dogma_edit.py \
  --input .tmp/feat-value-encoding-fidelity/2026-03-09.md \
  --tier T1 \
  --affected-axiom "Endogenous-First" \
  --proposed-delta "Clarify scope of endogenous sources" \
  --output /tmp/t1-proposal.md

# Read proposed delta from stdin
echo "Add signal-preservation bullet" | uv run python scripts/propose_dogma_edit.py \
  --input .tmp/branch/2026-03-09.md \
  --tier T2 \
  --affected-axiom "Compression-on-Ascent" \
  --proposed-delta -
```

**Flags**:

| Flag | Required | Description |
|------|----------|-------------|
| `--input PATH` | Yes | Path to a scratchpad session `.md` file |
| `--tier T1\|T2\|T3` | Yes | Stability tier (T1=Axioms, T2=Guiding Principles, T3=Operational Constraints) |
| `--affected-axiom STR` | Yes | Name/heading of the affected axiom or section |
| `--proposed-delta STR` | No | Proposed change text; `-` reads from stdin (default: `-`) |
| `--output PATH` | No | Output path for the Markdown proposal; default: stdout |

**Exit codes**:
- `0` — success, or coherence fails for T2/T3 (non-blocking)
- `1` — coherence fails and tier is T1 (blocking); or session file unreadable

**Stability tiers** (from `dogma-neuroplasticity.md §Pattern Catalog C1`):

| Tier | Layer | Threshold | ADR required? |
|------|-------|-----------|---------------|
| T1 | Axioms (`MANIFESTO.md §axioms`) | 3 signals | Yes |
| T2 | Guiding Principles (`MANIFESTO.md` non-axiom + `AGENTS.md §1`) | 3 signals | Yes |
| T3 | Operational Constraints (`AGENTS.md` sections) | 2 signals | No |

**Dependencies**: stdlib only — imports `detect_drift` and `audit_provenance` from `scripts/` (no third-party packages required beyond existing deps).

**Related**: `scripts/detect_drift.py` (WATERMARK_PHRASES), `scripts/audit_provenance.py` (extract_manifesto_axioms), `docs/research/dogma-neuroplasticity.md` (full back-propagation protocol spec).

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
