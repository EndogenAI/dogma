# MCP E2E Testing Runbook (Phase 2 Retrospective)

## Purpose

This runbook captures how to execute and interpret the Phase 1 MCP end-to-end integration suite in `tests/integration/test_mcp_e2e.py`.

For pipeline wiring, gates, and metric-threshold policy, use `docs/guides/mcp-quality-metrics.md`. This runbook intentionally does not redefine metric thresholds.

## Canonical Commands

Run the full MCP E2E matrix:

```bash
uv run pytest tests/integration/test_mcp_e2e.py -m integration -v
```

Run only filesystem-sensitive (`io`-marked) tests:

```bash
uv run pytest tests/integration/test_mcp_e2e.py -m io -v
```

Fail-fast triage — stop on first failure:

```bash
uv run pytest tests/integration/test_mcp_e2e.py -m integration -x --maxfail=1 -v
```

Re-run one specific case by pytest node id:

```bash
uv run pytest tests/integration/test_mcp_e2e.py::test_mcp_e2e_query_case_matrix[e2e_query_docs_precise_scope] -v
```

## Marker Usage

- `integration`: module-level marker (`pytestmark = pytest.mark.integration`) covering the E2E file.
- `io`: applied to tests that perform filesystem interactions or use path-sensitive behavior.

Practical usage:
- Use `-m integration` to run this suite directly.
- Keep `io` in mind when combining marker filters in broader test runs.

## Reading Pass/Fail Output and Case IDs

The parameterized matrix test prints one line per case in verbose mode (`-v`):

- Format: `test_mcp_e2e_query_case_matrix[<case_id>]`
- Example case id: `e2e_query_docs_precise_scope`

Interpretation:
- `PASSED`: tool output matched schema expectations (`ok`, `errors`, and tool-specific fields).
- `FAILED`: assertion mismatch in either common schema checks or tool-specific result fields.

Use the bracketed case id to isolate and re-run exactly one failing matrix case via node id.

## Canonical Tool-to-Case Matrix

Each canonical MCP tool has two variants in the matrix:

| Tool | Variant case IDs |
|---|---|
| `check_substrate` | `e2e_check_substrate_directive`, `e2e_check_substrate_contextual` |
| `validate_agent_file` | `e2e_validate_agent_file_precise`, `e2e_validate_agent_file_loose` |
| `validate_synthesis` | `e2e_validate_synthesis_strict`, `e2e_validate_synthesis_lenient` |
| `scaffold_agent` | `e2e_scaffold_agent_structured`, `e2e_scaffold_agent_ambiguous_request` |
| `scaffold_workplan` | `e2e_scaffold_workplan_issue_dense`, `e2e_scaffold_workplan_minimal` |
| `run_research_scout` | `e2e_run_research_scout_specific`, `e2e_run_research_scout_refresh` |
| `query_docs` | `e2e_query_docs_precise_scope`, `e2e_query_docs_broad_scope` |
| `prune_scratchpad` | `e2e_prune_scratchpad_init`, `e2e_prune_scratchpad_check_only` |

## Re-running a Single Case by Node ID

Workflow:

1. Copy the failing case id from verbose pytest output.
2. Build node id: `tests/integration/test_mcp_e2e.py::test_mcp_e2e_query_case_matrix[<case_id>]`.
3. Re-run with `-v`.

Template:

```bash
uv run pytest tests/integration/test_mcp_e2e.py::test_mcp_e2e_query_case_matrix[<case_id>] -v
```

## Troubleshooting

- Invalid path assertions:
  - Symptom: `validate_agent_file` or `validate_synthesis` returns `ok: false` with path errors.
  - Cause: test intentionally checks out-of-repo path rejection (`/tmp/outside-repo.md`).
  - Action: verify the failing path is repository-resident when expecting success.

- Invalid URL scheme edge case:
  - Symptom: `run_research_scout` fails and `cache_path` is `None`.
  - Cause: non-HTTPS URL (`http://...`) is rejected by design.
  - Action: use `https://` URLs for success-path runs.

- Monkeypatch determinism assumptions:
  - Symptom: non-deterministic output, unexpected subprocess behavior, or schema drift in mocked results.
  - Cause: deterministic mocks were bypassed or modified (validation/scaffolding/research/scratchpad stubs).
  - Action: confirm fixture `deterministic_tool_mocks` is active and monkeypatched helpers still return expected structures.

## Related Guide

For quality gate behavior, reporting workflow, and CI/pipeline integration details, see `docs/guides/mcp-quality-metrics.md`.