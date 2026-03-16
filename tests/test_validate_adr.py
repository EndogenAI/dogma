"""Tests for scripts/validate_adr.py — Issue #281.

Covers:
- Happy path: a valid ADR passes all checks.
- Missing frontmatter: fails with appropriate error.
- Missing required frontmatter fields: fails per missing field.
- Missing required section headings: fails per missing section.
- Body too short: fails with word count error.
- Parametrized test: all existing ADRs in docs/decisions/ pass.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_adr import (  # noqa: E402
    get_section_headings,
    parse_frontmatter,
    section_present,
    validate_file,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_ADR_CONTENT = """\
---
Status: Accepted
Date: 2026-01-01
Deciders: Test team
---

# ADR-TEST: Example Decision

## Context

This is a test ADR to validate the validator itself. It needs enough context to describe
the problem being solved. The project requires a mechanism to validate ADR structure
consistently across all decision records in the repository. Agents read ADRs and act on
their Status fields; without validation, a missing Status field is invisible until an
agent misinterprets the decision. This section provides the context for the example and
explains why a structured, automated validation approach was chosen over manual review.

## Decision Drivers

- Agents must be able to determine if a decision is Accepted, Proposed, or Superseded.
- ADRs must include a Context section describing the problem and a Consequences section
  describing the tradeoffs of the chosen option.
- Pre-commit enforcement catches schema violations before they reach the main branch.

## Considered Options

1. No validation — prone to drift; agents may act on incomplete ADRs.
2. Manual review only — inconsistent; relies on reviewer memory.
3. Automated validator (validate_adr.py) — deterministic, runs in pre-commit (**chosen**).

## Decision

Adopt validate_adr.py as the canonical ADR validator. It runs in pre-commit and CI.

## Consequences

- All existing ADRs must conform to the schema.
- New ADRs are validated before they can be committed.
- Schema drift is caught at commit time, not at agent-read time.
"""


# ---------------------------------------------------------------------------
# Unit tests — parse_frontmatter
# ---------------------------------------------------------------------------


def test_parse_frontmatter_valid():
    """Valid frontmatter is parsed and body is returned separately."""
    content = "---\nStatus: Accepted\nDate: 2026-01-01\n---\n\n# Body text here"
    fm, body = parse_frontmatter(content)
    assert fm is not None
    assert fm["Status"] == "Accepted"
    assert "Body text here" in body


def test_parse_frontmatter_missing():
    """Content without frontmatter returns (None, full_content)."""
    content = "# ADR-001: No frontmatter\n\n## Context\nSome text."
    fm, body = parse_frontmatter(content)
    assert fm is None
    assert body == content


def test_parse_frontmatter_invalid_yaml():
    """Malformed YAML frontmatter returns (None, full_content)."""
    content = "---\nInvalid: [unclosed\n---\n\n# Body"
    fm, body = parse_frontmatter(content)
    assert fm is None


# ---------------------------------------------------------------------------
# Unit tests — get_section_headings
# ---------------------------------------------------------------------------


def test_get_section_headings():
    """Returns lowercase heading texts for ## and ### headings."""
    content = "# Title\n## Context\n### Sub-section\n## Decision\n"
    headings = get_section_headings(content)
    assert "context" in headings
    assert "sub-section" in headings
    assert "decision" in headings
    # Title (h1) is NOT included
    assert "title" not in headings


# ---------------------------------------------------------------------------
# Unit tests — section_present
# ---------------------------------------------------------------------------


def test_section_present_match():
    """section_present returns True when a pattern matches a heading."""
    assert section_present(["decision drivers"], [r"driver"]) is True
    assert section_present(["considered options"], [r"option"]) is True
    assert section_present(["alternatives"], [r"alternative"]) is True


def test_section_present_no_match():
    """section_present returns False when no pattern matches."""
    assert section_present(["context", "decision"], [r"driver"]) is False


def test_section_present_exact_decision():
    """Heading 'decision' (exact) matches the decision-outcome pattern."""
    assert section_present(["decision"], [r"^decision$"]) is True
    # 'decision drivers' must NOT match the exact 'decision' pattern
    assert section_present(["decision drivers"], [r"^decision$"]) is False


# ---------------------------------------------------------------------------
# Unit tests — validate_file (via tmp files)
# ---------------------------------------------------------------------------


def test_happy_path(tmp_path):
    """A fully valid ADR passes all checks."""
    adr = tmp_path / "ADR-test.md"
    adr.write_text(VALID_ADR_CONTENT, encoding="utf-8")
    errors = validate_file(adr)
    assert errors == [], f"Unexpected errors: {errors}"


