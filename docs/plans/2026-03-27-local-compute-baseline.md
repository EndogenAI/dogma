---
title: "Local Compute Baseline Establishment"
branch: feat/establish-local-compute-baseline
unblocks_issues: [131]
date: 2026-03-27
status: Active
---

# Workplan: Local Compute Baseline Establishment

## Objective

Establish and verify a working local-compute baseline on the
`feat/establish-local-compute-baseline` branch. The four phases: correct provider model
names in `data/inference-providers.yml` to match pulled Ollama models; verify end-to-end
routing against the live stack; add integration tests for the Ollama provider; and build a
session cost-log harness for token-burn tracking (unblocks issue #131 — H1 token-burn
hypothesis). Each domain phase is gated by Review before execution continues.

---

## Dependency Map

- **Phase 1 → Phase 2**: routing verification cannot succeed until
  `inference-providers.yml` model names match pulled Ollama models.
- **Phase 2 → Phase 3**: integration tests assert live Ollama behaviour; a confirmed
  E2E pass is the precondition for writing tests expected to pass against the live stack.
- **Phase 3 APPROVED → Phase 4**: session cost log is independent of integration tests
  but must not ship to the same PR until Phase 3 is APPROVED.
- **Phase 4 APPROVED → Phase 5**: GitHub agent opens the PR only after all domain phases
  carry a Review APPROVED verdict.

---

## Phases

### Phase 1 — Fix Provider Model Names

**Agent**: Executive Scripter
**Effort**: ~30 min
**Description**: Edit `data/inference-providers.yml` to replace stale model-name entries
with the exact strings used by the pulled Ollama models. Add `phi3:mini`, `qwen2.5:3b`,
`tinyllama:latest`; remove `llama3.2`, `mistral`, and `phi3` (exact-string mismatch
against live stack).

**Tasks**:
1. Open `data/inference-providers.yml` and locate the `local-ollama` provider block.
2. Replace the three stale model IDs (`llama3.2`, `mistral`, `phi3`) with the three
   correct IDs (`phi3:mini`, `qwen2.5:3b`, `tinyllama:latest`).
3. Confirm no other file in `data/` or `mcp_server/` references the removed model IDs
   in a way that would cause a runtime failure.
4. Spot-check: `uv run python -c "from mcp_server.tools.inference import route_inference_request; import json; print(json.dumps(route_inference_request('hello', 'phi3:mini')))"` — confirm `"ok": true` and `"local": true` in the response.

**Deliverables**:
- D1: `data/inference-providers.yml` updated — `phi3:mini`, `qwen2.5:3b`,
  `tinyllama:latest` present under `local-ollama` `model_ids`; `llama3.2`, `mistral`,
  `phi3` removed.
- D2: Spot-check result (`"ok": true`, `"local": true`) recorded in scratchpad.

**Depends on**: nothing
**Gate**: Phase 1 Review gate must return APPROVED before Phase 2 begins.
**Status**: ⬜ Not started

---

### Phase 1 Review Gate

**Agent**: Review
**Description**: Validate that the `data/inference-providers.yml` edit is correct and
all acceptance criteria are fully met.

**Acceptance Criteria**:
1. `data/inference-providers.yml` contains `phi3:mini`, `qwen2.5:3b`, `tinyllama:latest`
   under the `local-ollama` `model_ids` list.
2. `data/inference-providers.yml` does NOT contain `llama3.2`, `mistral`, or `phi3`
   (bare, without tag suffix) under any provider.
3. No file in `data/` or `mcp_server/` references the removed model IDs in a breaking way.
4. Scratchpad records D2 spot-check showing `"ok": true` and `"local": true`.

**Return**: `APPROVED` or `REQUEST CHANGES — [criterion number: one-line reason]`
**Gate**: Phase 2 does not begin until verdict is `APPROVED`.
**Status**: ⬜ Not started

---

### Phase 2 — End-to-End Routing Verification

**Agent**: Executive Orchestrator (direct — no delegation)
**Effort**: ~1 hr
**Description**: Verification-only step. No new code or files produced. Run
`health_check_services.py` and a direct `route_inference_request` call against the live
Ollama stack to confirm the Phase 1 fix produces a passing end-to-end baseline.

**Tasks**:
1. Run: `uv run python scripts/health_check_services.py --provider-type local`
   — confirm exit 0 and Ollama provider appears in the healthy list.
2. Run: `uv run python -c "from mcp_server.tools.inference import route_inference_request; import json; print(json.dumps(route_inference_request('hello', 'phi3:mini')))"`
   — confirm `"ok": true` and `"local": true` in the response.
3. Record both command outputs verbatim in the scratchpad under
   `## Phase 2 Verification Output`.

**Deliverables**:
- D1: Scratchpad section `## Phase 2 Verification Output` contains verbatim output of
  both commands.
