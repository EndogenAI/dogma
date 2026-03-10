---
title: "Shell PREEXEC Governor: Runtime Interception of Heredoc Commands via zsh preexec and bash DEBUG Trap"
status: Final
research_issue: "#150"
closes_issue: "#150"
date: 2026-03-10
---

# Shell PREEXEC Governor: Runtime Interception of Heredoc Commands

> **Status**: Final
> **Research Question**: Can a zsh `preexec` / bash `DEBUG` trap function as a reliable project-scoped runtime governor that intercepts heredoc-containing commands before execution, and what are its failure modes, false-positive characteristics, and delivery mechanism?
> **Date**: 2026-03-10
> **Related**: [`docs/research/programmatic-governors.md`](programmatic-governors.md) (enforcement stack taxonomy, Watt governor analogy, Governor A/B/C/D placement hierarchy)

---

## 1. Executive Summary

A shell `preexec` / `DEBUG` trap intercepts commands at the runtime boundary — **before** execution, **after** the LLM tool call has been forwarded to the shell. This positions it as Governor B in the enforcement stack defined in `docs/research/programmatic-governors.md`: the highest-fidelity interceptor reachable from outside the terminal middleware layer.

**Five research questions were investigated.** Summary verdicts:

1. **Reliability of heredoc interception** — zsh `preexec` (via ZLE `accept-line` wrapping) can reliably detect and *block* heredoc commands. Bash `DEBUG` trap detects them but requires `kill -INT $$` to achieve blocking. Reliability differs between interactive and non-interactive contexts.
2. **Failure modes** — Four primary failure modes with explicit mitigations: piped-to-subshell bypass, `eval` partial bypass in zsh, process substitution, and non-interactive-script bypass. None is exploitable by an interactive LLM agent using the VS Code terminal tool.
3. **Project-scoped delivery via direnv** — Achievable via minimal global footprint pattern: `.envrc` exports `PREEXEC_GOVERNOR_ENABLED=1`; a one-time block in `~/.zshrc` / `~/.bashrc` conditionally registers hooks when the variable is set. Direnv's architectural constraint (subprocess-only execution) prevents direct function injection; env-var triggering is the correct workaround.
4. **False-positive rate** — The heredoc-file-write pattern (`cat > file <<` / `tee file <<`) has low false-positive rate. The broader heredoc pattern (`<< ['"]?[A-Z_]+`) has a moderate false-positive rate against legitimate shell scripting; the narrow pattern is recommended for project governor use.
5. **Existing tooling at this intercept point** — `atuin` (history), `bash-preexec` (DEBUG emulation), and `zsh-safe-rm` (safety wrapper) all use the same hook. `zsh-syntax-highlighting` uses the earlier ZLE layer. No existing tool targets heredoc-write blocking specifically.

**MANIFESTO.md alignment**: This research is a direct implementation of the **Algorithms Before Tokens** axiom (`MANIFESTO.md` § 2): the heredoc prohibition is an instruction-layer rule; the `preexec` governor is the algorithmic enforcement layer that the substrate cannot override by generating a more confident token sequence. The **Endogenous-First** axiom (`MANIFESTO.md` § 1) is applied by building from the existing `programmatic-governors.md` enforcement stack taxonomy rather than re-deriving it.

---

## 2. Hypothesis Validation

This section maps the five research questions from issue #150 to empirical findings.

---

### Q1 — Can zsh `preexec` / bash `DEBUG` trap reliably intercept heredoc-containing commands?

**Verdict**: YES for detection; YES for blocking with the correct mechanism; NO for non-interactive contexts (by design).

#### zsh

Zsh's `preexec` hook fires after the user presses Enter but before the command executes. It receives the full typed command string as `$1`, **including the `<< 'EOF'` heredoc delimiter and body**. For multi-line heredocs entered interactively, zsh accumulates the full heredoc text and passes it to `preexec` intact.

However, `preexec` alone **cannot abort execution** — it is a notification hook, not a veto hook. To block heredoc commands in zsh, the correct mechanism is to wrap the `accept-line` ZLE widget:

```zsh
function _governor_accept_line() {
  # Match heredoc operator; covers << 'EOF', << "EOF", << \EOF, <<EOF
  if [[ "$BUFFER" =~ $'<<[[:space:]]*[\'\\"]?[A-Z_a-z]' ]]; then
    zle -M $'\e[31m[GOVERNOR] Heredoc blocked. Use create_file or replace_string_in_file.\e[0m'
    return 1      # Prevents accept-line from executing the command
  fi
  zle .accept-line   # Delegate to the original accept-line
}
zle -N accept-line _governor_accept_line
```

The `zle -N accept-line` replacement intercepts at the ZLE layer — **before** `preexec` fires, before the command reaches the shell engine. Return value 1 from the widget cancels execution entirely. This is the highest-fidelity blocking mechanism in zsh.

#### bash

Bash's `DEBUG` trap fires before each simple command. The `$BASH_COMMAND` variable contains the command text **including redirection operators** (`>`, `>>`, `<<`). For `cat > /tmp/foo << 'EOF'`, `$BASH_COMMAND` is set to the full command including the `<< 'EOF'` operator, making detection reliable.

Unlike zsh, bash provides no ZLE equivalent for interactive input interception. Blocking from a `DEBUG` trap requires sending `SIGINT` to the process group:

```bash
_heredoc_governor() {
  # $BASH_COMMAND is the command about to execute
  if [[ "$BASH_COMMAND" =~ \<\<[[:space:]]*[\'\"]?[A-Za-z_] ]]; then
    echo "[GOVERNOR] Heredoc blocked: ${BASH_COMMAND}" >&2
    kill -INT $$      # Cancel current command line via SIGINT
  fi
}
trap '_heredoc_governor' DEBUG
```

The `kill -INT $$` approach is well-established: it delivers SIGINT to the current shell process, which interrupts the pending interactive command without terminating the shell session.

**Reliability summary**:

| Shell | Detection | Blocking mechanism | Reliability |
|---|---|---|---|
| zsh (ZLE wrap) | ✅ Full command buffer including body | ZLE widget return 1 | High — fires before execution |
| zsh (preexec only) | ✅ Full command text | Warning only — cannot abort | Partial — audit trail, no block |
| bash (DEBUG trap) | ✅ `$BASH_COMMAND` includes `<<` operator | `kill -INT $$` | High for interactive; variable in scripts |
| bash (non-interactive) | ✅ If trap is set | `kill -INT $$` | Only if `BASH_ENV` loads traps |

---

### Q2 — What are the failure modes?

Three tiers of failure modes are identified: **architectural constraints** (cannot be fixed by implementation changes), **implementation gaps** (fixable with additional code), and **edge cases** (low probability, low impact for the target threat model).

#### Tier 1 — Architectural Constraints

**FM-1: Piped-to-subshell bypass (Critical)**

```bash
echo "cat > /tmp/test << 'EOF'" | bash
# OR
bash -c "cat > /tmp/test << 'EOF'
content
EOF"
```

Commands piped or passed directly to a new shell process bypass the parent shell's `preexec`/`DEBUG` trap entirely. The child `bash` process has its own execution context; no trap propagates across the `bash` fork.

*Mitigation*: This attack vector requires the agent to explicitly invoke a new shell interpreter. For VS Code terminal tool usage, all commands share a single shell session. The risk applies to agents explicitly using `subprocess` or `os.system` with shell=True in Python — not to the terminal tool directly.

**FM-2: Process substitution bypass (Moderate)**

```bash
bash <(cat <<'EOF'
heredoc_content
EOF
)
```

Process substitution creates an anonymous pipe subprocess. The inner heredoc executes in the subprocess context. The parent shell's trap does not fire for the subprocess commands.

*Mitigation*: The regex pattern can be extended to detect `<(` process substitution chains, though false-positive rate increases. For the heredoc-write threat model, process substitution is an unlikely spontaneous pattern for LLM-generated code.

#### Tier 2 — Implementation Gaps

**FM-3: `eval` partial bypass in zsh**

```zsh
eval "cat > /tmp/test << 'EOF'\ncontent\nEOF"
```

In zsh, the ZLE `accept-line` hook sees `eval "cat > /tmp/test << 'EOF'..."` as the buffer. The regex matches the `<<` pattern within the string argument, so this IS detected. In bash, `eval` causes the DEBUG trap to fire twice — once for `eval` (detected) and once for the eval'd command (also detected, doubly caught).

*Verdict*: eval bypass is NOT a real gap with the regex-based detection — the `<<` marker is present in the command buffer regardless of wrapping. ✅