def test_missing_frontmatter(tmp_path):
    """An ADR without YAML frontmatter fails."""
    content = VALID_ADR_CONTENT.split("---\n\n", 1)[1]  # strip frontmatter
    adr = tmp_path / "ADR-nofm.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("frontmatter" in e.lower() for e in errors), errors


def test_missing_frontmatter_field_status(tmp_path):
    """An ADR missing 'Status' in frontmatter fails."""
    content = VALID_ADR_CONTENT.replace("Status: Accepted\n", "")
    adr = tmp_path / "ADR-nostatus.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("status" in e.lower() for e in errors), errors


def test_missing_frontmatter_field_date(tmp_path):
    """An ADR missing 'Date' in frontmatter fails."""
    content = VALID_ADR_CONTENT.replace("Date: 2026-01-01\n", "")
    adr = tmp_path / "ADR-nodate.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("date" in e.lower() for e in errors), errors


def test_missing_frontmatter_field_deciders(tmp_path):
    """An ADR missing 'Deciders' in frontmatter fails."""
    content = VALID_ADR_CONTENT.replace("Deciders: Test team\n", "")
    adr = tmp_path / "ADR-nodeciders.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("deciders" in e.lower() for e in errors), errors


def test_missing_section_context(tmp_path):
    """An ADR missing the Context section fails."""
    content = VALID_ADR_CONTENT.replace("## Context\n", "## Background\n")
    adr = tmp_path / "ADR-nocontext.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("Context" in e for e in errors), errors


def test_missing_section_drivers(tmp_path):
    """An ADR missing the Decision Drivers section fails."""
    content = VALID_ADR_CONTENT.replace("## Decision Drivers\n", "## Other\n")
    adr = tmp_path / "ADR-nodrivers.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("Driver" in e for e in errors), errors


def test_missing_section_options(tmp_path):
    """An ADR missing the Considered Options section fails."""
    content = VALID_ADR_CONTENT.replace("## Considered Options\n", "## Something Else\n")
    adr = tmp_path / "ADR-nooptions.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("Option" in e or "Alternative" in e for e in errors), errors


def test_missing_section_decision_outcome(tmp_path):
    """An ADR missing the Decision / Outcome section fails."""
    content = VALID_ADR_CONTENT.replace("## Decision\n", "## Resolution\n")
    adr = tmp_path / "ADR-nodecision.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("Decision Outcome" in e or "Outcome" in e or "Decision" in e for e in errors), errors


def test_missing_section_consequences(tmp_path):
    """An ADR missing the Consequences section fails."""
    content = VALID_ADR_CONTENT.replace("## Consequences\n", "## Notes\n")
    adr = tmp_path / "ADR-noconseq.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("Consequence" in e or "Pros" in e for e in errors), errors


def test_body_too_short(tmp_path):
    """An ADR with fewer than MIN_BODY_WORDS words in the body fails."""
    content = """\
---
Status: Accepted
Date: 2026-01-01
Deciders: Test team
---

# ADR-short: Short Decision

## Context

Short.

## Decision Drivers

- Short.

## Considered Options

1. Short.

## Decision

Short.

## Consequences

Short.
"""
    adr = tmp_path / "ADR-short.md"
    adr.write_text(content, encoding="utf-8")
    errors = validate_file(adr)
    assert any("too short" in e.lower() or "body" in e.lower() for e in errors), errors


# ---------------------------------------------------------------------------
# Parametrized test: all existing ADRs must pass
# ---------------------------------------------------------------------------

_adr_files = sorted(REPO_ROOT.glob("docs/decisions/ADR-*.md"))


@pytest.mark.parametrize("adr_path", _adr_files, ids=[p.name for p in _adr_files])
def test_existing_adrs_pass(adr_path):
    """Every committed ADR in docs/decisions/ must pass validation."""
    errors = validate_file(adr_path)
    assert errors == [], f"{adr_path.name} failed:\n" + "\n".join(f"  - {e}" for e in errors)


# ---------------------------------------------------------------------------
# Subprocess integration test
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_cli_pass(tmp_path):
    """CLI exits 0 when a valid file is passed."""
    adr = tmp_path / "ADR-cli.md"
    adr.write_text(VALID_ADR_CONTENT, encoding="utf-8")
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_adr.py", str(adr)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.integration
def test_cli_fail_on_missing_frontmatter(tmp_path):
    """CLI exits 1 when frontmatter is missing."""
    content = "# ADR-cli-nofm\n\n## Context\nSome context here.\n"
    adr = tmp_path / "ADR-cli-nofm.md"
    adr.write_text(content, encoding="utf-8")
    result = subprocess.run(
        ["uv", "run", "python", "scripts/validate_adr.py", str(adr)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