- D2: Both commands returned a healthy/ok status (confirmed in scratchpad).

**Depends on**: Phase 1 Review APPROVED
**Gate**: Phase 3 does not begin until D1 and D2 are recorded in the scratchpad. No
Review gate — verification-only; no new files produced.
**Status**: ⬜ Not started

---

### Phase 3 — Integration Tests for Live Ollama Stack

**Agent**: Executive Scripter
**Effort**: ~2 hrs
**Description**: Add 3–5 integration tests to `tests/test_inference_integration.py` that
verify the live Ollama stack. All tests must be `@pytest.mark.integration` and skip
gracefully when Ollama is not reachable.

**Tasks**:
1. Create `tests/test_inference_integration.py`.
2. Add a module-level skip guard that probes `http://localhost:11434/` and skips all
   tests if Ollama is unreachable (not failed).
3. Implement the following test cases:
   - **(a) Health check**: `health_check_services.py --provider-type local` exits 0 and
     Ollama appears in the healthy list.
   - **(b) Route and respond**: `route_inference_request(prompt="hello", model_id="phi3:mini")` returns `"ok": true` and a non-empty `"response"` field.
   - **(c) Provider preference**: when both local and cloud providers are configured,
     routing returns `"local": true` for a model available locally.
4. Confirm every test function is decorated `@pytest.mark.integration`.
5. Run `uv run pytest tests/test_inference_integration.py -m integration -v` with live
   Ollama — confirm all pass.
6. Run without Ollama reachable — confirm all tests are skipped (not errored).

**Deliverables**:
- D1: `tests/test_inference_integration.py` present with ≥3 test cases covering (a),
  (b), (c).
- D2: All tests pass with live Ollama (exit 0).
- D3: All tests skip (not fail) without Ollama reachable.
- D4: Every test function decorated `@pytest.mark.integration`.

**Depends on**: Phase 2 D1 and D2 confirmed in scratchpad
**Gate**: Phase 3 Review gate must return APPROVED before Phase 4 begins.
**Status**: ✅ Complete

---

### Phase 3 Review Gate

**Agent**: Review
**Description**: Validate integration tests against all acceptance criteria before Phase 4
begins.

**Acceptance Criteria**:
1. `tests/test_inference_integration.py` exists and contains ≥3 test functions.
2. Every test function is decorated with `@pytest.mark.integration`.
3. A skip guard is present that probes `http://localhost:11434/` and skips (not errors)
   if Ollama is unreachable.
4. Test cases cover all three specified behaviours: health-check exit 0,
   route-and-respond with non-empty `response` field, and provider-preference returns
   `"local": true`.
5. `integration` marker is registered in `pyproject.toml` markers list (repo runs
   `--strict-markers`).
6. No unexpected external dependencies introduced beyond `mcp_server.tools.inference`
   and `scripts.health_check_services`.

**Return**: `APPROVED` or `REQUEST CHANGES — [criterion number: one-line reason]`
**Gate**: Phase 4 does not begin until verdict is `APPROVED`.
**Status**: ✅ Complete — APPROVED

---

### Phase 4 — Session Cost Log Harness

**Agent**: Executive Scripter
**Effort**: ~4–6 hrs
**Description**: Build `scripts/session_cost_log.py` that records per-session token-burn
metrics to `session_cost_log.json`. This is the measurement substrate that unblocks
issue #131 (H1 token-burn hypothesis). Must ship with a full test file
`tests/test_session_cost_log.py` covering ≥80% of the script.

**Tasks**:
1. Author `scripts/session_cost_log.py` with:
   - Opening docstring: purpose, inputs, outputs, and usage example.
   - `log_session_cost(session_id, model, tokens_in, tokens_out, phase, timestamp)` —
     appends one record to `session_cost_log.json`.
   - `read_log()` — returns the full list of records from `session_cost_log.json`.
   - JSON schema: each record must have exactly `session_id`, `model`, `tokens_in`,
     `tokens_out`, `phase`, `timestamp`.
   - `--dry-run` CLI flag: prints the record that would be written without writing to
     disk.
2. Author `tests/test_session_cost_log.py` covering:
   - Happy path: `log_session_cost(...)` writes a record containing all six required
     fields.
   - Append: multiple calls append records; prior records are not overwritten.
   - `read_log()`: returns the correct count after N writes.
   - `--dry-run`: no file is written; stdout contains the expected record.
   - Invalid input: missing a required field raises `ValueError` (or equivalent).
3. Run `uv run pytest tests/test_session_cost_log.py -v` — confirm all pass.
4. Confirm coverage ≥80%: `uv run pytest tests/test_session_cost_log.py --cov=scripts/session_cost_log --cov-report=term-missing`.

