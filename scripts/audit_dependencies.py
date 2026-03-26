#!/usr/bin/env python3
"""
Quarterly dependency audit script with CVE checking.

**Purpose**: Audit uv.lock dependencies for known CVE vulnerabilities. Reads dependency
names and versions from the lockfile, cross-checks against a local CVE database
(.cache/cve-db.json if present), and reports High+ severity vulnerabilities.

**Inputs**:
- uv.lock (default: ./uv.lock)
- .cache/cve-db.json (optional — if absent, logs "No CVE DB" and exits 0)

**Outputs**:
- Stdout: List of vulnerable packages with CVE IDs and severity
- Exit code 0: No High+ CVEs found (or no CVE DB)
- Exit code 1: High+ severity vulnerabilities detected

**Usage**:
    # Run audit on default uv.lock
    uv run python scripts/audit_dependencies.py

    # Specify custom lockfile path
    uv run python scripts/audit_dependencies.py --lock-file /path/to/uv.lock

    # Dry-run mode (parse lockfile, skip CVE check)
    uv run python scripts/audit_dependencies.py --dry-run

**Exit codes**:
    0: No High+ CVEs detected (or no CVE DB available)
    1: High+ severity CVEs found
    2: I/O error (lockfile not found, invalid JSON)

**CI integration**: Runs quarterly via .github/workflows/quarterly-dependency-audit.yml
(cron: 0 0 1 */3 * — 1st of each quarter).

**Related**:
- scripts/subscribe_cve_feeds.py — Future automation for CVE DB population
- Issue #361 — LLM05 Supply Chain Vulnerability mitigation
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_uv_lock(lock_path: Path) -> list[dict[str, str]]:
    """
    Parse uv.lock and extract dependency names and versions.

    Args:
        lock_path: Path to uv.lock file

    Returns:
        List of dicts: [{"name": "package-name", "version": "1.2.3"}, ...]

    Note:
        This is a simplified parser. uv.lock uses TOML format with a [[package]]
        array. Each package has a `name` and `version` field.
    """
    dependencies = []

    try:
        content = lock_path.read_text()
    except FileNotFoundError:
        print(f"Error: Lockfile not found at {lock_path}", file=sys.stderr)
        sys.exit(2)

    # Simple TOML parsing for [[package]] sections
    # Format: [[package]]\nname = "foo"\nversion = "1.2.3"
    current_package: dict[str, str] = {}

    for line in content.splitlines():
        line = line.strip()

        if line == "[[package]]":
            if current_package:
                dependencies.append(current_package)
            current_package = {}
        elif line.startswith("name = "):
            name = line.split("=", 1)[1].strip().strip('"')
            current_package["name"] = name
        elif line.startswith("version = "):
            version = line.split("=", 1)[1].strip().strip('"')
            current_package["version"] = version

    # Append last package
    if current_package:
        dependencies.append(current_package)

    return dependencies


def load_cve_database(db_path: Path) -> dict[str, list[dict[str, Any]]]:
    """
    Load CVE database from .cache/cve-db.json.

    Expected format:
    {
        "package-name": [
            {
                "cve_id": "CVE-2024-1234",
                "severity": "HIGH",
                "cvss_score": 8.5,
                "affected_versions": ["1.0.0", "1.1.0"],
                "description": "..."
            }
        ]
    }

    Args:
        db_path: Path to CVE database JSON file

    Returns:
        Dict mapping package names to lists of CVE records
    """
    if not db_path.exists():
        return {}

    try:
        with db_path.open() as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {db_path}: {e}", file=sys.stderr)
        sys.exit(2)


def check_vulnerabilities(
    dependencies: list[dict[str, str]],
    cve_db: dict[str, list[dict[str, Any]]],
) -> tuple[int, list[str]]:
    """
    Cross-check dependencies against CVE database.

    Args:
        dependencies: List of {name, version} dicts from uv.lock
        cve_db: CVE database mapping package names to CVE records

    Returns:
        Tuple: (count_high_severity, list_of_vulnerable_packages)

        Where list_of_vulnerable_packages contains strings like:
        "package-name==1.2.3 (CVE-2024-1234: HIGH, CVSS 8.5)"
    """
    high_severity_count = 0
    vulnerable_packages = []

    for dep in dependencies:
        name = dep.get("name", "")
        version = dep.get("version", "")

        if name not in cve_db:
            continue

        for cve in cve_db[name]:
            # Check if version is affected
            affected_versions = cve.get("affected_versions", [])
            if version not in affected_versions:
                continue

            severity = cve.get("severity", "UNKNOWN").upper()
            cvss_score = cve.get("cvss_score", 0.0)

            # Count High+ severity (CVSS >= 7.0 or severity = HIGH/CRITICAL)
            if cvss_score >= 7.0 or severity in {"HIGH", "CRITICAL"}:
                high_severity_count += 1
                cve_id = cve.get("cve_id", "UNKNOWN")
                vulnerable_packages.append(f"{name}=={version} ({cve_id}: {severity}, CVSS {cvss_score})")

    return high_severity_count, vulnerable_packages


def audit_lock_file(lock_path: Path, cve_db_path: Path) -> tuple[int, list[str]]:
    """
    Main audit function: parse lockfile, load CVE DB, cross-check.

    Args:
        lock_path: Path to uv.lock
        cve_db_path: Path to .cache/cve-db.json

    Returns:
        Tuple: (count_high_severity, list_of_vulnerable_packages)
    """
    dependencies = parse_uv_lock(lock_path)
    print(f"Parsed {len(dependencies)} dependencies from {lock_path}")

    cve_db = load_cve_database(cve_db_path)
    if not cve_db:
        print(f"No CVE database found at {cve_db_path} — skipping vulnerability check")
        return 0, []

    print(f"Loaded CVE database with {len(cve_db)} package entries")

    return check_vulnerabilities(dependencies, cve_db)


def main() -> int:
    """Entry point for dependency audit script."""
    parser = argparse.ArgumentParser(
        description="Audit uv.lock dependencies for CVE vulnerabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--lock-file",
        type=Path,
        default=Path("uv.lock"),
        help="Path to uv.lock file (default: ./uv.lock)",
    )
    parser.add_argument(
        "--cve-db",
        type=Path,
        default=Path(".cache/cve-db.json"),
        help="Path to CVE database JSON (default: .cache/cve-db.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse lockfile only, skip CVE check",
    )

    args = parser.parse_args()

    if args.dry_run:
        dependencies = parse_uv_lock(args.lock_file)
        print(f"[DRY RUN] Would audit {len(dependencies)} dependencies")
        for dep in dependencies[:5]:  # Show first 5
            name = dep.get("name", "<missing-name>")
            version = dep.get("version", "<missing-version>")
            print(f"  - {name}=={version}")
        if len(dependencies) > 5:
            print(f"  ... and {len(dependencies) - 5} more")
        return 0

    count_high, vulnerable = audit_lock_file(args.lock_file, args.cve_db)

    if count_high == 0:
        print("\n✓ No High+ severity CVEs detected")
        return 0

    print(f"\n✗ Found {count_high} High+ severity CVE(s):\n")
    for vuln in vulnerable:
        print(f"  - {vuln}")

    print("\nAction required: Review and update affected dependencies")
    return 1


if __name__ == "__main__":
    sys.exit(main())
