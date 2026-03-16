---
Status: Accepted
Date: 2026-03-10
Deciders: EndogenAI core team
---

# ADR-007: Adopt `bash-preexec` for Interactive Shell Governor API

---

## Context

The interactive shell governor (see [`docs/research/shell-preexec-governor.md`](../research/infrastructure/shell-preexec-governor.md)) requires a `preexec` hook — a callback that fires before each interactive command — to intercept heredoc writes and kill-signal the shell session when a forbidden pattern is detected.

Bash does not natively expose a `preexec_functions` array. The closest primitive is the `DEBUG` trap (`trap '...' DEBUG`), which fires before every simple command. Using the raw `DEBUG` trap directly works but has two problems:

1. **Fragility**: Any other tool that also sets a `DEBUG` trap (e.g., `atuin`, shell profilers, test harnesses) will silently overwrite or be overwritten by the governor's trap, breaking one or both.
2. **API mismatch with zsh**: zsh exposes a `preexec_functions` array natively. Bash users targeting both shells must maintain two code paths unless a compatibility shim is present.

`bash-preexec` (rcaloras/bash-preexec) is a widely-deployed shim that provides the `preexec_functions` / `precmd_functions` array API for bash, matching zsh's native interface. Tools like `atuin` already depend on it, making coexistence with third-party tools proven. It manages `DEBUG` trap delegation internally so multiple consumers can register callbacks without conflict.

**Scope**: this decision applies only to interactive shell sessions. CI runs in non-interactive bash; the governor and `bash-preexec` are never loaded there.

## Decision Drivers

- Bash does not expose a native `preexec_functions` array; using the raw `DEBUG` trap directly conflicts with other tools (atuin, profilers) that also need `DEBUG` trap access
- zsh exposes `preexec_functions` natively; bash users need a compatibility shim for cross-shell parity
- `bash-preexec` already has proven coexistence with widely-deployed tools (atuin), reducing integration risk

## Considered Options

1. **Raw `bash DEBUG` trap** — fragile; any other tool setting a `DEBUG` trap silently overwrites the governor's trap, breaking either tool
2. **Function wrapping (`eval` + `alias`)** — complex; not compatible with non-interactive shells; maintenance burden
3. **`bash-preexec` shim (rcaloras/bash-preexec)** — standardized `preexec_functions` API; proven coexistence; manages `DEBUG` trap delegation internally (**chosen**)
4. **zsh-only governor** — excludes bash users; insufficient given mixed bash/zsh team environments

## Decision

**Adopt `bash-preexec`** as the hook-registration layer for the interactive shell governor on bash.

- The governor registers its heredoc-interception callback via `preexec_functions+=('_endogenai_preexec')` — not by setting `trap '...' DEBUG` directly.
- `bash-preexec` handles `DEBUG` trap multiplexing; the governor does not own the trap.
- **`bash-preexec` does not block commands on its own.** Blocking (killing the shell session when a forbidden pattern is detected) still requires the `kill -INT $$` pattern inside the callback. `bash-preexec` provides the API surface; the blocking mechanism is unchanged.
- zsh requires no shim — `preexec_functions` is native.

## Consequences

- **One-time machine setup** (bash users only): `source ~/.config/bash-preexec.sh` (or the installation path chosen by the user) must be added to `~/.bashrc`. This is documented in the governor setup guide.
- **Non-interactive shells are unaffected**: CI, pre-commit hooks, and `uv run` subprocesses run non-interactive bash and never load `bash-preexec` or the governor.
- **Blocking capability is unchanged**: the `kill -INT $$` pattern used to abort forbidden commands remains in place inside the `preexec` callback. `bash-preexec` is additive — it does not weaken the blocking guarantee.
- **Third-party tool coexistence is improved**: `atuin`, shell profilers, and other `preexec_functions`-based tools can now coexist without overwriting the governor's callback.
- **`bash-preexec` is not a project dependency**: it is a user-machine prerequisite, not a Python package. It does not appear in `pyproject.toml` or `uv.lock`.

## References

- [`docs/research/shell-preexec-governor.md`](../research/infrastructure/shell-preexec-governor.md) — R5, Q5: bash-preexec adoption rationale
- [https://github.com/rcaloras/bash-preexec](https://github.com/rcaloras/bash-preexec) — upstream library