**FM-4: Here-string confusion (Low)**

The pattern `<<<` (here-string in bash/zsh) is syntactically distinct from `<<` (heredoc). The regex `<<[[:space:]]*['"]?[A-Za-z_]` does not match `<<<` because here-strings are followed by a space and the string content, not a delimiter identifier. No false negative expected. ✅

#### Tier 3 — Edge Cases

**FM-5: Non-interactive script execution bypass**

Shell scripts run as `bash script.sh` do not load `~/.bashrc` (unless `--rcfile` is specified for interactive mode). The `DEBUG` trap is therefore not active. This is by design — the governor targets interactive terminal commands, not batch script execution.

*Mitigation*: For batch-script coverage, the pre-commit `no-heredoc-writes` pygrep hook (Governor C) remains the correct enforcement layer.

**FM-6: Sourced subshells with `set +T`**

If a script explicitly unsets flag inheritance (`set +T`), DEBUG traps are not inherited by subshell contexts. This is an explicit user action to defeat the trap and is unlikely in spontaneous LLM-generated code.

*Mitigation*: Combine with pre-commit hook for defense-in-depth.

**FM-7: Attenuated detection for complex quoting**

```bash
cat > /tmp/test << LIMIT
content
LIMIT
```

Unquoted delimiters (`LIMIT` vs `'EOF'`) undergo variable expansion in the heredoc body. The regex must cover both quoted and unquoted forms: `<<[[:space:]]*['\\"]?[A-Za-z_][A-Za-z0-9_]*`. The provided implementation handles this.

**Failure mode summary table**:

| Failure Mode | Severity | LLM-agent exploitable? | Mitigation |
|---|---|---|---|
| Piped-to-subshell (`bash -c "..."`) | Medium | Low — requires explicit new shell | Pre-commit hook (Governor C) |
| Process substitution | Low | Very low — non-spontaneous | Extended regex or defense-in-depth |
| eval | None — detected | No | Regex catches `<<` in eval string |
| Non-interactive scripts | Medium | Low for terminal tool | Pre-commit hook covers committed files |
| `set +T` / trap inheritance | Low | Very low — explicit action | Defense-in-depth with pre-commit |

---

### Q3 — Can it be delivered via `.envrc` (direnv) as a project-scoped activation with no global shell pollution?

**Verdict**: PARTIAL — minimal global footprint is achievable; zero global footprint is architecturally impossible.

#### Direnv Architectural Constraint

Direnv evaluates `.envrc` in a **bash subprocess** to collect exported environment variables. Shell functions, aliases, ZLE widgets, and signal traps are **not exportable** as environment variables — they exist only within the subprocess context and are discarded when `direnv exec` completes. This is not a bug; it is the fundamental design of the Unix process model.

The correct delivery pattern works within this constraint:

#### Implementation: Minimal Global Footprint Pattern

**Step 1 — `.envrc` (project-scoped trigger)**:

```bash
# .envrc
export PREEXEC_GOVERNOR_ENABLED=1
```

**Step 2 — `~/.zshrc` (one-time global setup block)**:

```zsh
# Project-scoped heredoc governor — activated by PREEXEC_GOVERNOR_ENABLED=1 in .envrc
# Fires on every prompt; installs/removes the ZLE hook dynamically
_install_heredoc_governor() {
  if [[ -n "$PREEXEC_GOVERNOR_ENABLED" ]]; then
    if (( ! ${+functions[_governor_accept_line]} )); then
      function _governor_accept_line() {
        if [[ "$BUFFER" =~ $'<<[[:space:]]*[\'\\"]?[A-Za-z_]' ]]; then
          zle -M $'\e[31m[GOVERNOR] Heredoc blocked. Use create_file or replace_string_in_file.\e[0m'
          return 1
        fi
        zle .accept-line
      }
      zle -N accept-line _governor_accept_line
    fi
  else
    # Outside project directory: remove the widget if it was installed
    if (( ${+functions[_governor_accept_line]} )); then
      zle -A .accept-line accept-line
      unfunction _governor_accept_line
    fi
  fi
}
add-zsh-hook precmd _install_heredoc_governor
```

**Step 2 (bash variant) — `~/.bashrc`**:

