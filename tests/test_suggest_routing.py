"""tests/test_suggest_routing.py — Tests for scripts/suggest_routing.py

Tests cover:
    - match_categories: keyword matching (hit, miss, case-insensitive)
    - topo_sort_agents: ordering respects AGENT_TOPO_ORDER
    - build_steps: correct step count, axiom annotation, FSM gates
    - get_fsm_gate: boundary / mid-step gate labels
    - format_table / format_markdown: output shape
    - main CLI: task, --format json/markdown, --all-steps, exit-code 2 for no match
"""

from __future__ import annotations

import json

import pytest

from scripts.suggest_routing import (
    build_steps,
    format_markdown,
    format_table,
    get_axiom_for_category,
    get_fsm_gate,
    load_amplification_table,
    load_classifier,
    load_fsm,
    main,
    match_categories,
    topo_sort_agents,
)

# ---------------------------------------------------------------------------
# Minimal YAML fixtures
# ---------------------------------------------------------------------------

MINIMAL_CLASSIFIER_YAML = """\
- category: scripting
  keywords: [script, implement, build]
  agent: Executive Scripter
  axiom: Programmatic-First
  description: Script authoring

- category: docs
  keywords: [docs, documentation, guide]
  agent: Executive Docs
  axiom: Documentation-First
  description: Documentation writing

- category: research
  keywords: [research, survey, fetch]
  agent: Executive Researcher
  axiom: Endogenous-First
  description: Research sprint
"""

MINIMAL_AMPLIFICATION_YAML = """\
- keywords: "scripting|automate|encode|ci"
  keyword_list: [scripting, automate, encode, ci]
  amplify: "Programmatic-First"
  expression_hint: "Encode as a script before the third time"

- keywords: "docs|documentation|guide"
  keyword_list: [docs, documentation, guide]
  amplify: "Documentation-First"
  expression_hint: "Always update docs alongside workflow changes"
"""

MINIMAL_FSM_YAML = """\
phase_types:
  - id: domain
    label: Domain Phase
  - id: review
    label: Review Gate
transitions:
  - from: domain
    to: review
    trigger: phase_complete
  - from: review
    to: domain
    trigger: approved
"""


@pytest.fixture()
def classifier_file(tmp_path):
    f = tmp_path / "classifier.yml"
    f.write_text(MINIMAL_CLASSIFIER_YAML, encoding="utf-8")
    return f


@pytest.fixture()
def amplification_file(tmp_path):
    f = tmp_path / "amp.yml"
    f.write_text(MINIMAL_AMPLIFICATION_YAML, encoding="utf-8")
    return f


@pytest.fixture()
def fsm_file(tmp_path):
    f = tmp_path / "fsm.yml"
    f.write_text(MINIMAL_FSM_YAML, encoding="utf-8")
    return f


@pytest.fixture()
def classifier(classifier_file):
    return load_classifier(classifier_file)


@pytest.fixture()
def amplification_table(amplification_file):
    return load_amplification_table(amplification_file)


@pytest.fixture()
def fsm(fsm_file):
    return load_fsm(fsm_file)


# ---------------------------------------------------------------------------
# match_categories
# ---------------------------------------------------------------------------


def test_match_categories_hit(classifier):
    results = match_categories("implement a new script", classifier)
    categories = [e["category"] for e in results]
    assert "scripting" in categories


def test_match_categories_miss(classifier):
    results = match_categories("deploy kubernetes cluster", classifier)
    assert results == []


def test_match_categories_case_insensitive(classifier):
    results = match_categories("RESEARCH the codebase", classifier)
    categories = [e["category"] for e in results]
    assert "research" in categories


def test_match_categories_multi(classifier):
    """A task mentioning docs and script should match both categories."""
    results = match_categories("implement a docs update script", classifier)
    categories = [e["category"] for e in results]
    assert "scripting" in categories
    assert "docs" in categories


def test_match_categories_no_duplicates(classifier):
    """Repeated keyword hits should not create duplicate entries."""
    results = match_categories("script script script", classifier)
    categories = [e["category"] for e in results]
    assert categories.count("scripting") == 1


# ---------------------------------------------------------------------------
# topo_sort_agents
# ---------------------------------------------------------------------------


def test_topo_sort_agents_known_order(classifier):
    """Researcher is topologically before Docs which is before Scripter."""
    entries = [
        {"category": "scripting", "agent": "Executive Scripter", "axiom": "Programmatic-First"},
        {"category": "research", "agent": "Executive Researcher", "axiom": "Endogenous-First"},
    ]
    sorted_entries = topo_sort_agents(entries)
    agents = [e["agent"] for e in sorted_entries]
    if "Executive Researcher" in agents and "Executive Scripter" in agents:
        assert agents.index("Executive Researcher") < agents.index("Executive Scripter")


def test_topo_sort_agents_unknown_agent_appended(classifier):
    """Agents not in AGENT_TOPO_ORDER should be appended at the end."""
    entries = [
        {"category": "scripting", "agent": "Executive Scripter", "axiom": "Programmatic-First"},
        {"category": "unknown", "agent": "Totally Unknown Agent", "axiom": "???"},
    ]
    sorted_entries = topo_sort_agents(entries)
    agents = [e["agent"] for e in sorted_entries]
    assert agents[-1] == "Totally Unknown Agent"


