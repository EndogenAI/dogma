"""validate_cascade.py — Validate T1→T5 governance cascade encoding for a client deployment.

Purpose:
    Checks that the encoding chain (MANIFESTO → AGENTS.md → agents → skills → session)
    is intact and that each tier references its parent tier. Implements
    client-manifesto-adoption-pattern.md Recommendation 2.

Inputs:
    --tier <1-5>           : Run only this tier's check (default: all)
    files                  : Optional paths (for tier 1: client-values.yml path)
    --repo-root <path>     : Repo root (default: cwd)
    --strict               : Exit 1 on any gap (default: advisory, exits 0)

Outputs:
    Prints per-tier status: PASS / WARN / FAIL
    Exit 0 if no FAIL; exit 1 if --strict and any WARN/FAIL; exit 1 if any FAIL

Usage:
    uv run python scripts/validate_cascade.py
    uv run python scripts/validate_cascade.py --tier 1 client-values.yml
    uv run python scripts/validate_cascade.py --strict
"""

import argparse
import re
import sys
from pathlib import Path


def check_tier1(repo_root: Path, files: list[str]) -> tuple[str, str]:
    """T1: Core Layer — MANIFESTO + AGENTS.md exist, or client-values.yml is valid."""
    if files:
        cvf = Path(files[0])
        if not cvf.exists():
            return "FAIL", f"client-values.yml not found: {cvf}"
        try:
            import yaml

            data = yaml.safe_load(cvf.read_text())
        except Exception as exc:
            return "FAIL", f"could not parse client-values.yml: {exc}"
        required = ["project_name", "domain", "mission"]
        missing = [k for k in required if k not in (data or {})]
        if missing:
            return "FAIL", f"client-values.yml missing keys: {', '.join(missing)}"
        empty = [k for k in required if not (data or {}).get(k)]
        if empty:
            return "WARN", f"client-values.yml has empty fields: {', '.join(empty)}"
        return "PASS", "client-values.yml has required fields"

    manifesto = repo_root / "MANIFESTO.md"
    agents = repo_root / "AGENTS.md"
    missing = [p.name for p in (manifesto, agents) if not p.exists()]
    if missing:
        return "FAIL", f"missing core files: {', '.join(missing)}"
    return "PASS", "MANIFESTO.md and AGENTS.md present"


def check_tier2(repo_root: Path) -> tuple[str, str]:
    """T2: Fleet Layer — AGENTS.md references MANIFESTO.md axioms."""
    agents_md = repo_root / "AGENTS.md"
    if not agents_md.exists():
        return "FAIL", "AGENTS.md not found"
    text = agents_md.read_text()
    pattern = re.compile(r"MANIFESTO\.md.{0,50}§|\[MANIFESTO\.md")
    count = len(pattern.findall(text))
    if count >= 3:
        return "PASS", f"{count} MANIFESTO axiom references in AGENTS.md"
    if count >= 1:
        return "WARN", f"only {count} MANIFESTO axiom reference(s) in AGENTS.md (need ≥3)"
    return "FAIL", "0 MANIFESTO axiom references in AGENTS.md"


def check_tier3(repo_root: Path) -> tuple[str, str]:
    """T3: Role Layer — .agent.md files have <constraints> tag."""
    agents_dir = repo_root / ".github" / "agents"
    if not agents_dir.exists():
        return "WARN", ".github/agents/ directory not found"
    agent_files = list(agents_dir.glob("*.agent.md"))
    if not agent_files:
        return "WARN", "no .agent.md files found"
    with_constraints = sum(1 for f in agent_files if "<constraints>" in f.read_text())
    ratio = with_constraints / len(agent_files)
    if ratio >= 0.5:
        return "PASS", f"{with_constraints}/{len(agent_files)} agent files have <constraints>"
    if ratio >= 0.25:
        return "WARN", f"only {with_constraints}/{len(agent_files)} agent files have <constraints> (need ≥50%)"
    return "FAIL", f"only {with_constraints}/{len(agent_files)} agent files have <constraints> (need ≥25%)"


def check_tier4(repo_root: Path) -> tuple[str, str]:
    """T4: Skill Layer — SKILL.md files reference MANIFESTO.md or AGENTS.md."""
    skills_dir = repo_root / ".github" / "skills"
    if not skills_dir.exists():
        return "WARN", ".github/skills/ directory not found"
    skill_files = list(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        return "WARN", "no SKILL.md files found"
    with_ref = sum(1 for f in skill_files if re.search(r"MANIFESTO\.md|AGENTS\.md", f.read_text()))
    ratio = with_ref / len(skill_files)
    if ratio >= 0.5:
        return "PASS", f"{with_ref}/{len(skill_files)} skills reference MANIFESTO.md or AGENTS.md"
    if ratio >= 0.25:
        return "WARN", f"only {with_ref}/{len(skill_files)} skills have governance reference (need ≥50%)"
    return "FAIL", f"only {with_ref}/{len(skill_files)} skills have governance reference (need ≥25%)"


def check_tier5() -> tuple[str, str]:
    """T5: Session Layer — runtime only."""
    return "PASS", "T5 (session behavior) can only be verified at runtime"


TIER_LABELS = {
    1: "Core Layer",
    2: "Fleet Layer",
    3: "Role Layer",
    4: "Skill Layer",
    5: "Session Layer",
}

TIER_CHECKS = {
    1: lambda root, files: check_tier1(root, files),
    2: lambda root, _files: check_tier2(root),
    3: lambda root, _files: check_tier3(root),
    4: lambda root, _files: check_tier4(root),
    5: lambda _root, _files: check_tier5(),
}


def run_checks(
    tiers: list[int],
    repo_root: Path,
    files: list[str],
    strict: bool,
) -> int:
    any_fail = False
    any_warn = False
    for tier in tiers:
        status, message = TIER_CHECKS[tier](repo_root, files)
        label = TIER_LABELS[tier]
        print(f"Tier {tier} ({label}): {status} — {message}")
        if status == "FAIL":
            any_fail = True
        elif status == "WARN":
            any_warn = True

    if any_fail:
        return 1
    if strict and any_warn:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate T1→T5 governance cascade encoding.")
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run only this tier's check (default: all)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional file paths (tier 1: client-values.yml)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repo root directory (default: cwd)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on any WARN or FAIL (default: only FAIL causes exit 1)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    tiers = [args.tier] if args.tier else [1, 2, 3, 4, 5]
    return run_checks(tiers, repo_root, args.files, args.strict)


if __name__ == "__main__":
    sys.exit(main())
