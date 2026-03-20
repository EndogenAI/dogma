# Implementation Planning: Substrate Distiller

**Date**: 2026-03-20
**Related Issue**: #401
**Depends on**:
- docs/research/endogenic-inline-docs-baseline.md
- docs/research/endogenic-inline-docs-synthesis.md

## Objective

Define implementation-ready requirements for a Substrate Distiller script that extracts inline governance metadata, computes RDI metrics, and integrates with the Review gate.

## Phase Plan

### Phase 1 - Requirements Definition ✅
- Script path, CLI, data model, exit codes defined.
Depends on: none

### Phase 2 - Review Gate Integration ✅
- Deterministic review handoff and fail conditions defined.
Depends on: Phase 1

### Phase 3 - RDI Definition ✅
- Formula, thresholds, and classification bands defined.
Depends on: Phase 1

### Phase 4 - Handoff to Implementation ✅
- Executive Scripter implementation and test delivery complete.
- Delivered artifacts: scripts/substrate_distiller.py and tests/test_substrate_distiller.py.
Depends on: Phases 2 and 3

## Scope

In scope:
- Python AST extraction from module, class, and function docstrings.
- x-governs extraction and normalization.
- Intent and Rationale block extraction.
- RDI metric calculation and threshold-based flagging.
- Output formats suitable for local checks and Review-agent consumption.

Out of scope:
- Direct mutation of AGENTS.md or docs/research files by the distiller.
- Network calls or external API dependencies.
- CI auto-fix behavior.

## Deliverable 1: Draft script requirements

Proposed script path:
- scripts/substrate_distiller.py

CLI contract:
- uv run python scripts/substrate_distiller.py --path scripts/ --format json
- uv run python scripts/substrate_distiller.py --path mcp_server/ --format markdown
- uv run python scripts/substrate_distiller.py --path . --threshold 0.08 --fail-on-debt

Arguments:
- --path <dir-or-file>: scan target.
- --format <json|markdown|table>: output rendering.
- --threshold <float>: minimum acceptable RDI.
- --fail-on-debt: exit non-zero when any module is below threshold.
- --include-private: include underscore-prefixed symbols.
- --summary-only: output aggregate metrics only.

Exit codes:
- 0: success, no threshold violations.
- 1: scan completed but threshold violations found with --fail-on-debt.
- 2: invalid arguments or parse errors.

Core data model:
- file_path: source file path.
- scope_type: module, class, function.
- scope_name: logical symbol name.
- x_governs: normalized list of axioms/constraints.
- intent_text: extracted Intent block text.
- rationale_text: extracted Rationale block text.
- rationale_token_count: token estimate from rationale text.
- implementation_token_count: token estimate from scoped implementation body.
- rdi: rationale_token_count / max(implementation_token_count, 1).
- debt_flag: boolean based on threshold.

## Deliverable 2: Review gate integration plan

Review gate checks should consume distiller output as deterministic evidence.

Integration sequence:
1. Run distiller in json mode for changed files.
2. Generate a compact summary for Review input:
   - files scanned
   - files missing x-governs
   - files missing Intent/Rationale blocks
   - files below RDI threshold
3. Fail review when either condition is true:
   - missing governance/rationale fields in changed modules
   - below-threshold RDI in governance-critical paths

Governance-critical path defaults:
- scripts/
- mcp_server/

Note:
- The initial Substrate Distiller scope is Python-only (AST). Markdown governance checks (for example, .github/agents/*.agent.md) should remain in existing markdown validators and may be integrated in a later multi-scanner phase.

Pre-commit option:
- Add optional local hook command:
  - uv run python scripts/substrate_distiller.py --path scripts/ --threshold 0.08 --fail-on-debt --summary-only

## Deliverable 3: RDI metric definition

RDI (Rationale Density Indicator) for a scope S:

RDI(S) = R_tokens(S) / max(I_tokens(S), 1)

Where:
- R_tokens(S): estimated token count for extracted Rationale text.
- I_tokens(S): estimated token count for implementation statements in S.

Initial threshold policy:
- Green: RDI >= 0.12
- Yellow: 0.08 <= RDI < 0.12
- Red: RDI < 0.08

Interpretation:
- Green: sufficiently self-governing.
- Yellow: watch list; acceptable for low-risk modules.
- Red: technical dogma debt; block when path is governance-critical.

## Implementation notes

Tokenizer strategy:
- Use whitespace token estimate for local determinism and speed.
- Keep implementation tokenization deterministic and dependency-free.

AST strategy:
- Use ast.parse + ast.get_docstring for module/class/function extraction.
- Ignore comments outside docstrings to avoid non-authoritative signal.
- Track line numbers for each extracted scope to aid review reporting.

Safety and reliability:
- Never execute scanned code.
- Treat parse failures as actionable diagnostics.
- Emit machine-readable diagnostics for CI and review consumption.

## Suggested test plan

Create tests in tests/test_substrate_distiller.py:
- Happy path: module/class/function extraction with full fields.
- Missing x-governs path: flagged correctly.
- Missing rationale path: flagged correctly.
- Threshold behavior: green/yellow/red classification.
- Exit code behavior: 0/1/2 semantics.
- Parse error behavior: robust diagnostics.

## Next action

Proceed to implementation phase with Executive Scripter:
- Build scripts/substrate_distiller.py from this contract.
- Add tests and marker usage consistent with pyproject marker policy.
- Run lint + tests + targeted validation before commit.

## Acceptance Criteria

- [x] Script requirements are explicit and implementation-ready.
- [x] Review gate integration and failure semantics are defined.
- [x] RDI formula and thresholds are documented.
- [x] Implementation script and tests are completed in a follow-up phase.
