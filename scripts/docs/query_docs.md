# `query\_docs`

query_docs.py
-------------
Purpose:
    BM25-based CLI for querying the EndogenAI/dogma documentation corpus.
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
    text:  "file:start_line-end_line\n<text_preview[0:200]>\n" per result
    json:  JSON array of result objects

Exit codes:
    0: success
    1: other runtime error
    2: invalid argument (argparse; e.g. unrecognized --scope or --output value)

Usage examples:
    uv run python scripts/query_docs.py "endogenous first" --scope manifesto
    uv run python scripts/query_docs.py "programmatic-first" --scope guides --top-n 3
    uv run python scripts/query_docs.py "BM25" --output json

## Usage

```bash
    uv run python scripts/query_docs.py "endogenous first" --scope manifesto
    uv run python scripts/query_docs.py "programmatic-first" --scope guides --top-n 3
    uv run python scripts/query_docs.py "BM25" --output json
```

<!-- hash:77c6f2af9520dbc6 -->
