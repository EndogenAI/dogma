---
title: Claude Code with Local LLM Integration
status: Final
closes_issue: 418
x-governs: [local-compute-first]
recommendations:
  - id: rec-4.1
    title: Document Endpoint-Switching Pattern
    status: accepted-for-adoption
    effort: 1-2 hours
  - id: rec-4.2
    title: Create lcc-Style Wrapper Script
    status: accepted
    effort: 3-4 hours
  - id: rec-4.3
    title: Add Task-Fit Decision Table to Session-Management Skill
    status: accepted-for-adoption
    effort: 30-45 minutes
  - id: rec-4.4
    title: Benchmark Local vs. Cloud for Research Sessions
    status: deferred
    effort: 6-8 hours
---

# Claude Code with Local LLM Integration

## 1. Executive Summary

This synthesis evaluates a bash wrapper script that configures Claude Code to use local LLM inference servers (llama.cpp, Ollama, LM Studio) instead of Anthropic's cloud API. The script performs health checks, auto-detects available models, and launches Claude Code pointed at a localhost endpoint — achieving zero marginal inference cost for well-defined agentic coding tasks.

**Key Findings**:
- Claude Code accepts any server that speaks Anthropic Messages API format — no model verification
- llama.cpp, Ollama, and LM Studio now natively support Anthropic API (no proxy needed)
- Qwen3 Coder Next is the recommended local model (trained for tool calling and multi-step planning)
- Use case: privacy-critical work (pentesting, reverse engineering) and cost-sensitive research sessions
- Author's script demonstrates health-check-before-launch discipline we already apply to container/service startup

**Adoption Recommendation**: **Feasible — Low to Medium Effort**  
Document the endpoint-switching pattern in `docs/guides/local-compute.md`. Consider scripting Ollama health check + model selection similar to author's `lcc` wrapper. Aligns directly with MANIFESTO § 3 Local Compute-First.

---

## 2. Hypothesis Validation

**Research Question**: What can we learn and adopt from the "Claude Code with local LLM" script that routes inference to local models?

### Hypothesis 1: Script intercepts Claude Code's API calls at runtime
**Result**: ❌ **Rejected**  
The script does not intercept or proxy API calls. It configures environment variables *before launch* to point Claude Code's API client at a localhost endpoint. Claude Code then makes requests directly to llama-server without middleware.

### Hypothesis 2: Local LLM integration requires custom proxy or translation layer
**Result**: ❌ **Rejected**  
llama.cpp added native Anthropic Messages API support. Ollama and LM Studio also provide Anthropic-compatible endpoints. No translation layer is needed — the inference server speaks the same protocol Claude Code expects.

### Hypothesis 3: Cost savings come with significant quality degradation
**Result**: ⚠️ **Partially Confirmed**  
Author states "Qwen3 Coder Next can't match the depth of the largest cloud models." However, for well-defined tasks (static analysis, firmware extraction, string inspection), local inference is "more than enough." Quality tradeoff is task-dependent, not universal.

### Hypothesis 4: Integration path exists for dogma toolchain
**Result**: ✅ **Confirmed**  
We already have Ollama infrastructure. Adding endpoint-switching documentation and optionally a health-check wrapper script is low-to-medium effort. Pattern aligns with existing async process handling and rate-limit gate disciplines.

### Hypothesis 5: Pattern overlaps with existing local-compute patterns
**Result**: ✅ **Confirmed**  
The health-check-before-launch discipline mirrors our container startup polling (Docker, Ollama daemon). Model auto-detection from `/v1/models` or Ollama `/api/tags` is analogous to `scripts/wait_for_github_run.py` polling GitHub Actions runs.

---

## 3. Pattern Catalog

### Pattern 3.1: Endpoint-Switching Wrapper

**Context**: Claude Code is tied to Anthropic's cloud by default. Privacy and cost concerns motivate local inference for specific task domains.

**Problem**: Configuring Claude Code for local inference requires manually exporting environment variables, remembering flags, and verifying the inference server is running. Copy-pasting this setup every session is error-prone and tedious.

**Solution**: Bash wrapper script that:
1. Checks inference server health (`/health` endpoint)
2. Queries available models (`/v1/models` or `/api/tags`)
3. Auto-selects if one model is loaded
4. Exports environment variables pointing Claude Code at localhost
5. Launches Claude Code with configured endpoint

