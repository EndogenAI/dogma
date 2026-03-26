"""Tests for scripts/validate_cascade.py."""

import importlib
from pathlib import Path

# Load script as module
spec = importlib.util.spec_from_file_location(
    "validate_cascade",
    Path(__file__).parent.parent / "scripts" / "validate_cascade.py",
)
validate_cascade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_cascade)


# ---------------------------------------------------------------------------
# Tier 1
# ---------------------------------------------------------------------------


def test_tier1_pass(tmp_path):
    cvf = tmp_path / "client-values.yml"
    cvf.write_text("project_name: Acme\ndomain: governance\nmission: Build trust\n")
    status, msg = validate_cascade.check_tier1(tmp_path, [str(cvf)])
    assert status == "PASS"
    assert "required fields" in msg


def test_tier1_warn(tmp_path):
    cvf = tmp_path / "client-values.yml"
    cvf.write_text("project_name: Acme\ndomain: governance\nmission: \n")
    status, msg = validate_cascade.check_tier1(tmp_path, [str(cvf)])
    assert status == "WARN"
    assert "mission" in msg


def test_tier1_fail(tmp_path):
    cvf = tmp_path / "client-values.yml"
    cvf.write_text("project_name: Acme\nmission: Build trust\n")
    status, msg = validate_cascade.check_tier1(tmp_path, [str(cvf)])
    assert status == "FAIL"
    assert "domain" in msg


def test_tier1_no_file_pass(tmp_path):
    (tmp_path / "MANIFESTO.md").write_text("# MANIFESTO\n")
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n")
    status, _ = validate_cascade.check_tier1(tmp_path, [])
    assert status == "PASS"


def test_tier1_no_file_fail(tmp_path):
    # Only AGENTS.md, no MANIFESTO.md
    (tmp_path / "AGENTS.md").write_text("# AGENTS\n")
    status, msg = validate_cascade.check_tier1(tmp_path, [])
    assert status == "FAIL"
    assert "MANIFESTO.md" in msg


# ---------------------------------------------------------------------------
# Tier 2
# ---------------------------------------------------------------------------


def test_tier2_pass(tmp_path):
    refs = "\n".join(
        [
            "See [MANIFESTO.md](MANIFESTO.md#1-endogenous-first)",
            "MANIFESTO.md § 2 Algorithms",
            "MANIFESTO.md § 3 Local",
            "[MANIFESTO.md § Ethical",
            "MANIFESTO.md § Foundational",
        ]
    )
    (tmp_path / "AGENTS.md").write_text(refs)
    status, msg = validate_cascade.check_tier2(tmp_path)
    assert status == "PASS"
    assert "MANIFESTO" in msg


def test_tier2_warn(tmp_path):
    (tmp_path / "AGENTS.md").write_text("[MANIFESTO.md some ref here\n")
    status, _ = validate_cascade.check_tier2(tmp_path)
    assert status == "WARN"


def test_tier2_fail(tmp_path):
    (tmp_path / "AGENTS.md").write_text("No references here at all.\n")
    status, msg = validate_cascade.check_tier2(tmp_path)
    assert status == "FAIL"
    assert "0" in msg


def test_tier2_missing_agents_md(tmp_path):
    status, msg = validate_cascade.check_tier2(tmp_path)
    assert status == "FAIL"
    assert "AGENTS.md" in msg


# ---------------------------------------------------------------------------
# Tier 3
# ---------------------------------------------------------------------------


def test_tier3_pass(tmp_path):
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    for i in range(8):
        content = "<constraints>\nsome rule\n</constraints>\n" if i < 6 else "no tag here\n"
        (agents_dir / f"agent{i}.agent.md").write_text(content)
    status, msg = validate_cascade.check_tier3(tmp_path)
    assert status == "PASS"
    assert "6/8" in msg


def test_tier3_warn(tmp_path):
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    for i in range(4):
        content = "<constraints>rule</constraints>" if i < 1 else "no tag"
        (agents_dir / f"agent{i}.agent.md").write_text(content)
    status, _ = validate_cascade.check_tier3(tmp_path)
    assert status == "WARN"


def test_tier3_fail(tmp_path):
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    for i in range(8):
        (agents_dir / f"agent{i}.agent.md").write_text("no constraints tag\n")
    status, _ = validate_cascade.check_tier3(tmp_path)
    assert status == "FAIL"


# ---------------------------------------------------------------------------
# Tier 4
# ---------------------------------------------------------------------------


def test_tier4_pass(tmp_path):
    skills_dir = tmp_path / ".github" / "skills"
    for i in range(4):
        d = skills_dir / f"skill{i}"
        d.mkdir(parents=True)
        content = "See AGENTS.md for governance\n" if i < 3 else "no reference\n"
        (d / "SKILL.md").write_text(content)
    status, msg = validate_cascade.check_tier4(tmp_path)
    assert status == "PASS"


def test_tier4_fail(tmp_path):
    skills_dir = tmp_path / ".github" / "skills"
    for i in range(4):
        d = skills_dir / f"skill{i}"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("no governance ref\n")
    status, _ = validate_cascade.check_tier4(tmp_path)
    assert status == "FAIL"


# ---------------------------------------------------------------------------
# Tier 5
# ---------------------------------------------------------------------------


def test_tier5_always_pass():
    status, msg = validate_cascade.check_tier5()
    assert status == "PASS"
    assert "runtime" in msg.lower()


# ---------------------------------------------------------------------------
# Integration — full run on actual repo root
# ---------------------------------------------------------------------------


def test_all_tiers_run():
    repo_root = Path(__file__).parent.parent
    exit_code = validate_cascade.main(["--repo-root", str(repo_root)])
    assert exit_code == 0
