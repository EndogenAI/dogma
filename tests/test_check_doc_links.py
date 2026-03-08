"""
Tests for scripts/check_doc_links.py

Covers:
- Happy path: all links resolve
- Broken relative link detected
- Absolute /path links skipped (site-root-relative URL pattern)
- http/https/mailto/# links skipped
- Links inside fenced code blocks skipped
- Placeholder targets ('...') skipped
- docs/research/sources/ excluded from default scan
- Exit code 0 when clean, 1 when broken links found
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_doc_links.py"


def run_check(files: list[Path]) -> tuple[int, str]:
    """Run check_doc_links.py against the given files and return (exit_code, stderr)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(f) for f in files],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stderr


# ------------------------------------------------------------------
# Unit tests (isolated via tmp_path)
# ------------------------------------------------------------------


@pytest.mark.io
def test_good_link_passes(tmp_path: Path) -> None:
    """A relative link that resolves to an existing file should pass."""
    target = tmp_path / "target.md"
    target.write_text("# Target\n")
    doc = tmp_path / "source.md"
    doc.write_text("See [target](target.md).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0
    assert stderr == ""


@pytest.mark.io
def test_broken_relative_link_fails(tmp_path: Path) -> None:
    """A relative link that does NOT resolve should fail with exit code 1."""
    doc = tmp_path / "source.md"
    doc.write_text("See [missing](subdir/missing.md).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 1
    assert "broken relative link" in stderr
    assert "subdir/missing.md" in stderr


@pytest.mark.io
def test_absolute_path_link_skipped(tmp_path: Path) -> None:
    """Links starting with '/' (site-root-relative) should be skipped entirely."""
    doc = tmp_path / "source.md"
    doc.write_text("See [API](/api/references/vscode-api#lm).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_https_link_skipped(tmp_path: Path) -> None:
    """https:// links should not be checked by this script."""
    doc = tmp_path / "source.md"
    doc.write_text("See [external](https://example.com/path).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_anchor_only_link_skipped(tmp_path: Path) -> None:
    """Pure anchor links (#section) should be skipped."""
    doc = tmp_path / "source.md"
    doc.write_text("Jump to [section](#section-heading).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_link_in_code_fence_skipped(tmp_path: Path) -> None:
    """Links inside fenced code blocks should NOT be checked."""
    doc = tmp_path / "source.md"
    doc.write_text("```markdown\n## Endogenous Sources\n\nRead [`MANIFESTO.md`](../../../MANIFESTO.md).\n```\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_placeholder_ellipsis_skipped(tmp_path: Path) -> None:
    """Placeholder targets like '...' should NOT be flagged as broken links."""
    doc = tmp_path / "source.md"
    doc.write_text("- **Issue**: [#XX Implement X](...)\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_link_with_anchor_fragment_resolves_file(tmp_path: Path) -> None:
    """A link like file.md#section should check that file.md exists."""
    target = tmp_path / "target.md"
    target.write_text("# Section\n")
    doc = tmp_path / "source.md"
    doc.write_text("See [section](target.md#section).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_wrong_depth_github_path_fails(tmp_path: Path) -> None:
    """The exact failure pattern from the CI breakage: .github/ from docs/ depth."""
    # Simulate docs/research/doc.md linking to .github/ without going up enough.
    research_dir = tmp_path / "docs" / "research"
    research_dir.mkdir(parents=True)
    doc = research_dir / "taxonomy.md"
    # This link is wrong: from docs/research/ you need ../../.github/ not .github/
    doc.write_text("See [AGENTS](.github/agents/AGENTS.md).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 1
    assert ".github/agents/AGENTS.md" in stderr


@pytest.mark.io
def test_correct_depth_github_path_passes(tmp_path: Path) -> None:
    """The corrected pattern: ../../.github/ from docs/research/ resolves correctly."""
    # Build a minimal repo-like structure in tmp_path.
    research_dir = tmp_path / "docs" / "research"
    research_dir.mkdir(parents=True)
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    agents_file = agents_dir / "AGENTS.md"
    agents_file.write_text("# AGENTS\n")

    doc = research_dir / "taxonomy.md"
    doc.write_text("See [AGENTS](../../.github/agents/AGENTS.md).\n")

    exit_code, stderr = run_check([doc])
    assert exit_code == 0


@pytest.mark.io
def test_multiple_files_reports_all_broken(tmp_path: Path) -> None:
    """When multiple files have broken links, all should be reported."""
    doc_a = tmp_path / "a.md"
    doc_a.write_text("[broken](nonexistent_a.md)\n")
    doc_b = tmp_path / "b.md"
    doc_b.write_text("[broken](nonexistent_b.md)\n")

    exit_code, stderr = run_check([doc_a, doc_b])
    assert exit_code == 1
    assert "nonexistent_a.md" in stderr
    assert "nonexistent_b.md" in stderr


# ------------------------------------------------------------------
# Integration: default scan excludes sources/
# ------------------------------------------------------------------


@pytest.mark.integration
def test_default_scan_excludes_sources_dir() -> None:
    """Default scan should cleanly exclude docs/research/sources/ (external content)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_doc_links", str(SCRIPT))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    files = mod.collect_default_files()
    sources_dir = mod.REPO_ROOT / "docs" / "research" / "sources"
    from_sources = [f for f in files if str(f).startswith(str(sources_dir))]
    assert from_sources == [], f"sources/ files should be excluded: {from_sources[:3]}"


@pytest.mark.integration
def test_full_repo_scan_passes() -> None:
    """Running against the full repo (default scope) should exit 0."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Full repo scan found broken links:\n{result.stderr}"
