"""Tests for scripts/check_domain_overlap.py"""

import sys

import pytest

# Import the script module for unit testing
sys.path.insert(0, "scripts")
import check_domain_overlap


def test_extract_keywords():
    """Test keyword extraction from branch names."""
    assert "governance" in check_domain_overlap.extract_keywords("feat/governance-audit")
    assert "audit" in check_domain_overlap.extract_keywords("feat/governance-audit")
    assert "feat" not in check_domain_overlap.extract_keywords("feat/governance-audit")

    keywords = check_domain_overlap.extract_keywords("fix/database-connection-pool")
    assert "database" in keywords
    assert "connection" in keywords
    assert "pool" in keywords


def test_extract_keywords_filters_stopwords():
    """Test that stop words are properly filtered."""
    keywords = check_domain_overlap.extract_keywords("feat/update-the-documentation-for-agents")
    assert "the" not in keywords
    assert "for" not in keywords
    assert "update" in keywords
    assert "documentation" in keywords
    assert "agents" in keywords


def test_check_overlap_logic():
    """Test overlap detection logic directly."""
    open_prs = [
        {"number": 10, "headRefName": "feat/governance-scripts", "title": "Add governance tooling"},
        {"number": 11, "headRefName": "chore/dependency-update", "title": "Update deps"},
    ]

    # Should detect overlap on "governance"
    warnings = check_domain_overlap.check_overlap("feat/governance-audit", open_prs)
    assert len(warnings) > 0
    assert "governance" in warnings[0].lower()

    # Should not detect overlap with different domain
    warnings = check_domain_overlap.check_overlap("feat/docs-formatting", open_prs)
    assert len(warnings) == 0


def test_check_overlap_self_skip():
    """Test that branch doesn't overlap with its own PR."""
    open_prs = [{"number": 15, "headRefName": "feat/governance-audit", "title": "Governance audit implementation"}]

    # Should not report overlap with itself
    warnings = check_domain_overlap.check_overlap("feat/governance-audit", open_prs)
    assert len(warnings) == 0


# Integration tests requiring gh CLI are marked for manual runs only
@pytest.mark.skip(reason="Integration test - requires gh CLI and live GitHub access")
def test_no_overlap_safe_integration():
    """Integration test - requires mocking gh CLI."""
    pass


@pytest.mark.skip(reason="Integration test - requires gh CLI and live GitHub access")
def test_main_branch_skipped_integration():
    """Integration test - requires actual script execution."""
    pass