```bash
# Project-scoped heredoc governor — activated by PREEXEC_GOVERNOR_ENABLED=1
_heredoc_governor() {
  if [[ "$BASH_COMMAND" =~ \<\<[[:space:]]*[\'\"\\]?[A-Za-z_] ]] \
      && [[ "$BASH_COMMAND" != *_heredoc_governor* ]]; then
    echo -e "\e[31m[GOVERNOR] Heredoc blocked: ${BASH_COMMAND}\e[0m" >&2
    kill -INT $$
  fi
}

# Install/remove trap based on direnv env var (refreshed at each prompt)
_update_governor_trap() {
  if [[ -n "$PREEXEC_GOVERNOR_ENABLED" ]]; then
    trap '_heredoc_governor' DEBUG
  else
    trap - DEBUG
  fi
}
PROMPT_COMMAND="_update_governor_trap;${PROMPT_COMMAND}"
```

#### Activation workflow

```bash
# One-time per repository clone
direnv allow

# Verify activation on next cd or prompt
echo $PREEXEC_GOVERNOR_ENABLED   # should print 1
```

The governor activates when entering the project directory and deactivates when leaving — fully project-scoped behavior with a one-time global shell config footprint of ~25 lines.

---

### Q4 — What is the false-positive rate on legitimate shell operations?

**Verdict**: Low for narrow heredoc-file-write pattern; moderate for broad heredoc pattern.

#### Pattern Analysis

Two detection strategies with different false-positive profiles:

**Narrow pattern** (recommended for governor): targets heredoc-to-file writes specifically.

```
^(cat[[:space:]]+[>|>>]+[[:space:]]+\S+[[:space:]]+<<|tee[[:space:]]+\S+[[:space:]]+<<)
```

False positives: near-zero for typical shell work. Targets only `cat > file <<` and `tee file <<` constructs. Misses heredoc content piped to non-file commands.

**Broad pattern** (higher coverage, higher false-positives):

```
<<[[:space:]]*['"]?[A-Za-z_][A-Za-z0-9_]*
```

False positives from legitimate heredoc uses in project development:

| Legitimate use case | Example | False positive? |
|---|---|---|
| Database CLI input | `mysql -u root << SQL` | ✅ Yes — blocked |
| OpenSSL / GPG key inputs | `gpg --batch << PARAMS` | ✅ Yes — blocked |
| SSH command bundles | `ssh host << COMMANDS` | ✅ Yes — blocked |
| Docker image build scripts | `docker build - << EOF` | ✅ Yes — blocked |
| Python import from stdin | `python3 << PYEOF` | ✅ Yes — blocked |
| `read` with heredoc body | `read var << INPUT` | ✅ Yes — blocked |
| `cat` to file (target) | `cat > file << EOF` | Block is intended |

For a purely AI-agent development session, legitimate interactive heredoc use is rare — most valid heredoc uses appear in shell script files (pre-commit hook covers those). The broad pattern is recommended for maximum coverage. Applications with heavy interactive CLI tool usage (DBA work, ops scripts) should use the narrow pattern or add per-command allowlisting.

#### Recommendation

Use the broad pattern with an **allowlist** for known-legitimate commands in specific project contexts:

```zsh
# Allowlist: commands where heredoc is legitimate
_GOVERNOR_ALLOWLIST=(mysql psql sqlite3 gpg openssl docker ssh sftp)

function _governor_accept_line() {
  if [[ "$BUFFER" =~ $'<<[[:space:]]*[\'\\"]?[A-Za-z_]' ]]; then
    # Check if the command noun is in the allowlist
    local cmd_noun="${BUFFER%% *}"
    if (( ! ${_GOVERNOR_ALLOWLIST[(Ie)$cmd_noun]} )); then
      zle -M $'\e[31m[GOVERNOR] Heredoc blocked. Use create_file or replace_string_in_file.\e[0m'
      return 1
    fi
  fi
  zle .accept-line
}
```

---

### Q5 — Is there existing tooling that already hooks this intercept point?

**Verdict**: YES — several tools use the same hooks; none targets heredoc-write blocking specifically.

#### Tools Using `preexec` / `precmd` (zsh)

