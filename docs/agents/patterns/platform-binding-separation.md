---
title: Platform Binding Separation Pattern
parent_directory: docs/agents/patterns
status: Active
---

# Platform Binding Separation Pattern

## Pattern

**Platform binding** = hard-coding assumptions about tools, versions, or execution environment into agent scripts or prompts.

Examples:
- Assuming Python 3.11 (not 3.13)
- Hard-coded path to `gh` CLI
- Assuming macOS, not Linux
- Assuming a specific pre-commit hook version

Platform-bound code is fragile — it breaks when the environment changes (new team member on Windows, Python upgraded, tool moved).

### Bad Example

```python
# ❌ Platform-bound (fragile)
PYTHON_VERSION = "3.11"
GH_PATH = "/usr/local/bin/gh"

if sys.version_info != (3, 11):
    raise RuntimeError("This script requires Python 3.11 exactly")

result = subprocess.run([GH_PATH, "issue", "list"])
```

### Good Example

```python
# ✅ Platform-agnostic (resilient)
# Store version assumptions in data/config.yml or pyproject.toml
# Always discover tools via which / shutil.which, not hard paths

python_version = sys.version_info[:2]  # (3, 13) is compatible
assert python_version >= (3, 11), f"Requires Python 3.11+, got {python_version}"

gh_path = shutil.which("gh")
if not gh_path:
    raise RuntimeError("gh CLI not found in PATH")

result = subprocess.run([gh_path, "issue", "list"])
```

## Application

For every agent script or workflow:

1. **Externalize version assumptions** to `pyproject.toml`, `data/config.yml`, or a `.version` file in the script directory
2. **Discover tools dynamically** via `shutil.which()` (Python) or `command -v` (shell)
3. **Document platform requirements** in a comment at the script top (e.g., "Requires gh ≥2.0; Python 3.11+")
4. **Test on multiple platforms** (CI should run on Linux + macOS if applicable)

See [`docs/toolchain/`](../../toolchain/) for tool-specific version assumptions and compatibility notes.
