# scripts/docs/

Auto-generated per-script Markdown documentation extracted from inline Python docstrings.

---

## What Is This?

Each `.md` file in this directory documents one script from `scripts/`. The content is
extracted from the module-level docstring in each script file — Purpose, Inputs, Outputs,
Usage examples, and Exit Codes.

These files are **committed to the repository** so that documentation is readable without
running any toolchain (Local Compute-First — MANIFESTO.md §3).

---

## Chosen Approach

**Tool**: `pydoc-markdown` (via a thin wrapper script — see below) for docstring extraction,
producing plain Markdown output. No HTML build required.

**Why pydoc-markdown over alternatives**:
- Produces plain `.md` output natively — no HTML pipeline needed
- Supports per-module output (one `.md` per script)
- Lightweight — no Sphinx dependency tree
- Compatible with the existing module-level docstring format used across all scripts

See `docs/research/scripts-documentation-generation.md` for the full tool evaluation.

---

## Regeneration Command

To regenerate documentation for all scripts:

```bash
uv run python scripts/generate_script_docs.py
```

To check which docs are stale (docstring changed since last generation):

```bash
uv run python scripts/generate_script_docs.py --check
```

To regenerate a single script's doc:

```bash
uv run python scripts/generate_script_docs.py --script prune_scratchpad
```

> **Note**: `scripts/generate_script_docs.py` is the forthcoming implementation script
> (see R1 in `docs/research/scripts-documentation-generation.md`). The initial docs in
> this directory were generated manually to prove the pipeline works.

---

## Coverage

| Script | Doc file | Status |
|--------|----------|--------|
| `prune_scratchpad.py` | `prune_scratchpad.md` | ✅ Generated |
| All other scripts | — | Pending `generate_script_docs.py` |

---

## Conventions

- Each doc file is named `<script-name>.md` (without the `.py` extension)
- The first line of each doc is a level-1 heading with the script name
- Sections follow the docstring structure: Purpose, Inputs, Outputs, Usage, Exit Codes
- A hidden HTML comment at the top stores the docstring content hash for staleness detection:
  `<!-- docstring-hash: <sha256[:8]> -->`
