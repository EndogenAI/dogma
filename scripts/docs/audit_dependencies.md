# `audit\_dependencies`

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

## Usage

```bash
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
```

<!-- hash:21e71aedc57e8c9c -->
