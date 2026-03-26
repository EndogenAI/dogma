---
title: "Agent Standardization Patterns"
status: Final
date: 2026-03-26
closes_issues: [331, 333, 337, 338, 336, 349, 380, 394]
recommendations:
- id: rec-agent-standardization-patterns-001
  title: "Decision-table encoding: schema-validated YAML in data/ with CI gate"
  status: accepted-for-adoption
  linked_issue: 331
  decision_ref: ""
- id: rec-agent-standardization-patterns-002
  title: "Multi-provider abstraction: extend rate-limit-profiles.yml with order key and implement inference_router.py"
  status: accepted-for-adoption
  linked_issue: 333
  decision_ref: ""
- id: rec-agent-standardization-patterns-003
  title: "L1/L2 validation: extend validate_agent_files.py with Pydantic BaseModel frontmatter and iter_errors pattern"
  status: accepted-for-adoption
  linked_issue: 337
  decision_ref: ""
- id: rec-agent-standardization-patterns-004
  title: "MCP standardization: audit tool files against 4-section docstring standard and {ok, errors} output contract"
  status: accepted-for-adoption
  linked_issue: 394
  decision_ref: ""
- id: rec-agent-standardization-patterns-005
  title: "Cross-platform path normalization: add _resolve_path() helper to mcp_server/_security.py"
  status: accepted-for-adoption
  linked_issue: 349
  decision_ref: ""
---

# Agent Standardization Patterns

## Executive Summary

This synthesis document covers four agent fleet standardization clusters required for Q2 Wave 2 Phase 3: (1) decision-table encoding in schema-validated YAML, (2) multi-provider LLM abstraction via routing and ordered fallback, (3) L1/L2 semantic output validation and schema-validated guardrails, and (4) MCP cross-platform tool registration standardization. All four clusters are addressed via endogenous patterns already present in the dogma substrate (`data/`, `scripts/`, `mcp_server/`), enriched with findings from LiteLLM, Pydantic v2, jsonschema, and the MCP specification. The primary governing axioms are **Endogenous-First** ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) — synthesize from existing system knowledge before reaching outward — and **Algorithms-Before-Tokens** ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)) — prefer deterministic, encoded solutions over interactive token burn.

---

## Hypothesis Validation

