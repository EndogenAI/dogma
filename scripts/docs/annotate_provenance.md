# `annotate\_provenance`

annotate_provenance.py
----------------------
Purpose:
    Scans Markdown and .agent.md files in a given scope for MANIFESTO.md axiom
    name mentions in the file body and suggests (or writes in-place) a 'x-governs:'
    YAML frontmatter annotation linking the file to the axioms it references.

    Enacts Pattern P1 (File-Level Provenance via x-governs: Annotation) from
    docs/research/value-provenance.md: makes the chain-of-custody relationship
    between agent files and foundational axioms explicit and machine-checkable.

    Controlled vocabulary: axiom names are sourced from MANIFESTO.md H2/H3 headings
    (primary) and the link registry concepts (supplementary). No axiom names are
    hardcoded as literals in this script.

Inputs:
    --scope       PATH   File or directory to annotate (default: .github/agents/)
    --dry-run            Preview proposed annotations; write nothing
    --registry    PATH   Path to link registry YAML (default: data/link_registry.yml)
    --manifesto   PATH   Path to MANIFESTO.md for axiom vocabulary
                         (default: auto-resolved MANIFESTO.md at repo root)
    --no-recurse         Process only files directly in --scope (no subdirectories)

Outputs:
    For each file that receives (or would receive) a x-governs: annotation:
        [ANNOTATE] path/to/file.md  x-governs: [axiom-one, axiom-two]
    For files already annotated:
        [SKIP] path/to/file.md  already has x-governs:
    For files with no axiom mentions:
        [SKIP] path/to/file.md  no axiom mentions found
    Summary line: "N files annotated (or would annotate), M files skipped"

Exit codes:
    0: success (annotations applied or previewed)
    1: error (registry not found, MANIFESTO.md not found, scope not found, or I/O failure)

Usage examples:
    uv run python scripts/annotate_provenance.py --dry-run
    uv run python scripts/annotate_provenance.py --scope .github/agents/ --dry-run
    uv run python scripts/annotate_provenance.py --scope docs/guides/testing.md
    uv run python scripts/annotate_provenance.py --scope docs/ --no-recurse
    uv run python scripts/annotate_provenance.py --registry data/link_registry.yml --dry-run

## Usage

```bash
    uv run python scripts/annotate_provenance.py --dry-run
    uv run python scripts/annotate_provenance.py --scope .github/agents/ --dry-run
    uv run python scripts/annotate_provenance.py --scope docs/guides/testing.md
    uv run python scripts/annotate_provenance.py --scope docs/ --no-recurse
    uv run python scripts/annotate_provenance.py --registry data/link_registry.yml --dry-run
```

<!-- hash:ab7c8cad55edadac -->