**Deliverables**:
- D1: `scripts/session_cost_log.py` with docstring, `log_session_cost`, `read_log`, and
  `--dry-run` flag.
- D2: JSON schema for `session_cost_log.json` documented in the script docstring (six
  required fields).
- D3: `tests/test_session_cost_log.py` with ≥5 test cases covering happy path, append,
  `read_log`, `--dry-run`, and invalid input.
- D4: `uv run pytest tests/test_session_cost_log.py -v` green (exit 0).
- D5: Coverage ≥80% confirmed; `--cov` output recorded in scratchpad.

**Depends on**: Phase 3 Review APPROVED
**Gate**: Phase 4 Review gate must return APPROVED before Phase 5 begins.
**Status**: ✅ Complete

---

### Phase 4 Review Gate

**Agent**: Review
**Description**: Validate script and tests against the Testing-First Requirement in
AGENTS.md before the GitHub agent opens the PR.

**Acceptance Criteria**:
1. `scripts/session_cost_log.py` exists with an opening docstring describing purpose,
   inputs, outputs, and usage.
2. `log_session_cost` and `read_log` are both present as callable public functions.
3. JSON records contain exactly the six required fields: `session_id`, `model`,
   `tokens_in`, `tokens_out`, `phase`, `timestamp`.
4. `--dry-run` flag is implemented and verified: no file written, expected record on
   stdout.
5. `tests/test_session_cost_log.py` exists with ≥5 test cases.
6. All tests in `tests/test_session_cost_log.py` pass (`uv run pytest tests/test_session_cost_log.py -v` exit 0).
7. Coverage ≥80% confirmed; `--cov` output recorded in scratchpad.

**Return**: `APPROVED` or `REQUEST CHANGES — [criterion number: one-line reason]`
**Gate**: Phase 5 does not begin until verdict is `APPROVED`.
**Status**: ✅ Complete — APPROVED

---

### Phase 5 — Commit & PR

**Agent**: GitHub
**Description**: Commit all changed files, push to `feat/establish-local-compute-baseline`,
and open a pull request targeting `main`. PR body must include `Unblocks #131`.

**Tasks**:
1. Stage all changed files: `data/inference-providers.yml`,
   `tests/test_inference_integration.py`, `scripts/session_cost_log.py`,
   `tests/test_session_cost_log.py`,
   `docs/plans/2026-03-27-local-compute-baseline.md`.
2. Commit using Conventional Commits — suggested grouping:
   - `feat(inference): fix provider model names for live Ollama stack` (Phase 1)
   - `test(inference): add integration tests for live Ollama stack` (Phase 3)
   - `feat(metrics): add session cost log harness` (Phase 4)
3. Push: `git push -u origin feat/establish-local-compute-baseline`.
4. Open PR — title: `feat(lcf): establish local compute baseline`; body includes
   `Unblocks #131` and a one-line summary per phase deliverable. Note: this establishes
   the baseline prerequisite but does NOT adopt Cognee (which is #131's actual scope).
5. Verify CI is green before requesting Copilot review.

**Deliverables**:
- D1: All phase deliverables committed to `feat/establish-local-compute-baseline`.
- D2: PR opened with `Unblocks #131` in the PR body (not `Closes` — Cognee adoption is a separate follow-up issue).
- D3: CI passing; Copilot review requested.

**Depends on**: Phase 4 Review APPROVED
**Status**: ✅ Complete

---

## Acceptance Criteria (Sprint-Level)

- [ ] `data/inference-providers.yml` — `phi3:mini`, `qwen2.5:3b`, `tinyllama:latest` present; `llama3.2`, `mistral`, `phi3` removed
- [ ] `route_inference_request(prompt="hello", model_id="phi3:mini")` returns `"ok": true, "local": true`
- [ ] `health_check_services.py --provider-type local` exits 0 with Ollama provider healthy
- [ ] `tests/test_inference_integration.py` — ≥3 `@pytest.mark.integration` tests; skips without Ollama
- [ ] `scripts/session_cost_log.py` — `log_session_cost`, `read_log`, `--dry-run` implemented with docstring
- [ ] `tests/test_session_cost_log.py` — ≥5 tests, all passing, coverage ≥80%
- [ ] PR open on `feat/establish-local-compute-baseline` with `Unblocks #131` (not `Closes` — this establishes the baseline; Cognee adoption is a separate issue)
- [ ] CI green before Copilot review requested

---

## Parallelisation Notes

None. The dependency chain is strictly linear: provider names must be correct before
E2E verification is meaningful; E2E verification must pass before integration tests can
be written and expected to pass; integration tests must be APPROVED before the cost-log
script ships to the same PR. No safe parallelisation window exists within this workplan.

---

## Open Questions

None — all acceptance criteria, agent assignments, success signals, and gate conditions
are fully specified above.
