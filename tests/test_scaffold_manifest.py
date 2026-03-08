"""
test_scaffold_manifest.py — Tests for scripts/scaffold_manifest.py

Covers:
- Happy path: creates manifest with default A–E sprints
- Happy path: creates manifest with custom description and sprints
- Happy path: creates manifest to custom output path
- Error: manifest already exists → exit 1
- Error: invalid --sprints JSON → exit 1
- Error: --sprints not a JSON object → exit 1
- Created file has correct structure (name, description, created, sprints, sources)
- Created manifest has empty sources list
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_scaffold(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/scaffold_manifest.py", *args],
        capture_output=True,
        text=True,
        cwd=cwd or Path(__file__).resolve().parent.parent,
    )


class TestScaffoldManifestHappyPath:
    def test_creates_manifest_with_default_sprints(self, tmp_path):
        output = tmp_path / "test-manifest.json"
        result = run_scaffold(["--name", "test-sprint", "--output", str(output)])
        assert result.returncode == 0
        assert output.exists()
        data = json.loads(output.read_text())
        assert data["name"] == "test-sprint"
        assert data["sources"] == []
        assert set(data["sprints"].keys()) == {"A", "B", "C", "D", "E"}

    def test_creates_manifest_with_custom_description(self, tmp_path):
        output = tmp_path / "custom.json"
        result = run_scaffold(
            [
                "--name",
                "my-sprint",
                "--description",
                "My custom description",
                "--output",
                str(output),
            ]
        )
        assert result.returncode == 0
        data = json.loads(output.read_text())
        assert data["description"] == "My custom description"

    def test_creates_manifest_with_custom_sprints(self, tmp_path):
        output = tmp_path / "custom-sprints.json"
        sprints = {"X": "Phase X", "Y": "Phase Y"}
        result = run_scaffold(
            [
                "--name",
                "two-sprint",
                "--sprints",
                json.dumps(sprints),
                "--output",
                str(output),
            ]
        )
        assert result.returncode == 0
        data = json.loads(output.read_text())
        assert data["sprints"] == sprints

    def test_output_contains_created_date(self, tmp_path):
        output = tmp_path / "dated.json"
        run_scaffold(["--name", "dated", "--output", str(output)])
        data = json.loads(output.read_text())
        assert "created" in data
        # Should be a date string like "2026-03-07"
        assert len(data["created"]) == 10

    def test_creates_parent_directories(self, tmp_path):
        output = tmp_path / "nested" / "deep" / "manifest.json"
        result = run_scaffold(["--name", "nested", "--output", str(output)])
        assert result.returncode == 0
        assert output.exists()

    def test_output_is_valid_json(self, tmp_path):
        output = tmp_path / "valid.json"
        run_scaffold(["--name", "valid", "--output", str(output)])
        # Should not raise
        json.loads(output.read_text())

    def test_output_ends_with_newline(self, tmp_path):
        output = tmp_path / "newline.json"
        run_scaffold(["--name", "newline", "--output", str(output)])
        assert output.read_text(encoding="utf-8").endswith("\n")


class TestScaffoldManifestErrors:
    def test_exits_1_if_file_already_exists(self, tmp_path):
        output = tmp_path / "existing.json"
        output.write_text('{"name": "existing"}', encoding="utf-8")
        result = run_scaffold(["--name", "existing", "--output", str(output)])
        assert result.returncode == 1
        assert "already exists" in result.stderr

    def test_exits_1_on_invalid_sprints_json(self, tmp_path):
        output = tmp_path / "bad.json"
        result = run_scaffold(
            [
                "--name",
                "bad",
                "--sprints",
                "not-json",
                "--output",
                str(output),
            ]
        )
        assert result.returncode == 1
        assert "not valid JSON" in result.stderr

    def test_exits_1_on_sprints_not_object(self, tmp_path):
        output = tmp_path / "bad2.json"
        result = run_scaffold(
            [
                "--name",
                "bad2",
                "--sprints",
                '["a", "b"]',
                "--output",
                str(output),
            ]
        )
        assert result.returncode == 1
        assert "JSON object" in result.stderr

    def test_exits_1_without_name(self, tmp_path):
        result = run_scaffold(["--output", str(tmp_path / "no-name.json")])
        assert result.returncode != 0
