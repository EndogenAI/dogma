---
title: "VS Code Problems Panel Diagnostics — Agent File Behaviour"
status: Final
closes_issue: 389
governs:
  - endogenous-first
  - documentation-first
---

# VS Code Problems Panel Diagnostics — Agent File Behaviour

## Executive Summary

The VS Code Problems panel surfaces three distinct error categories in this repository's `.agent.md` and `SKILL.md` files. This document synthesizes the root causes, VS Code's internal diagnostic architecture, and concrete fix recommendations for each category.

**Category A** (38 errors): `Attribute 'governs' is not supported` — Copilot Chat's `prompts-diagnostics-provider` uses a hardcoded internal schema for `.agent.md` frontmatter that does not include `governs:`. The `yaml.schemas` workspace setting does not affect this validator. No VS Code user setting suppresses a specific diagnostic provider. Accept as permanent non-blocking warnings; `governs:` remains valid governance metadata.

**Category B** (8 errors): `Unknown tool 'dogma-governance/*'` — MCP tool names listed in `.agent.md` frontmatter are validated statically at edit time against the set of currently registered tools. When the `dogma-governance` MCP server is not running, its tools are unrecognized. Runtime behavior silently ignores unavailable tools. Consolidating to the `dogma-governance/*` glob syntax may suppress these errors; if not, accept as non-blocking warnings.

**Category C** (281 errors — regression): Dead link errors caused by `/`-rooted paths (`/AGENTS.md`) that the `prompts-diagnostics-provider` resolves against the OS filesystem root (`/`) on macOS, not the workspace root. The fix is to revert to `../../`-relative paths from `.github/` and remove the `no-relative-traversal-in-agent-files` pre-commit hook that enforced the wrong convention.

---

## Hypothesis Validation

### H1: `yaml.schemas` controls Copilot Chat frontmatter validation

**Status: Refuted.**

The workspace `settings.json` maps `.vscode/agent-frontmatter.schema.json` to all `.agent.md` and `SKILL.md` files via `yaml.schemas`. That schema defines `governs:` as a valid property. Despite this, 38 `Attribute 'governs' is not supported` errors fire from `prompts-diagnostics-provider`. This provider is implemented inside the GitHub Copilot Chat extension and uses a hardcoded internal schema derived from the official VS Code custom-agents specification. It does not consult `yaml.schemas` from workspace or user settings. The `yaml.schemas` setting feeds the **redhat.vscode-yaml** extension's validator, which is a separate diagnostic collection.

### H2: `/`-rooted paths resolve to workspace root in `.agent.md` files

**Status: Refuted (confirmed root cause of Category C).**

A previous commit (`8cb59a7` + `c822565`) converted all `../../` relative links to `/`-rooted paths (e.g. `/AGENTS.md`, `/docs/guides/session-management.md`) on the assumption that VS Code resolves `/`-rooted links in Markdown relative to the workspace root. This hypothesis is incorrect: on macOS, `/`-rooted URI paths in Markdown link targets resolve to the OS filesystem root (`/`), not the workspace root. A link to `/AGENTS.md` is `file:///AGENTS.md` which does not exist. Stash `stash@{0}` on this branch contains the correct reversion to `../../`-relative paths for all 55 affected files.

### H3: The `no-relative-traversal-in-agent-files` pre-commit hook prevents the correct fix

**Status: Confirmed.**

The hook (id: `no-relative-traversal-in-agent-files`) was added to enforce `/`-rooted paths — simultaneously with the incorrect migration. Its `entry` pattern `'\]\(\.\./\.\.'` blocks any `../../`-style link in `.github/agents/` and `.github/skills/`. This hook must be removed (not merely disabled) before the stash can be popped cleanly.

### H4: MCP tool validation in `.agent.md` is runtime-only

**Status: Partially refuted.**

VS Code documentation states "If a given tool is not available when using the custom agent, it is ignored" — this applies at **runtime**, when Copilot Chat loads the agent. However, the `prompts-diagnostics-provider` also performs **static validation at edit time** against the set of currently registered tools (including those from active MCP servers). When the `dogma-governance` MCP server is offline, its 8 individually-named tools are unrecognized and generate errors. Using the `dogma-governance/*` glob syntax (documented as a valid way to include all tools of an MCP server) may bypass individual-name validation.

---

## Pattern Catalog

### Pattern 1 — Hardcoded Internal Schema vs. `yaml.schemas`

