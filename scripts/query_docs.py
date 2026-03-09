"""
query_docs.py
-------------
Purpose:
    BM25-based CLI for querying the EndogenAI/Workflows documentation corpus.
    Implements on-demand retrieval over scoped corpus slices, enabling agents
    to fetch precisely the section they need rather than bulk-loading entire
    documents.

    Enacts AGENTS.md Axioms 2 and 3: Algorithms Before Tokens (deterministic
    BM25 scoring over interactive token burn) and Local Compute-First
    (pure-Python, in-process execution, no external services).

Inputs:
    query           Positional — search query string
    --scope         Corpus scope: manifesto|agents|guides|research|toolchain|skills|all
                    (default: all)
    --top-n         Number of results to return (default: 5)
    --output        Output format: text|json (default: text)

Outputs:
    text:  "file:start_line-end_line\\n<text_preview[0:200]>\\n" per result
    json:  JSON array of result objects

Exit codes:
    0: success
    1: other runtime error
    2: invalid argument (argparse; e.g. unrecognized --scope or --output value)

Usage examples:
    uv run python scripts/query_docs.py "endogenous first" --scope manifesto
    uv run python scripts/query_docs.py "programmatic-first" --scope guides --top-n 3
    uv run python scripts/query_docs.py "BM25" --output json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from rank_bm25 import BM25Okapi

# ---------------------------------------------------------------------------
# Repo root resolution
# ---------------------------------------------------------------------------


def find_repo_root() -> Path:
    """Walk up from this file until pyproject.toml is found."""
    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Corpus scope definitions
# ---------------------------------------------------------------------------

SCOPE_PATHS: dict[str, list[str]] = {
    "manifesto": ["MANIFESTO.md"],
    "agents": ["AGENTS.md", ".github/agents/*.agent.md"],
    "guides": ["docs/guides/*.md"],
    "research": ["docs/research/*.md"],
    "toolchain": ["docs/toolchain/*.md"],
    "skills": [".github/skills/**/*.md"],
    "all": [
        "MANIFESTO.md",
        "AGENTS.md",
        ".github/agents/*.agent.md",
        "docs/guides/*.md",
        "docs/research/*.md",
        "docs/toolchain/*.md",
        ".github/skills/**/*.md",
    ],
}


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_markdown(text: str, filepath: str) -> list[dict]:
    """Split Markdown text into paragraph-level chunks.

    Rules:
    - Split on blank lines; each chunk: {text, file, start_line, end_line}
    - Prefix chunk text with nearest parent ## heading for navigability
    - Skip chunks with ≤3 non-whitespace words
    - Treat triple-backtick fences as single atomic chunks
    """
    if not text.strip():
        return []

    lines = text.splitlines()
    # Collect raw segments: (start_0idx, end_0idx, seg_text, is_fence)
    segments: list[tuple[int, int, str, bool]] = []
    i = 0
    seg_start = 0
    seg_lines: list[str] = []

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            # Flush current non-fence paragraph
            if seg_lines:
                segments.append((seg_start, i - 1, "\n".join(seg_lines), False))
                seg_lines = []
            # Collect fence as single atomic unit
            fence_start = i
            fence_lines = [line]
            i += 1
            while i < len(lines):
                fence_lines.append(lines[i])
                if lines[i].strip().startswith("```") and len(fence_lines) > 1:
                    break
                i += 1
            segments.append((fence_start, min(i, len(lines) - 1), "\n".join(fence_lines), True))
            seg_start = min(i + 1, len(lines))

        elif line.strip() == "":
            if seg_lines:
                segments.append((seg_start, i - 1, "\n".join(seg_lines), False))
                seg_lines = []
            seg_start = i + 1

        else:
            if not seg_lines:
                seg_start = i
            seg_lines.append(line)

        i += 1

    # Flush trailing non-fence segment
    if seg_lines:
        segments.append((seg_start, len(lines) - 1, "\n".join(seg_lines), False))

    # Build chunks with heading context
    current_heading = ""
    chunks: list[dict] = []

    for start, end, seg_text, is_fence in segments:
        # Update heading tracker from the first heading line in non-fence segments
        if not is_fence:
            for seg_line in seg_text.splitlines():
                if re.match(r"^#{1,2}\s+", seg_line):
                    current_heading = seg_line.lstrip("#").strip()
                    break

        words = seg_text.split()
        if len(words) <= 3:
            continue

        prefix = f"[{current_heading}] " if current_heading else ""
        chunks.append(
            {
                "text": prefix + seg_text,
                "file": filepath,
                "start_line": start + 1,
                "end_line": end + 1,
            }
        )

    return chunks


# ---------------------------------------------------------------------------
# Corpus building
# ---------------------------------------------------------------------------


def build_corpus(scope: str, repo_root: Path) -> list[dict]:
    """Resolve SCOPE_PATHS[scope] globs from repo_root and chunk all files.

    Raises KeyError for unknown scope.
    Silently skips missing or unreadable files.
    """
    if scope not in SCOPE_PATHS:
        raise KeyError(f"Unknown scope: {scope!r}. Valid scopes: {list(SCOPE_PATHS)}")

    corpus: list[dict] = []
    seen: set[Path] = set()

    for pattern in SCOPE_PATHS[scope]:
        matched = sorted(repo_root.glob(pattern))
        if not matched:
            # Treat as literal path fallback for non-glob patterns
            candidate = repo_root / pattern
            if candidate.exists():
                matched = [candidate]
        for path in matched:
            if path in seen:
                continue
            seen.add(path)
            try:
                file_text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel = str(path.relative_to(repo_root))
            corpus.extend(chunk_markdown(file_text, rel))

    return corpus


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------


def run_query(query: str, corpus: list[dict], top_n: int) -> list[dict]:
    """Run BM25Okapi query over corpus; return top-N results descending by score."""
    if not corpus:
        return []

    tokenized = [chunk["text"].lower().split() for chunk in corpus]
    bm25 = BM25Okapi(tokenized)
    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)

    ranked = sorted(
        zip(scores, corpus),
        key=lambda x: x[0],
        reverse=True,
    )
    return [chunk for _, chunk in ranked[:top_n]]


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_output(results: list[dict], mode: str) -> str:
    """Format results as text or JSON.

    text: "file:start_line-end_line\\n<text_preview[0:200]>\\n" per result
    json: json.dumps(results, indent=2)
    """
    if mode == "json":
        return json.dumps(results, indent=2)

    output_lines: list[str] = []
    for r in results:
        header = f"{r['file']}:{r['start_line']}-{r['end_line']}"
        preview = r["text"][:200]
        output_lines.append(f"{header}\n{preview}\n")
    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="BM25 query over the EndogenAI/Workflows documentation corpus.")
    parser.add_argument("query", help="Search query string")
    parser.add_argument(
        "--scope",
        default="all",
        choices=list(SCOPE_PATHS),
        help="Corpus scope (default: all)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )
    parser.add_argument(
        "--output",
        default="text",
        choices=["text", "json"],
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    corpus = build_corpus(args.scope, repo_root)
    results = run_query(args.query, corpus, args.top_n)
    print(format_output(results, args.output))
    sys.exit(0)


if __name__ == "__main__":
    main()
