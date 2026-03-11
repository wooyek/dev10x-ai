#!/usr/bin/env bash
# Shared tool detection with installation guide URLs.
#
# Usage (source in your script):
#   source "$(dirname "${BASH_SOURCE[0]}")/../../bin/require-tool.sh"
#   require_tool jq
#   require_tool yq

set -euo pipefail

# ── Installation URLs ─────────────────────────────────────────
declare -A _TOOL_INSTALL_URL=(
    [jq]="https://jqlang.github.io/jq/download/"
    [yq]="https://github.com/mikefarah/yq#install"
    [gh]="https://cli.github.com/manual/installation"
)

# require_tool <name>
#   Checks tool is available on PATH.
#   Exits with an actionable error + install URL if missing.
require_tool() {
    local name="$1"

    if command -v "$name" &>/dev/null; then
        return 0
    fi

    local url="${_TOOL_INSTALL_URL[$name]:-}"
    echo >&2 "ERROR: '$name' not found on PATH."
    if [[ -n "$url" ]]; then
        echo >&2 "Install: $url"
    fi
    exit 1
}
