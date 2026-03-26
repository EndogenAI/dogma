# `fetch\_source`

fetch_source.py — Source fetcher and local cache for EndogenAI research scouts.

Purpose
-------
Fetch a URL, distil the HTML into clean Markdown (headings, bold, links, code blocks,
lists — noise stripped), save the result to a local cache directory (.cache/sources/),
and maintain a manifest so subsequent requests check the cache before hitting the
network. Agents can then use read_file on the cached .md path instead of re-fetching,
saving tokens and network round-trips.

The distillation step converts HTML structure directly into Markdown rather than dumping
plain text, so the cached file is immediately useful as research context without further
processing.

This script exists because research scouts repeatedly re-fetched the same web sources
(Anthropic Engineering, arXiv, Towards Data Science) across sessions, loading 10–20 KB
pages through the context window every time. Per the programmatic-first principle in
AGENTS.md, that task has now happened more than twice interactively and must be encoded
as a committed script.

Inputs
------
- A URL (positional argument)
- Optional flags: --slug, --check, --path, --force, --list, --dry-run

Outputs
-------
- Distilled Markdown file at .cache/sources/<slug>.md
- Updated .cache/sources/manifest.json
- Local file path printed to stdout on success
- Cache-hit note printed to stderr when returning a cached result
- --list: table of all cached sources (slug, URL, date fetched, file size)

Usage Examples
--------------
# Fetch and cache a URL (prints local path to stdout)
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470

# Fetch with explicit slug
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --slug aigne-afs-paper

# Dry run: show what would happen without fetching/writing
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --dry-run

# Check if URL is cached (exit 0 = cached, exit 2 = not cached)
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --check

# Print local path of cached URL without re-fetching
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --path

# Re-fetch even if already cached
uv run python scripts/fetch_source.py https://arxiv.org/abs/2512.05470 --force

# List all cached sources
uv run python scripts/fetch_source.py --list

Exit Codes
----------
0  Success (fetch or cache hit)
1  Fetch error (network failure, HTTP 4xx/5xx) or usage error
2  Cache miss (--check mode only)

## Usage

```bash
# No usage example found in docstring
```

<!-- hash:7132ba11ff209b01 -->
