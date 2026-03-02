---
name: dx:git-alias-setup
description: Set up git aliases that reduce permission friction by wrapping
  $(git merge-base ...) subshells into stable command prefixes.
user-invocable: true
invocation-name: dx:git-alias-setup
allowed-tools:
  - Bash(~/.claude/skills/git-alias-setup/scripts/git-alias-setup.sh)
---

**Announce:** "Using dx:git-alias-setup to configure branch-comparison aliases."

# dx:git-alias-setup — Git Alias Configuration

Configures global git aliases that wrap `$(git merge-base ...)` subshells.
Without these aliases, commands like `git log $(git merge-base develop HEAD)..HEAD`
trigger extra permission prompts because the `$()` substitution shifts
the Bash command prefix.

## Usage

Run the setup script:

```bash
~/.claude/skills/git-alias-setup/scripts/git-alias-setup.sh
```

## Aliases Configured

| Alias                | Equivalent                                                  |
|----------------------|-------------------------------------------------------------|
| `git develop-log`    | `git log --oneline $(git merge-base develop HEAD)..HEAD`    |
| `git develop-diff`   | `git diff $(git merge-base develop HEAD)..HEAD`             |
| `git develop-rebase` | `git rebase -i --autosquash $(git merge-base develop HEAD)` |

## When to Use

The session start hook checks for these aliases automatically.
If they are missing, it will suggest running this skill.

After setup, use `git develop-log` instead of the full subshell form
in all git operations to avoid permission friction.

## Scope

Aliases are set globally (`--global`) so they persist across all
repositories and sessions.
