"""
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
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / ".cache" / "sources"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

USER_AGENT = "Mozilla/5.0 (compatible; EndogenAI-Scout/1.0)"
REQUEST_TIMEOUT = 15  # seconds

# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------


def make_slug(url: str) -> str:
    """Derive a filesystem-safe slug from a URL.

    Strips the scheme and 'www.', replaces separators with '-', truncates to 60 chars.
    Example: https://arxiv.org/abs/2512.05470 -> arxiv-org-abs-2512-05470
    """
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"^www\.", "", slug)
    slug = re.sub(r"[/?.=&]", "-", slug)
    slug = re.sub(r"[^a-zA-Z0-9\-_]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60]


# ---------------------------------------------------------------------------
# HTML → Markdown distiller
# ---------------------------------------------------------------------------

_SKIP_TAGS = {
    "script",
    "style",
    "nav",
    "footer",
    "head",
    "noscript",
    "header",
    "aside",
    "form",
    "button",
}
_HEADING_MAP = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}


class _MarkdownConverter(HTMLParser):
    """Convert HTML to clean Markdown, skipping non-content blocks.

    Supported mappings:
      h1–h6  → # through ######
      p      → paragraph (double newline)
      strong/b → **bold**
      em/i   → *italic*
      code   → `inline code`
      pre    → fenced code block
      a      → [text](href)
      ul/li  → - item
      ol/li  → 1. item
      blockquote → > quote
      hr     → ---
      br     → line break
    """

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth: int = 0
        self._skip_stack: list[str] = []
        self._parts: list[str] = []
        self._in_title: bool = False
        self.title: str = ""
        self._in_pre: bool = False
        self._in_code: bool = False
        # Anchor buffering: when inside <a>, collect text separately
        self._link_href: str | None = None
        self._link_parts: list[str] = []
        # List context
        self._list_stack: list[str] = []  # 'ul' or 'ol' per nesting level

    # ------------------------------------------------------------------
    def _skip_active(self) -> bool:
        return self._skip_depth > 0

    def _emit(self, text: str) -> None:
        """Route text to the link buffer or the main output."""
        if self._link_href is not None:
            self._link_parts.append(text)
        else:
            self._parts.append(text)

    # ------------------------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list) -> None:
        tag_lower = tag.lower()
        attrs_dict = dict(attrs)

        if tag_lower in _SKIP_TAGS:
            self._skip_depth += 1
            self._skip_stack.append(tag_lower)
            return
        if self._skip_active():
            return

        if tag_lower == "title":
            self._in_title = True
            return

        if tag_lower in _HEADING_MAP:
            self._emit(f"\n\n{_HEADING_MAP[tag_lower]} ")
        elif tag_lower == "p":
            self._emit("\n\n")
        elif tag_lower == "br":
            self._emit("  \n")
        elif tag_lower in ("strong", "b"):
            self._emit("**")
        elif tag_lower in ("em", "i"):
            self._emit("*")
        elif tag_lower == "code" and not self._in_pre:
            self._emit("`")
            self._in_code = True
        elif tag_lower == "pre":
            self._emit("\n\n```\n")
            self._in_pre = True
        elif tag_lower == "a":
            href = attrs_dict.get("href", "").strip()
            if href and not href.startswith(("javascript:", "#")):
                self._link_href = href
                self._link_parts = []
        elif tag_lower == "li":
            if self._list_stack and self._list_stack[-1] == "ol":
                self._emit("\n1. ")
            else:
                self._emit("\n- ")
        elif tag_lower == "ul":
            self._list_stack.append("ul")
            self._emit("\n")
        elif tag_lower == "ol":
            self._list_stack.append("ol")
            self._emit("\n")
        elif tag_lower == "blockquote":
            self._emit("\n\n> ")
        elif tag_lower == "hr":
            self._emit("\n\n---\n\n")
        elif tag_lower in ("div", "section", "article", "main"):
            self._emit("\n")
        elif tag_lower in ("td", "th"):
            self._emit(" | ")
        elif tag_lower == "tr":
            self._emit("\n")

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()

        if self._skip_stack and self._skip_stack[-1] == tag_lower:
            self._skip_stack.pop()
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_active():
            return

        if tag_lower == "title":
            self._in_title = False
            return

        if tag_lower in _HEADING_MAP:
            self._emit("\n\n")
        elif tag_lower == "p":
            self._emit("\n\n")
        elif tag_lower in ("strong", "b"):
            self._emit("**")
        elif tag_lower in ("em", "i"):
            self._emit("*")
        elif tag_lower == "code" and self._in_code:
            self._emit("`")
            self._in_code = False
        elif tag_lower == "pre":
            self._emit("\n```\n\n")
            self._in_pre = False
        elif tag_lower == "a":
            if self._link_href is not None:
                link_text = "".join(self._link_parts).strip()
                if link_text:
                    self._parts.append(f"[{link_text}]({self._link_href})")
                else:
                    self._parts.append(self._link_href)
                self._link_href = None
                self._link_parts = []
        elif tag_lower in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()
            self._emit("\n")
        elif tag_lower in ("div", "section", "article", "main"):
            self._emit("\n")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            if not self.title:
                self.title = data.strip()
            return
        if self._skip_active():
            return
        # Inside <pre>, preserve whitespace verbatim
        if self._in_pre:
            self._emit(data)
            return
        # Collapse whitespace in normal flow (mirrors browser rendering)
        normalised = re.sub(r"[ \t]+", " ", data)
        self._emit(normalised)

    def get_markdown(self) -> str:
        raw = "".join(self._parts)
        # Collapse excessive blank lines, strip trailing spaces per line
        cleaned = re.sub(r"\n{3,}", "\n\n", raw)
        lines = [line.rstrip() for line in cleaned.split("\n")]
        return "\n".join(lines).strip()


def extract_markdown_and_title(html_bytes: bytes, encoding: str = "utf-8") -> tuple[str, str]:
    """Return (markdown_text, page_title) distilled from raw HTML bytes."""
    try:
        html_str = html_bytes.decode(encoding, errors="replace")
    except (LookupError, UnicodeDecodeError):
        html_str = html_bytes.decode("utf-8", errors="replace")

    converter = _MarkdownConverter()
    converter.feed(html_str)
    return converter.get_markdown(), converter.title


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"version": 1, "sources": {}}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Core fetch logic
# ---------------------------------------------------------------------------


def fetch_url(url: str) -> tuple[bytes, str]:
    """Fetch *url* and return (body_bytes, content_type).

    Raises urllib.error.URLError / urllib.error.HTTPError on failure.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        content_type: str = resp.headers.get_content_type() or "application/octet-stream"
        body = resp.read()
    return body, content_type


