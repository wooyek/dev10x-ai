#!/usr/bin/env bash
# Tests for create-worktree.sh userspace settings propagation (GH-555)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CREATE_SCRIPT="$SCRIPT_DIR/scripts/create-worktree.sh"

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

cleanup() {
    if [ -n "${TEST_DIR:-}" ] && [ -d "$TEST_DIR" ]; then
        cd /tmp
        git -C "$MAIN_REPO" worktree remove "$WT_PATH" --force 2>/dev/null || true
        rm -rf "$TEST_DIR"
    fi
}
trap cleanup EXIT

TEST_DIR=$(mktemp -d)
MAIN_REPO="$TEST_DIR/main"
WT_PATH="$TEST_DIR/wt-new"

# Set up a bare main repo with an initial commit
git init "$MAIN_REPO" --initial-branch=develop >/dev/null 2>&1
cd "$MAIN_REPO"
git commit --allow-empty -m "init" >/dev/null 2>&1

# ── Test 1: Propagates userspace project settings from CWD ──────
echo "Test 1: Propagates userspace project settings from CWD"

SOURCE_ENCODED=$(echo "$MAIN_REPO" | tr '/.' '--')
TARGET_ENCODED=$(echo "$WT_PATH" | tr '/.' '--')
mkdir -p "$HOME/.claude/projects/$SOURCE_ENCODED"
echo '{"permissions":{"allow":["Write","Edit"]}}' > \
    "$HOME/.claude/projects/$SOURCE_ENCODED/settings.local.json"

cd "$MAIN_REPO"
"$CREATE_SCRIPT" "$WT_PATH" "test/branch-1"

TARGET_SETTINGS="$HOME/.claude/projects/$TARGET_ENCODED/settings.local.json"
if [ -f "$TARGET_SETTINGS" ]; then
    if grep -q '"Write"' "$TARGET_SETTINGS"; then
        pass "userspace settings propagated with Write permission"
    else
        fail "userspace settings exist but missing Write permission"
    fi
else
    fail "userspace settings not created for new worktree"
fi

# Clean up worktree and test artifacts
git -C "$MAIN_REPO" worktree remove "$WT_PATH" --force 2>/dev/null || true
rm -rf "$WT_PATH"
rm -f "$HOME/.claude/projects/$SOURCE_ENCODED/settings.local.json"
rmdir "$HOME/.claude/projects/$SOURCE_ENCODED" 2>/dev/null || true
rm -f "$TARGET_SETTINGS"
rmdir "$HOME/.claude/projects/$TARGET_ENCODED" 2>/dev/null || true

# ── Test 2: Does not overwrite existing userspace settings ───────
echo "Test 2: Does not overwrite existing target userspace settings"

mkdir -p "$HOME/.claude/projects/$SOURCE_ENCODED"
echo '{"permissions":{"allow":["Write"]}}' > \
    "$HOME/.claude/projects/$SOURCE_ENCODED/settings.local.json"
mkdir -p "$HOME/.claude/projects/$TARGET_ENCODED"
echo '{"permissions":{"allow":["Bash(git:*)"]}}' > \
    "$HOME/.claude/projects/$TARGET_ENCODED/settings.local.json"

cd "$MAIN_REPO"
"$CREATE_SCRIPT" "$WT_PATH" "test/branch-2"

TARGET_SETTINGS="$HOME/.claude/projects/$TARGET_ENCODED/settings.local.json"
if grep -q 'Bash' "$TARGET_SETTINGS"; then
    pass "existing userspace settings preserved (not overwritten)"
else
    fail "existing userspace settings were overwritten"
fi

git -C "$MAIN_REPO" worktree remove "$WT_PATH" --force 2>/dev/null || true
rm -rf "$WT_PATH"
rm -f "$HOME/.claude/projects/$SOURCE_ENCODED/settings.local.json"
rmdir "$HOME/.claude/projects/$SOURCE_ENCODED" 2>/dev/null || true
rm -f "$TARGET_SETTINGS"
rmdir "$HOME/.claude/projects/$TARGET_ENCODED" 2>/dev/null || true

# ── Test 3: No source userspace settings → no propagation ───────
echo "Test 3: No propagation when source has no userspace settings"

cd "$MAIN_REPO"
"$CREATE_SCRIPT" "$WT_PATH" "test/branch-3"

TARGET_SETTINGS="$HOME/.claude/projects/$TARGET_ENCODED/settings.local.json"
if [ ! -f "$TARGET_SETTINGS" ]; then
    pass "no userspace settings created when source has none"
else
    fail "unexpected userspace settings created"
    rm -f "$TARGET_SETTINGS"
    rmdir "$HOME/.claude/projects/$TARGET_ENCODED" 2>/dev/null || true
fi

git -C "$MAIN_REPO" worktree remove "$WT_PATH" --force 2>/dev/null || true
rm -rf "$WT_PATH"

# ── Test 4: Encoding handles dots in path correctly ──────────────
echo "Test 4: Path encoding handles dots (e.g., .worktrees)"
DOTPATH="/work/bl/.worktrees/bl-zebra-1"
ENCODED=$(echo "$DOTPATH" | tr '/.' '--')
EXPECTED="-work-bl--worktrees-bl-zebra-1"
if [ "$ENCODED" = "$EXPECTED" ]; then
    pass "path encoding handles dots correctly"
else
    fail "expected '$EXPECTED' but got '$ENCODED'"
fi

# ── Summary ─────────────────────────────────────────────────────
echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
