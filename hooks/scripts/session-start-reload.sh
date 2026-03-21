#!/usr/bin/env bash
# SessionStart hook — detect and offer prior session state reload.
# Reads the persisted state file (if any) and injects it as
# additionalContext so the agent is aware of prior session work.

set -euo pipefail

toplevel=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [[ -z "$toplevel" ]]; then
    exit 0
fi

project_hash=$(printf '%s' "$toplevel" | md5sum | cut -d' ' -f1)
state_dir="$HOME/.claude/projects/_session_state"
state_file="$state_dir/${project_hash}.json"

if [[ ! -f "$state_file" ]]; then
    exit 0
fi

timestamp=$(jq -r '.timestamp // empty' < "$state_file")
if [[ -z "$timestamp" ]]; then
    rm -f "$state_file"
    exit 0
fi

file_epoch=$(date -d "$timestamp" +%s 2>/dev/null || echo 0)
now_epoch=$(date +%s)
age_hours=$(( (now_epoch - file_epoch) / 3600 ))

if [[ $age_hours -gt 24 ]]; then
    stale_flag=" (STALE — ${age_hours}h old, may be outdated)"
else
    stale_flag=""
fi

branch=$(jq -r '.branch // "unknown"' < "$state_file")
worktree=$(jq -r '.worktree // ""' < "$state_file")
session_id=$(jq -r '.session_id // ""' < "$state_file")
modified=$(jq -r '.modified_files | if length > 0 then map("- " + .) | join("\n") else "none" end' < "$state_file")
staged=$(jq -r '.staged_files | if length > 0 then map("- " + .) | join("\n") else "none" end' < "$state_file")
commits=$(jq -r '.recent_commits | if length > 0 then join("\n") else "none" end' < "$state_file")

context="Prior session state detected${stale_flag}:
- Branch: ${branch}"

if [[ -n "$worktree" ]]; then
    context+="
- Worktree: ${worktree}"
fi

context+="
- Last active: ${timestamp}
- Session ID: ${session_id}

Modified files:
${modified}

Staged files:
${staged}

Recent commits:
${commits}

Resume prior session with: claude --resume ${session_id}"

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

escaped=$(escape_for_json "$context")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${escaped}"
  }
}
EOF

rm -f "$state_file"
