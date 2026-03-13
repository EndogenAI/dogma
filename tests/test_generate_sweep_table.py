"""tests/test_generate_sweep_table.py

Unit and integration tests for scripts/generate_sweep_table.py

Tests cover:
- detect_recency(): YAML with Recent/Mid/Old date, no date, malformed frontmatter
- detect_citations(): markdown link, bare text, absent
- build_already_cited(): all 3 cited, 2 cited, 1 cited, none cited
- format_table(): column count, Status emoji, Synthesis synthesises cell, Operational dash
- --mark-read integration: YAML updated to ✅ and table file written
- --dry-run: output to stdout, no file written
- Exit codes: --mark-read with unknown doc exits 1
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import generate_sweep_table as sut  # noqa: E402 — after sys.path manipulation

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "generate_sweep_table.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_entry(**overrides) -> dict:
    """Return a minimal enriched entry dict suitable for format_table()."""
    base = {
        "name": "test-doc.md",
        "doc_type": "Raw Research",
        "synthesises": [],
        "relevance_values_encoding": {"rating": "M", "rationale": "test rationale"},
        "relevance_bubble_clusters": {"rating": "M", "rationale": "bubble rationale"},
        "relevance_endogenic_design": {"rating": "H", "rationale": "endo rationale"},
        "scout_depth": "Thorough",
        "scout_depth_reason": "high relevance",
        "status": "\u2b1c",
        "recency": "Recent",
        "already_cited": "No",
    }
    base.update(overrides)
    return base


def _write_minimal_yaml(path: Path, entries: list) -> None:
    """Write a minimal corpus-sweep-data.yml to path."""
    data = {"docs": entries}
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _make_primary_papers(research_dir: Path, content: str = "") -> None:
    """Create the three primary paper stubs in research_dir."""
    for name in ["values-encoding.md", "bubble-clusters-substrate.md", "endogenic-design-paper.md"]:
        (research_dir / name).write_text(f"---\ntitle: {name}\n---\n# Paper\n{content}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# detect_recency
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_detect_recency_recent_unquoted(tmp_path):
    """Unquoted ISO date in 2026-03 range returns Recent."""
    doc = tmp_path / "doc.md"
    # PyYAML will parse this as datetime.date(2026, 3, 10)
    doc.write_text("---\ndate: 2026-03-10\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Recent"


@pytest.mark.io
def test_detect_recency_recent_quoted(tmp_path):
    """Quoted ISO date in 2026-03 range returns Recent."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ndate: '2026-03-01'\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Recent"


@pytest.mark.io
def test_detect_recency_mid(tmp_path):
    """Date in 2026-02 returns Mid."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ndate: '2026-02-15'\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Mid"


@pytest.mark.io
def test_detect_recency_old_2025(tmp_path):
    """Date in 2025 returns Old."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ndate: '2025-11-01'\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Old"


@pytest.mark.io
def test_detect_recency_old_2026_01(tmp_path):
    """Date in 2026-01 returns Old."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ndate: '2026-01-20'\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Old"


@pytest.mark.io
def test_detect_recency_no_date_field(tmp_path):
    """Frontmatter without date field returns Unknown."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ntitle: No Date Doc\nstatus: Draft\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Unknown"