def cache_source(url: str, slug: str, dry_run: bool = False, force: bool = False) -> Path:
    """Fetch *url*, cache it under *slug*, update manifest. Return local path."""
    manifest = load_manifest()
    cache_path = CACHE_DIR / f"{slug}.md"

    # Check existing cache
    if not force and slug in manifest["sources"] and cache_path.exists():
        print(f"# cache hit: {cache_path}", file=sys.stderr)
        print(cache_path)
        return cache_path

    if dry_run:
        print(f"[dry-run] Would fetch: {url}", file=sys.stderr)
        print(f"[dry-run] Would save to: {cache_path} (distilled Markdown)", file=sys.stderr)
        print(f"[dry-run] Would update manifest: {MANIFEST_PATH}", file=sys.stderr)
        print(cache_path)
        return cache_path

    # Fetch
    try:
        body, content_type = fetch_url(url)
    except urllib.error.HTTPError as exc:
        print(f"[fetch_source] HTTP error {exc.code} fetching {url}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"[fetch_source] URL error fetching {url}: {exc.reason}", file=sys.stderr)
        sys.exit(1)

    # Warn on PDF
    if content_type == "application/pdf" or url.lower().endswith(".pdf"):
        msg = f"[fetch_source] Warning: {url} appears to be a PDF — binary content saved as-is."
        print(msg, file=sys.stderr)

    # Extract / distil content
    if "html" in content_type:
        text, title = extract_markdown_and_title(body)
    else:
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            text = repr(body)
        title = ""

    # Write cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")

    # Update manifest
    manifest["sources"][slug] = {
        "url": url,
        "slug": slug,
        "title": title,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "file": str(cache_path.relative_to(REPO_ROOT)),
        "content_type": content_type,
        "size_bytes": len(text.encode("utf-8")),
    }
    save_manifest(manifest)

    print(cache_path)
    return cache_path


# ---------------------------------------------------------------------------
# CLI handlers
# ---------------------------------------------------------------------------


def cmd_list() -> None:
    """Print a table of all cached sources."""
    manifest = load_manifest()
    sources = manifest.get("sources", {})
    if not sources:
        print("No cached sources.")
        return

    # Column widths
    col_slug = max(len("SLUG"), max(len(s) for s in sources))
    col_url = max(len("URL"), max(len(v["url"]) for v in sources.values()))
    col_date = 19  # YYYY-MM-DDTHH:MM:SS
    col_size = max(len("SIZE"), max(len(str(v.get("size_bytes", 0))) + 1 for v in sources.values()))

    header = f"{'SLUG':<{col_slug}}  {'URL':<{col_url}}  {'FETCHED_AT':<{col_date}}  {'SIZE':>{col_size}}"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for slug, meta in sorted(sources.items()):
        size_str = f"{meta.get('size_bytes', 0)}B"
        url_str = meta["url"]
        date_str = meta.get("fetched_at", "")
        print(f"{slug:<{col_slug}}  {url_str:<{col_url}}  {date_str:<{col_date}}  {size_str:>{col_size}}")


def cmd_check(url: str, slug: str) -> None:
    """Exit 0 if cached, 2 if not."""
    manifest = load_manifest()
    cache_path = CACHE_DIR / f"{slug}.md"
    if slug in manifest["sources"] and cache_path.exists():
        print(f"cached: {cache_path}")
        sys.exit(0)
    else:
        print(f"not cached: {url}", file=sys.stderr)
        sys.exit(2)


def cmd_path(url: str, slug: str) -> None:
    """Print local path of cached URL without re-fetching; exit 2 if not cached."""
    manifest = load_manifest()
    cache_path = CACHE_DIR / f"{slug}.md"
    if slug in manifest["sources"] and cache_path.exists():
        print(cache_path)
    else:
        print(f"not cached: {url}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fetch_source.py",
        description="Fetch a URL into the local .cache/sources/ cache and maintain a manifest.",
    )
    parser.add_argument("url", nargs="?", help="URL to fetch and cache.")
    parser.add_argument(
        "--slug",
        default=None,
        help="Human-readable filename slug (auto-generated if not provided).",
    )
    parser.add_argument("--check", action="store_true", help="Exit 0 if cached, 2 if not. No fetch.")
    parser.add_argument("--path", action="store_true", help="Print local path without re-fetching.")
    parser.add_argument("--force", action="store_true", help="Re-fetch even if already cached.")
    parser.add_argument("--list", action="store_true", help="List all cached sources.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without fetching or writing.")
    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # --list requires no URL
    if args.list:
        cmd_list()
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    slug = args.slug or make_slug(args.url)

    if args.check:
        cmd_check(args.url, slug)
        return

    if args.path:
        cmd_path(args.url, slug)
        return

    cache_source(args.url, slug, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