**Canonical Example** (from XDA article):
```bash
#!/bin/bash
# ~/.local/bin/lcc — Claude Code Local Launcher

# Configurable via env vars
HOST="${LCC_HOST:-localhost}"
PORT="${LCC_PORT:-8080}"
ENDPOINT="http://${HOST}:${PORT}"

# Health check
if ! curl -sf "${ENDPOINT}/health" > /dev/null; then
    echo "Error: llama-server not reachable at ${ENDPOINT}"
    echo "Start with: llama-server --model /path/to/model.gguf --port ${PORT}"
    exit 1
fi

# Query available models
MODELS=$(curl -sf "${ENDPOINT}/v1/models" | jq -r '.data[].id')
MODEL_COUNT=$(echo "$MODELS" | wc -l)

# Auto-select if exactly one model
if [ "$MODEL_COUNT" -eq 1 ]; then
    MODEL="$MODELS"
else
    echo "Available models:"
    echo "$MODELS" | nl
    read -p "Select model number: " SELECTION
    MODEL=$(echo "$MODELS" | sed -n "${SELECTION}p")
fi

# Export and launch
export ANTHROPIC_BASE_URL="${ENDPOINT}"
export ANTHROPIC_MODEL="$MODEL"
claude-code "$@"
```

**Consequences**:
- ✅ Single-command launch reduces friction
- ✅ Health check prevents cryptic failure modes (launching before server ready)
- ✅ Auto-selection when unambiguous choices exist
- ❌ Requires llama-server or Ollama pre-installed and configured
- ❌ Hardware requirements: RTX 3090 class or better for usable token throughput

**MANIFESTO Alignment**: Implements § 3 Local Compute-First by making local inference the default path when privacy or cost constraints apply.

---

### Pattern 3.2: Anthropic API Compatibility Layer (Native)

**Context**: Third-party inference servers (llama.cpp, Ollama, LM Studio) historically required proxies or adapters to work with clients expecting Anthropic's API format.

**Problem**: Proxies add latency, maintenance burden, and failure modes. Clients tied to Anthropic's API couldn't easily switch to local inference without custom middleware.

**Solution**: Inference servers now provide **native Anthropic Messages API endpoints**. llama.cpp's `llama-server`, Ollama, and LM Studio all expose `/v1/messages` endpoints that accept the same request schema Claude Code sends.

**Canonical Example**:
```bash
# llama.cpp native Anthropic API support
llama-server --model qwen3-coder-next.gguf --port 8080

# Claude Code makes requests to localhost:8080/v1/messages
# No proxy, no translation — direct protocol compatibility
```

**Key Technical Insight**: Claude Code does not verify it's connected to an actual Anthropic-hosted Claude model. If the response conforms to Anthropic Messages API schema, Claude Code accepts it. This "protocol-over-identity" design enables drop-in local replacement.

**Consequences**:
- ✅ Zero-latency local inference (no network round-trip)
- ✅ No proxy maintenance or failure modes
- ✅ Drop-in replacement for cloud endpoint
- ❌ Model quality ceiling: local models < largest cloud models
- ❌ Requires models trained for tool calling (e.g., Qwen3 Coder Next)

**Anti-Pattern**: Assuming Claude Code requires API key validation or cloud connectivity. The client is protocol-agnostic — it only checks response structure, not origin.

---

### Pattern 3.3: Task-Fit Stratification for Local vs. Cloud

**Context**: Not all tasks benefit equally from local inference. Well-defined, repetitive workflows (e.g., static analysis, firmware extraction) tolerate lower reasoning depth better than novel problem-solving.

**Problem**: Blanket "local-first" or "cloud-only" policies waste either cost or capability. Choosing the wrong tier for a task produces either budget overruns or quality degradation.

**Solution**: Stratify task domains into **local-suitable** (cookie-cutter procedures, privacy-critical, high-volume) and **cloud-required** (novel reasoning, maximal depth, one-off synthesis). Route to local inference when task fit is strong; fall back to cloud when depth matters more than cost.

