# `migrate\_agent\_xml`

scripts/migrate_agent_xml.py

Bulk-migrate .agent.md body sections to hybrid Markdown + XML format.

Purpose:
    Transform one or more .github/agents/*.agent.md files from plain-prose bodies
    to the hybrid Markdown + XML schema recommended by the EndogenAI xml-agent-
    instruction-format research (docs/research/xml-agent-instruction-format.md).

    The hybrid schema keeps `## Section` headings as the outer document skeleton
    (for human readability and IDE navigation) while wrapping each section's prose
    content in a semantic XML tag for Claude's instruction parsing.

    YAML frontmatter is never modified. Only the body below the closing `---` fence
    is transformed.

Behaviour:
    1. Parse YAML frontmatter — preserve verbatim, do not touch.
    2. Split body into sections at `## Heading` boundaries.
    3. For each section, look up the canonical XML tag from the heading-to-tag map.
    4. If a tag is found and the section body has ≥ MIN_BODY_LINES non-empty lines,
       wrap the body in <tag>...</tag> preserving all blank lines and indentation.
    5. Sections not in the tag map, or with fewer than MIN_BODY_LINES lines, are
       passed through unchanged.
    6. Validate resulting XML well-formedness (all opened tags closed).
    7. Output: --dry-run prints unified diff to stdout; without --dry-run, writes
       in-place.

Tag map (heading keyword → XML tag):
    Persona, Role                         → <persona>
    Instructions, Behavior, Workflow      → <instructions>
    Context, Environment, Endogenous      → <context>
    Examples                              → <examples>
    Tools, Tool Guidance                  → <tools>
    Constraints, Guardrails, Scope        → <constraints>
    Output Format, Response Format,
      Deliverables, Completion Criteria   → <output>

Inputs:
    --file <path>    Single file to migrate.
    --all            Migrate all *.agent.md in .github/agents/.
    --dry-run        Print diff without writing.
    --min-lines <n>  Skip files whose body has fewer than N non-empty lines.
                     (default: 30)
    --model-scope    Only migrate files where `model` field starts with this value.
                     Use 'all' to disable filtering. (default: disabled — all files)
    --tag-map <json> JSON string overriding section heading → tag mapping.

Outputs:
    stdout: dry-run diff output, or confirmation of written files.
    stderr: warnings (skipped files, well-formedness issues).

Exit codes:
    0  Success (no parse/well-formedness errors), including no-op runs.
    1  Parse error or well-formedness failure.

Usage examples:
    # Dry-run a single file
    uv run python scripts/migrate_agent_xml.py \
        --file .github/agents/executive-researcher.agent.md --dry-run

    # Migrate a single file in-place
    uv run python scripts/migrate_agent_xml.py \
        --file .github/agents/executive-researcher.agent.md

    # Dry-run all agent files
    uv run python scripts/migrate_agent_xml.py --all --dry-run

    # Migrate all files, skip those with < 40 body lines
    uv run python scripts/migrate_agent_xml.py --all --min-lines 40

    # Preview with a custom tag override (JSON)
    uv run python scripts/migrate_agent_xml.py --file agent.md --dry-run \
        --tag-map '{"Workflow": "instructions", "Philosophy": "context"}'

## Usage

```bash
    # Dry-run a single file
    uv run python scripts/migrate_agent_xml.py \
        --file .github/agents/executive-researcher.agent.md --dry-run

    # Migrate a single file in-place
    uv run python scripts/migrate_agent_xml.py \
        --file .github/agents/executive-researcher.agent.md

    # Dry-run all agent files
    uv run python scripts/migrate_agent_xml.py --all --dry-run

    # Migrate all files, skip those with < 40 body lines
    uv run python scripts/migrate_agent_xml.py --all --min-lines 40

    # Preview with a custom tag override (JSON)
    uv run python scripts/migrate_agent_xml.py --file agent.md --dry-run \
        --tag-map '{"Workflow": "instructions", "Philosophy": "context"}'
```

<!-- hash:f1038a8da6f06224 -->