| Hypothesis | Status | Evidence |
|---|---|---|
| H1: Decision tables can be schema-validated YAML with CI-consumable structure | **Confirmed** | `data/delegation-gate.yml`, `data/phase-gate-fsm.yml`, `data/governance-thresholds.yml` all demonstrate working schema-encoded decision/routing tables with programmatic consumers. `classic-programmatic-patterns-dogma-legibility.md` confirms Grade-0 legibility vs Grade 14+ prose equivalents. |
| H2: Multi-provider LLM routing (ordered fallback, cooldown, retry) can be encoded in YAML profiles with a deterministic gate script | **Confirmed** | `data/rate-limit-profiles.yml` already encodes provider-specific sleep/retry/circuit-breaker thresholds. LiteLLM `Router` demonstrates `order`-key priority, `fallbacks` chains, and cooldown-pool isolation. |
| H3: L1 rule-based schema validation (< 5 ms) followed by L2 classifier-assisted semantic validation reduces guardrail bypass rate vs rules-only | **Confirmed** | AGENTS.md § Security Guardrails documents the Rebedea et al. (2023) and Inan et al. (2023) finding: hybrid pipeline reduces bypass from ~18% to ~3%. Pydantic v2 `BeforeValidator`/`AfterValidator` and jsonschema `iter_errors()` implement the L1 layer in production. |
| H4: MCP tool registration can be standardized via `@mcp.tool()` + JSON Schema `inputSchema` + consistent docstring structure | **Confirmed** | `mcp_server/dogma_server.py` already registers 9 tools via `@mcp.tool()`. MCP specification defines `tools/list` and `tools/call` protocol messages with `name`, `description`, and `inputSchema` fields. |
| H5: Cross-platform path normalization is achievable with standard `pathlib.Path` without socket/port changes (confirmed scope #336) | **Confirmed** | `pathlib.Path` eliminates platform separators; MCP spec does not mandate a specific transport — registration standardization is independent of socket/port binding. |

---

## Pattern Catalog

### Pattern 1: Schema-Validated Decision Tables (Clusters #331, #380)

**Summary**: Encode routing tables, decision gates, and governance constraints as schema-validated YAML files in `data/`. Each file carries a header comment block documenting governing axiom, reference links, and schema rationale. Programmatic consumers load the file with `yaml.safe_load()`, fail-fast on unknown keys via a `frozenset` allowlist, and expose a typed lookup function.

**Evidence from endogenous sources**:

- `data/delegation-gate.yml` — encodes executive routing routes and governance boundary impermeability as a flat YAML mapping. Header comment cites AGENTS.md and the delegation-routing skill. Programmatic consumer: `scripts/analyse_fleet_coupling.py` and the delegation-routing skill.
- `data/phase-gate-fsm.yml` — FSM for the 6-state Orchestrator lifecycle (INIT → PHASE_RUNNING → GATE_CHECK → COMPACT_CHECK → COMMIT → CLOSED). Each state carries `guard:` preconditions as inline strings — a guard-clause pattern applied to YAML. Consumer: `scripts/check_substrate_health.py`.
- `data/governance-thresholds.yml` — numeric thresholds for `encoding_coverage` and `cross_reference_density`, each with `rationale:` inline. Consumer: `.github/workflows/quarterly-audit.yml` CI gate. Implements **Algorithms-Before-Tokens** ([MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens)): thresholds are deterministic numbers, not prose instructions.
- `data/rate-limit-profiles.yml` — per-provider, per-operation sleep/retry/circuit-breaker policy. Schema: `providers: {name: {policies: {operation: {sleep_sec, retry_limit, circuit_breaker_threshold}}}}`. Consumer: `scripts/rate_limit_config.py` `get_policy()`.

**Conflict-detection hook**: When a new delegation route is added to `data/delegation-gate.yml`, `scripts/check_fleet_integration.py` validates that the referenced agent file exists. This is the pre-delegation conflict-detection hook pattern.

**CI validation pattern** (from `scripts/validate_agent_files.py`): unknown YAML keys are caught via `frozenset` allowlists (`_VALID_REC_STATUSES`, `_VALID_SCOPES`) checked at parse time with hard-fail exits. The same pattern applies to any schema-validated YAML table.

**Canonical example**: `data/governance-thresholds.yml` encodes two governance quality gates (`min_principles_passing: 0.60`, `min_mean_crd: 0.30`) with inline rationale strings, consumed by a quarterly-audit CI workflow. The table eliminates the prose instruction "remember to check encoding coverage before each sprint" — a T2 → T4 shift per the [MANIFESTO.md §2](../../MANIFESTO.md#2-algorithms-before-tokens) Algorithms-Before-Tokens principle. An LLM agent looks up the threshold in one read rather than parsing multi-clause prose; the CI workflow fails deterministically if the value falls below the number.

**Anti-pattern**: Encoding routing decisions directly inside script source code (e.g., hardcoded `if provider == "claude": sleep 60` in `rate_limit_gate.py` without a YAML profile). This means a policy change requires modifying and re-testing a Python script rather than editing a YAML file. The anti-pattern was identified when `rate_limit_gate.py` v0 used hardcoded thresholds — `data/rate-limit-profiles.yml` was subsequently introduced to separate policy from mechanism.

---

### Pattern 2: Multi-Provider LLM Abstraction — Routing and Ordered Fallback (Cluster #333)

**Summary**: Build a provider-agnostic LLM client that accepts a YAML-encoded ordered provider list with `order`, `provider`, and `model` keys. The client iterates the list in ascending `order` priority, attempting each provider until one succeeds or all are exhausted. Cooldown state for each provider is tracked in a circuit-breaker log. This scope is constrained to routing and fallback only — no streaming, tool-call forwarding, or cost accounting (confirmed scope, 2026-03-26).

**Evidence from LiteLLM** (external, source: `docs-litellm-ai-docs-routing.md`):

- `Router(model_list=..., routing_strategy="simple-shuffle")` — production-recommended stateless routing across multiple deployments. Model list is a YAML-serialisable list of dicts with `model_name` (alias), `litellm_params.model` (actual provider/model string), and optional `order`, `rpm`, `tpm`, `weight` keys.
- **Deployment ordering**: `litellm_params["order"]` accepts an integer priority. Lower values = higher priority. When `order=1` deployment is in cooldown, router automatically advances to `order=2`.
- **Cooldown-pool isolation**: `allowed_fails: N` + `cooldown_time: T` per deployment. When a deployment exceeds `allowed_fails` in a rolling window, it is removed from the active pool for `cooldown_time` seconds. Other healthy deployments continue serving — isolation prevents cascading failure across the pool.
- **Exponential backoff on RateLimitError**: LiteLLM `router.py` applies fixed retry for generic errors and exponential backoff specifically for `RateLimitError`. `retry_after` sets a minimum floor (e.g., `retry_after=5` means ≥5s between retries regardless of backoff calculation).
- **Health check**: `router.healthy_deployments` property returns deployments not in cooldown. Latency-based routing uses `lowestlatency_logger.get_available_deployments()` to short-list before selecting.

**Endogenous mapping to `data/rate-limit-profiles.yml`**: The provider policy schema in `data/rate-limit-profiles.yml` already encodes the same three parameters LiteLLM uses: `sleep_sec` (≡ `cooldown_time`), `retry_limit` (≡ `allowed_fails`), `circuit_breaker_threshold` (≡ pool-wide circuit-breaker). A dogma-native inference router can load this file via `rate_limit_config.get_policy()` and apply the same cooldown isolation pattern without importing LiteLLM.

**Canonical example**: A `providers:` ordered fallback list in `data/rate-limit-profiles.yml` with `order: 1` for `claude` (conservative, 60s sleep), `order: 2` for `gpt-4` (moderate, 30s sleep), `order: 3` for `local-localhost` (unrestricted, 0s sleep). The inference router iterates in order, checks the circuit-breaker log for cooldown state, calls the provider, and on `RateLimitError` marks the provider in cooldown and tries the next. Local-first fallback (`local-localhost`) instantiates **Local-Compute-First** ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)): when cloud providers are rate-limited, the router degrades gracefully to a local Ollama endpoint without user intervention.