| Tool | Hook used | Purpose | Relevant to governor? |
|---|---|---|---|
| **atuin** | `preexec_functions`, `precmd_functions` | Shell history recording and search | ✅ Confirms `preexec_functions` array supports multiple hooks safely |
| **zsh-safe-rm** | `preexec_functions` | Intercepts `rm` commands, adds confirmation | ✅ Direct precedent for safety-blocking via preexec |
| **zsh-syntax-highlighting** | `zle add-zle-hook-widget` | Real-time syntax highlighting in ZLE buffer | ✅ Uses ZLE layer (earlier than preexec); no blocking capability |
| **zsh-autosuggestions** | `zle add-zle-hook-widget`, `precmd_functions` | Fish-style auto-complete suggestions | Observational only; no blocking |
| **starship** | `precmd_functions` | Prompt rendering | No relevance to blocking |
| **oh-my-zsh** | Manages `preexec_functions` / `precmd_functions` | Plugin framework | Framework compatibility — functions registered via array work within OMZ |

#### Tools Using `DEBUG` Trap (bash)

| Tool | Hook used | Purpose |
|---|---|---|
| **bash-preexec** (rcaloras/bash-preexec) | Wraps `DEBUG` trap + `PROMPT_COMMAND` | Emulates zsh's `preexec_functions`/`precmd_functions` API for bash |
| **blesh** (akinomyoga/ble.sh) | Line editor replacement including DEBUG hooks | Full readline replacement with hooks at multiple layers |
| **hstr** | `PROMPT_COMMAND` | History search; uses precmd, not DEBUG |

#### Key Finding: bash-preexec as a Compatibility Layer

`bash-preexec` (a single-file library sourced from `~/.bashrc`) provides a `preexec_functions` array for bash that mirrors zsh's interface. Using it allows a **unified governor implementation** across both shells:

```bash
# After sourcing bash-preexec
preexec_functions+=(_heredoc_governor_preexec)

_heredoc_governor_preexec() {
  local cmd="$1"
  if [[ "$cmd" =~ <<[[:space:]]*[\'\"]?[A-Za-z_] ]]; then
    echo -e "\e[31m[GOVERNOR] Heredoc detected (post-accept): ${cmd}\e[0m" >&2
    # preexec fires after accept — cannot block; this is an audit-log entry
    # For blocking in bash, the DEBUG trap + kill -INT approach remains required
  fi
}
```

Note: `bash-preexec`'s `preexec_functions` fires *after* the user presses Enter (same timing as zsh's `preexec`), not before. For actual blocking in bash, the `DEBUG` trap + `kill -INT $$` pattern remains the correct implementation.

---

## 3. Pattern Catalog

### Governor Placement in the Enforcement Stack

Building on the Governor A/B/C/D hierarchy from `programmatic-governors.md`, the shell PREEXEC governor occupies Governor B — the highest-fidelity accessible intercept point:

```
LLM generates command
      ↓
[Governor A — terminal middleware: NOT ACCESSIBLE — no VS Code Copilot extension API]
      ↓
Shell receives command string
      ↓
[Governor B — zsh ZLE accept-line / bash DEBUG trap: ACCESSIBLE, blocks before execution]
      ↓
Command executes
      ↓
[Governor C — pre-commit pygrep hook: ACCESSIBLE, git-commit boundary only]
      ↓
[Governor D — post-hoc audit regex: ACCESSIBLE, forensic/logging only]
```

**Canonical example**: A project-scoped `preexec` governor registered from `.envrc` + `~/.zshrc` intercepts `cat > /tmp/file << 'EOF'` at the ZLE layer (zsh) before the command is executed. The ZLE `accept-line` widget returns 1, canceling execution and displaying `[GOVERNOR] Heredoc blocked. Use create_file or replace_string_in_file.` The pre-commit hook (Governor C) provides defense-in-depth — if the Governor B is not installed (e.g., on a different machine or in a CI script), no heredoc-written file can be committed.

**Anti-pattern**: Registering the governor only in `preexec_functions` (not the ZLE layer) in zsh. `preexec` fires *after* the user presses Enter — the command is already accepted and will execute. A `preexec`-only implementation can log and warn, but cannot block. This creates a false sense of security: the audit trail records the violation but the heredoc has already written the file. Use the ZLE `accept-line` wrapper for actual blocking in zsh.

---

### Enforcement Stack Comparison