**Canonical Example** (from XDA article use case):
```
Local-Suitable Tasks (Qwen3 Coder Next via llama.cpp):
- Static binary analysis (readelf, strings, symbol extraction)
- Firmware filesystem extraction (binwalk, partition identification)
- Hardcoded credential scanning
- Multi-file refactoring with known patterns

Cloud-Required Tasks (Claude Sonnet 4.5):
- Novel architecture reverse engineering (first encounter)
- Deep protocol analysis (reconstruct undocumented API)
- Multi-layered synthesis across large codebases
```

**Decision Heuristic**:
- **Local if**: Task is well-defined, privacy-critical, or high-volume (>10 inferences/session)
- **Cloud if**: Task requires maximal reasoning depth, novel problem space, or one-off synthesis

**Consequences**:
- ✅ Cost savings on bulk operations (zero marginal cost)
- ✅ Privacy preservation for sensitive data
- ✅ Cloud budget reserved for high-value tasks
- ❌ Requires upfront task classification (adds cognitive overhead)
- ❌ Hybrid setup increases configuration complexity

**MANIFESTO Alignment**: Extends § 3 Local Compute-First with pragmatic cloud fallback stratification rather than dogmatic "local-only" constraint.

---

## 4. Recommendations

### Rec 4.1: Document Endpoint-Switching Pattern — **ADOPT (Low Effort)**

**Action**: Create `docs/guides/claude-code-local-inference.md` documenting how to point Claude Code at Ollama or llama-server.

**Rationale**: We already have Ollama infrastructure. Documenting the endpoint-switching pattern enables any contributor to shift research sessions to local inference when privacy or cost constraints apply. This is a **documentation-only change** — no new tooling required.

**Implementation**:
1. Document environment variables (`ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`)
2. Provide Ollama setup steps (`ollama pull qwen2.5-coder`, `ollama serve`)
3. Add health check one-liner: `curl -sf http://localhost:11434/api/tags`
4. Reference from `docs/guides/local-compute.md` and `AGENTS.md § Toolchain Reference`

**Acceptance Criteria**:
- [ ] Guide created at `docs/guides/claude-code-local-inference.md`
- [ ] Cross-referenced from `docs/guides/local-compute.md`
- [ ] Includes Ollama and llama.cpp setup paths
- [ ] Health check command documented
- [ ] Effort estimate added to guide (≤30 min first-time setup)

**Status**: Proposed  
**Effort**: 1-2 hours (documentation authoring + review)  
**Blocked by**: None

---

### Rec 4.2: Create `lcc`-Style Wrapper Script — **CONSIDER (Medium Effort)**

**Action**: Port the author's `lcc` bash script to our `scripts/` directory as `scripts/claude_local.sh`. Adapt for Ollama (query `/api/tags` instead of `/v1/models`).

**Rationale**: Reduces friction for local inference adoption. Health check + auto-launch pattern aligns with our existing async process handling discipline (`scripts/wait_for_github_run.py`). Makes local inference the default path when constraints apply.

**Implementation**:
1. Port `lcc` script structure to `scripts/claude_local.sh`
2. Add Ollama-specific model query: `curl -sf http://localhost:11434/api/tags | jq -r '.models[].name'`
3. Auto-select if one model loaded, otherwise prompt
4. Export `ANTHROPIC_BASE_URL` and `ANTHROPIC_MODEL`
5. Launch Claude Code with passed args: `claude-code "$@"`
6. Add usage examples to `scripts/README.md`

**Acceptance Criteria**:
- [ ] Script created at `scripts/claude_local.sh`
- [ ] Health check for Ollama daemon (`/api/tags` endpoint)
- [ ] Auto-selection when one model available
- [ ] Exit code 1 if Ollama not reachable (with helpful error message)
- [ ] Documented in `scripts/README.md`
- [ ] Testing: script successfully launches Claude Code after `ollama pull qwen2.5-coder`

**Status**: Proposed  
**Effort**: 3-4 hours (script authoring + testing + docs)  
**Blocked by**: None (Ollama already in toolchain)

---

### Rec 4.3: Add Task-Fit Decision Table to Session-Management Skill — **ADOPT (Low Effort)**

**Action**: Extend `.github/skills/session-management/SKILL.md` with a **Local vs. Cloud Decision Table** that agents consult at session start.

**Rationale**: Stratifies session tasks by inference tier. Prevents over-reliance on cloud (cost waste) or under-reliance (quality degradation). Aligns with MANIFESTO § 3 Local Compute-First while acknowledging pragmatic cloud fallback.

