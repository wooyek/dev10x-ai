# Proposed Changes for Lessons Learned Implementation

This document details the changes that should be applied to implement lessons learned from PR #285.

## File: `.claude/rules/mcp-tools.md`

### Change 1: Clarify Error Response Handling for Domain-Specific Keys

**Location**: Lines 40-47 (section "Tool Declaration Pattern")

**Current text** (lines 44-45):
```
- Some tools return only tool-specific fields without a `success` flag

Callers must know each tool's specific success response format.
```

**Updated text** (replace lines 44-45):
```
- Some tools return only tool-specific fields without a `success` flag —
  if using a domain-specific success key (e.g., `"created": True`), use
  the same key in error responses (e.g., `{"created": False, "error":
  "msg"}`) for consistency

Callers must know each tool's specific success response format.
```

**Rationale**: PR #285 demonstrated inconsistency in error response patterns (e.g., `create_worktree` returning `{"created": False}` while other tools use `{"success": False}`). This clarification prevents tool-specific confusion by establishing a consistency principle.

---

### Change 2: Add Migration Pattern Documentation

**Location**: After line 131 (after "MCP tool names belong only in" section)

**New section to add**:

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

**Rationale**: PR #285 used this pattern intentionally ("for transition safety"), but no documentation existed. This pattern will recur as MCP migration continues across skills.

---

## Value Filter Application

### Items Accepted (2)

1. **Improve MCP tool error response documentation**
   - ✓ Deduplication: Concept exists but needs clarification
   - ✓ Recurrence: PR #285 demonstrates pattern across multiple tools
   - ✓ Actionability: Concrete guidance on domain-specific keys
   - ✓ Budget: File at 131 lines; adding ~3 lines stays under 200-line budget

2. **Document MCP migration pattern (dual-path declarations)**
   - ✓ Deduplication: Not currently documented
   - ✓ Recurrence: Pattern demonstrated in PR #285; expected to recur
   - ✓ Actionability: Concrete documentation of migration approach
   - ✓ Budget: File at 131 lines; adding ~20 lines = ~151 total (under budget)

### Items Filtered (3)

1. **Item 1: MCP error response consistency check (reviewer-generic.md)**
   - ✗ Budget gate: File at 66 lines; agent spec budget is 50. Already over budget.

2. **Item 2: PR body formatting enforcement**
   - ✗ Recurrence test: Single instance in PR #285. Filter requires 2+ PRs to justify permanent rule addition.

3. **Item 3: MCP tool name verification (reviewer-skill.md)**
   - ✗ Budget gate: File at 91 lines; agent spec budget is 50. Already over budget.

---

## Summary

- **Files changed**: 1 (`.claude/rules/mcp-tools.md`)
- **Lines added**: ~23 total
- **Current file size**: 131 lines
- **New file size**: ~154 lines (within 200-line budget)
- **Minimum threshold met**: Yes (2 items survive filtering)
