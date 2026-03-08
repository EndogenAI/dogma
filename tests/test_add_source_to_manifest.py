"""
test_add_source_to_manifest.py — Tests for scripts/add_source_to_manifest.py

Covers:
- Happy path: adds a source to an existing manifest
- Happy path: adds multiple sources sequentially
- Happy path: dry-run shows preview without writing
- Error: manifest not found → exit 1
- Error: duplicate URL → exit 1
- Error: invalid sprint key (not in manifest's sprints) → exit 1
- Error: missing required arguments → exit 1
- Default priority is 'medium' if not specified
- Reason field is optional and stored correctly
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def make_blank_manifest(path: Path, sprints: dict | None = None) -> None:
    """Helper: write a minimal manifest JSON to path."""
    sprints = sprints or {"A": "Sprint A", "B": "Sprint B"}
    data = {
        "name": "test-manifest",
        "description": "Test manifest",
        "created": "2026-03-07",
        "sprints": sprints,
        "sources": [],
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_add(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/add_source_to_manifest.py", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


class TestAddSourceHappyPath:
    def test_adds_source_to_manifest(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        result = run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/paper",
                "--title",
                "Test Paper",
                "--sprint",
                "A",
            ]
        )
        assert result.returncode == 0
        data = json.loads(manifest.read_text())
        assert len(data["sources"]) == 1
        assert data["sources"][0]["url"] == "https://example.com/paper"
        assert data["sources"][0]["title"] == "Test Paper"
        assert data["sources"][0]["sprint"] == "A"

    def test_default_priority_is_medium(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/p2",
                "--title",
                "Paper 2",
                "--sprint",
                "A",
            ]
        )
        data = json.loads(manifest.read_text())
        assert data["sources"][0]["priority"] == "medium"

    def test_explicit_priority_stored(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/p3",
                "--title",
                "High Priority",
                "--sprint",
                "B",
                "--priority",
                "high",
            ]
        )
        data = json.loads(manifest.read_text())
        assert data["sources"][0]["priority"] == "high"

    def test_reason_stored_when_provided(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/p4",
                "--title",
                "Paper with reason",
                "--sprint",
                "A",
                "--reason",
                "Key evidence for H1",
            ]
        )
        data = json.loads(manifest.read_text())
        assert data["sources"][0]["reason"] == "Key evidence for H1"

    def test_status_set_to_pending(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/p5",
                "--title",
                "Pending Source",
                "--sprint",
                "A",
            ]
        )
        data = json.loads(manifest.read_text())
        assert data["sources"][0]["status"] == "pending"

    def test_multiple_sources_accumulate(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        for i in range(3):
            run_add(
                [
                    "--manifest",
                    str(manifest),
                    "--url",
                    f"https://example.com/p{i}",
                    "--title",
                    f"Paper {i}",
                    "--sprint",
                    "A",
                ]
            )
        data = json.loads(manifest.read_text())
        assert len(data["sources"]) == 3

    def test_dry_run_does_not_write(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        result = run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/dry",
                "--title",
                "Dry Run Paper",
                "--sprint",
                "A",
                "--dry-run",
            ]
        )
        assert result.returncode == 0
        data = json.loads(manifest.read_text())
        assert len(data["sources"]) == 0  # not written

    def test_dry_run_shows_preview(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        result = run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/dry2",
                "--title",
                "Preview Paper",
                "--sprint",
                "B",
                "--dry-run",
            ]
        )
        assert "dry-run" in result.stdout.lower() or "Would add" in result.stdout


class TestAddSourceErrors:
    def test_exits_1_if_manifest_not_found(self, tmp_path):
        result = run_add(
            [
                "--manifest",
                str(tmp_path / "nonexistent.json"),
                "--url",
                "https://example.com/x",
                "--title",
                "X",
                "--sprint",
                "A",
            ]
        )
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_exits_1_on_duplicate_url(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest)
        run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/dup",
                "--title",
                "First",
                "--sprint",
                "A",
            ]
        )
        result = run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/dup",
                "--title",
                "Duplicate",
                "--sprint",
                "A",
            ]
        )
        assert result.returncode == 1
        assert "already in manifest" in result.stderr

    def test_exits_1_on_invalid_sprint(self, tmp_path):
        manifest = tmp_path / "manifest.json"
        make_blank_manifest(manifest, sprints={"A": "Sprint A"})
        result = run_add(
            [
                "--manifest",
                str(manifest),
                "--url",
                "https://example.com/z",
                "--title",
                "Wrong Sprint",
                "--sprint",
                "Z",  # Z is not in sprints
            ]
        )
        assert result.returncode == 1
        assert "sprint" in result.stderr.lower()

    def test_exits_nonzero_without_required_args(self):
        result = run_add(["--manifest", "docs/research/manifests/something.json"])
        assert result.returncode != 0
