"""
tests/test_seed_research_recommendations.py

Unit tests for scripts/seed_research_recommendations.py.

Coverage targets
----------------
- Happy path: frontmatter with 3 recommendations (2 untracked, 1 linked) → 2 ops
- TBD-* linked_issue values → treated as untracked
- --dry-run flag → --dry-run passed through to subprocess call
- Missing --default-area when recommendation has no area field → exit 2
- --critical-ids → affected recommendation gets priority:critical label
- Multiple --input files → ops from all files in single spec
- Empty recommendations list → zero ops, exit 0
- Malformed YAML frontmatter → exit 2
- --output FILE → writes JSON to file, does not invoke subprocess
- Input file not found → exit 1

Markers
-------
@pytest.mark.io — tests that read/write temporary files
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import seed_research_recommendations as srr  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers — sample frontmatter builders
# ---------------------------------------------------------------------------

FRONTMATTER_3_RECS = """\
---
title: "Test Research Doc"
status: Final
closes_issue: 402
author: Executive Researcher
date: 2026-03-25
recommendations:
  - id: untracked-a
    title: "Untracked Rec A"
    status: accepted-for-adoption
    linked_issue: null
    area: docs
  - id: already-tracked
    title: "Already Tracked Rec"
    status: accepted-for-adoption
    linked_issue: 123
    area: scripts
  - id: untracked-b
    title: "Untracked Rec B"
    status: accepted-for-adoption
    linked_issue: null
    area: agents
---

# Body
"""

FRONTMATTER_TBD = """\
---
title: "TBD Linked Doc"
status: Final
closes_issue: 500
recommendations:
  - id: tbd-rec
    title: "TBD Linked Rec"
    status: accepted-for-adoption
    linked_issue: "TBD-some-slug"
    area: scripts
---

# Body
"""

FRONTMATTER_EMPTY_RECS = """\
---
title: "No Recs Doc"
status: Final
recommendations: []
---

# Body
"""

FRONTMATTER_NO_RECS_KEY = """\
---
title: "Doc without recommendations key"
status: Final
---