**Anti-pattern**: A single-provider client with no fallback list. When the sole provider returns HTTP 429 the agent session stalls until manual restart. This was the failure mode that Sprint 17 observed, motivating `rate_limit_gate.py` and the provider policy profiles. A hardcoded string `model = "claude-3-opus"` without an ordered fallback list is the anti-pattern.

---

### Pattern 3: L1/L2 Semantic Output Validation and Schema-Validated Guardrails (Clusters #337, #338)

**Summary**: Implement a two-stage validation pipeline. Stage L1 (rule-based, < 5 ms) rejects structurally invalid inputs using Pydantic/jsonschema schema validation and regex/frozenset rule checks. Stage L2 (classifier-assisted, 150–400 ms) evaluates semantic quality — whether LLM output satisfies the acceptance criteria specified in the task prompt — using a secondary LLM call or a trained classifier. The two-stage pipeline reduces guardrail bypass from ~18% (rules only) to ~3% (hybrid), per Rebedea et al. (2023) and Inan et al. (2023) cited in AGENTS.md § Security Guardrails and `docs/research/owasp-llm-threat-model.md`.

**L1 — Rule-based schema validation** (evidence from `scripts/validate_agent_files.py`:

- **YAML frontmatter parsing**: `yaml.safe_load()` on the frontmatter block. Unknown keys produce hard errors; missing required keys produce specific gap messages. This is the jsonschema `validate()` pattern applied without importing jsonschema.
- **Frozenset allowlists**: `_VALID_REC_STATUSES = frozenset({...})` checked at parse time; any unknown status triggers `sys.exit(1)`. O(1) lookup, < 1 ms per check.
- **Regex patterns**: `_HEREDOC_PATTERN`, `_MANIFESTO_SECTION_RE`, `_CROSSREF_RE` precompiled at module import and applied in O(n) line sweeps. Precompilation moves cost to import time; runtime checks are ~µs per line.
- **Structural count checks**: section heading count, tool array length, mandatory XML wrapper presence — all deterministic string operations with no LLM call.

**L1 — Pydantic v2 for YAML constraint files** (evidence from `docs-pydantic-dev-latest-concepts-validators.md`):

- `BeforeValidator(fn)` — runs before Pydantic's internal type coercion. Use for normalisation (e.g., `.lower().strip()` on status strings). Runtime: < 1 ms.
- `AfterValidator(fn)` — runs after type coercion. Use for business constraint checks (e.g., `value in _VALID_STATUSES`). Raises `ValueError` on failure.
- `field_validator('field', mode='before'|'after'|'plain'|'wrap')` — decorator form, useful for class-based constraint models that mirror the YAML schema.
- `iter_errors()` from jsonschema returns a lazy iterator of all validation errors rather than failing on the first — important for producing actionable gap lists in `validate_*` scripts rather than single-error exits.

**L2 — Classifier-assisted semantic validation** (evidence from AGENTS.md § Security Guardrails, `docs/research/owasp-llm-threat-model.md`):

- Triggered when: output contains paraphrased bypass phrasing; bulk write exceeds 10 items not in workplan; external-content sources contain instruction-like text.
- Default L2 implementation in dogma: surface as explicit decision menu to user (human-in-the-loop). Full LLM meta-classifier is deferred until a D4 research doc and ethics rubric pass are committed (per `docs/guides/runtime-action-behaviors.md`).
- The hybrid pipeline (L1 rule gate + L2 classifier/human) reduces bypass from ~18% to ~3% — validated by Rebedea et al. (NeMo Guardrails, 2023) and Inan et al. (Llama Guard, 2023).

**Canonical example**: `scripts/validate_agent_files.py` implements the full L1 pipeline: YAML-safe parse → frozenset status check → regex pattern sweeps → structural count checks → per-check gap accumulation → single exit(0)/exit(1) report. No LLM call. Execution time: < 100 ms on the largest agent files. This is the **Endogenous-First** ([MANIFESTO.md §1](../../MANIFESTO.md#1-endogenous-first)) reference implementation: it encodes all known agent-file constraints as deterministic rules that run locally, eliminating the need for an agent to re-apply those constraints interactively.

**Anti-pattern**: Relying on a single LLM call to evaluate whether an agent file is compliant. A single LLM classification: (a) is non-deterministic — the same file may pass on one run and fail on another; (b) costs 1,000–10,000 tokens per check; (c) cannot be run in CI. The anti-pattern was present before `validate_agent_files.py` existed — agents would post the file content to another agent for review, burning tokens and producing inconsistent verdicts. L1 programmatic validation eliminated this loop for structural checks.

---

### Pattern 4: MCP Cross-Platform Tool Standardization (Clusters #336, #394)

**Summary**: Standardize MCP tool registration using `@mcp.tool()` decorators with consistent naming (snake_case), self-documenting docstrings (purpose, args, returns, usage), and JSON Schema `inputSchema` from Python type annotations. Cross-platform path handling uses `pathlib.Path` throughout — never string concatenation with `os.sep`. Scope for this sprint is registration standardization and path normalization; socket/port binding is out of scope (confirmed scope, 2026-03-26).

**MCP specification conventions** (evidence from `modelcontextprotocol-io-docs-concepts-tools.md`):

- Tool `name`: unique string identifier. Convention per spec: lowercase with underscores (`get_weather`, `run_research_scout`). This is snake_case — consistent with Python function names and importable as a module identifier.
- Tool `description`: human-readable string of functionality. Must describe what the tool does, not how. Consumed by LLM clients for tool selection — description quality directly affects routing accuracy.
- Tool `inputSchema`: JSON Schema object (type: object, properties: {}, required: []). FastMCP derives this automatically from Python type annotations. Explicit `description` per parameter improves LLM argument construction.
- `tools/list` response: array of tool objects. `listChanged: true` capability signals that tools can be added/removed at runtime; clients may re-query.
- `tools/call` protocol: `method: "tools/call"`, `params: {name: str, arguments: {}}`. Result: `{content: [{type, text/data}], isError: bool}`.

**Endogenous conventions** (evidence from `mcp_server/dogma_server.py` and `mcp_server/tools/`):

- Registration: `@mcp.tool()` decorator on module-level function. All 9 tools in `dogma_server.py` follow this pattern. Function name becomes the MCP tool name.
- Docstring structure: 4-section format: purpose sentence → Args block (`arg: type — description`) → Returns block (JSON schema of output dict) → Usage examples. This docstring structure is also the L1 validation target for `validate_agent_file()`.
- Output contract: all tools return `dict` with `{ok: bool, ..., errors: list[str]}`. Uniform error surface enables L1 structural checks on MCP responses.
- Path handling: `mcp_server/_security.py` defines `REPO_ROOT = Path(__file__).parent.parent` using `pathlib.Path`. Tool path parameters are validated via `validate_repo_path()` before any file operation — no string concatenation.

**Cross-platform path normalization**:

- `pathlib.Path` normalizes separators automatically: `Path("a") / "b" / "c"` → `a/b/c` on POSIX, `a\b\c` on Windows, with no manual `os.sep` interpolation.
- `Path.resolve()` produces an absolute, canonicalized path — useful for validating that a user-supplied path stays within `REPO_ROOT` (prevents path traversal).
- `str(Path(...))` for display only; use `Path` objects for all internal path operations.

**Canonical example**: `mcp_server/tools/research.py` `run_research_scout()` — registered via `@mcp.tool()`, snake_case name matches function, 4-section docstring, returns `{"ok": bool, "url": str, "cache_path": str | None, "errors": list[str]}`. Path to cache is constructed as `REPO_ROOT / ".cache" / "sources" / slug` using `pathlib.Path`. SSRF validation via `validate_url()` runs before any network call. The tool is fully discoverable via `tools/list` with no additional registration manifest.

**Anti-pattern**: Registering MCP tools with a separate tool manifest JSON file that must be kept in sync with the implementation. When the manifest and the `@mcp.tool()` implementation diverge, `tools/list` returns stale definitions. The anti-pattern was present in early MCP server drafts that used a `tools_manifest.json` alongside the Python code — FastMCP eliminates this by deriving the manifest from decorators and type annotations at server startup.

---

## Recommendations

1. **#331 / #380 — Decision-table encoding**: All new routing tables and governance constraints with ≥3 conditional branches must be encoded as schema-validated YAML in `data/`. Each file must carry a header comment block (governing axiom, reference links, rationale). CI gate: add `validate_yaml_schema()` call to `check_substrate_health.py` for each `data/*.yml` file declared in `substrate-atlas.yml`.

2. **#333 — Multi-provider abstraction**: Extend `data/rate-limit-profiles.yml` with an `order` key per provider (1=primary, 2=fallback, 3=local). Implement `scripts/inference_router.py` that loads the ordered list, tracks cooldown state in `.cache/rate-limit-audit.log`, and applies exponential backoff on `RateLimitError` before advancing to the next provider. Use `rate_limit_config.get_policy()` as the policy source — no hardcoded thresholds in the router script.

3. **#337 / #338 — L1/L2 validation**: Extend `validate_agent_files.py` with Pydantic `BaseModel` for the frontmatter block to replace ad-hoc YAML key checks with typed model validation. Add `iter_errors()` pattern from jsonschema for YAML constraint files to produce exhaustive gap lists rather than fail-fast. L2 semantic validation remains human-in-the-loop per `docs/guides/runtime-action-behaviors.md` until a separate D4 doc and ethics rubric are committed.

4. **#336 / #394 — MCP standardization**: Audit all 5 tool files in `mcp_server/tools/` against the 4-section docstring standard and `{ok, ..., errors}` output contract. Add `validate_mcp_tools()` check to `scripts/validate_agent_files.py --skills` path for the MCP server tools. Replace any `str + os.sep` path constructions with `pathlib.Path` operators in all tool files.

5. **#349 — Cross-platform path normalization**: Add a single `_resolve_path(user_path: str) -> Path` helper to `mcp_server/_security.py` that: (a) coerces to `Path`, (b) resolves to absolute, (c) validates it stays within `REPO_ROOT`. Any tool accepting a file path must pass through this helper — no raw string path parameters.

---

## Sources

### Endogenous (primary)

- [`data/delegation-gate.yml`](../../data/delegation-gate.yml) — routing table pattern, governance boundary encoding
- [`data/phase-gate-fsm.yml`](../../data/phase-gate-fsm.yml) — FSM-as-YAML, guard-clause in YAML states
- [`data/governance-thresholds.yml`](../../data/governance-thresholds.yml) — numeric threshold tables with inline rationale
- [`data/rate-limit-profiles.yml`](../../data/rate-limit-profiles.yml) — provider policy profiles; ordered fallback schema
- [`scripts/validate_agent_files.py`](../../scripts/validate_agent_files.py) — L1 rule-based validation pipeline (frozenset, regex, structural counts)
- [`scripts/validate_synthesis.py`](../../scripts/validate_synthesis.py) — D4 document validation; required heading checks
- [`scripts/rate_limit_gate.py`](../../scripts/rate_limit_gate.py) — circuit-breaker pattern; provider-aware sleep injection
- [`scripts/rate_limit_config.py`](../../scripts/rate_limit_config.py) — YAML policy loader; typed `get_policy()` lookup
- [`mcp_server/dogma_server.py`](../../mcp_server/dogma_server.py) — `@mcp.tool()` registration; 9 production tools
- [`mcp_server/tools/research.py`](../../mcp_server/tools/research.py) — canonical 4-section docstring; SSRF-safe path handling
- [`mcp_server/_security.py`](../../mcp_server/_security.py) — `REPO_ROOT` via `pathlib.Path`; `validate_repo_path()`
- [`docs/research/classic-programmatic-patterns-dogma-legibility.md`](classic-programmatic-patterns-dogma-legibility.md) — decision-table and FSM patterns; Grade-0 vs Grade 14+ legibility comparison
- [`docs/research/owasp-llm-threat-model.md`](owasp-llm-threat-model.md) — two-stage guardrail pipeline; Rebedea et al. (2023); Inan et al. (2023)
- [`AGENTS.md § Security Guardrails`](../../AGENTS.md#security-guardrails) — two-stage gate protocol; Stage 1 and Stage 2 trigger conditions

### External (secondary)

- LiteLLM Router documentation. `docs-litellm-ai-docs-routing.md`. https://docs.litellm.ai/docs/routing (fetched 2026-03-26). Covers: `order`-key priority, cooldown-pool isolation, exponential backoff on RateLimitError, `healthy_deployments` health check.
- Pydantic v2 Validators documentation. `docs-pydantic-dev-latest-concepts-validators.md`. https://docs.pydantic.dev/latest/concepts/validators/ (fetched 2026-03-26). Covers: BeforeValidator, AfterValidator, PlainValidator, WrapValidator, field_validator decorator modes.
- jsonschema Python library documentation. `python-jsonschema-readthedocs-io-en-stable.md`. https://python-jsonschema.readthedocs.io/en/stable/ (fetched 2026-03-26). Covers: `validate()`, `iter_errors()` lazy validation, Draft 2020-12 support.
- Model Context Protocol — Tools specification. `modelcontextprotocol-io-docs-concepts-tools.md`. https://modelcontextprotocol.io/docs/concepts/tools (fetched 2026-03-26). Covers: tool `name`/`description`/`inputSchema`/`outputSchema`, `tools/list`, `tools/call`, `listChanged` capability.
- Rebedea, T., et al. (2023). "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications." arXiv:2310.10501. Cited in `docs/research/owasp-llm-threat-model.md`. Evidence: two-stage (rule+classifier) pipeline reduces bypass rate from ~18% to ~3%.
- Inan, H., et al. (2023). "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations." arXiv:2312.06674. Cited in `docs/research/owasp-llm-threat-model.md`. Evidence: classifier-layer augmentation of rule-based guardrails.
