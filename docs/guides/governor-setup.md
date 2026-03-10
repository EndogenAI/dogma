# Governor B Setup Guide

> **One-time developer setup for the runtime heredoc governor.**

---

## 1. Overview

Governor B is the **runtime shell governor** for this project. It intercepts heredoc-containing commands at the shell input layer — before execution — and blocks them, displaying a remediation message.

**Position in the enforcement stack:**

- Governor A (pre-commit) catches heredoc writes in files at `git commit` time.
- Governor B (this guide) catches heredoc writes in interactive terminal sessions — closing the gap between "the command executes" and "the file is committed".

This governor is project-scoped: it activates when you enter the project directory (via `direnv`) and deactivates when you leave.

**References:**
- Full technical background: [`docs/research/shell-preexec-governor.md`](../research/shell-preexec-governor.md)
- bash-preexec adoption decision: [`docs/decisions/ADR-007-bash-preexec.md`](../decisions/ADR-007-bash-preexec.md)

---

## 2. Prerequisites

- **zsh or bash** shell
- **[direnv](https://direnv.net)** installed and hooked into your shell
  - macOS: `brew install direnv`
  - Then add the hook to your shell rc file: `eval "$(direnv hook zsh)"` (zsh) or `eval "$(direnv hook bash)"` (bash)
- **bash users only**: [bash-preexec](https://github.com/rcaloras/bash-preexec) sourced in `~/.bashrc`
  - Per the adoption decision at [`docs/decisions/ADR-007-bash-preexec.md`](../decisions/ADR-007-bash-preexec.md)
  - Install: `curl -s https://raw.githubusercontent.com/rcaloras/bash-preexec/master/bash-preexec.sh -o ~/.bash-preexec.sh && echo '[[ -f ~/.bash-preexec.sh ]] && source ~/.bash-preexec.sh' >> ~/.bashrc`

---

## 3. zsh Setup (one-time, per machine)

Add this block to `~/.zshrc`:

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

The block registers a ZLE `accept-line` widget that intercepts input **before** the command executes. It uses:

- **Pattern**: `<<[[:space:]]*['"]?[A-Za-z_]` — matches all heredoc forms (`<< 'EOF'`, `<< "EOF"`, `<<EOF`)
- **Allowlist**: `mysql psql sqlite3 gpg openssl docker ssh` — these commands legitimately use heredocs interactively and are not blocked
- **Conditional activation**: the widget registers only when `$PREEXEC_GOVERNOR_ENABLED` is set (checked on each prompt via `precmd` hook)

---

## 4. bash Setup (one-time, per machine)

Add this block to `~/.bashrc`:

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

This uses the `DEBUG` trap + `kill -INT $$` pattern: the trap fires before each shell command, detects the heredoc operator in `$BASH_COMMAND`, and sends SIGINT to the shell process to cancel execution. Same pattern, allowlist, and conditional activation as the zsh variant.

---

## 5. Project Activation

After completing the shell setup above, run once from the project root:

```bash
direnv allow   # run once after cloning — activates PREEXEC_GOVERNOR_ENABLED=1 from .envrc
```

Direnv will now export `PREEXEC_GOVERNOR_ENABLED=1` whenever you enter this project directory, activating the governor.

---

## 6. Acceptance Test

After setup, verify the governor is active by attempting a heredoc write in the project terminal:

```
cat > /tmp/test << 'EOF'
hello
EOF
```

**Expected**: `[GOVERNOR] Heredoc blocked. Use create_file or replace_string_in_file.` — the command does not execute and returns to the prompt.

**If the command executes instead**, the governor is not active. Diagnose:

```bash
echo $PREEXEC_GOVERNOR_ENABLED   # should print 1
```

If empty, re-run `direnv allow` from the project root and open a new terminal. If still empty, verify direnv is hooked into your shell rc file.

---

## 7. Governor Stack Reference

The full enforcement stack for heredoc prevention in this project:

| Governor | Layer | Mechanism | Scope |
|----------|-------|-----------|-------|
| Governor A | Pre-commit | `no-heredoc-writes` pygrep hook | All committed files |
| Governor B | Runtime shell | ZLE `accept-line` / `DEBUG` trap | Interactive terminal sessions |

The two layers are complementary, not redundant: Governor A catches heredocs in staged files; Governor B blocks them from executing in the first place. Both must be active for defense-in-depth.

For architecture details, see [`docs/research/shell-preexec-governor.md`](../research/shell-preexec-governor.md).
