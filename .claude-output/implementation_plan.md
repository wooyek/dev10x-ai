# Implementation Plan for Lessons Learned PR #285

## Value Filter Results
- **Items Surviving Filter**: 2 (minimum threshold met ✓)
- **Filtered Items (Skipped)**: 3

### Surviving Items

1. **Item 4: Improve MCP tool error response documentation**
   - File: `.claude/rules/mcp-tools.md`
   - Change: Clarify domain-specific error key handling (lines 40-47)
   - Concept: Partially exists but needs clarification
   - Status: Ready for implementation

2. **Item 5: Document MCP migration pattern (dual-path declarations)**
   - File: `.claude/rules/mcp-tools.md`
   - Change: Add new subsection after "MCP tool names belong only in..." (line 131)
   - Concept: Not documented; pattern demonstrated in PR #285
   - Status: Ready for implementation

### Skipped Items (with reasons)

1. **Item 1: MCP error response consistency check (reviewer-generic.md)**
   - Reason: Budget gate failed
   - Details: File at 66 lines; budget is 50. Already over budget.

2. **Item 2: PR body formatting enforcement**
   - Reason: Recurrence test failed
   - Details: Single observation in PR #285; filter requires 2+ PRs to justify permanent rule

3. **Item 3: MCP tool name verification (reviewer-skill.md)**
   - Reason: Budget gate failed
   - Details: File at 91 lines; budget is 50. Already over budget.

## Exact Changes to Apply

### Change 1: Clarify error response patterns

**In `.claude/rules/mcp-tools.md`, update the "Important" paragraph (lines 40-47):**

OLD:
```
- Some tools return only tool-specific fields without a `success` flag
```

NEW:
```
- Some tools return only tool-specific fields without a `success` flag —
  if using a domain-specific success key (e.g., `"created": True`), use
  the same key in error responses (e.g., `{"created": False, "error":
  "msg"}`) for consistency
```

### Change 2: Add Migration Pattern section

**In `.claude/rules/mcp-tools.md`, add after line 131 (end of "MCP tool names belong only in" section):**

```markdown
### Migration Pattern: Dual-Path Declarations

When migrating a skill from shell-script invocation to MCP tools, declare
both paths during transition:

\`\`\`yaml
allowed-tools:
  - mcp__plugin_Dev10x_git__tool_name     # New MCP path
  - Bash(/path/to/script.sh:*)            # Fallback for compatibility
\`\`\`

**Why**: Allows skills to be updated gradually; older Claude Code versions
continue working with Bash paths while newer versions prefer MCP tools.

**When to remove dual-path**: Once the MCP server is deployed to all users,
remove the Bash fallback entries (not required, but cleans up dead code).

**Document in commit message**: If using this pattern, note in the PR body:
"Dual-path declarations included for backwards compatibility; Bash paths
can be removed after [date/version] deployment."
```

## PR Details

- **Branch**: `claude/lessons-pr-285`
- **Target**: `develop`
- **Status**: Draft (do NOT merge)
- **PR Title**: `🤖 Clarify MCP error handling and document migration patterns`
- **Outcome**: Reviewers can enforce consistent error response structure across MCP servers and understand backwards-compatibility approach during MCP migration

## JTBD Job Story

**When** extending MCP servers with new tools, **I want to** have clear guidance on error response consistency so **I can** avoid confusion between uniform errors and domain-specific success keys.

**When** migrating skills to MCP tools, **I want to** understand the dual-path declaration pattern so **I can** maintain backwards compatibility during gradual rollout.
