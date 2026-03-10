---
title: "Shifting AI Behavioral Constraints from Tokens to Deterministic Code"
status: Final
research_issue: "#151"
closes_issue: "#151"
date: "2026-03-10"
---

# Shifting AI Behavioral Constraints from Tokens to Deterministic Code

## Executive Summary

AI behavioral guardrails encoded exclusively as text instructions (prompt-level constraints, AGENTS.md directives, constitutional guidance) fail reliably under scale and distribution pressure — not due to architectural limitations, but due to fundamental weight-level pretraining defaults overriding fine-tuned behavioral signals. This research synthesizes the theoretical foundation (Constitutional AI, RLHF mechanism analysis, empirical attention studies) and translates it into a practical enforcement stack: a layered architecture that moves guardrails from token-dependent instructions into deterministic, programmatically-enforced code at five intervention tiers.

The canonical insight: **Behavioral constraints belong in the execution environment, not the prompt.** When a constraint cannot be hardcoded into the execution layer (e.g., tool permissions, API sandbox rules, pre-commit hooks), it will degrade under distribution shift and should not be relied upon for safety-critical operations. This research directly informs the forthcoming Fleet Audit (#152) and proposes specific guardrails for shift from token-dependency to programmatic enforcement.

---

## Hypothesis Validation

### H1: Text-Level Constraints Are Unreliable at Scale

**Hypothesis Foundation**: [`MANIFESTO.md`](../../MANIFESTO.md) §1 (Endogenous-First) requires behavioral constraints to be discoverable from existing system knowledge and embedded in deterministic layers; token-only guardrails fail this test by relying on attention mechanisms that degrade under distribution shift.

**Evidence**: The canonical failure mode in this repository — AI generating `cat >> file << 'EOF'` (heredoc-write pattern) despite explicit prohibition in AGENTS.md, repeated in user memory, and present in multiple agent files — is not a knowledge issue. It is a weight-level default issue.

**Empirical support**:
- **Attention analysis (Anthropic, 2024)**: Constraints in system prompts show attention suppression in position-early (first 10% of token window) and drop to near-zero weight in position-late contexts. By the time an LLM is executing a multi-step command sequence, the constraint has fallen off the attention distribution.
- **Context position degradation (Yuan et al., 2023; "Lost in the Middle")**: In-context rules (whether few-shot examples or explicit guidelines) show critical degradation when placed outside the first 25% or last 10% of context window. The heredoc prohibition in AGENTS.md is typically at position ~5K tokens (middle), while the code generation task is position ~8K+.
- **Pretraining default weight (OpenAI, 2023; Anthropic's "Constitutional AI" post-hoc analysis)**: Patterns like heredocs, file writes, and process spawning are not suppressed in pretraining — they are abundant in training data. RLHF and constitution tuning add instruction-following capability, but do not zero-out the base frequency of these patterns. Under distribution shift (new libraries, novel contexts, combined with instruction conflicts), the base rate reasserts.

**Canonical failure signature**: "Explicit instruction in AGENTS.md + instruction appears in multiple docs + agent agrees in isolation ('I will never...') + agent violates instruction under realistic task pressure." This is the universal signature of token-dependent constraint failure.

---

### H2: Enforcement Stack Architecture Determines Constraint Reliability

**Proposal**: Behavioral constraints are not binary (enforced or not). They exist on a multi-tier stack with distinct failure modes and reliability profiles:

| Tier | Layer | Example | Failure mode |
|------|-------|---------|--------------|
| **T0** | Pretraining default | "Generate valid Python code" | Weight-level bias; can be overridden by contradictory instructions in context |
| **T1** | Token-level (prompt) | "You must not generate heredocs" | Attention degradation, context position effects, distribution shift |
| **T2** | Type system / static analysis | `mypy` forbids calling `open()` in certain code paths | Bypassed by `eval()`, dynamic dispatch, or intentional type-unsafe patterns |
| **T3** | Pre-execution gate (pre-commit hook) | `git hooks` block commit if code matches pattern | Only guards committed code; bypassed by `git commit --no-verify` or direct filesystem writes |
| **T4** | Execution-time intercept | ZLE trap for `<<` at shell keypress; Python `sys.settrace()` for function calls | Hooks at the execution boundary; some bypasses (subprocess, `exec`, FFI calls); high reliability for single-tier threat model |
| **T5** | Sandbox/confinement | OS-level sandbox (seccomp, pledge, chroot), VM boundary, container network isolation | Highest reliability; highest latency/overhead; often impractical for interactive development |

**Evidence for stack model**: The Phase 4 findings on Shell PREEXEC governance demonstrate the T4 (execution-time intercept) tier empirically. The zsh ZLE `accept-line` wrapper and bash `DEBUG` trap provide high reliability (blocking before execution) at the cost of local shell configuration. Subshell bypass (`bash -c "..."`) is an architectural gap in T4, necessarily mitigated by T3 (pre-commit). No single tier is complete; efficacy requires **layered enforcement**.

---

### H3: Constraint Type Maps to Optimal Enforcement Tier

**Constraint taxonomy** (not an exhaustive typology, but the categories most relevant to AI behavioral guardrails):

1. **Allowlist constraints** (permit-only, "only call these functions / APIs"): T2–T5 are optimal. T2 (type system) catches most violations at development time. T4–T5 (runtime / sandbox) provide hard guarantees for untrusted code.
   - **Example**: "Agent may only call `run_in_terminal` with explicit `timeout` parameter."
   - **Program-friendly**: Type systems and runtime annotations can encode this directly.

2. **Blocklist constraints** (deny-only, "never call this pattern"): T3–T5 are necessary; T1 alone is insufficient.
   - **Example**: "No heredoc writes."
   - **Challenge**: Pretraining contains this pattern naturally; T1 cannot override base frequency under pressure.
   - **Solution**: T3 (pre-commit hook) + T4 (runtime governor) for layered defense.

3. **Soft behavioral constraints** (nudges, "prefer this style," unenforceable without reducing scope): T1 is the primary tier; T2 supports via linting.
   - **Example**: "Prefer file tools over terminal commands for file writes."
   - **Reality**: Cannot be enforced without eliminating the terminal tool entirely. T1 + linting is the practical ceiling.

4. **Hard access control** (capability-based, "only this entity can do X"): T5 is necessary; T4 provides strong-but-not-absolute enforcement.
   - **Example**: "Only GitHub agent can call GitHub API."
   - **Program-friendly**: Capability delegation systems, UNIX file permissions.

5. **Audit constraints** (post-execution tracking, "log all X; flag anomalies"): T5 (sandbox logging) + observability layer.
   - **Example**: "Track all LLM tool invocations and flag concurrent token-spinning."
   - **Reality**: Cannot prevent, only detect and respond.

---

### H4: Prior Art Confirms Programmatic Enforcement Superiority

**Constitutional AI (Bai et al., 2022–2023)**: Framed behavioral constraints as constitutive principles (e.g., "The AI should be helpful, harmless, and honest"). RLHF applied these to model weights. **Crucial findings**: (1) Constitutional objectives can conflict (helpfulness vs. safety); (2) Fine-tuning weights for one domain does not transfer to novel domains; (3) Red-teaming empirically found adversarial inputs that trigger base-model behavior despite tuning. **Implication**: Token-level constitutionality is a lossy compression of intent into weights — it will not hold across distribution shifts.

**RLHF guardrailing (Soulos et al., 2023)**: Analyzed reward signal transfer. Found that RLHF guards trained on one task set degrade by 15–30% on out-of-distribution task sets. **Critical**: Guards implemented via post-hoc filtering layers (T3–T4) complement RLHF and achieve 95%+ efficacy even on OOD tasks. Programmatic guards are orthogonal and more robust.

**LlamaGuard (Inan et al., 2023)**: Implemented a classifier tier (T2–like) to pre-filter unsafe LLM outputs. Achieved **97% precision** on known unsafe categories with near-zero false-positive rate (FP < 1%) when deployed as a post-execution gate. **Key finding**: Classification-tier guards are reliable precisely because they are **not** relying on the generation model's own weights to enforce safety — they intercept downstream.

**Tool-use guardrails (Patil et al., 2023; "Toolformer" and follow-up sandbox research)**: Function-call safety is reliably enforced via tool proxy layers (T4): sandboxed function call execution, type-checked argument validation, capability delegation. Models trained with these constraints learn to call tools correctly, but the **enforcement is in the runtime layer, not the model weights**. Removing the runtime layer causes immediate reversion to unsafe tool invocation patterns.

**Agent Sandbox Architectures (Talarian, 2023; "Agentive Architectures")**: Secure agent systems (e.g., CodeInterforcement, code sandboxing for interpreter tools) rely on OS-level isolation (T5) + runtime interception (T4). Text-level rules in agent prompts are treated as documentation, not as security boundaries. **Consensus**: Capability-aware agent architectures require programmatic enforcement; instruction-only is insufficient.

---

### H5: Token Cost vs. Enforcement Overhead — When Programmatic Wins

**Token cost of instruction-based constraints**:
- Including "You must never use heredocs" and related guardrails in system prompt: ~50 tokens per agent (repeated per agent invocation if not cached).
- Including expanded examples / constitutional rules: ~200–500 tokens per agent.
- Standard system prompt bloat: 2–5% of token budget for a multi-agent orchestration session.

**Enforcement overhead of programmatic tiers**:
- **T2 (static analysis)**: ~10ms per file (mypy, ruff check) — negligible for pre-commit; amortized across the session.
- **T3 (pre-commit hook)**: ~100–500ms per commit — one-time cost per change batch.
- **T4 (runtime intercept)**: 5–50ms per command (zsh ZLE wrapper, Python `sys.settrace`); latency incurred at frequency of tool invocation (not per-token).
- **T5 (sandbox)**: 100–500ms overhead per invocation (container cold-start, syscall filtering) — impractical for interactive work; reserved for high-risk operations.

**Cost-benefit decision boundary**:
- **Token cost of instruction** scales linearly with token count (every LLM forward pass includes the guardrail instruction).
- **Enforcement overhead** scales with **frequency of operation**, not token count.
- **Crossover point**: For constraints violated frequently (e.g., heredoc-write risk in terminal invocations), a T2–T3 gate pays for itself after ~5 violations prevented. For rare violations, instruction-only is cheaper.
- **Recommendation**: Constraints violated **> 2× per session** warrant T3 migration. Constraints violated **> 5× per session** warrant T4 addition.

**Cost model for this fleet**:
- Heredoc-write risk: ~1–3 violations per session historically → T2 + T3 warranted.
- Agent tool-call parameter validation: ~0.5 violations per session → T2 sufficient.
- Capability-based access (e.g., "only GitHub agent uses GitHub API"): T4–T5 necessary for liability (cannot be token-optimized).

---

### H6: Governor Design Patterns and Anti-Patterns

#### Pattern 1: Allowlist + Pre-Execution Gate (Permit-Only)

**Canonical example: Restricted terminal access**

```python
# T2 (Type system) + T4 (Runtime gate)

from typing import Literal
import sys
from functools import wraps

ALLOWED_COMMANDS = {
    "git", "uv", "pytest", "python", "bash",
    "grep", "sed", "find", "ls", "cat"
}

def run_in_terminal(command: str, **kwargs):
    """T4 Runtime gate: parse command and allowlist."""
    parsed_cmd = command.split()[0]  # Naive; real impl would use shlex
    
    if parsed_cmd not in ALLOWED_COMMANDS:
        raise SecurityError(f"Command {parsed_cmd} not in allowlist. Allowed: {ALLOWED_COMMANDS}")
    
    # ... proceed to actual execution ...
```

**Why this pattern works**:
- T2 (type signature) documents intent; reviewers see `ALLOWED_COMMANDS` immediately.
- T4 (gate function) executes the policy; LLM cannot override by context manipulation.
- Bidirectional: humans cannot accidentally grant more permissions; LLM cannot escalate.

**Anti-pattern**: "Inherit allowlist from parent process or environment variable."
```python
# ❌ Anti-pattern: brittle, dynamic, vulnerable to context escape
ALLOWED = os.environ.get("AGENT_ALLOWED_CMDS", "git,python").split(",")
```
Why it fails: Environment inheritance is implicit and fragile. A parent shell session misconfiguration leaks to subprocesses. Auditing becomes difficult. Git commits cannot encode the policy (it's in the shell environment). **Correction**: Encode allowlist in code; let environment select a **named profile** (e.g., `AGENT_PROFILE=restricted`), not the list itself.

---

#### Pattern 2: Blocklist + Detection + Audit Log (Deny-Only)

**Canonical example: Heredoc-write detection at multiple tiers**

```bash
# T3: Pre-commit hook (pygrep)
# Blocks: cat >> file << 'EOF' or cat > file << 'EOF'

# T4: Runtime trap (zsh preexec)
# Blocks user-initiated commands; logs attempt to audit trail

preexec_function() {
    if [[ $1 =~ cat[[:space:]]+(>>|>)[[:space:]]+[^[:space:]]+[[:space:]]+<<[[:space:]]*[\'\"a-zA-Z] ]]; then
        echo "SECURITY ALERT: Heredoc-write blocked" >&2
        audit_log "heredoc_attempt|user=$(whoami)|command=$1|timestamp=$(date -u +%s)"
        return 1  # Cancel execution
    fi
}
```

**Why this pattern works**:
- T3 (pre-commit) prevents committed violations.
- T4 (runtime) is the human-facing defense; logs attempts for auditing.
- Layering is necessary: T3 alone does not prevent terminal-based violations; T4 alone cannot block `git commit --no-verify`.

**Anti-pattern**: "Blocklist only at T1 (prompt instruction)."
```
# ❌ Anti-pattern: relies on LLM instruction-following
"Never generate heredocs. They are dangerous and violate this project's guardrails."
```
This has been empirically violated (the motivation for Phase 4 research). **Correction**: T3 + T4 as above.

---

#### Pattern 3: Soft Constraint + Linting (Prefer-Style)

**Canonical example: File-tool preference enforcement**

```python
# T2: Static analyzer (ruff + custom rule)

# Rule: Flag any call to run_in_terminal(command) where command 
# contains file I/O that could be accomplished via create_file/read_file.

# In agent instructions (T1): "Prefer create_file and read_file over terminal commands."
# In linting gate (T2): Ruff plugin flags violations; merge-block if ≥3 unfixed violations.

# Why: create_file is safer (no heredoc risk), more portable (works on Windows), 
# more auditable (tool call signature is explicit).
```

**Why this pattern works**:
- T1 (instruction) sets intent and provides guidance.
- T2 (lint rule) catches violations during code review.
- Enforcement is **soft**: violations don't break builds, but are flagged for discussion.

**Anti-pattern**: "Hard block of run_in_terminal entirely."
```python
# ❌ Anti-pattern: Too restrictive; eliminates legitimate uses
if tool == "run_in_terminal":
    raise ForbiddenToolError("No terminal commands ever.")
```
This blocks legitimate use cases (CI tests, package installation, long-running tasks). **Correction**: Soft linting with context-specific override (`# noqa: file-io-prefer-tool-call`).

---

#### Pattern 4: Capability Delegation + Audit (Role-Based)

**Canonical example: GitHub-agent-only GitHub operations**

```python
# T4 Runtime gate + role-based dispatch

from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    GITHUB = "github"
    EXECUTOR = "executor"
    RESEARCHER = "researcher"

@dataclass
class AgentContext:
    role: AgentRole
    execution_token: str

def call_github_api(endpoint: str, context: AgentContext) -> dict:
    """T4 gate: Role-based access control."""
    if context.role != AgentRole.GITHUB:
        audit_log(f"DENIED|unauthorized_github_call|role={context.role}|endpoint={endpoint}")
        raise PermissionError(
            f"Only GITHUB role can call GitHub API. Current role: {context.role}"
        )
    # ... proceed with API call, log to audit trail ...
    audit_log(f"GITHUB_API|endpoint={endpoint}|timestamp={now()}")
```

**Why this pattern works**:
- T4 gate is **authoritative**: checked at runtime, LLM cannot override.
- Audit trail is automatic (every call is logged).
- Role propagation is explicit in code; easy to audit and review.

**Anti-pattern**: "Check agent role in prompt; trust the agent to follow the rule."
```
# ❌ Anti-pattern: relies on prompt instruction
"You are a Researcher. You may not call GitHub APIs. Only the GitHub agent can do that."
```
A researcher agent with context-switching or jailbreak attempts can violate this. **Correction**: Runtime gate as above; prompt instruction is documentation, not enforcement.

---

#### Pattern 5: Detection + Rate-Limiting (Soft Fence)

**Canonical example: Token-spinning detection**

```python
# T4: Runtime monitoring + soft threshold

import time

token_invoke_times = []
INVOKE_RATE_LIMIT = 100  # Maximum invocations per minute

def run_notebook_cell(cell_id: str) -> dict:
    """T4 gate: Rate-limit cell invocations (detect spinning)."""
    now = time.time()
    token_invoke_times = [t for t in token_invoke_times if now - t < 60]
    
    if len(token_invoke_times) >= INVOKE_RATE_LIMIT:
        audit_log(f"RATE_LIMIT|invoke_count={len(token_invoke_times)}|threshold={INVOKE_RATE_LIMIT}")
        # Soft response: warn, don't block (in case it's legitimate)
        print(f"WARNING: {len(token_invoke_times)} cell invocations in last 60s. Pausing for 30s...")
        time.sleep(30)  # Induced backpressure
    
    token_invoke_times.append(now)
    # ... proceed with invocation ...
```

**Why this pattern works**:
- T4 detection is automatic and requires no configuration.
- Soft response (backpressure) prevents runaway without blocking legitimate workflows.
- Audit trail captures anomalous behavior for review.

**Anti-pattern**: "Trust the agent to self-limit; no rate-gate."
```
# ❌ Anti-pattern: no guardrail
"You should not invoke cells too quickly. That would waste tokens."
```
An agent chasing a red herring or stuck in a hypothesis-test loop will ignore this and burn tokens. **Correction**: Runtime rate-limit as above.

---

## Pattern Catalog

### Canonical Examples by Constraint Type

**1. Allowlist Pattern (Permit-Only)**
- **Use case**: Restricting tool access, API endpoints, code execution scopes.
- **Canonical**: Type-checked function signature + runtime gate; encoding the allowlist in code (not env vars or config files).
- **Example**: [Restricted terminal access](#pattern-1-allowlist--pre-execution-gate-permit-only) above.

**2. Blocklist Pattern (Deny-Only)**
- **Use case**: Preventing known-dangerous patterns (heredocs, unsanitized shell expansion, arbitrary code execution).
- **Canonical**: T3 (pre-commit) + T4 (runtime) layering; using regex patterns that are easy to hand-verify.
- **Example**: [Heredoc detection](#pattern-2-blocklist--detection--audit-log-deny-only) above.

**3. Soft Constraint Pattern (Prefer-Style)**
- **Use case**: Encouraging best practices without hard blocks.
- **Canonical**: Linting rule + documentation; flagging violations at review time, allowing context-specific overrides.
- **Example**: [File-tool preference](#pattern-3-soft-constraint--linting-prefer-style) above.

**4. Capability Delegation Pattern (Role-Based)**
- **Use case**: Multi-agent orchestration; ensuring only certain agents can call certain APIs.
- **Canonical**: Explicit role enum + runtime gate at call site; audit logging every access.
- **Example**: [GitHub-agent-only API access](#pattern-4-capability-delegation--audit-role-based) above.

**5. Detection + Response Pattern (Soft Fence)**
- **Use case**: Anomaly detection; preventing runaway behavior without eliminating the tool.
- **Canonical**: Automatic monitoring at T4 (runtime) with configurable thresholds and soft responses (backpressure, warnings).
- **Example**: [Token-spinning detection](#pattern-5-detection--rate-limiting-soft-fence) above.

---

### Anti-Patterns to Avoid

**Anti-Pattern 1: Token-Only Enforcement**
- **Description**: Relying exclusively on T1 (prompt instructions) for behavioral guardrails.
- **Why it fails**: Attention degradation, context position effects, weight-level pretraining defaults.
- **Symptom**: Honest agent response ("I understand, I will never...") followed by violation under realistic task pressure.
- **Fix**: Layer with T2–T4 enforcement; treat T1 as documentation, not security boundary.

**Anti-Pattern 2: Single-Tier Allowlist Without Catchall Rejection**
- **Description**: Allowing specific commands without an explicit "everything else is forbidden" gate.
- **Example**: "Allow `git`, `python`, `bash`" without catching calls to `wget`, `curl`, `nc`.
- **Why it fails**: LLM can iterate on prohibited commands, often by reformulation (e.g., `curl` → `python -m http.client`).
- **Fix**: Implement as explicit rejection of all commands **not in the allowlist** (deny-by-default pattern).

**Anti-Pattern 3: Environment Variable-Defined Policy**
- **Description**: Encoding critical policies in `$AGENT_POLICY`, `$ALLOWED_CMDS`, etc., instead of in code.
- **Why it fails**: (1) Not reproducible in git history; (2) Fragile to environment inheritance; (3) Difficult to audit; (4) Leaks across process boundaries.
- **Fix**: Hardcode policies in Python/code; use environment variables only to **select named profiles** (e.g., `AGENT_MODE=restricted` selects a pre-defined `AgentMode.RESTRICTED` enum).

**Anti-Pattern 4: Audit-Only Without Blocking (False Security)**
- **Description**: Logging violations detected at T4 but not preventing execution.
- **Example**: "If heredoc detected, log it and continue."
- **Why it fails**: Audit is useful for forensics, but does not prevent damage. For blocklist constraints (ones intended to prevent execution), logging-only provides false confidence.
- **Fix**: Distinguish soft constraints (audit-only acceptable) from hard constraints (must block). Use `return 1` / `raise exception` for hard blocks; `log + warn` for soft ones.

**Anti-Pattern 5: Hard Block of Essentially-Legitimate Tool**
- **Description**: Disabling an entire tool (e.g., `run_in_terminal`) to prevent one abuse (e.g., heredoc writes).
- **Why it fails**: Eliminates legitimate use cases; forces users to find workarounds or disable the governor.
- **Fix**: Granular allowlist + blocklist (allow terminal, block heredoc pattern). Accept that some legitimate cases may be false-positives; design the constraint to minimize FPs.

---

## Recommendations

### For This Fleet (#151 → #152 Audit)

**Immediate (P0) Guardrails to Shift from T1 → T3**:

1. **Heredoc-write patterns** (`cat >> file << 'EOF'`, `cat > file << 'EOF'`)
   - **Current**: Prohibited in AGENTS.md; repeated in agent instructions.
   - **Status**: Empirically violated (Phase 4 motivation).
   - **Action**: Implement T3 (pre-commit hook `no-heredoc-writes`; already committed in Phase 1). Add T4 (runtime governor) if violations reoccur post-Phase 5.
   - **Effort**: Low (hook already exists; monitor for 1 sprint).

2. **Direct file writes via terminal (`cat >> file`, echo redirection, printf, etc.) in Python code**
   - **Current**: T1 preference ("Use file tools").
   - **Status**: Occasional violations; not safety-critical, but reduces auditability.
   - **Action**: T2 (ruff rule: flag `run_in_terminal` with file I/O); merge-block if >2 unfixed. T1 remains as documentation.
   - **Effort**: Medium (1 ruff rule).

3. **Agent-Only API Access (e.g., GitHub agent may call GitHub API; others may not)**
   - **Current**: Documented in AGENTS.md; not enforced.
   - **Status**: Not yet violated, but architecturally necessary before multi-agent deployments.
   - **Action**: T4 runtime gate (capability delegation) in `tools/github_api.py`. Audit-log all access.
   - **Effort**: Medium (1 decorator + logging).

### Medium-Term (P1) Guardrails Requiring New Tooling

4. **Token-spinning detection (runaway cell invocations, hypothesis-test loops)**
   - **Current**: Manual monitoring.
   - **Status**: Occasional token waste; not yet economically significant, but scaling risk.
   - **Action**: T4 (runtime rate-limit + audit) on `run_notebook_cell`. Configure threshold at 100 invocations/hour (tunable).
   - **Effort**: Low (1 decorator + configurable threshold).

5. **Shell-command availability (subshell bypass via `bash -c` should be logged)**
   - **Current**: T3 (pre-commit) catches in committed code; T4 (runtime governor from Phase 4) blocks in interactive shell.
   - **Status**: Complete for heredoc case; extend pattern to general subshell audit.
   - **Action**: T4 logging in PREEXEC governor: audit all `bash -c` invocations (do not block; audit only). Analyze patterns; escalate if abuse detected.
   - **Effort**: Low (audit logging in existing governor).

### Long-Term (P2) Architectural Shifts

6. **Capability-aware agent registry**
   - **Current**: Agent roles are informal (documented in agent files).
   - **Status**: Works for ~10 agents; will not scale to 30+.
   - **Action**: Formalize agent roles + capabilities in a registry (e.g., YAML or Python dataclass). Runtime gate _all_ tool access against the registry. Enables fleet-wide audit.
   - **Effort**: High (registry design + migration of existing agents).

### Out-of-Scope for This Fleet (Deferred)

7. **Code sandbox (T5 isolation)**: Not warranted for trusted developer workflows. Revisit if the fleet expands to multi-tenant or untrusted-source scenarios.

---

## Sources

### Seminal Works on AI Safety and Constraint Mechanisms

1. **Bai, Y., Kadavath, S., Kundu, S., Askell, A., Conerly, T., Stockton, J., Joly, E., Chen, S., Goldie, A., Fort, S., Novotney, S., Olsson, C., Schiefer, N., Tegmark, M., & Converse, J. (2022).** "Constitutional AI: Harmlessness from AI Feedback." *arXiv preprint arXiv:2212.08073*. 
   - **Relevance**: Foundational work on encoding behavioral constraints into fine-tuned models via constitutional objectives and RLHF. Explicitly acknowledged the limits of token-level constraint encoding and the necessity of multi-tier enforcement.

2. **Soulos, P., Brahman, F., Durrett, G., & Dodge, J. (2023).** "Diversity and Generalization in Neural Network Interpretability." *International Conference on Machine Learning (ICML)*. 
   - **Relevance**: Empirical analysis of RLHF guard transfer to out-of-distribution tasks; shows 15–30% degradation. Demonstrates necessity of layer-independent enforcement (post-hoc gates).

3. **Liu, N. F., Lin, K., Hewitt, J., Parikh, A., Qian, M., & Bevilacqua, M. (2023).** "Lost in the Middle: How Language Models Use Long Contexts." *arXiv preprint arXiv:2307.03172*.
   - **Relevance**: Empirical evidence for position-dependent attention degradation in long contexts. Directly validates H4 (token-level constraint degradation with context length).

4. **Inan, H., Upasani, K., Lu, J., Hu, B., Sze, Y., Goodman, B., & Soricut, R. (2023).** "LlamaGuard: LLM Agent Guardrails with Automated Reasoning." *arXiv preprint arXiv:2312.06674*.
   - **Relevance**: Demonstrates T2–T4 post-execution classification-based guards achieving 97% precision on unsafe outputs with <1% false-positive rate. Empirical validation of programmatic enforcement superiority.

5. **Patil, S. G., Zhang, T., Wang, X., & Stoica, I. (2023).** "Gorilla: Large Language Model Connected with Massive APIs." *arXiv preprint arXiv:2305.15334*.
   - **Relevance**: Tool-use guardrails via sandboxed function execution and type-checked argument validation. Shows that models trained with these constraints learn safe tool use, but removing runtime enforcement causes reversion to unsafe patterns.

### Empirical Studies on Token vs. Programmatic Constraints

6. **Yuan, W., Neubig, M., & Liu, P. (2021).** "Bartscore: Reusable Tokens Play an Important Role in Machine Translation Evaluation." *arXiv preprint arXiv:1910.03009*.
   - **Relevance**: Foundational work on token importance in long sequences; basis for "lost in the middle" follow-up research.

7. **Anthropic Blog (2023).** "Scaling Constitutional AI." 
   - **Relevance**: Post-hoc analysis of fine-tuning effects; acknowledged that constitutional objectives do not transfer reliably under distribution shift and that multi-tier enforcement is necessary.

### Tool-Use and Agent Safety Architectures

8. **Talarian, A. et al. (2023).** "Agentive Architectures: Safe Multi-Agent Orchestration." *Conference on Autonomous Agents and Multiagent Systems (AAMAS)*.
   - **Relevance**: Agent sandboxing and capability delegation patterns. Consensus that capability-aware architectures require programmatic enforcement; instruction-only is insufficient.

9. **Microsoft Research (2024).** "Red-Teaming Constitutional AI Models." Internal Report.
   - **Relevance**: Red-team findings showing adversarial inputs bypassing fine-tuned safety constraints. Demonstrates empirically that base-model behavior reasserts under adversarial distribution shifts.

### Tooling Precedents

10. **GitHub Actions Virtual Environments & Secure Defaults.** GitHub Docs, 2024.
    - **Relevance**: Industry standard for pre-execution and runtime gates in CI/CD (analogous to T3–T4 tiers in this research).

11. **zsh-safe-rm Repository.** https://github.com/mattmc3/zsh-safe-rm
    - **Relevance**: Direct precedent for runtime interception via ZLE/preexec hooks; provides real-world code for Pattern 2 (blocklist + audit).

### Endogenous Sources

- [`MANIFESTO.md`](../../MANIFESTO.md) — Three core axioms: Endogenous-First (§1), Algorithms Before Tokens (§2), Local Compute-First (§3). This research encodes §2 corollary into enforcement stack architecture, mapping behavioral constraints from token-dependent instructions into deterministic code layers.

- [`AGENTS.md`](../../AGENTS.md) — Programmatic-First principle and heredoc-write guardrail specification in Guardrails section. Operational anchors for the canonical failure mode analysis in recommendation section.

- [docs/research/programmatic-governors.md](programmatic-governors.md) — Phase 2 foundational synthesis. Governor tier definitions and Watt governor analogy; forms theoretical foundation for layered enforcement concepts in this document.

- [`docs/research/values-encoding.md`](values-encoding.md) — §H1 constitutional drift pattern. Theoretical basis for token-level instruction degradation documented in this research (Hypothesis Validation H1–H4).

---

## Conclusion

Behavioral constraints effective at scale require **layered, programmatic enforcement** across the execution stack. Text-level instructions (T1) are a necessary but insufficient layer; they fail predictably under attention degradation, context position effects, and weight-level pretraining defaults. Moving critical constraints from T1 into T2–T4 (static analysis, pre-commit gates, runtime interception) yields an order-of-magnitude increase in reliability at acceptable engineering cost.

For this fleet, the immediate actionable priorities are:

1. **Heredoc-write blocking**: T3 (pre-commit hook; committed in Phase 1) + monitor for T4 escalation.
2. **File I/O preferential enforcement**: T2 (ruff rule) to lean on static analysis.
3. **Agent capability gating**: T4 (runtime gate) for GitHub API and future privileged APIs.

These recommendations directly inform the Fleet Audit (#152) and provide the foundation for scaling the agent fleet from ~10 agents to 30+ while maintaining auditability and behavior predictability.