**Implementation**:
Add a new section to `session-management` skill:

```markdown
### Local vs. Cloud Inference Decision

| Task Domain | Local-Suitable? | Recommended Tier | Rationale |
|-------------|-----------------|------------------|-----------|
| Research Scout (web scraping, source caching) | ✅ Yes | Ollama (qwen2.5-coder) | High-volume, well-defined extraction |
| Research Synthesizer (structured doc authoring) | ⚠️ Conditional | Cloud (Sonnet 4.5) if novel synthesis; Local if template-driven | Depth vs. speed tradeoff |
| Code review (linting, format checks) | ✅ Yes | Ollama | Deterministic rules, high-volume |
| Novel architecture design | ❌ No | Cloud (Sonnet 4.5) | Maximal reasoning depth required |
| Pentesting / reverse engineering | ✅ Yes (privacy-critical) | llama.cpp (local-only) | Sensitive data must not leave network |
```

**Acceptance Criteria**:
- [ ] Decision table added to `session-management` skill
- [ ] Table includes ≥5 common task domains
- [ ] References MANIFESTO § 3 Local Compute-First
- [ ] Cross-referenced from `docs/guides/claude-code-local-inference.md`

**Status**: Proposed  
**Effort**: 30-45 minutes (table authoring + skill update)  
**Blocked by**: None

---

### Rec 4.4: Benchmark Local vs. Cloud for Research Sessions — **DEFER (High Effort)**

**Action**: Run a controlled benchmark: identical research task (e.g., Scout phase on a known topic) executed twice — once with Ollama, once with cloud Sonnet. Measure token count, wall-clock time, synthesis quality (via Review agent score).

**Rationale**: Provides quantitative cost/quality tradeoff data. Validates or refutes hypothesis that local inference is "more than enough" for research Scout phases. Benchmark results inform Rec 4.3 decision table refinement.

**Implementation**:
1. Select representative research topic (e.g., prior OPEN_RESEARCH.md entry)
2. Execute Scout phase with Ollama (qwen2.5-coder), log token count + time
3. Execute Scout phase with cloud Sonnet, log token count + time
4. Pass both Scout outputs to Synthesizer; compare Review agent scores
5. Document findings in `docs/research/local-cloud-inference-benchmark.md`

**Acceptance Criteria**:
- [ ] Benchmark protocol defined (task selection, metrics)
- [ ] Two Scout runs completed (local + cloud)
- [ ] Token count, wall-clock time, and Review scores recorded
- [ ] Synthesis doc committed with findings
- [ ] Decision table in Rec 4.3 updated based on results

**Status**: Deferred  
**Effort**: 6-8 hours (benchmark setup + execution + synthesis)  
**Blocked by**: Rec 4.1 (need docs/guides before benchmark makes sense)

---

## 5. Sources

### Primary Source
- Conway, Adam. "[I wrote a script to run Claude Code with my local LLM, and skipping the cloud has never been easier](https://www.xda-developers.com/wrote-script-run-claude-code-local-llm-skipping-cloud/)." *XDA Developers*, 2026-03-20. Cached: `.cache/sources/xda-developers-com-wrote-script-run-claude-code-local-llm-sk.md`
- Author's GitHub Gist: https://gist.github.com/Incipiens/9f70ce27d9fa4c39bca9fafcb6ef2753

### Related Endogenous Sources
- [`MANIFESTO.md § 3 Local Compute-First`](../../MANIFESTO.md#3-local-compute-first) — foundational axiom validated by this research
- [`docs/research/infrastructure/async-process-handling.md`](./infrastructure/async-process-handling.md) — health check polling pattern (parallel to `lcc` script's `/health` check)
- [`scripts/wait_for_github_run.py`](../../scripts/wait_for_github_run.py) — canonical example of service readiness polling
- [`.github/skills/rate-limit-resilience/SKILL.md`](../../.github/skills/rate-limit-resilience/SKILL.md) — circuit-breaker logic (complementary to local inference fallback)

### External References
- llama.cpp Anthropic API support: https://github.com/ggerganov/llama.cpp/pull/8099
- Ollama Anthropic-compatible endpoint: https://ollama.com/blog/anthropic-api
- Qwen3 Coder Next model card: https://huggingface.co/Qwen/Qwen3-Coder-Next