@pytest.mark.io
def test_detect_recency_no_frontmatter(tmp_path):
    """File with no frontmatter returns Unknown."""
    doc = tmp_path / "doc.md"
    doc.write_text("# Just a heading\nno frontmatter here\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Unknown"


@pytest.mark.io
def test_detect_recency_malformed_frontmatter(tmp_path):
    """Malformed YAML in frontmatter returns Unknown."""
    doc = tmp_path / "doc.md"
    doc.write_text("---\ndate: [\nmalformed yaml: {unclosed\n---\n# Doc\n", encoding="utf-8")
    assert sut.detect_recency(doc) == "Unknown"


@pytest.mark.io
def test_detect_recency_missing_file(tmp_path):
    """Non-existent file returns Unknown (no exception)."""
    doc = tmp_path / "nonexistent.md"
    assert sut.detect_recency(doc) == "Unknown"


# ---------------------------------------------------------------------------
# detect_citations
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_detect_citations_markdown_link(tmp_path):
    """Filename appearing inside a markdown link is detected."""
    paper = tmp_path / "paper.md"
    paper.write_text(
        "See [agent fleet](docs/research/agent-fleet-design-patterns.md) for details.\n",
        encoding="utf-8",
    )
    assert sut.detect_citations(paper, "agent-fleet-design-patterns.md") is True


@pytest.mark.io
def test_detect_citations_bare_reference(tmp_path):
    """Filename appearing as bare text is detected."""
    paper = tmp_path / "paper.md"
    paper.write_text(
        "The doc agent-fleet-design-patterns.md covers this topic.\n",
        encoding="utf-8",
    )
    assert sut.detect_citations(paper, "agent-fleet-design-patterns.md") is True


@pytest.mark.io
def test_detect_citations_absent(tmp_path):
    """Filename not present in paper returns False."""
    paper = tmp_path / "paper.md"
    paper.write_text("# Paper\nNo references to that document here.\n", encoding="utf-8")
    assert sut.detect_citations(paper, "agent-fleet-design-patterns.md") is False


@pytest.mark.io
def test_detect_citations_partial_name_not_matched(tmp_path):
    """Partial filename match does not produce a false positive."""
    paper = tmp_path / "paper.md"
    # Contains 'agent-fleet' but not the full filename
    paper.write_text("See agent-fleet for details.\n", encoding="utf-8")
    assert sut.detect_citations(paper, "agent-fleet-design-patterns.md") is False


# ---------------------------------------------------------------------------
# build_already_cited
# ---------------------------------------------------------------------------


def test_build_already_cited_all_three():
    """Doc cited in all three papers returns 'Yes (all)'."""
    citations_map = {
        "values": {"doc.md", "other.md"},
        "bubble": {"doc.md"},
        "endogenic": {"doc.md"},
    }
    assert sut.build_already_cited("doc.md", citations_map) == "Yes (all)"


def test_build_already_cited_values_and_endogenic():
    """Doc cited in values and endogenic returns 'Yes (values/endogenic)'."""
    citations_map = {
        "values": {"doc.md"},
        "bubble": set(),
        "endogenic": {"doc.md"},
    }
    assert sut.build_already_cited("doc.md", citations_map) == "Yes (values/endogenic)"


def test_build_already_cited_bubble_only():
    """Doc cited only in bubble returns 'Yes (bubble)'."""
    citations_map = {
        "values": set(),
        "bubble": {"doc.md"},
        "endogenic": set(),
    }
    assert sut.build_already_cited("doc.md", citations_map) == "Yes (bubble)"


def test_build_already_cited_values_and_bubble():
    """Doc cited in values and bubble returns 'Yes (values/bubble)'."""
    citations_map = {
        "values": {"doc.md"},
        "bubble": {"doc.md"},
        "endogenic": set(),
    }
    assert sut.build_already_cited("doc.md", citations_map) == "Yes (values/bubble)"


def test_build_already_cited_none():
    """Doc not cited in any paper returns 'No'."""
    citations_map = {
        "values": set(),
        "bubble": set(),
        "endogenic": set(),
    }
    assert sut.build_already_cited("doc.md", citations_map) == "No"


def test_build_already_cited_empty_map():
    """Empty citations_map returns 'No'."""
    assert sut.build_already_cited("doc.md", {}) == "No"


# ---------------------------------------------------------------------------
# format_table
# ---------------------------------------------------------------------------


def test_format_table_produces_three_lines_for_one_entry():
    """format_table with one entry returns header + separator + 1 row."""
    entry = _minimal_entry()
    result = sut.format_table([entry])
    lines = [ln for ln in result.split("\n") if ln.strip()]
    assert len(lines) == 3


def test_format_table_column_count():
    """Each row in the table has exactly 10 columns (11 pipe characters)."""
    entry = _minimal_entry()
    result = sut.format_table([entry])
    lines = [ln for ln in result.split("\n") if ln.strip()]
    # Check header, separator, and data row all have 11 pipes
    for line in lines:
        assert line.count("|") == 11, f"Wrong pipe count in: {line!r}"


def test_format_table_status_emoji_present():
    """Status emoji appears in the formatted table."""
    entry = _minimal_entry(status="\u2705")
    result = sut.format_table([entry])
    assert "\u2705" in result


def test_format_table_synthesis_synthesises_cell():
    """Synthesis entry with multiple constituents shows abbreviated names."""
    entry = _minimal_entry(
        doc_type="Synthesis",
        synthesises=["raw-a.md", "raw-b.md", "raw-c.md"],
    )
    result = sut.format_table([entry])
    # .md stripped, names joined with comma
    assert "raw-a" in result
    assert "raw-b" in result
    assert "raw-c" in result
    assert ".md" not in result.split("|")[3]  # Synthesises cell (col index 3)


def test_format_table_operational_empty_synthesises_shows_dash():
    """Operational entry with no synthesises shows em dash in Synthesises cell."""
    entry = _minimal_entry(doc_type="Operational", synthesises=[])
    result = sut.format_table([entry])
    # Em dash U+2014 in Synthesises column
    assert "\u2014" in result


def test_format_table_multiple_entries_row_count():
    """N entries produce N data rows plus header and separator."""
    entries = [_minimal_entry(name=f"doc-{i}.md") for i in range(5)]
    result = sut.format_table(entries)
    lines = [ln for ln in result.split("\n") if ln.strip()]
    assert len(lines) == 5 + 2  # 5 data rows + header + separator


def test_format_table_recency_in_row():
    """Recency field value appears in the table row."""
    entry = _minimal_entry(recency="Mid")
    result = sut.format_table([entry])
    data_row = [ln for ln in result.split("\n") if ln.strip()][2]
    assert "Mid" in data_row


def test_format_table_already_cited_in_row():
    """already_cited field value appears in the table row."""
    entry = _minimal_entry(already_cited="Yes (values/endogenic)")
    result = sut.format_table([entry])
    assert "Yes (values/endogenic)" in result


# ---------------------------------------------------------------------------
# generate_header
# ---------------------------------------------------------------------------


def test_generate_header_contains_title():
    """Header contains the standard title."""
    entries = [_minimal_entry()]
    result = sut.generate_header(entries, {})
    assert "# Corpus Sweep Table" in result


def test_generate_header_summary_counts():
    """Summary counts in header match the entries."""
    entries = [
        _minimal_entry(scout_depth="Thorough", doc_type="Synthesis"),
        _minimal_entry(scout_depth="Thorough", doc_type="Raw Research"),
        _minimal_entry(scout_depth="Skim"),
        _minimal_entry(scout_depth="Skip"),
    ]
    result = sut.generate_header(entries, {})
    assert "**Thorough**: 2 (of which 1 are Synthesis docs" in result
    assert "**Skim**: 1" in result
    assert "**Skip**: 1" in result
    assert "**Total**: 4" in result


def test_generate_header_cross_ref_section():
    """Header includes cross-reference pre-scan section."""
    citations_map = {
        "values": {"doc-a.md"},
        "bubble": set(),
        "endogenic": {"doc-b.md"},
    }
    result = sut.generate_header([_minimal_entry()], citations_map)
    assert "values-encoding.md" in result
    assert "doc-a.md" in result
    assert "doc-b.md" in result


# ---------------------------------------------------------------------------
# update_status (unit)
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_update_status_marks_read(tmp_path):
    """update_status changes status field to the given value."""
    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(
        data_file,
        [
            {
                "name": "target.md",
                "doc_type": "Raw Research",
                "synthesises": [],
                "relevance_values_encoding": {"rating": "M", "rationale": "t"},
                "relevance_bubble_clusters": {"rating": "M", "rationale": "t"},
                "relevance_endogenic_design": {"rating": "H", "rationale": "t"},
                "scout_depth": "Skim",
                "scout_depth_reason": "test",
                "status": "\u2b1c",
            }
        ],
    )
    sut.update_status(data_file, "target.md", "\u2705")
    with open(data_file, encoding="utf-8") as f:
        updated = yaml.safe_load(f)
    assert updated["docs"][0]["status"] == "\u2705"


@pytest.mark.io
def test_update_status_accepts_name_without_extension(tmp_path):
    """update_status normalises doc name by appending .md if absent."""
    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(
        data_file,
        [
            {
                "name": "target.md",
                "doc_type": "Raw Research",
                "synthesises": [],
                "relevance_values_encoding": {"rating": "M", "rationale": "t"},
                "relevance_bubble_clusters": {"rating": "M", "rationale": "t"},
                "relevance_endogenic_design": {"rating": "H", "rationale": "t"},
                "scout_depth": "Skim",
                "scout_depth_reason": "test",
                "status": "\u2b1c",
            }
        ],
    )
    sut.update_status(data_file, "target", "\u23f3")
    with open(data_file, encoding="utf-8") as f:
        updated = yaml.safe_load(f)
    assert updated["docs"][0]["status"] == "\u23f3"


@pytest.mark.io
def test_update_status_unknown_doc_exits_1(tmp_path):
    """update_status exits with code 1 when doc not found."""
    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(data_file, [])
    with pytest.raises(SystemExit) as exc_info:
        sut.update_status(data_file, "nonexistent.md", "\u2705")
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# CLI integration — --mark-read
# ---------------------------------------------------------------------------


def _run_script(args: list, cwd: str = None) -> subprocess.CompletedProcess:
    """Run generate_sweep_table.py as a subprocess using the current interpreter."""
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        cwd=cwd or str(Path(__file__).parent.parent),
        env={**os.environ},
    )


