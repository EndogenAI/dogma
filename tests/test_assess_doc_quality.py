"""tests/test_assess_doc_quality.py

Tests for scripts/assess_doc_quality.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from assess_doc_quality import (
    assess,
    completeness_score,
    main,
    readability_score,
    structural_score,
)
from markdown_it import MarkdownIt

SAMPLE_MD = """\
# Introduction

This is a **sample** document for testing doc quality assessment.

## Section One

This section contains some prose with a **bold term** and a [link](http://example.com).

| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |

**Canonical example**: This is a canonical pattern.

- List item 1
- List item 2

## Section Two

Another section with more content about **important concepts** and **key ideas**.

```python
# Code block example
print("hello world")
```

**Anti-pattern**: This is what not to do.
"""


# ---------------------------------------------------------------------------
# readability_score
# ---------------------------------------------------------------------------


class TestReadabilityScore:
    def test_empty_text_returns_100(self):
        _, score = readability_score("")
        assert score == 100.0

    def test_returns_tuple_of_floats(self):
        fk, score = readability_score("The quick brown fox jumps. This is simple text.")
        assert isinstance(fk, float)
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0

    def test_simple_text_gets_high_score(self):
        # Very simple short sentences → lower FK grade → higher score
        text = "This is easy. Read this. Simple words. Short sentences." * 10
        _, score = readability_score(text)
        assert score > 50.0

    def test_score_within_bounds(self):
        _, score = readability_score(SAMPLE_MD)
        assert 0.0 <= score <= 100.0


# ---------------------------------------------------------------------------
# structural_score
# ---------------------------------------------------------------------------


class TestStructuralScore:
    def test_returns_dict_and_float(self):
        md = MarkdownIt()
        metrics, score = structural_score(SAMPLE_MD, md)
        assert isinstance(metrics, dict)
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0

    def test_metrics_contains_expected_keys(self):
        md = MarkdownIt()
        metrics, _ = structural_score(SAMPLE_MD, md)
        assert "heading_density_per_1000" in metrics
        assert "table_count" in metrics
        assert "list_open_count" in metrics
        assert "fence_count" in metrics
        assert "list_code_ratio" in metrics

    def test_doc_with_headings_tables_gets_nonzero_score(self):
        md = MarkdownIt()
        _, score = structural_score(SAMPLE_MD, md)
        assert score > 0.0

    def test_plain_text_gets_low_structure(self):
        md = MarkdownIt()
        _, score = structural_score("no structure here at all just plain words " * 50, md)
        assert score < 50.0

    def test_empty_text_handled(self):
        md = MarkdownIt()
        metrics, score = structural_score("", md)
        assert score == 0.0


# ---------------------------------------------------------------------------
# completeness_score
# ---------------------------------------------------------------------------


class TestCompletenessScore:
    def test_returns_dict_and_float(self):
        metrics, score = completeness_score(SAMPLE_MD)
        assert isinstance(metrics, dict)
        assert 0.0 <= score <= 100.0

    def test_canonical_and_antipattern_counted(self):
        text = "**Canonical example**: Yes.\n**Anti-pattern**: No.\n"
        metrics, _ = completeness_score(text)
        assert metrics["labeled_blocks"] == 2

    def test_citation_lines_counted(self):
        text = "[Link text](http://example.com) is a citation.\nAnother [ref](url) here.\n"
        metrics, _ = completeness_score(text)
        assert metrics["citation_lines"] >= 2

    def test_empty_doc_returns_zero_score(self):
        _, score = completeness_score("")
        assert score == 0.0

    def test_bold_terms_counted(self):
        text = "**TermA** and **TermB** are bold.\n"
        metrics, _ = completeness_score(text)
        assert metrics["bold_terms"] >= 2


# ---------------------------------------------------------------------------
# assess (integration)
# ---------------------------------------------------------------------------


class TestAssess:
    @pytest.mark.io
    def test_happy_path_returns_composite(self, tmp_path):
        doc = tmp_path / "test.md"
        doc.write_text(SAMPLE_MD)
        result = assess(doc)
        assert "composite_score" in result
        assert 0.0 <= result["composite_score"] <= 100.0

    @pytest.mark.io
    def test_result_contains_all_keys(self, tmp_path):
        doc = tmp_path / "test.md"
        doc.write_text(SAMPLE_MD)
        result = assess(doc)
        assert "readability" in result
        assert "structural" in result
        assert "completeness" in result
        assert "word_count" in result
        assert "file" in result

    @pytest.mark.io
    def test_delta_with_targets_file(self, tmp_path):
        doc = tmp_path / "myfile.md"
        doc.write_text(SAMPLE_MD)
        targets = tmp_path / ".reading-level-targets.yml"
        targets.write_text("default: 12\n")
        result = assess(doc, delta_path=targets)
        assert "delta" in result

    @pytest.mark.io
    def test_delta_none_when_targets_missing(self, tmp_path):
        doc = tmp_path / "myfile.md"
        doc.write_text(SAMPLE_MD)
        targets = tmp_path / ".nonexistent.yml"
        result = assess(doc, delta_path=targets)
        assert result.get("delta") is None


# ---------------------------------------------------------------------------
# main (CLI)
# ---------------------------------------------------------------------------


class TestMain:
    @pytest.mark.io
    def test_json_output(self, tmp_path, capsys):
        doc = tmp_path / "test.md"
        doc.write_text(SAMPLE_MD)
        rc = main([str(doc), "--output", "json"])
        assert rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "composite_score" in data
        assert "readability" in data

    @pytest.mark.io
    def test_missing_file_exits_1(self, tmp_path):
        rc = main([str(tmp_path / "nonexistent.md")])
        assert rc == 1

    @pytest.mark.io
    def test_human_output_default(self, tmp_path, capsys):
        doc = tmp_path / "test.md"
        doc.write_text(SAMPLE_MD)
        rc = main([str(doc)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Composite score" in captured.out

    @pytest.mark.io
    def test_non_markdown_treated_as_plain_text(self, tmp_path):
        doc = tmp_path / "test.txt"
        doc.write_text("Plain text file. Not markdown. Words and more words." * 20)
        rc = main([str(doc)])
        assert rc == 0

    @pytest.mark.io
    def test_delta_flag(self, tmp_path, capsys):
        doc = tmp_path / "test.md"
        doc.write_text(SAMPLE_MD)
        targets = tmp_path / "targets.yml"
        targets.write_text("default: 12\n")
        rc = main([str(doc), "--delta", str(targets)])
        assert rc == 0