**Finding**: VS Code extensions that provide file-type-specific diagnostics (Copilot Chat's `prompts-diagnostics-provider`) use their own internal schema, completely independent of the `yaml.schemas` workspace setting. The `yaml.schemas` setting influences only the **redhat.vscode-yaml** extension's validator.

**Canonical example**: The `agent-frontmatter.schema.json` in this project defines `governs:` with full type and enum validation. Assigning it to `*.agent.md` via `yaml.schemas` suppresses YAML extension warnings but has zero effect on `prompts-diagnostics-provider` errors, which continue to fire for `governs:`.

**Anti-pattern**: Assuming that providing a custom JSON Schema via `yaml.schemas` will prevent all frontmatter-related diagnostics across all VS Code validators. Different validators maintain independent schema registries; workspace settings only configure the YAML extension, not the Copilot Chat extension's internal validator.

**Implication for suppression**: There is no documented VS Code user-facing setting to suppress diagnostics from a specific named provider (`prompts-diagnostics-provider`). Settings like `editor.problems.visibility`, and the non-existent `problems.exclude`, do not offer per-provider filtering. The only mechanism available to extension authors — the `DiagnosticCollection` API — is not user-configurable. Therefore, Category A errors must be accepted as permanent non-blocking noise.

---

### Pattern 2 — Static vs. Runtime Tool Availability

**Finding**: Tool names in `.agent.md` frontmatter undergo two separate validation passes:
1. **Static** (edit time): `prompts-diagnostics-provider` checks each tool name against currently registered tools. MCP tools are registered only while the MCP server process is running.
2. **Runtime** (session time): Copilot Chat silently ignores any tool that is unavailable when the agent is loaded.

**Canonical example**: `executive-orchestrator.agent.md` lists `dogma-governance/check_substrate` (and 7 other individual tool names) in its frontmatter. While the `dogma-governance` MCP server is running (via `uv run python -m mcp_server.dogma_server`), zero errors. When the server is stopped, 8 `Unknown tool` errors appear. Runtime behavior is unaffected.

**Anti-pattern**: Listing individual MCP tool names fully qualified (e.g. `dogma-governance/check_substrate`) when the `dogma-governance/*` glob syntax is supported and may resolve static validation errors more gracefully. VS Code documentation: "To include all tools of an MCP server, use the `<server name>/*` format."

---

### Pattern 3 — Link Path Resolution in `.github/` Subtree

**Finding**: Markdown link paths in files under `.github/agents/` and `.github/skills/` must use `../../`-relative paths to reach workspace root files. `/`-rooted paths resolve to the OS filesystem root on macOS, not the workspace root.

**Canonical example** (correct): `[AGENTS.md](../../AGENTS.md)` from `.github/agents/executive-orchestrator.agent.md` resolves to `<workspace>/AGENTS.md`. ✅

**Anti-pattern**: `[AGENTS.md](/AGENTS.md)` — the `/`-rooted form resolves to `/AGENTS.md` (i.e. `file:///AGENTS.md`) which does not exist on macOS, producing a dead-link diagnostic for every such reference. With 281 such links across 55 files, this was a significant regression. ❌

**Scope note**: The `../../` traversal restriction documented in AGENTS.md ("files inside `.github/agents/` and `.github/skills/` must use workspace-root-relative `/path` links — VS Code's `prompts-diagnostics-provider` cannot resolve `../../` traversal from those locations") is **incorrect**. The opposite is true: `prompts-diagnostics-provider` resolves `../../` correctly and fails on `/`-rooted paths.

---

## Recommendations

### RQ-A: `governs:` attribute errors — RENAME TO `x-governs:` (issue #390)

**Finding**: No VS Code user setting suppresses `prompts-diagnostics-provider` frontmatter validation. The `governs:` key is not in the official custom-agent schema and will never be recognized unless GitHub ships a schema update or adds `additionalProperties: true`.

**Recommendation**: Rename `governs:` to `x-governs:` in all `.agent.md` and `SKILL.md` frontmatter (tracked as issue #390). This eliminates all 40 Category A errors at the source. The previous recommendation to accept these as permanent non-blocking was wrong: it only asked whether VS Code settings could suppress the errors, not whether our own files could be changed to avoid them entirely. Update `scripts/validate_agent_files.py` to read `x-governs:` after the rename.

---

### RQ-B: MCP tool validation errors — CONSOLIDATE TO GLOB THEN ACCEPT

**Finding**: 8 `Unknown tool 'dogma-governance/*'` errors fire when the MCP server is not running. VS Code documents `<server name>/*` as a valid tool reference syntax.

**Recommendation (Phase 2 implementation)**:
1. In `executive-orchestrator.agent.md`, replace the 8 individually-named `dogma-governance/<tool>` entries with the single glob `dogma-governance/*`.
2. Observe whether static validation clears the errors when the server is offline.
3. If the glob syntax passes static validation → 8 errors resolved permanently.
4. If the glob syntax still errors → accept as non-blocking warnings and document: "MCP tool validation errors appear when `dogma-governance` server is offline; start with `uv run python -m mcp_server.dogma_server` to suppress."

The glob syntax change is a net improvement regardless: it reduces frontmatter verbosity and is more maintainable as the MCP server's tool set evolves.

---

### RQ-C: Diagnostics suppression — NO MECHANISM EXISTS

**Finding**: `problems.exclude` does not exist as a VS Code setting. No documented user-facing setting allows per-provider diagnostic suppression for `prompts-diagnostics-provider`. `markdown.validate.enabled: false` (already set) disables the built-in Markdown validator but does not affect Copilot Chat's validator. `editor.problems.visibility` is not a real VS Code setting.

**Recommendation**: Do not attempt further settings-based suppression. The only durable remediation paths are:
- Fix the root cause of each error category (recommendations for RQ-A, RQ-B, RQ-D)
- Rename `governs:` → `x-governs:` in all agent/skill frontmatter to eliminate Category A errors at the source (issue #390)

---

### RQ-D: Path resolution regression — REVERT STASH + REMOVE HOOK (PHASE 2 PRIORITY)

**Finding**: `/`-rooted paths from `.github/` resolve to OS filesystem root on macOS, causing 281 dead-link errors. The correct form is `../../`-relative paths. The `no-relative-traversal-in-agent-files` pre-commit hook currently blocks the fix.

**Recommendation (Phase 2 implementation — highest priority)**:
1. Remove the `no-relative-traversal-in-agent-files` hook from `.pre-commit-config.yaml`.
2. Pop `stash@{0}` which already contains the correct reversion across all 55 files.
3. Update the AGENTS.md documentation block that says "files inside `.github/agents/` and `.github/skills/` must use workspace-root-relative `/path` links" — correct it to "files inside `.github/agents/` and `.github/skills/` must use `../../`-relative paths for cross-directory links."
4. Update any other guides, agent files, or skill files that repeat the incorrect `/`-path convention.
5. This resolves ~281 link errors (Category C) completely.

**Verification**: After popping stash, run `uv run python scripts/validate_agent_files.py --all` and confirm zero link errors for the reverted files.

---

## Sources

- [VS Code Custom Agents documentation](https://code.visualstudio.com/docs/copilot/customization/custom-agents) — official frontmatter schema; tool availability runtime semantics. Cached: `.cache/sources/code-visualstudio-com-docs-copilot-customization-custom-agen.md` (2026-03-07).
- [VS Code Extension API — `languages` namespace](https://code.visualstudio.com/api/references/vscode-api#LanguageModelChat) — `DiagnosticCollection` API; per-provider diagnostic architecture. Cached: `.cache/sources/code-visualstudio-com-api-references-vscode-api-LanguageMode.md` (2026-03-07).
- [VS Code Agent Skills documentation](https://code.visualstudio.com/docs/copilot/customization/agent-skills) — Agent file frontmatter schema cross-reference. Cached: `.cache/sources/code-visualstudio-com-docs-copilot-customization-agent-skill.md` (2026-03-08).
- Repository artifact — `.vscode/agent-frontmatter.schema.json` — custom JSON Schema defining `governs:` property. Endogenous source.
- Repository artifact — `.pre-commit-config.yaml` — `no-relative-traversal-in-agent-files` hook definition. Endogenous source.
- Repository artifact — `stash@{0}` on branch `triage/problems-panel-cleanup` — diff showing `/`-rooted → `../../`-relative reversion across 55 files. Endogenous source.
- Git commits `8cb59a7` + `c822565` on branch `triage/problems-panel-cleanup` — original `/`-rooted path migration; source of Category C regression. Endogenous source.
- Issue #389 body and comments — root-cause analysis of all three error categories; stash manifest. Endogenous source (AccessiT3ch).