def _minimal_yaml_entry(name: str = "test-doc.md") -> dict:
    return {
        "name": name,
        "doc_type": "Raw Research",
        "synthesises": [],
        "relevance_values_encoding": {"rating": "M", "rationale": "test"},
        "relevance_bubble_clusters": {"rating": "M", "rationale": "test"},
        "relevance_endogenic_design": {"rating": "H", "rationale": "test"},
        "scout_depth": "Skim",
        "scout_depth_reason": "test",
        "status": "\u2b1c",
    }


@pytest.mark.io
def test_mark_read_updates_yaml_and_writes_table(tmp_path):
    """--mark-read updates status to ✅ in YAML and regenerates the table file."""
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    _make_primary_papers(research_dir)
    (research_dir / "test-doc.md").write_text("---\ndate: '2026-03-01'\n---\n# Test Doc\n", encoding="utf-8")

    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(data_file, [_minimal_yaml_entry("test-doc.md")])

    output_file = tmp_path / "sweep-table.md"

    result = _run_script(
        [
            "--data-file",
            str(data_file),
            "--research-dir",
            str(research_dir),
            "--mark-read",
            "test-doc.md",
            "--output",
            str(output_file),
        ]
    )
    assert result.returncode == 0, result.stderr

    # YAML status updated
    with open(data_file, encoding="utf-8") as f:
        updated = yaml.safe_load(f)
    assert updated["docs"][0]["status"] == "\u2705"

    # Table file written
    assert output_file.exists()
    table_content = output_file.read_text(encoding="utf-8")
    assert "# Corpus Sweep Table" in table_content
    assert "\u2705" in table_content


