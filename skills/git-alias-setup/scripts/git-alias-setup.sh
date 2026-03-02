#!/usr/bin/env bash
# Sets up git aliases that wrap $(git merge-base ...) subshells.
# These aliases keep Bash command prefixes stable for Claude Code
# permission matching, eliminating unnecessary approval prompts.

set -euo pipefail

ALIASES=(
    "develop-log:git log --oneline \$(git merge-base develop HEAD)..HEAD"
    "develop-diff:git diff \$(git merge-base develop HEAD)..HEAD"
    "develop-rebase:git rebase -i --autosquash \$(git merge-base develop HEAD)"
)

for entry in "${ALIASES[@]}"; do
    name="${entry%%:*}"
    value="${entry#*:}"

    existing=$(git config --global --get "alias.${name}" 2>/dev/null || true)
    if [[ -n "$existing" ]]; then
        echo "  ✓ git ${name} (already configured)"
    else
        git config --global "alias.${name}" "!${value}"
        echo "  + git ${name} (configured)"
    fi
done

echo ""
echo "Aliases ready. Use:"
echo "  git develop-log     — commits since diverging from develop"
echo "  git develop-diff    — diff since diverging from develop"
echo "  git develop-rebase  — interactive autosquash rebase onto develop"
