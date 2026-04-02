#!/usr/bin/env bash
# SessionStart hook — thin shim delegating to dev10x.hooks.session.
# All logic lives in src/dev10x/hooks/session.py.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$SCRIPT_DIR/../.."
export PYTHONPATH="${PLUGIN_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

exec python3 -c "from dev10x.hooks.session import session_reload; session_reload()"
