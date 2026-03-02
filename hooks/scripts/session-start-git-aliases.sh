#!/usr/bin/env bash
# SessionStart hook
# Checks if git branch-comparison aliases are configured.
# Reports available aliases so the agent uses them instead of
# $(git merge-base ...) subshells that break permission matching.

set -euo pipefail

ALIASES=(develop-log develop-diff develop-rebase)

missing=()
present=()

for alias in "${ALIASES[@]}"; do
    if git config --get "alias.${alias}" >/dev/null 2>&1; then
        present+=("$alias")
    else
        missing+=("$alias")
    fi
done

if [[ ${#missing[@]} -eq 0 ]]; then
    echo "Git aliases available: ${present[*]}"
    echo "Use \`git develop-log\`, \`git develop-diff\`, \`git develop-rebase\`"
    echo "instead of \$(git merge-base ...) to avoid permission prompts."
else
    echo "Git aliases missing: ${missing[*]}"
    echo "Run the git-alias-setup skill (/dx:git-alias-setup) to configure them."
    echo "These aliases reduce permission friction by avoiding \$(git merge-base ...) subshells."
fi
