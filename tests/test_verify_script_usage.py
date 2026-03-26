"""Tests for scripts/verify-script-usage.py"""

from __future__ import annotations

# Allow importing the script (it has a hyphen in its name)
import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parent.parent / "scripts" / "verify-script-usage.py"
spec = importlib.util.spec_from_file_location("verify_script_usage", _SCRIPT)
_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(_mod)  # type: ignore[union-attr]
main = _mod.main
check_file = _mod.check_file


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


@pytest.mark.io
class TestCheckFile:
    def test_no_code_blocks_clean(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.md", "# Title\n\nJust prose, nothing here.\n")
        assert check_file(f) == []

    def test_help_present_clean(self, tmp_path: Path) -> None:
        content = "```bash\nuv run python scripts/foo.py\nuv run python scripts/foo.py --help\n```\n"
        f = _write(tmp_path, "b.md", content)
        assert check_file(f) == []

    def test_help_in_prose_does_not_suppress_block(self, tmp_path: Path) -> None:
        # With per-block tracking, --help in prose does NOT suppress a violation
        # in a subsequent code block that lacks --help.
        content = "Use --help to see options.\n\n```bash\nuv run python scripts/foo.py\n```\n"
        f = _write(tmp_path, "c.md", content)
        assert len(check_file(f)) == 1

    def test_violation_detected(self, tmp_path: Path) -> None:
        content = "```bash\nuv run python scripts/foo.py --run\n```\n"
        f = _write(tmp_path, "d.md", content)
        violations = check_file(f)
        assert len(violations) == 1
        assert "CLI invocation without --help" in violations[0][1]

    def test_python_scripts_prefix(self, tmp_path: Path) -> None:
        content = "```bash\npython scripts/bar.py\n```\n"
        f = _write(tmp_path, "e.md", content)
        assert len(check_file(f)) == 1

    def test_python3_scripts_prefix(self, tmp_path: Path) -> None:
        content = "```bash\npython3 scripts/baz.py\n```\n"
        f = _write(tmp_path, "f.md", content)
        assert len(check_file(f)) == 1

    def test_skip_vendor_dir(self, tmp_path: Path) -> None:
        vendor = tmp_path / "vendor"
        vendor.mkdir()
        f = _write(vendor, "g.md", "```bash\nuv run python scripts/foo.py\n```\n")
        assert check_file(f) == []

    def test_skip_site_dir(self, tmp_path: Path) -> None:
        site = tmp_path / "site"
        site.mkdir()
        f = _write(site, "h.md", "```bash\nuv run python scripts/foo.py\n```\n")
        assert check_file(f) == []


@pytest.mark.io
class TestMain:
    def test_advisory_mode_exits_0_with_violations(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "i.md", "```bash\nuv run python scripts/foo.py\n```\n")
        result = main([str(f)])
        assert result == 0

    def test_strict_exits_1_on_violation(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "j.md", "```bash\nuv run python scripts/foo.py\n```\n")
        result = main(["--strict", str(f)])
        assert result == 1

    def test_strict_exits_0_when_clean(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "k.md", "```bash\nuv run python scripts/foo.py --help\n```\n")
        result = main(["--strict", str(f)])
        assert result == 0

    def test_no_files_exits_0(self) -> None:
        assert main([]) == 0
