"""scripts/validate_agent_files.py

Programmatic encoding-fidelity gate for agent files — equivalent to
validate_synthesis.py but for `.agent.md` files in `.github/agents/`.

Purpose:
    Enforce a minimum structural bar on agent files to prevent encoding drift
    in the MANIFESTO → AGENTS.md → agent files → session prompts chain.

Checks:
    1. Valid YAML frontmatter with required fields: ``name``, ``description``.
    2. Required section headings present (fuzzy keyword matching):
       - Endogenous Sources section (confirms the agent reads before acting)
       - Action section (Workflow, Checklist, Conventions, or equivalent)
       - Quality-gate section (Completion Criteria or Guardrails)
    3. At least one back-reference to MANIFESTO.md or AGENTS.md (cross-reference
       density ≥ 1).  Low density signals likely encoding drift.
    4. No heredoc-based file writes (``cat >> ... << 'EOF'`` patterns), which
       silently corrupt Markdown content containing backticks.
    5. No ``Fetch-before-check`` guardrail label (correct label is
       ``Check-before-fetch`` — check cache first, then fetch only if absent).
    6. No ``## Phase N Review Output`` heading (use ``## Review Output``
       as defined in ``review.agent.md``).

Inputs:
    [file ...]    One or more .agent.md files to validate.  (positional, optional)
    --all         Scan every *.agent.md in .github/agents/ AND every SKILL.md
                  in .github/skills/*/SKILL.md.
    --skills      Scan every SKILL.md in .github/skills/*/SKILL.md.
    --strict      Reserved for future use — currently a no-op flag.

Outputs:
    stdout:  Human-readable pass/fail summary with specific gap list per file.
    stderr:  Nothing (all output goes to stdout for easy capture).

Exit codes:
    0  All checks passed.
    1  One or more checks failed — specific gap(s) reported to stdout.

Usage examples:
    # Validate a single agent file
    uv run python scripts/validate_agent_files.py .github/agents/executive-orchestrator.agent.md

    # Validate all agent files in .github/agents/
    uv run python scripts/validate_agent_files.py --all

    # Validate all SKILL.md files in .github/skills/
    uv run python scripts/validate_agent_files.py --skills

    # Integrate into CI (non-zero exit blocks the job)
    for f in .github/agents/*.agent.md; do
        uv run python scripts/validate_agent_files.py "$f"
    done
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AGENTS_DIR = Path(".github/agents")
SKILLS_DIR = Path(".github/skills")

# --- Skill-specific validation constants ---
_SKILL_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")
_CONSECUTIVE_HYPHENS_RE = re.compile(r"--")
SKILL_NAME_MAX_LEN = 64
SKILL_DESCRIPTION_MIN_LEN = 10
SKILL_DESCRIPTION_MAX_LEN = 1024
SKILL_BODY_MIN_LEN = 100

# YAML frontmatter fields that must be present and non-empty in every agent file.
REQUIRED_FRONTMATTER: list[str] = ["name", "description"]

# Required section categories.  Each entry is (human label, [keywords]).
# A section passes if any heading contains any of its keywords (case-insensitive).
REQUIRED_SECTIONS: list[tuple[str, list[str]]] = [
    ("Endogenous Sources", ["endogenous", "read before acting"]),
    (
        "Action section (Workflow/Checklist/Conventions/Scope/Methodology)",
        ["workflow", "checklist", "conventions", "playbook", "scope", "methodology"],
    ),
    ("Quality-gate section (Completion Criteria or Guardrails)", ["completion criteria", "guardrails"]),
]

# Negation words that indicate a heredoc pattern is being *prohibited*, not instructed.
_HEREDOC_NEGATIONS = frozenset(["never", "avoid", "don't", "dont", "do not", "wrong", "prohibited", "not use"])

# Regex matching the core heredoc cat-append pattern.
_HEREDOC_PATTERN = re.compile(r"cat\s*>>?\s*\S+\s*<<\s*['\"]?EOF", re.IGNORECASE)

# Pattern for MANIFESTO.md or AGENTS.md cross-references.
_CROSSREF_RE = re.compile(r"MANIFESTO\.md|AGENTS\.md")

# Frontmatter block pattern.
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# Pattern for the incorrect 'Fetch-before-check' label ordering.
_FETCH_BEFORE_CHECK_PATTERN = re.compile(r"fetch-before-check", re.IGNORECASE)

# Pattern for the incorrect '## Phase N Review Output' heading.
_PHASE_N_REVIEW_RE = re.compile(r"##\s+Phase\s+N\s+Review\s+Output", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict[str, str]:
    """Return a flat dict of YAML frontmatter key → raw string value."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fm: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            v = val.strip()
            if len(v) >= 2 and v[0] in ('"', "'") and v[0] == v[-1]:
                v = v[1:-1]
            fm[key.strip()] = v
    return fm


def extract_headings(text: str) -> list[str]:
    """Return all Markdown H2 headings (## ...) from the document body."""
    body_start = 0
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match:
        body_start = fm_match.end()
    body = text[body_start:]
    return [line.rstrip() for line in body.splitlines() if line.startswith("## ")]