def test_topo_sort_agents_output_length(classifier):
    entries = [
        {"category": "scripting", "agent": "Executive Scripter", "axiom": "Programmatic-First"},
        {"category": "docs", "agent": "Executive Docs", "axiom": "Documentation-First"},
    ]
    sorted_entries = topo_sort_agents(entries)
    assert len(sorted_entries) == 2


# ---------------------------------------------------------------------------
# build_steps
# ---------------------------------------------------------------------------


def test_build_steps_count(classifier, amplification_table, fsm):
    steps = build_steps("implement a script", classifier, amplification_table, fsm)
    assert len(steps) == 1
    assert steps[0]["agent"] == "Executive Scripter"


def test_build_steps_has_required_keys(classifier, amplification_table, fsm):
    steps = build_steps("implement a script", classifier, amplification_table, fsm)
    required = {"step", "agent", "category", "description", "axiom", "fsm_gate"}
    assert required <= steps[0].keys()


def test_build_steps_no_match_returns_empty(classifier, amplification_table, fsm):
    steps = build_steps("deploy kubernetes pod", classifier, amplification_table, fsm)
    assert steps == []


def test_build_steps_all_steps(classifier, amplification_table, fsm):
    steps = build_steps("", classifier, amplification_table, fsm, include_all=True)
    assert len(steps) == len(classifier)


def test_build_steps_step_numbers_sequential(classifier, amplification_table, fsm):
    steps = build_steps("", classifier, amplification_table, fsm, include_all=True)
    for i, step in enumerate(steps, start=1):
        assert step["step"] == i


# ---------------------------------------------------------------------------
# get_axiom_for_category
# ---------------------------------------------------------------------------


def test_get_axiom_known(amplification_table):
    axiom = get_axiom_for_category(amplification_table, "scripting")
    assert axiom == "Programmatic-First"


def test_get_axiom_unknown_returns_default(amplification_table):
    axiom = get_axiom_for_category(amplification_table, "nonexistent_xyz_category")
    assert axiom == "Algorithms-Before-Tokens"


# ---------------------------------------------------------------------------
# get_fsm_gate
# ---------------------------------------------------------------------------


def test_get_fsm_gate_returns_string(fsm):
    gate = get_fsm_gate(fsm, 0, 3)
    assert isinstance(gate, str)


# ---------------------------------------------------------------------------
# format_table / format_markdown
# ---------------------------------------------------------------------------


def test_format_table_contains_agent(classifier, amplification_table, fsm):
    steps = build_steps("", classifier, amplification_table, fsm, include_all=True)
    output = format_table(steps)
    assert "Executive Scripter" in output
    assert "Executive Docs" in output


def test_format_markdown_headers(classifier, amplification_table, fsm):
    steps = build_steps("", classifier, amplification_table, fsm, include_all=True)
    output = format_markdown(steps)
    assert "##" in output or "**" in output


def test_format_markdown_contains_agent(classifier, amplification_table, fsm):
    steps = build_steps("", classifier, amplification_table, fsm, include_all=True)
    output = format_markdown(steps)
    assert "Executive Docs" in output


# ---------------------------------------------------------------------------
# main CLI
# ---------------------------------------------------------------------------


@pytest.mark.io
def test_main_table(classifier_file, amplification_file, fsm_file, capsys):
    rc = main(
        [
            "implement a new script",
            "--classifier",
            str(classifier_file),
            "--amplification-table",
            str(amplification_file),
            "--fsm",
            str(fsm_file),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Executive Scripter" in out


@pytest.mark.io
def test_main_json(classifier_file, amplification_file, fsm_file, capsys):
    rc = main(
        [
            "implement a new script",
            "--classifier",
            str(classifier_file),
            "--amplification-table",
            str(amplification_file),
            "--fsm",
            str(fsm_file),
            "--format",
            "json",
        ]
    )
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["agent"] == "Executive Scripter"


@pytest.mark.io
def test_main_markdown(classifier_file, amplification_file, fsm_file, capsys):
    rc = main(
        [
            "write some documentation",
            "--classifier",
            str(classifier_file),
            "--amplification-table",
            str(amplification_file),
            "--fsm",
            str(fsm_file),
            "--format",
            "markdown",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Executive Docs" in out


@pytest.mark.io
def test_main_all_steps(classifier_file, amplification_file, fsm_file, capsys):
    rc = main(
        [
            "--all-steps",
            "--classifier",
            str(classifier_file),
            "--amplification-table",
            str(amplification_file),
            "--fsm",
            str(fsm_file),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Executive Scripter" in out
    assert "Executive Docs" in out


@pytest.mark.io
def test_main_no_match_exit_2(classifier_file, amplification_file, fsm_file):
    rc = main(
        [
            "deploy kubernetes cluster with helm",
            "--classifier",
            str(classifier_file),
            "--amplification-table",
            str(amplification_file),
            "--fsm",
            str(fsm_file),
        ]
    )
    assert rc == 2


@pytest.mark.io
def test_main_missing_classifier(tmp_path, amplification_file, fsm_file):
    rc = main(
        [
            "implement a script",
            "--classifier",
            str(tmp_path / "missing.yml"),
            "--amplification-table",
            str(amplification_file),
            "--fsm",
            str(fsm_file),
        ]
    )
    assert rc == 1