| Layer | Mechanism | Timing | What it covers | Limitation |
|---|---|---|---|---|
| **Static analysis** | `shellcheck`, `ruff` | Pre-author (CI/IDE) | Shell script files with known anti-patterns; type errors | Interactive commands; runtime-only patterns |
| **Pre-commit hook** (Governor C) | pygrep `no-heredoc-writes` | Git commit boundary | Heredocs in staged files about to be committed | Does not prevent execution; only prevents commit |
| **Runtime governor** (Governor B) | zsh ZLE wrap / bash DEBUG + `kill -INT` | Before shell execution | All interactive heredoc commands regardless of whether files are staged | Requires per-machine shell setup; subshell bypass |
| **Post-hoc audit** (Governor D) | `validate_session.py` / scratchpad scan | After execution | Session log evidence; forensic coverage | Cannot prevent damage; best-effort coverage |

The three tiers are not substitutes — they cover different positions in the threat model and must coexist for defense-in-depth. The runtime governor closes the gap between "heredoc executes" and "heredoc is committed."

---

### Minimal Complete Implementation

#### zsh (project-scoped via direnv)

**.envrc**:
```bash
export PREEXEC_GOVERNOR_ENABLED=1
```

**~/.zshrc addition** (one-time global setup):
```zsh
# EndogenAI Workflows: project-scoped heredoc governor
_GOVERNOR_ALLOWLIST=(mysql psql sqlite3 gpg openssl docker ssh)

_install_heredoc_governor() {
  if [[ -n "$PREEXEC_GOVERNOR_ENABLED" ]]; then
    if ! zle -l accept-line 2>/dev/null | grep -q _governor_accept_line; then
      function _governor_accept_line() {
        if [[ "$BUFFER" =~ $'<<[[:space:]]*[\'\\"]?[A-Za-z_]' ]]; then
          local cmd_noun="${BUFFER%% *}"
          if (( ! ${_GOVERNOR_ALLOWLIST[(Ie)$cmd_noun]} )); then
            zle -M $'\e[31m[GOVERNOR] Heredoc blocked. Use create_file or replace_string_in_file.\e[0m'
            return 1
          fi
        fi
        zle .accept-line
      }
      zle -N accept-line _governor_accept_line
    fi
  fi
}
add-zsh-hook precmd _install_heredoc_governor
```

#### bash (project-scoped via direnv)

**~/.bashrc addition**:
```bash
# EndogenAI Workflows: project-scoped heredoc governor
_GOVERNOR_ALLOWLIST="mysql psql sqlite3 gpg openssl docker ssh"

_heredoc_governor() {
  # Skip if we're inside the governor function itself
  [[ "$BASH_COMMAND" == *_heredoc_governor* ]] && return 0
  if [[ "$BASH_COMMAND" =~ \<\<[[:space:]]*[\'\"\\]?[A-Za-z_] ]]; then
    local cmd_noun="${BASH_COMMAND%% *}"
    if [[ " $_GOVERNOR_ALLOWLIST " != *" $cmd_noun "* ]]; then
      echo -e "\e[31m[GOVERNOR] Heredoc blocked: ${BASH_COMMAND}\e[0m" >&2
      kill -INT $$
    fi
  fi
}

_update_governor_trap() {
  if [[ -n "$PREEXEC_GOVERNOR_ENABLED" ]]; then
    trap '_heredoc_governor' DEBUG
  else
    trap - DEBUG 2>/dev/null
  fi
}
PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND;}_update_governor_trap"
```

---

## 4. Recommendations

### R1 — Install the zsh ZLE governor via direnv for this project (Priority: High)

Add `export PREEXEC_GOVERNOR_ENABLED=1` to `.envrc` and the `~/.zshrc` block from the Pattern Catalog. This closes the execute-before-commit gap identified in `programmatic-governors.md` Recommendation R1. **Acceptance criteria**: `cat > /tmp/test << 'EOF'` typed in the project terminal is immediately blocked with `[GOVERNOR] Heredoc blocked` and returns to the prompt without executing.

### R2 — Use the narrow pygrep pattern for pre-commit (Priority: High, already implemented)

The existing `no-heredoc-writes` hook in `.pre-commit-config.yaml` is correct and should not be removed. It is Governor C — defense-in-depth even when the runtime governor is active. R2 is already satisfied by commit `8095621`.

### R3 — Document the governor stack in AGENTS.md (Priority: Medium)

Add a "Programmatic Governors" subsection to `AGENTS.md` per Recommendation R4 in `programmatic-governors.md`. The three tiers (runtime, pre-commit, post-hoc) should be named with their respective activation commands.