def _extract_body(text: str) -> str:
    """Return the document body after the frontmatter block."""
    fm_match = _FRONTMATTER_RE.match(text)
    return text[fm_match.end() :] if fm_match else text


def _get_frontmatter_value(text: str, key: str) -> str:
    """Return the full string value of *key* from YAML frontmatter.

    Handles both inline scalars and block scalars (the ``|`` indicator).
    An inline value is returned as-is; a block scalar's lines are joined
    with a single space after stripping per-line whitespace.
    """
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return ""
    lines = fm_match.group(1).splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith(f"{key}:"):
            continue
        after_colon = stripped[len(key) + 1 :].strip()
        if after_colon and after_colon not in ("|", "|-", "|+"):
            # Strip surrounding single/double quotes from inline scalars
            if len(after_colon) >= 2 and after_colon[0] in ('"', "'") and after_colon[0] == after_colon[-1]:
                return after_colon[1:-1]
            return after_colon  # inline scalar
        if after_colon in ("|", "|-", "|+"):
            # Collect indented block-scalar continuation lines
            block: list[str] = []
            for nxt in lines[i + 1 :]:
                if nxt and not nxt[0].isspace():
                    break
                block.append(nxt.strip())
            return " ".join(filter(None, block)).strip()
    return ""


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------


def validate(file_path: Path) -> tuple[bool, list[str]]:
    """Validate *file_path*. Returns (passed, list_of_failure_messages)."""
    failures: list[str] = []

    # --- Check 0: file exists ---
    if not file_path.exists():
        return False, [f"File not found: {file_path}"]
    if not file_path.is_file():
        return False, [f"Path is not a file: {file_path}"]

    text = file_path.read_text(encoding="utf-8")

    # --- Check 1: YAML frontmatter ---
    fm = parse_frontmatter(text)
    if not fm:
        failures.append("No YAML frontmatter found (expected --- block at top of file)")
    else:
        for key in REQUIRED_FRONTMATTER:
            if not fm.get(key):
                failures.append(f"Missing or empty frontmatter field: '{key}'")

    # --- Check 2: required sections ---
    headings_lower = [h.lower() for h in extract_headings(text)]
    for section_label, keywords in REQUIRED_SECTIONS:
        matched = any(kw in h for kw in keywords for h in headings_lower)
        if not matched:
            failures.append(
                f"Missing required section '{section_label}' (expected a heading matching one of: {keywords})"
            )

    # --- Check 3: cross-reference density ---
    if not _CROSSREF_RE.search(text):
        failures.append(
            "Cross-reference density too low: no back-reference to MANIFESTO.md or AGENTS.md found "
            "(add at least one link to maintain encoding fidelity)"
        )

    # --- Check 4: no heredoc file writes (negation-aware) ---
    # A line is only flagged if the cat >> pattern appears WITHOUT a clear
    # negation marker on the same line (e.g. guardrail warnings are not flagged).
    for line in text.splitlines():
        if _HEREDOC_PATTERN.search(line):
            lower = line.lower()
            if not any(neg in lower for neg in _HEREDOC_NEGATIONS):
                failures.append(
                    "Heredoc file write detected (cat >> ... << 'EOF' pattern) outside a negation context — "
                    "use create_file / replace_string_in_file built-in tools instead "
                    "(heredocs silently corrupt Markdown containing backticks)"
                )
                break

    # --- Check 5: no Fetch-before-check label (negation-aware) ---
    for line in text.splitlines():
        if _FETCH_BEFORE_CHECK_PATTERN.search(line):
            lower = line.lower()
            if not any(neg in lower for neg in _HEREDOC_NEGATIONS):
                failures.append(
                    "Guardrail label ordering error: 'Fetch-before-check' found — correct label is "
                    "'Check-before-fetch' (check cache first, then fetch only if absent)"
                )
                break

    # --- Check 6: no '## Phase N Review Output' heading ---
    if _PHASE_N_REVIEW_RE.search(text):
        failures.append(
            "Heading contract violation: '## Phase N Review Output' found — use '## Review Output' "
            "(defined in review.agent.md; do not restate with 'Phase N' prefix)"
        )

    passed = len(failures) == 0
    return passed, failures