@pytest.mark.io
def test_mark_in_progress_updates_yaml(tmp_path):
    """--mark-in-progress updates status to ⏳ in YAML."""
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    _make_primary_papers(research_dir)
    (research_dir / "test-doc.md").write_text("---\ndate: '2026-03-01'\n---\n# Test\n", encoding="utf-8")

    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(data_file, [_minimal_yaml_entry("test-doc.md")])

    output_file = tmp_path / "sweep-table.md"

    result = _run_script(
        [
            "--data-file",
            str(data_file),
            "--research-dir",
            str(research_dir),
            "--mark-in-progress",
            "test-doc.md",
            "--output",
            str(output_file),
        ]
    )
    assert result.returncode == 0, result.stderr

    with open(data_file, encoding="utf-8") as f:
        updated = yaml.safe_load(f)
    assert updated["docs"][0]["status"] == "\u23f3"


# ---------------------------------------------------------------------------
# CLI integration — --dry-run
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_dry_run_output_to_stdout_no_file_written(tmp_path):
    """--dry-run prints table to stdout and does not write any file."""
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    _make_primary_papers(research_dir)
    (research_dir / "test-doc.md").write_text("---\ndate: '2026-03-01'\n---\n# Test\n", encoding="utf-8")

    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(data_file, [_minimal_yaml_entry("test-doc.md")])

    output_file = tmp_path / "sweep-table.md"

    result = _run_script(
        [
            "--data-file",
            str(data_file),
            "--research-dir",
            str(research_dir),
            "--output",
            str(output_file),
            "--dry-run",
        ]
    )
    assert result.returncode == 0, result.stderr
    # Output went to stdout
    assert "# Corpus Sweep Table" in result.stdout
    # File was NOT written
    assert not output_file.exists()


# ---------------------------------------------------------------------------
# CLI integration — exit codes
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_mark_read_unknown_doc_exits_1(tmp_path):
    """--mark-read with a doc not in the YAML exits with code 1."""
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    _make_primary_papers(research_dir)

    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(data_file, [_minimal_yaml_entry("existing-doc.md")])

    result = _run_script(
        [
            "--data-file",
            str(data_file),
            "--research-dir",
            str(research_dir),
            "--mark-read",
            "nonexistent-doc.md",
        ]
    )
    assert result.returncode == 1


@pytest.mark.io
def test_missing_primary_paper_exits_1(tmp_path):
    """Missing primary paper causes exit with code 1."""
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    # Only create two of the three primary papers
    (research_dir / "values-encoding.md").write_text("# Values\n", encoding="utf-8")
    (research_dir / "bubble-clusters-substrate.md").write_text("# Bubble\n", encoding="utf-8")
    # endogenic-design-paper.md intentionally omitted

    data_file = tmp_path / "corpus-sweep-data.yml"
    _write_minimal_yaml(data_file, [_minimal_yaml_entry()])

    result = _run_script(
        [
            "--data-file",
            str(data_file),
            "--research-dir",
            str(research_dir),
        ]
    )
    assert result.returncode == 1
