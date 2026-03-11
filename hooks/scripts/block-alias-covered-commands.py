#!/usr/bin/env python3
"""PreToolUse hook: block git commands covered by aliases.

Blocks:
  1. ENV=value git ... — env prefix shifts effective command prefix,
     breaking allow-rule matching (broadens GIT_SEQUENCE_EDITOR check)
  2. $(git merge-base <branch> HEAD) — use git {branch}-{action} aliases

Exit codes:
  0 — allow
  2 — block
"""

from __future__ import annotations

import json
import re
import sys

ENV_PREFIX_GIT_RE = re.compile(r"^[A-Z_]+=\S*\s+git\b")

MERGE_BASE_RE = re.compile(r"\$\(git\s+merge-base\s+(\w+)\s+HEAD\)")

GIT_SUBCOMMAND_RE = re.compile(r"\bgit\s+(log|diff|rebase)\b")

ENV_PREFIX_MSG = (
    "⚠️  ENV=value prefix before `git` blocked — permission friction risk.\n\n"
    "The env-var prefix shifts the effective command prefix, breaking\n"
    "allow-rule matching and causing unnecessary permission prompts.\n\n"
    "Solutions:\n"
    "  • Drop the prefix if unnecessary:\n"
    "      {bare_command}\n"
    "  • For rebase operations, use aliases:\n"
    "      git develop-rebase    — interactive rebase onto develop\n"
    "  • For rebase --continue, no env prefix is needed:\n"
    "      git rebase --continue\n\n"
    "If aliases are missing, run: /dev10x:git-alias-setup"
)

MERGE_BASE_MSG = (
    "⚠️  $(git merge-base ...) subshell blocked — permission friction risk.\n\n"
    "The subshell shifts the effective command prefix, breaking allow-rule\n"
    "matching and causing unnecessary permission prompts.\n\n"
    "Use the git alias instead:\n"
    "    git {alias}\n\n"
    "Available aliases:\n"
    "    git {{branch}}-log       — log since diverging from branch\n"
    "    git {{branch}}-diff      — diff since diverging from branch\n"
    "    git {{branch}}-rebase    — interactive rebase onto branch\n\n"
    "If aliases are missing, run: /dev10x:git-alias-setup"
)


def block(message: str) -> None:
    result = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }
    print(json.dumps(result), file=sys.stderr)
    sys.exit(2)


def extract_bare_command(command: str) -> str:
    match = re.match(r"^[A-Z_]+=\S*\s+(.*)", command)
    return match.group(1) if match else command


def suggest_alias(
    *,
    branch: str,
    subcommand: str | None,
) -> str:
    if subcommand and branch:
        return f"{branch}-{subcommand}"
    if branch:
        return f"{branch}-log"
    return "{branch}-{action}"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    if ENV_PREFIX_GIT_RE.match(command):
        bare = extract_bare_command(command=command)
        block(ENV_PREFIX_MSG.format(bare_command=bare))

    merge_match = MERGE_BASE_RE.search(command)
    if merge_match:
        branch = merge_match.group(1)
        sub_match = GIT_SUBCOMMAND_RE.search(command)
        subcommand = sub_match.group(1) if sub_match else None
        alias = suggest_alias(branch=branch, subcommand=subcommand)
        block(MERGE_BASE_MSG.format(alias=alias))

    sys.exit(0)


if __name__ == "__main__":
    main()
