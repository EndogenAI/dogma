"""
tests/conftest.py

Shared pytest fixtures for all script tests.

Provides:
- tmp_repo: Temporary isolated git repository for testing file operations
- git_mock: Mocks git commands to return predictable branch names and refs
- sample_markdown: Generates sample markdown content for scratchpad testing
- sample_agent_md: Generates sample .agent.md content
- sample_research_md: Generates sample research synthesis documents
"""

import os
import subprocess
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def tmp_repo(tmp_path, monkeypatch):
    """
    Create an isolated temporary git repository.
    
    Initialises git, configures user.name and user.email, and changes
    working directory to the repo. Useful for testing file operations
    that interact with git (e.g., prune_scratchpad.py).
    
    Yields:
        Path: The root of the temporary repo.
    
    Cleans up automatically (pytest tmp_path fixture handles cleanup).
    """
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    
    # Initialise git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    
    # Create initial commit so branches work
    initial_file = repo_path / "README.md"
    initial_file.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    
    yield repo_path


@pytest.fixture
def git_branch_mock(monkeypatch):
    """
    Mock git branch resolution to return a predictable branch name.
    
    Useful for testing scripts that call `git rev-parse --abbrev-ref HEAD`.
    By default returns 'feat/test-branch'. Can be overridden per test.
    
    Yields:
        A function that takes a branch name and patches git to return it.
    """
    def set_branch(branch: str = "feat/test-branch"):
        def mock_run(*args, **kwargs):
            if args[0] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
                result = MagicMock()
                result.stdout = branch.encode()
                result.returncode = 0
                return result
            return subprocess.run(*args, **kwargs)
        
        monkeypatch.setattr(subprocess, "run", mock_run)
    
    set_branch()
    return set_branch


@pytest.fixture
def today_date():
    """Return today's date for consistent test dating."""
    return date.today().strftime("%Y-%m-%d")


@pytest.fixture
def sample_markdown(today_date):
    """
    Generate sample markdown content for scratchpad testing.
    
    Yields a dict with 'content' and 'file_path' keys for testing
    prune_scratchpad.py and related file operations.
    """
    content = f"""# Session Scratchpad — {today_date}

## Orchestration Plan

This is the plan section.

Line 2 of content.

## Phase 1 Output

This is phase 1 output that should remain live.

More details about phase 1.

## Phase 2 Results

This phase is complete and should be archived.

Some result content here.

## Session Summary

Session complete at {today_date}.
"""
    return {"content": content, "today": today_date}


@pytest.fixture
def sample_agent_md():
    """Generate a sample .agent.md file for scaffold_agent.py testing."""
    return """---
name: Test Agent
description: A test agent for unit testing
tools:
  - search
  - read
  - edit
handoffs:
  - label: Hand off to Review
    agent: Review
---

## Role

Test role description.

## Capabilities

- Test capability 1
- Test capability 2
"""


@pytest.fixture
def sample_d3_synthesis():
    """
    Generate a sample D3 per-source synthesis document
    for validate_synthesis.py testing.
    """
    return """---
url: https://example.com/test-source
cache_path: .cache/sources/example-com-test-source.md
slug: example-test-source
title: Test Source Synthesis
---

# Example Test Source Synthesis

## Summary

Brief summary of the source.

## Key Findings

- Finding 1
- Finding 2

## Methodology

How we analysed this.

## Strengths

What this source does well.

## Limitations

Limitations of the source.

## Relevance to Endogenic Development

Why this matters to the project.

## Related Sources

- [Other source](./other-source.md)

## Referenced By

(Populated by link_source_stubs.py)
"""


@pytest.fixture
def sample_d4_synthesis():
    """
    Generate a sample D4 issue synthesis document
    for validate_synthesis.py testing.
    """
    return """---
title: Agent Fleet Design Patterns
status: Final
---

# Agent Fleet Design Patterns

## Executive Summary

Summary of research findings.

## Key Discoveries

Multiple discoveries covered here in detail.

## Implications for Endogenic Development

How this applies to the methodology.

## Recommended Actions

Recommendations from the research.

## Project Relevance

How this connects to current work.
"""


@pytest.fixture
def monkeypatch_env(monkeypatch):
    """
    Convenience fixture for setting environment variables in tests.
    
    Usage:
        def test_something(monkeypatch_env):
            monkeypatch_env("MY_VAR", "value")
    """
    def set_env(key: str, value: str):
        monkeypatch.setenv(key, value)
    
    return set_env
