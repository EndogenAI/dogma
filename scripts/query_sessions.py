"""
query_sessions.py
-----------------
Purpose:
    BM25-based CLI for querying cross-session scratchpad files in .tmp/*/
    Enables retrieval of prior session findings, decisions, and context across
    branches and dates.

    Enacts AGENTS.md Axioms 2 and 3: Algorithms Before Tokens (deterministic
    BM25 scoring over interactive token burn) and Local Compute-First
    (pure-Python, in-process execution, no external services).

Inputs:
    query           Positional — search query string
    --branch        Branch filter: <branch-slug> or "all" (default: all)
    --top-n         Number of results to return (default: 5)
    --output        Output format: text|json (default: text)

Outputs:
    text:  "branch/file:start_line-end_line\n<text_preview[0:200]>\n" per result
    json:  JSON array of result objects

Exit codes:
    0: success
    1: other runtime error
    2: invalid argument (argparse)

Usage examples:
    uv run python scripts/query_sessions.py "memory governance"
    uv run python scripts/query_sessions.py "issue #552" --branch feat-open-harness-sprint
    uv run python scripts/query_sessions.py "Phase 1 completed" --branch all --top-n 10
    uv run python scripts/query_sessions.py "Research Scout" --output json
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
# Session file discovery
# ---------------------------------------------------------------------------


def collect_session_files(repo_root: Path, branch_filter: str) -> list[Path]:
    """
    Collect all scratchpad files from .tmp/*/

    Args:
        repo_root: Repository root path
        branch_filter: "all" or specific branch slug

    Returns:
        List of session file paths (excludes _index.md)
    """
    tmp_dir = repo_root / ".tmp"
    if not tmp_dir.exists():
        return []

    session_files = []

    for branch_dir in tmp_dir.iterdir():
        if not branch_dir.is_dir():
            continue

        # Check branch filter
        if branch_filter != "all" and branch_dir.name != branch_filter:
            continue

        # Collect all .md files except _index.md
        for md_file in branch_dir.glob("*.md"):
            if md_file.name != "_index.md":
                session_files.append(md_file)

    return sorted(session_files)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_markdown(text: str, filepath: str) -> list[dict]:
    """Split Markdown text into paragraph-level chunks.

    Rules:
    - Split on blank lines; each chunk: {text, file, start_line, end_line, branch}
    - Prefix chunk text with nearest parent ## heading for navigability
    - Skip chunks with ≤3 non-whitespace words
    - Treat triple-backtick fences as single atomic chunks
    """
    if not text.strip():
        return []

    lines = text.splitlines()
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
                heading_match = re.match(r"^##\s+(.+)", seg_line)
                if heading_match:
                    current_heading = heading_match.group(1)
                    break

        # Skip trivial chunks
        word_count = len(re.findall(r"\S+", seg_text))
        if word_count <= 3:
            continue

        # Prefix with heading context
        chunk_text = seg_text
        if current_heading and not seg_text.startswith("#"):
            chunk_text = f"## {current_heading}\n{seg_text}"

        # Extract branch from filepath (.tmp/<branch>/<date>.md)
        filepath_obj = Path(filepath)
        branch = filepath_obj.parent.name if filepath_obj.parent.name != ".tmp" else "unknown"

        chunks.append(
            {
                "text": chunk_text,
                "file": str(filepath),
                "branch": branch,
                "start_line": start + 1,  # 1-indexed
                "end_line": end + 1,
            }
        )

    return chunks


# ---------------------------------------------------------------------------
# BM25 indexing and search
# ---------------------------------------------------------------------------


def index_sessions(session_files: list[Path]) -> tuple[BM25Okapi, list[dict]]:
    """
    Build BM25 index from session files.

    Args:
        session_files: List of session file paths

    Returns:
        (bm25_index, chunks) tuple
    """
    all_chunks = []

    for filepath in session_files:
        try:
            text = filepath.read_text(encoding="utf-8")
            chunks = chunk_markdown(text, str(filepath.relative_to(find_repo_root())))
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Warning: skipping {filepath}: {e}", file=sys.stderr)
            continue

    if not all_chunks:
        # Return empty index
        return BM25Okapi([[""]]), []

    # Tokenize for BM25
    tokenized = [chunk["text"].lower().split() for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized)

    return bm25, all_chunks


def search_sessions(query: str, bm25_index: BM25Okapi, chunks: list[dict], top_n: int) -> list[dict]:
    """
    Search session chunks using BM25.

    Args:
        query: Search query string
        bm25_index: Pre-built BM25 index
        chunks: Chunk metadata list
        top_n: Number of results to return

    Returns:
        List of top-n scored chunks
    """
    if not chunks:
        return []

    tokenized_query = query.lower().split()
    scores = bm25_index.get_scores(tokenized_query)

    # Pair scores with chunks
    scored = [(score, chunk) for score, chunk in zip(scores, chunks)]
    scored.sort(reverse=True, key=lambda x: x[0])

    return [chunk for score, chunk in scored[:top_n] if score > 0]


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_text(results: list[dict]) -> str:
    """Format results as human-readable text."""
    if not results:
        return "No results found.\n"

    output = []
    for chunk in results:
        # Format: branch/file:L1-L2
        location = f"{chunk['file']}:{chunk['start_line']}-{chunk['end_line']}"
        preview = chunk["text"][:200].replace("\n", " ")
        output.append(f"{location}\n{preview}\n")

    return "\n".join(output)


def format_json(results: list[dict]) -> str:
    """Format results as JSON array."""
    return json.dumps(results, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Query cross-session scratchpad files")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--branch", default="all", help="Branch filter: <branch-slug> or 'all' (default: all)")
    parser.add_argument("--top-n", type=int, default=5, help="Number of results to return (default: 5)")
    parser.add_argument(
        "--output", choices=["text", "json"], default="text", help="Output format: text|json (default: text)"
    )

    args = parser.parse_args()

    try:
        repo_root = find_repo_root()
        session_files = collect_session_files(repo_root, args.branch)

        if not session_files:
            print(f"No session files found for branch filter: {args.branch}", file=sys.stderr)
            return 1

        bm25_index, chunks = index_sessions(session_files)
        results = search_sessions(args.query, bm25_index, chunks, args.top_n)

        if args.output == "json":
            print(format_json(results))
        else:
            print(format_text(results))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
