# Skill Implementation Patterns

The codebase supports two distinct skill patterns. Review expectations differ
based on which pattern a skill uses.

## Pattern 1: Script-Based Skills

Directory contains `scripts/` with executable implementations.

**Characteristics**:
- SKILL.md provides overview and usage
- Actual implementation in `scripts/` (shell, Python, etc.)
- Examples: `gh-pr-create`, `git-commit`, `git-groom`

**Reviewer expectations** (from `reviewer-skill.md`):
- Items 4, 5, 6: Script existence, permissions, error handling
- Item 8: `allowed-tools` must declare `Bash(...)` entries
- Item 32: Output format validation

**Flag as CRITICAL if missing**: Actual implementation scripts

## Pattern 2: Orchestration-Based Skills

Directory contains only SKILL.md; Claude interprets and executes the workflow.

**Characteristics**:
- SKILL.md documents a multi-step workflow
- Claude reads and executes each step
- External tools called via `allowed-tools` declarations
- Examples: `gh-pr-request-review`, `park`

**Reviewer expectations** (from `reviewer-skill.md`):
- Items 4, 5: Do NOT apply (no scripts expected)
- Item 8: **Critical** — all external tool calls must be in `allowed-tools`
- Items 15c, 19: Config schema and decision gate enforcement
- Item 14a: Orchestration list formatting in SKILL.md

**Flag as CRITICAL if missing**: `allowed-tools` declarations for external
tools or decision gates; will cause per-invocation approval prompts.

## Pattern Detection

Determine which pattern applies:
1. Check if skill directory contains `scripts/` subdirectory
   - Yes → Script-based; apply Items 4, 5, 6, 32
   - No → Continue to step 2
2. Check if SKILL.md references local paths like `${CLAUDE_PLUGIN_ROOT}/skills/...`
   - Yes → Script-based; likely missing scripts directory
   - No → Proceed to step 3
3. Check if SKILL.md references external binaries or `~/.claude/tools/` only
   - Yes + no `scripts/` → Orchestration-based; Items 4, 5 do NOT apply
   - No → Ambiguous; flag as INFO for author clarification

## Pattern 3: Optional Parameter Handling

When multi-step orchestrations need configurable behavior, make parameters
optional with sensible defaults:

**Good practice:**
```bash
BASE_BRANCH="${2:-}"  # Allow override; default to auto-detection
if [ -z "$BASE_BRANCH" ]; then
    BASE_BRANCH=$(detect-base-branch)
fi
```

**Benefits:**
- Existing callers don't break when new parameters are added
- Scripts can be invoked standalone or as part of a pipeline
- Default behavior is clear and maintainable

**Examples:** `gh-pr-create`, `git-commit` — parameters expand over time as
features grow, but backward compatibility is preserved.

## Pattern 4: Source-Based Dependency Injection

For cross-script dependencies, use shell `source` to inject environment
variables rather than shell-script composition:

**Good practice:**
```bash
source "$SCRIPT_DIR/detect-base-branch.sh"
# Now BASE_BRANCH is available in the calling script
```

**Benefits:**
- Dependencies are explicit and single-sourced
- Testable: can mock the sourced script in unit tests
- Avoids subprocess overhead (no subshell needed)
- Logic is shared, not duplicated across scripts

**Examples:** `gh-pr-create` uses `source detect-base-branch.sh` to set
environment variables that downstream steps depend on.