### R4 — Use the broad heredoc pattern with an allowlist for the governor (Priority: Medium)

The broader `<<[[:space:]]*['"]?[A-Za-z_]` pattern maximizes coverage. Populate the allowlist (`mysql`, `psql`, `gpg`, `openssl`, `docker`, `ssh`) to minimize false positives for valid interactive use. This is preferred over the narrow `cat > file <<` pattern because legitimate LLM-generated code rarely uses those other commands in interactive heredoc form.

### R5 — Consider bash-preexec for cross-shell consistency (Priority: Low)

For teams using bash as their primary shell, sourcing `bash-preexec` provides a unified `preexec_functions` API. However, for blocking (not just auditing), the `DEBUG` trap + `kill -INT` approach remains necessary regardless of `bash-preexec`. The recommendation is to use `bash-preexec` for teams who want consistent API surface and add the `DEBUG` trap blocking on top of it.

### R6 — Validate installation in CI environment health check (Priority: Low)

Add a check for `PREEXEC_GOVERNOR_ENABLED` to the environment validation agent (`env-validator.agent.md`) to confirm the governor is active in development environments. This is a documentation and onboarding measure, not a CI enforcement (CI runner shells are non-interactive).

---

## 5. Sources

1. **Zsh User's Guide — Hooks** (`man zsh`, `zle(1)`, `zshmisc(1)`): Documents `preexec_functions` array, triggered before each command after the user presses Enter. Timing: after `accept-line` widget commits the buffer, before execution. Cannot abort execution. `preexec` receives the full command text as `$1`.

2. **Zsh ZLE (Zsh Line Editor) Documentation** (`zle(1)`, `zshzle(1)`): Documents `zle -N accept-line` for wrapping the accept-line widget. Return value 1 from a widget wrapper cancels the action (does not execute the command). This is the blocking mechanism. `zle -M` displays a message on the status line without printing to stdout/stderr.

3. **Bash Reference Manual — `trap` builtin** (gnu.org/software/bash/manual): `trap 'handler' DEBUG` fires before each simple command, `for`, `case`, `select`, `until`. `$BASH_COMMAND` is set to the command about to execute, including I/O redirections. `kill -INT $$` sends SIGINT to the current shell process, interrupting the interactive command.

4. **direnv documentation** (direnv.net/man/direnv-stdlib.1.html): `.envrc` runs in a bash subprocess; only exported variables propagate to the parent shell. Functions, aliases, traps, ZLE widgets are not propagable. The env-var trigger pattern (export an activation variable, check it in `~/.zshrc`) is the canonical workaround for project-scoped shell customization.

5. **rcaloras/bash-preexec** (GitHub): Implements `preexec_functions` and `precmd_functions` arrays for bash via a `DEBUG` trap wrapper. Widely used by history tools (atuin, hstr). Confirms that multiple hooks in `preexec_functions` array coexist safely.

6. **atuin source** (GitHub: atuinsh/atuin): Uses `preexec_functions` in zsh and `DEBUG` trap in bash for history recording. Demonstrates production use of the same intercept point with no interference to other registered hooks.

7. **zsh-safe-rm** (GitHub: mattmc3/zsh-safe-rm): Uses `preexec_functions` to intercept `rm` commands and prompt for confirmation. Direct precedent for using `preexec_functions` as a safety-blocking governor. Limitation: fires after Enter (does not block); uses `read` prompt to pause rather than return 1 from ZLE.

8. **programmatic-governors.md** (this repository): Governor placement hierarchy (A/B/C/D), Watt governor analogy, and H3 validation (strongest reachable governor is Shell preexec; terminal middleware is inaccessible). Read before authoring this document per endogenous-first constraint.

9. **MANIFESTO.md §3 — Algorithms Before Tokens** (this repository): The foundational axiom asserting that deterministic programmatic enforcement is preferred over instruction-level tokens. This research document is a direct implementation artifact of that axiom: the `preexec` governor is the algorithmic layer that removes the heredoc decision from the token generation path entirely.

10. **MANIFESTO.md §1 — Endogenous-First** (this repository): Governs the research approach — `programmatic-governors.md` was read before external sources were consulted to avoid re-deriving the constraint taxonomy and to build on prior session knowledge.
