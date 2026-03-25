"""tests/test_audit_ai_dependencies.py

Tests for scripts/audit_ai_dependencies.py

Covers:
1. test_detect_providers_claude
2. test_detect_providers_openai
3. test_detect_providers_ollama
4. test_detect_providers_no_match
5. test_detect_providers_multiple_in_one_line
6. test_scan_file_returns_records
7. test_scan_file_unreadable_returns_empty
8. test_aggregate_by_provider
9. test_main_dry_run_outputs_yaml
10. test_main_missing_directory_returns_1
11. test_main_writes_output_file
12. test_main_output_uses_raw_references_key
"""

from __future__ import annotations

# Import module under test
import importlib
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

audit_mod = importlib.import_module("scripts.audit_ai_dependencies")
_detect_providers = audit_mod._detect_providers
scan_file = audit_mod.scan_file
aggregate_by_provider = audit_mod.aggregate_by_provider
main = audit_mod.main


# ---------------------------------------------------------------------------
# 1–5: _detect_providers
# ---------------------------------------------------------------------------


class TestDetectProviders:
    def test_detect_providers_claude(self) -> None:
        results = _detect_providers("uses anthropic claude-3 model")
        ids = [r[0] for r in results]
        assert "claude" in ids

    def test_detect_providers_openai(self) -> None:
        results = _detect_providers("calls api.openai.com endpoint")
        ids = [r[0] for r in results]
        assert "openai" in ids

    def test_detect_providers_ollama(self) -> None:
        results = _detect_providers("curl http://localhost:11434/api/generate")
        ids = [r[0] for r in results]
        assert "ollama" in ids

    def test_detect_providers_no_match(self) -> None:
        results = _detect_providers("just a plain comment with no providers")
        assert results == []

    def test_detect_providers_multiple_in_one_line(self) -> None:
        results = _detect_providers("uses openai and anthropic claude together")
        ids = [r[0] for r in results]
        assert "openai" in ids
        assert "claude" in ids


# ---------------------------------------------------------------------------
# 6–7: scan_file
# ---------------------------------------------------------------------------


class TestScanFile:
    def test_scan_file_returns_records(self, tmp_path: Path) -> None:
        f = tmp_path / "agent.md"
        f.write_text("uses claude-3-opus model\nno other providers here\n")
        records = scan_file(f)
        assert len(records) >= 1
        assert records[0]["provider_id"] == "claude"
        assert records[0]["file"] == str(f)
        assert "evidence" in records[0]

    def test_scan_file_unreadable_returns_empty(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.py"
        # scan_file catches OSError; missing file raises OSError on read
        records = scan_file(missing)
        assert records == []


# ---------------------------------------------------------------------------
# 8: aggregate_by_provider
# ---------------------------------------------------------------------------


class TestAggregateByProvider:
    def test_aggregate_by_provider(self) -> None:
        records = [
            {
                "file": "a.py",
                "provider_id": "claude",
                "provider_name": "Anthropic / Claude",
                "line_number": 1,
                "evidence": "x",
            },
            {
                "file": "b.py",
                "provider_id": "claude",
                "provider_name": "Anthropic / Claude",
                "line_number": 5,
                "evidence": "y",
            },
            {
                "file": "a.py",
                "provider_id": "openai",
                "provider_name": "OpenAI",
                "line_number": 2,
                "evidence": "z",
            },
        ]
        summary = aggregate_by_provider(records)
        assert summary["claude"]["reference_count"] == 2
        assert set(summary["claude"]["files"]) == {"a.py", "b.py"}
        assert summary["openai"]["reference_count"] == 1


# ---------------------------------------------------------------------------
# 9–12: main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_main_dry_run_outputs_yaml(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        agents_dir = tmp_path / "agents"
        scripts_dir = tmp_path / "scripts"
        agents_dir.mkdir()
        scripts_dir.mkdir()
        (agents_dir / "test.agent.md").write_text("uses claude-3 here\n")

        with patch.object(audit_mod, "_get_root", return_value=tmp_path):
            rc = main(["--dry-run", "--agents-dir", str(agents_dir), "--scripts-dir", str(scripts_dir)])

        assert rc == 0
        out = capsys.readouterr().out
        parsed = yaml.safe_load(out)
        assert "scan_date" in parsed
        assert "providers" in parsed

    def test_main_missing_directory_returns_1(self, tmp_path: Path) -> None:
        rc = main(["--agents-dir", str(tmp_path / "no_agents"), "--scripts-dir", str(tmp_path / "no_scripts")])
        assert rc == 1

    def test_main_writes_output_file(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        scripts_dir = tmp_path / "scripts"
        agents_dir.mkdir()
        scripts_dir.mkdir()
        out_file = tmp_path / "inventory.yml"

        with patch.object(audit_mod, "_get_root", return_value=tmp_path):
            rc = main(["--agents-dir", str(agents_dir), "--scripts-dir", str(scripts_dir), "--output", str(out_file)])

        assert rc == 0
        assert out_file.exists()
        parsed = yaml.safe_load(out_file.read_text())
        assert "scan_date" in parsed

    def test_main_output_uses_raw_references_key(self, tmp_path: Path) -> None:
        """Regression: output must use raw_references[], not dependencies[]."""
        agents_dir = tmp_path / "agents"
        scripts_dir = tmp_path / "scripts"
        agents_dir.mkdir()
        scripts_dir.mkdir()
        (scripts_dir / "demo.py").write_text("import anthropic  # claude usage\n")
        out_file = tmp_path / "inv.yml"

        with patch.object(audit_mod, "_get_root", return_value=tmp_path):
            main(["--agents-dir", str(agents_dir), "--scripts-dir", str(scripts_dir), "--output", str(out_file)])

        parsed = yaml.safe_load(out_file.read_text())
        assert "raw_references" in parsed, "output must use 'raw_references' key (not 'dependencies')"
        assert "dependencies" not in parsed
