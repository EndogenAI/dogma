"""Tests for scripts/apply_retrofit_patch.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import scripts.apply_retrofit_patch as apply_retrofit_patch


def _write_doc(path: Path, body: str, *, frontmatter_extra: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    extra = f"{frontmatter_extra.rstrip()}\n" if frontmatter_extra else ""
    path.write_text(
        f"---\ntitle: Test Doc\nstatus: Final\n{extra}---\n\n{body}",
        encoding="utf-8",
    )


def _write_patch(path: Path, *, doc: str, recommendations: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "doc": doc,
        "recommendations": recommendations,
    }
    path.write_text(yaml.dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")


class TestApplyRetrofitPatch:
    @pytest.mark.io
    def test_dry_run_reports_target_without_modifying_document(self, tmp_path: Path, capsys) -> None:
        doc_path = tmp_path / "docs" / "research" / "dry-run.md"
        patch_path = tmp_path / "data" / "retrofit-patches" / "dry-run.yml"

        _write_doc(
            doc_path,
            "## Body\n\nOriginal text.\n",
            frontmatter_extra=(
                "recommendations:\n"
                "  - id: rec-existing-001\n"
                "    title: Existing\n"
                "    status: deferred\n"
                "    linked_issue: null\n"
                '    decision_ref: ""\n'
            ),
        )
        _write_patch(
            patch_path,
            doc=str(doc_path),
            recommendations=[
                {
                    "id": "rec-test-dry-run-001",
                    "title": "Preview only",
                    "status": "adopted",
                    "linked_issue": 123,
                    "decision_ref": "",
                }
            ],
        )

        original_text = doc_path.read_text(encoding="utf-8")

        exit_code = apply_retrofit_patch.patch_docs(patch_path.parent.resolve(), dry_run=True)

        assert exit_code == 0
        assert doc_path.read_text(encoding="utf-8") == original_text
        assert "Dry run: would patch dry-run.md" in capsys.readouterr().out

    @pytest.mark.io
    def test_patch_uses_authoritative_doc_field_instead_of_filename(self, tmp_path: Path) -> None:
        doc_path = tmp_path / "docs" / "research" / "actual-doc.md"
        patch_path = tmp_path / "data" / "retrofit-patches" / "mismatched-name.yml"

        _write_doc(doc_path, "## Body\n\nOriginal text.\n")
        _write_patch(
            patch_path,
            doc=str(doc_path),
            recommendations=[
                {
                    "id": "rec-test-001",
                    "title": "Keep this",
                    "status": "deferred",
                    "linked_issue": None,
                    "decision_ref": "",
                    "_match_note": "strip me",
                    "_confidence": "low",
                }
            ],
        )

        apply_retrofit_patch.patch_docs(patch_path.parent.resolve())

        patched = yaml.safe_load(doc_path.read_text(encoding="utf-8").split("---", 2)[1])
        assert patched["recommendations"] == [
            {
                "id": "rec-test-001",
                "title": "Keep this",
                "status": "deferred",
                "linked_issue": None,
                "decision_ref": "",
            }
        ]

    @pytest.mark.io
    def test_patch_preserves_body_content_after_frontmatter_update(self, tmp_path: Path) -> None:
        doc_path = tmp_path / "docs" / "research" / "body-check.md"
        patch_path = tmp_path / "data" / "retrofit-patches" / "body-check.yml"
        body = "## Section\n\n---\n\nBody cafe\u0301 text.\n"

        _write_doc(doc_path, body)
        _write_patch(
            patch_path,
            doc=str(doc_path),
            recommendations=[
                {
                    "id": "rec-test-002",
                    "title": "Body preserved",
                    "status": "adopted",
                    "linked_issue": 123,
                    "decision_ref": "",
                }
            ],
        )

        apply_retrofit_patch.patch_docs(patch_path.parent.resolve())

        updated_text = doc_path.read_text(encoding="utf-8")
        assert "## Section" in updated_text
        assert "---\n\nBody cafe\u0301 text." in updated_text
        assert "rec-test-002" in updated_text

    @pytest.mark.io
    def test_malformed_top_level_recommendations_mapping_is_rejected(self, tmp_path: Path, capsys) -> None:
        doc_path = tmp_path / "docs" / "research" / "invalid-payload.md"
        patch_path = tmp_path / "data" / "retrofit-patches" / "invalid-payload.yml"

        _write_doc(doc_path, "## Body\n\nOriginal text.\n")
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(
            yaml.dump(
                {
                    "doc": str(doc_path),
                    "recommendations": {
                        "id": "rec-invalid-001",
                        "title": "Not a list",
                        "status": "deferred",
                    },
                },
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

        original_text = doc_path.read_text(encoding="utf-8")
        apply_retrofit_patch.patch_docs(patch_path.parent.resolve())

        assert doc_path.read_text(encoding="utf-8") == original_text
        assert "must be a YAML list" in capsys.readouterr().out

    @pytest.mark.io
    def test_patch_docs_uses_repo_root_when_called_outside_repo_cwd(self, tmp_path: Path, monkeypatch) -> None:
        repo_root = tmp_path / "repo"
        outside_cwd = tmp_path / "outside"
        outside_cwd.mkdir()

        doc_path = repo_root / "docs" / "research" / "outside-cwd.md"
        patch_path = repo_root / ".cache" / "retrofit-patches" / "outside-cwd.yml"

        _write_doc(doc_path, "## Body\n\nOriginal text.\n")
        _write_patch(
            patch_path,
            doc="docs/research/outside-cwd.md",
            recommendations=[
                {
                    "id": "rec-test-003",
                    "title": "Resolve from repo root",
                    "status": "adopted",
                    "linked_issue": 301,
                    "decision_ref": "",
                }
            ],
        )

        monkeypatch.setattr(
            apply_retrofit_patch,
            "__file__",
            str(repo_root / "scripts" / "apply_retrofit_patch.py"),
        )
        monkeypatch.chdir(outside_cwd)

        apply_retrofit_patch.patch_docs()

        patched = yaml.safe_load(doc_path.read_text(encoding="utf-8").split("---", 2)[1])
        assert patched["recommendations"][0]["id"] == "rec-test-003"

    @pytest.mark.io
    def test_fully_malformed_recommendations_list_does_not_overwrite_existing_entries(
        self, tmp_path: Path, capsys
    ) -> None:
        doc_path = tmp_path / "docs" / "research" / "existing-recommendations.md"
        patch_path = tmp_path / "data" / "retrofit-patches" / "existing-recommendations.yml"

        _write_doc(
            doc_path,
            "## Body\n\nOriginal text.\n",
            frontmatter_extra=(
                "recommendations:\n"
                "  - id: rec-existing-001\n"
                "    title: Preserve me\n"
                "    status: deferred\n"
                "    linked_issue: null\n"
                '    decision_ref: ""\n'
            ),
        )
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(
            yaml.dump(
                {
                    "doc": str(doc_path),
                    "recommendations": ["not-a-mapping"],
                },
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

        original_text = doc_path.read_text(encoding="utf-8")
        apply_retrofit_patch.patch_docs(patch_path.parent.resolve())

        assert doc_path.read_text(encoding="utf-8") == original_text
        assert "contained no valid mappings" in capsys.readouterr().out

    @pytest.mark.io
    def test_main_returns_nonzero_when_any_patch_cannot_be_applied(self, tmp_path: Path, capsys) -> None:
        patch_path = tmp_path / "data" / "retrofit-patches" / "missing-doc.yml"

        _write_patch(
            patch_path,
            doc=str(tmp_path / "docs" / "research" / "missing.md"),
            recommendations=[
                {
                    "id": "rec-missing-doc-001",
                    "title": "Missing target",
                    "status": "deferred",
                    "linked_issue": None,
                    "decision_ref": "",
                }
            ],
        )

        exit_code = apply_retrofit_patch.main(["--patch-dir", str(patch_path.parent)])

        assert exit_code == 1
        assert "does not exist" in capsys.readouterr().out