def validate_skill_file(path: Path) -> list[str]:
    """Validate a SKILL.md file for encoding fidelity.

    Returns a list of error strings; an empty list means all checks passed.
    Checks applied:
      1. YAML frontmatter present.
      2. Required fields: ``name`` and ``description``.
      3. Name format: ``^[a-z][a-z0-9-]*[a-z0-9]$``, max 64 chars, no ``--``.
      4. Name matches parent directory name.
      5. Description length: ≥10 and ≤1024 chars.
      6. Cross-reference density: body contains ≥1 ref to AGENTS.md or MANIFESTO.md.
      7. Minimum body length: ≥100 chars (after frontmatter).
    """
    errors: list[str] = []

    if not path.exists():
        return [f"File not found: {path}"]
    if not path.is_file():
        return [f"Path is not a file: {path}"]

    text = path.read_text(encoding="utf-8")

    # Check 1: frontmatter present
    fm = parse_frontmatter(text)
    if not fm:
        errors.append("No YAML frontmatter found (expected --- block at top of file)")
        return errors  # remaining checks require frontmatter

    # Check 2: required fields
    name_val = _get_frontmatter_value(text, "name")
    desc_val = _get_frontmatter_value(text, "description")

    if not name_val:
        errors.append("Missing or empty frontmatter field: 'name'")
    if not desc_val:
        errors.append("Missing or empty frontmatter field: 'description'")

    # Check 3: name format (only if name is present)
    if name_val:
        if len(name_val) > SKILL_NAME_MAX_LEN:
            errors.append(f"Frontmatter 'name' exceeds {SKILL_NAME_MAX_LEN} characters (got {len(name_val)})")
        if not _SKILL_NAME_RE.match(name_val):
            errors.append(
                f"Frontmatter 'name' must match ^[a-z][a-z0-9-]*[a-z0-9]$ "
                f"(lowercase kebab-case, no leading/trailing hyphens): {name_val!r}"
            )
        elif _CONSECUTIVE_HYPHENS_RE.search(name_val):
            errors.append(f"Frontmatter 'name' must not contain consecutive hyphens: {name_val!r}")

        # Check 4: name matches parent directory
        parent_dir = path.parent.name
        if name_val != parent_dir:
            errors.append(f"Frontmatter 'name' ({name_val!r}) must match the parent directory name ({parent_dir!r})")

    # Check 5: description length
    if desc_val:
        desc_len = len(desc_val)
        if desc_len < SKILL_DESCRIPTION_MIN_LEN:
            errors.append(
                f"Frontmatter 'description' is too short ({desc_len} chars, minimum {SKILL_DESCRIPTION_MIN_LEN})"
            )
        if desc_len > SKILL_DESCRIPTION_MAX_LEN:
            errors.append(
                f"Frontmatter 'description' is too long ({desc_len} chars, maximum {SKILL_DESCRIPTION_MAX_LEN})"
            )

    # Check 6: cross-reference density (body only)
    body = _extract_body(text)
    if not _CROSSREF_RE.search(body):
        errors.append(
            "Cross-reference density too low: no back-reference to MANIFESTO.md or AGENTS.md "
            "found in body (add at least one link to maintain encoding fidelity)"
        )

    # Check 7: minimum body length
    body_stripped = body.strip()
    if len(body_stripped) < SKILL_BODY_MIN_LEN:
        errors.append(f"Body is too short ({len(body_stripped)} chars after frontmatter, minimum {SKILL_BODY_MIN_LEN})")

    # Check 8: no '## Phase N Review Output' heading
    if _PHASE_N_REVIEW_RE.search(text):
        errors.append(
            "Heading contract violation: '## Phase N Review Output' found — use '## Review Output' "
            "(defined in review.agent.md; do not restate with 'Phase N' prefix)"
        )

    return errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate agent and skill files for encoding fidelity.",
        epilog="Exit 0 = all pass. Exit 1 = one or more checks failed.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="file",
        help="One or more .agent.md or SKILL.md files to validate.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="scan_all",
        help=(f"Scan every *.agent.md in {AGENTS_DIR}/ AND every SKILL.md in {SKILLS_DIR}/*/SKILL.md."),
    )
    parser.add_argument(
        "--skills",
        action="store_true",
        dest="scan_skills",
        help=f"Scan every SKILL.md in {SKILLS_DIR}/*/SKILL.md.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future use.",
    )
    args = parser.parse_args()

    agent_targets: list[Path] = []
    skill_targets: list[Path] = []

    if args.scan_all:
        agent_targets = sorted(AGENTS_DIR.glob("*.agent.md"))
        skill_targets = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    elif args.scan_skills:
        skill_targets = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    elif args.files:
        for f in args.files:
            p = Path(f)
            if p.name == "SKILL.md":
                skill_targets.append(p)
            else:
                agent_targets.append(p)
    else:
        parser.print_help()
        sys.exit(0)

    total = len(agent_targets) + len(skill_targets)
    if total == 0:
        print("No files found — nothing to validate.")
        sys.exit(0)

    overall_pass = True
    failed_count = 0

    for file_path in agent_targets:
        passed, failures = validate(file_path)
        if passed:
            print(f"PASS  {file_path}")
        else:
            overall_pass = False
            failed_count += 1
            print(f"FAIL  {file_path}")
            for msg in failures:
                print(f"      • {msg}")

    for file_path in skill_targets:
        errors = validate_skill_file(file_path)
        if not errors:
            print(f"PASS  {file_path}")
        else:
            overall_pass = False
            failed_count += 1
            print(f"FAIL  {file_path}")
            for msg in errors:
                print(f"      • {msg}")

    print()
    if overall_pass:
        print(f"All {total} file(s) passed.")
    else:
        print(f"{failed_count} of {total} file(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