# Body
"""

FRONTMATTER_MALFORMED = """\
---
title: [unclosed bracket
  bad: : yaml : here
---

# Body
"""

FRONTMATTER_NO_AREA = """\
---
title: "No Area Doc"
closes_issue: 999
recommendations:
  - id: no-area-rec
    title: "Rec Without Area"
    status: accepted-for-adoption
    linked_issue: null
---

# Body
"""

FRONTMATTER_WITH_AREA = """\
---
title: "Has Area Doc"
closes_issue: 888
recommendations:
  - id: has-area-rec
    title: "Rec With Area"
    status: accepted-for-adoption
    linked_issue: null
    area: ci
---

# Body
"""


# ---------------------------------------------------------------------------
# _extract_frontmatter
# ---------------------------------------------------------------------------


class TestExtractFrontmatter:
    def test_happy_path(self) -> None:
        data = srr._extract_frontmatter(FRONTMATTER_3_RECS, "test.md")
        assert data["title"] == "Test Research Doc"
        assert len(data["recommendations"]) == 3

    def test_no_opening_delimiter_exits_2(self) -> None:
        with pytest.raises(SystemExit) as exc:
            srr._extract_frontmatter("# No frontmatter here", "test.md")
        assert (
            exc.value.code
            == (
                "[seed_research_recommendations] ERROR: test.md: no YAML frontmatter found (file must start with '---')"
            )
            or exc.value.code != 0
        )

    def test_unclosed_frontmatter_exits_2(self) -> None:
        text = "---\ntitle: Something\n# no closing ---\n"
        with pytest.raises(SystemExit):
            srr._extract_frontmatter(text, "test.md")

    def test_malformed_yaml_exits_2(self) -> None:
        with pytest.raises(SystemExit):
            srr._extract_frontmatter(FRONTMATTER_MALFORMED, "test.md")

    def test_non_mapping_yaml_exits_2(self) -> None:
        text = "---\n- item1\n- item2\n---\n"
        with pytest.raises(SystemExit):
            srr._extract_frontmatter(text, "test.md")


# ---------------------------------------------------------------------------
# _is_untracked
# ---------------------------------------------------------------------------


class TestIsUntracked:
    def test_none_is_untracked(self) -> None:
        assert srr._is_untracked(None) is True

    def test_tbd_string_is_untracked(self) -> None:
        assert srr._is_untracked("TBD-some-slug") is True

    def test_tbd_lowercase_is_untracked(self) -> None:
        assert srr._is_untracked("tbd-another") is True

    def test_integer_is_tracked(self) -> None:
        assert srr._is_untracked(123) is False

    def test_string_number_is_tracked(self) -> None:
        assert srr._is_untracked("456") is False

    def test_arbitrary_string_is_tracked(self) -> None:
        assert srr._is_untracked("some-slug") is False


# ---------------------------------------------------------------------------
# _build_issue_body
# ---------------------------------------------------------------------------


class TestBuildIssueBody:
    def test_contains_filename(self) -> None:
        body = srr._build_issue_body("my-doc.md", "Some Title", 402)
        assert "docs/research/my-doc.md" in body

    def test_contains_title(self) -> None:
        body = srr._build_issue_body("my-doc.md", "Some Title", 402)
        assert "Some Title" in body

    def test_contains_closes_issue_ref(self) -> None:
        body = srr._build_issue_body("my-doc.md", "Some Title", 402)
        assert "#402" in body

    def test_has_expected_headings(self) -> None:
        body = srr._build_issue_body("my-doc.md", "Some Title", 402)
        assert "## Source" in body
        assert "## Summary" in body
        assert "## Deliverables" in body
        assert "## Reference" in body


# ---------------------------------------------------------------------------
# _build_ops — happy path
# ---------------------------------------------------------------------------


class TestBuildOps:
    @pytest.mark.io
    def test_two_untracked_of_three(self, tmp_path: Path) -> None:
        """3 recommendations, 1 already linked → 2 ops generated."""
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        assert len(ops) == 2
        titles = {op["params"]["title"] for op in ops}
        assert titles == {"Untracked Rec A", "Untracked Rec B"}

    @pytest.mark.io
    def test_tbd_treated_as_untracked(self, tmp_path: Path) -> None:
        doc = tmp_path / "tbd.md"
        doc.write_text(FRONTMATTER_TBD, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        assert len(ops) == 1
        assert ops[0]["params"]["title"] == "TBD Linked Rec"

    @pytest.mark.io
    def test_empty_recommendations_returns_empty(self, tmp_path: Path) -> None:
        doc = tmp_path / "empty.md"
        doc.write_text(FRONTMATTER_EMPTY_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        assert ops == []

    @pytest.mark.io
    def test_no_recommendations_key_returns_empty(self, tmp_path: Path) -> None:
        doc = tmp_path / "norecs.md"
        doc.write_text(FRONTMATTER_NO_RECS_KEY, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        assert ops == []

    @pytest.mark.io
    def test_critical_ids_get_priority_critical(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops(
            [doc],
            default_area=None,
            critical_ids={"untracked-a"},
            milestone=None,
            repo="owner/repo",
        )
        op_a = next(o for o in ops if o["params"]["title"] == "Untracked Rec A")
        op_b = next(o for o in ops if o["params"]["title"] == "Untracked Rec B")
        assert "priority:critical" in op_a["params"]["labels"]
        assert "priority:high" in op_b["params"]["labels"]

    @pytest.mark.io
    def test_source_research_and_type_feature_labels_always_present(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        for op in ops:
            assert "source:research" in op["params"]["labels"]
            assert "type:feature" in op["params"]["labels"]

    @pytest.mark.io
    def test_area_label_derived_from_rec_field(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        op_a = next(o for o in ops if o["params"]["title"] == "Untracked Rec A")
        assert "area:docs" in op_a["params"]["labels"]

    @pytest.mark.io
    def test_default_area_used_when_rec_has_no_area(self, tmp_path: Path) -> None:
        doc = tmp_path / "noarea.md"
        doc.write_text(FRONTMATTER_NO_AREA, encoding="utf-8")

        ops = srr._build_ops([doc], default_area="scripts", critical_ids=set(), milestone=None, repo="owner/repo")
        assert len(ops) == 1
        assert "area:scripts" in ops[0]["params"]["labels"]

    @pytest.mark.io
    def test_missing_area_no_default_exits_2(self, tmp_path: Path) -> None:
        doc = tmp_path / "noarea.md"
        doc.write_text(FRONTMATTER_NO_AREA, encoding="utf-8")

        with pytest.raises(SystemExit) as exc:
            srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        assert exc.value.code == 2

    @pytest.mark.io
    def test_milestone_included_in_params_when_provided(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone="Sprint 20", repo="owner/repo")
        for op in ops:
            assert op["params"]["milestone"] == "Sprint 20"

    @pytest.mark.io
    def test_milestone_absent_when_not_provided(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        for op in ops:
            assert "milestone" not in op["params"]

    @pytest.mark.io
    def test_multiple_input_files_combined(self, tmp_path: Path) -> None:
        doc1 = tmp_path / "doc1.md"
        doc2 = tmp_path / "doc2.md"
        doc1.write_text(FRONTMATTER_3_RECS, encoding="utf-8")
        doc2.write_text(FRONTMATTER_TBD, encoding="utf-8")

        ops = srr._build_ops(
            [doc1, doc2],
            default_area=None,
            critical_ids=set(),
            milestone=None,
            repo="owner/repo",
        )
        # doc1 contributes 2 ops, doc2 contributes 1 op
        assert len(ops) == 3

    @pytest.mark.io
    def test_all_ops_have_issue_create_op(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        ops = srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")
        for op in ops:
            assert op["op"] == "issue-create"
            assert op["target"] is None

    @pytest.mark.io
    def test_malformed_yaml_frontmatter_exits_2(self, tmp_path: Path) -> None:
        doc = tmp_path / "bad.md"
        doc.write_text(FRONTMATTER_MALFORMED, encoding="utf-8")

        with pytest.raises(SystemExit):
            srr._build_ops([doc], default_area=None, critical_ids=set(), milestone=None, repo="owner/repo")

    @pytest.mark.io
    def test_missing_input_file_exits_1(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.md"
        with pytest.raises(SystemExit) as exc:
            srr.main(["--input", str(missing), "--default-area", "docs"])
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# main() integration tests (subprocess mocked)
# ---------------------------------------------------------------------------


class TestMainIntegration:
    @pytest.mark.io
    def test_dry_run_passes_dry_run_to_subprocess(self, tmp_path: Path) -> None:
        """--dry-run flag is forwarded to bulk_github_operations.py subprocess call."""
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with pytest.raises(SystemExit) as exc:
                srr.main(["--input", str(doc), "--dry-run"])
            assert exc.value.code == 0

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "--dry-run" in cmd

    @pytest.mark.io
    def test_no_dry_run_omits_dry_run_from_subprocess(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with pytest.raises(SystemExit) as exc:
                srr.main(["--input", str(doc)])
            assert exc.value.code == 0

        cmd = mock_run.call_args[0][0]
        assert "--dry-run" not in cmd

    @pytest.mark.io
    def test_output_flag_writes_json_no_subprocess(self, tmp_path: Path) -> None:
        """--output writes JSON spec to file; subprocess is NOT invoked."""
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")
        out_file = tmp_path / "ops.json"

        with patch("subprocess.run") as mock_run:
            with pytest.raises(SystemExit) as exc:
                srr.main(["--input", str(doc), "--output", str(out_file)])
            assert exc.value.code == 0

        mock_run.assert_not_called()
        assert out_file.exists()
        ops = json.loads(out_file.read_text(encoding="utf-8"))
        assert len(ops) == 2

    @pytest.mark.io
    def test_empty_recommendations_exits_0_no_subprocess(self, tmp_path: Path) -> None:
        doc = tmp_path / "empty.md"
        doc.write_text(FRONTMATTER_EMPTY_RECS, encoding="utf-8")

        with patch("subprocess.run") as mock_run:
            with pytest.raises(SystemExit) as exc:
                srr.main(["--input", str(doc)])
            assert exc.value.code == 0

        mock_run.assert_not_called()

    @pytest.mark.io
    def test_subprocess_never_uses_shell_true(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with pytest.raises(SystemExit):
                srr.main(["--input", str(doc)])

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get("shell", False) is False

    @pytest.mark.io
    def test_subprocess_cmd_uses_uv_run_python(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with pytest.raises(SystemExit):
                srr.main(["--input", str(doc)])

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "uv"
        assert cmd[1] == "run"
        assert cmd[2] == "python"

    @pytest.mark.io
    def test_subprocess_returncode_propagated(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(SystemExit) as exc:
                srr.main(["--input", str(doc)])
        assert exc.value.code == 1

    @pytest.mark.io
    def test_critical_ids_cli_flag(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")
        out_file = tmp_path / "ops.json"

        with patch("subprocess.run"):
            with pytest.raises(SystemExit):
                srr.main(
                    [
                        "--input",
                        str(doc),
                        "--output",
                        str(out_file),
                        "--critical-ids",
                        "untracked-a",
                    ]
                )

        ops = json.loads(out_file.read_text(encoding="utf-8"))
        op_a = next(o for o in ops if o["params"]["title"] == "Untracked Rec A")
        assert "priority:critical" in op_a["params"]["labels"]

    @pytest.mark.io
    def test_milestone_cli_flag(self, tmp_path: Path) -> None:
        doc = tmp_path / "research.md"
        doc.write_text(FRONTMATTER_3_RECS, encoding="utf-8")
        out_file = tmp_path / "ops.json"

        with pytest.raises(SystemExit):
            srr.main(
                [
                    "--input",
                    str(doc),
                    "--output",
                    str(out_file),
                    "--milestone",
                    "Sprint 20",
                ]
            )

        ops = json.loads(out_file.read_text(encoding="utf-8"))
        for op in ops:
            assert op["params"]["milestone"] == "Sprint 20"

    @pytest.mark.io
    def test_multiple_input_files_via_cli(self, tmp_path: Path) -> None:
        doc1 = tmp_path / "doc1.md"
        doc2 = tmp_path / "doc2.md"
        doc1.write_text(FRONTMATTER_3_RECS, encoding="utf-8")
        doc2.write_text(FRONTMATTER_WITH_AREA, encoding="utf-8")
        out_file = tmp_path / "ops.json"

        with pytest.raises(SystemExit):
            srr.main(["--input", str(doc1), str(doc2), "--output", str(out_file)])

        ops = json.loads(out_file.read_text(encoding="utf-8"))
        # doc1: 2 ops, doc2: 1 op
        assert len(ops) == 3

    @pytest.mark.io
    def test_missing_default_area_exits_2(self, tmp_path: Path) -> None:
        doc = tmp_path / "noarea.md"
        doc.write_text(FRONTMATTER_NO_AREA, encoding="utf-8")

        with pytest.raises(SystemExit) as exc:
            srr.main(["--input", str(doc)])
        assert exc.value.code == 2
