#!/usr/bin/env bash
# Create a git worktree, optionally from a different repo root.
#
# Usage: create-worktree.sh <worktree-path> <branch-name> [repo-root]
#   worktree-path: absolute path for the new worktree
#   branch-name:   new branch to create (e.g. user/TICKET-123/feature-description)
#   repo-root:     optional; defaults to current working directory's git root
#                  useful when running from a different directory, e.g.:
#                  create-worktree.sh /work/myproject/.worktrees/myproject-1 \
#                    user/TICKET-123/feature /work/myproject/myproject

set -euo pipefail

WORKTREE_PATH="${1:?Usage: create-worktree.sh <worktree-path> <branch-name> [repo-root]}"
BRANCH_NAME="${2:?Usage: create-worktree.sh <worktree-path> <branch-name> [repo-root]}"
REPO_ROOT="${3:-}"

if [ -n "$REPO_ROOT" ]; then
    git -C "$REPO_ROOT" worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"
else
    git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"
fi

# Propagate userspace project settings so new worktrees inherit
# Write/Edit permissions from the active session. (GH-555)
#
# Claude Code stores per-project permissions in TWO locations:
#   1. <project>/.claude/settings.local.json  (in-project, copied by
#      post-checkout hooks via rsync from ORIGINAL_REPO)
#   2. ~/.claude/projects/<encoded-path>/settings.local.json  (userspace,
#      path-specific — NOT copied by any hook)
#
# Location 2 is where session-accumulated permissions live. Each
# worktree path gets its own userspace directory, so a new worktree
# starts with an empty one. Background agents reading that empty
# file find no Write/Edit rules and get blocked.
#
# Fix: copy the source worktree's userspace project settings to the
# new worktree's userspace directory.
SOURCE_CWD="$(pwd)"
if [ -n "$REPO_ROOT" ]; then
    SOURCE_CWD="$REPO_ROOT"
fi

# Encode paths the same way Claude Code does: replace / and . with -
encode_path() {
    echo "$1" | tr '/.' '--'
}

SOURCE_ENCODED=$(encode_path "$SOURCE_CWD")
TARGET_ENCODED=$(encode_path "$WORKTREE_PATH")
USERSPACE_DIR="$HOME/.claude/projects"

SOURCE_USERSPACE="$USERSPACE_DIR/$SOURCE_ENCODED/settings.local.json"
TARGET_USERSPACE="$USERSPACE_DIR/$TARGET_ENCODED/settings.local.json"

if [ -f "$SOURCE_USERSPACE" ] && [ ! -f "$TARGET_USERSPACE" ]; then
    mkdir -p "$USERSPACE_DIR/$TARGET_ENCODED"
    cp "$SOURCE_USERSPACE" "$TARGET_USERSPACE"
fi
