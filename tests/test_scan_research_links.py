"""
test_scan_research_links.py — Tests for scripts/scan_research_links.py

Covers:
- Happy path: scans research_docs tier and finds URLs
- Happy path: scans sources tier
- Happy path: scans cache tier
- Happy path: --scope all combines all tiers
- Happy path: --output writes JSON to file
- Happy path: --filter applies regex to URLs
- Happy path: deduplication across files
- Noise filtering: internal GitHub repo links excluded
- Noise filtering: badge URLs excluded
- min-depth filtering
- Missing directories handled gracefully (no exit 1)
- Output JSON structure is correct
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_scan(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/scan_research_links.py", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def make_md(directory: Path, filename: str, content: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    f = directory / filename
    f.write_text(content, encoding="utf-8")
    return f


class TestScanResearchLinksHappyPath:
    def test_returns_zero_exit_on_empty_dir(self, tmp_path):
        # Even if directories are missing, shouldn't crash
        result = run_scan(["--scope", "cache"])
        assert result.returncode == 0

    def test_output_is_valid_json(self, tmp_path):
        result = run_scan(["--scope", "research_docs"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "unique_urls" in data
        assert "urls" in data
        assert isinstance(data["urls"], list)

    def test_output_to_file(self, tmp_path):
        output = tmp_path / "scan-result.json"
        result = run_scan(["--scope", "research_docs", "--output", str(output)])
        assert result.returncode == 0
        assert output.exists()
        data = json.loads(output.read_text())
        assert "urls" in data

    def test_filter_applies_to_results(self, tmp_path):
        # --filter arxiv should only return arxiv.org URLs
        result = run_scan(["--scope", "all", "--filter", "arxiv"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert "arxiv" in entry["url"].lower()

    def test_url_entries_have_required_fields(self, tmp_path):
        result = run_scan(["--scope", "research_docs"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert "url" in entry
            assert "tier" in entry
            assert "sources" in entry
            assert isinstance(entry["sources"], list)

    def test_scanned_files_count_is_integer(self):
        result = run_scan(["--scope", "research_docs"])
        data = json.loads(result.stdout)
        assert isinstance(data["scanned_files"], int)

    def test_deduplication_across_tiers(self):
        # If the same URL appears in multiple docs, unique_urls should count it once
        result = run_scan(["--scope", "all"])
        data = json.loads(result.stdout)
        urls = [entry["url"] for entry in data["urls"]]
        assert len(urls) == len(set(urls)), "Duplicate URLs found in output"


class TestScanResearchLinksNoise:
    def test_internal_repo_links_excluded(self):
        result = run_scan(["--scope", "all"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert "EndogenAI/Workflows" not in entry["url"]

    def test_badge_urls_excluded(self):
        result = run_scan(["--scope", "all"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert "badge.svg" not in entry["url"]
            assert "img.shields.io" not in entry["url"]


class TestScanResearchLinksScopes:
    def test_scope_research_docs_only(self):
        result = run_scan(["--scope", "research_docs"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert entry["tier"] == "research_docs"

    def test_scope_sources_only(self):
        result = run_scan(["--scope", "sources"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert entry["tier"] == "sources"

    def test_scope_cache_only(self):
        result = run_scan(["--scope", "cache"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            assert entry["tier"] == "cache"

    def test_invalid_filter_exits_1(self):
        result = run_scan(["--filter", "[invalid-regex"])
        assert result.returncode == 1
        assert "regex" in result.stderr.lower()


class TestScanResearchLinksMinDepth:
    def test_min_depth_2_excludes_bare_domains(self):
        result = run_scan(["--scope", "research_docs", "--min-depth", "2"])
        data = json.loads(result.stdout)
        for entry in data["urls"]:
            # All returned URLs should have at least 2 path segments
            from urllib.parse import urlparse

            parsed = urlparse(entry["url"])
            path_parts = [p for p in parsed.path.strip("/").split("/") if p]
            assert len(path_parts) >= 2, f"URL has < 2 path segments: {entry['url']}"
