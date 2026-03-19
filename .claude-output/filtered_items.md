# Lessons Learned Filtering Summary

Applied the Value Filter to all proposed changes from lessons learned report.

## Items Skipped (with reasons)

### 1. Add MCP error response consistency check to reviewer-generic.md
- **Priority**: High
- **Skip reason**: **Budget gate exceeded**
- **Details**:
  - Current line count: 66 lines
  - Budget for agent specs: 50 lines
  - File is already over budget
  - Adding 3-4 lines would exceed further
- **Action**: SKIP per budget constraints

### 2. Clarify or enforce PR body formatting rule
- **Priority**: High
- **Skip reason**: **Recurrence test failed**
- **Details**:
  - Evidence: "Single instance in PR #285"
  - Filter requirement: Pattern must occur in 2+ PRs
  - One-off observations do not justify permanent rule additions
- **Action**: SKIP; observe for recurrence in future PRs

### 3. Add MCP tool name verification to reviewer-skill.md
- **Priority**: Medium
- **Skip reason**: **Budget gate exceeded**
- **Details**:
  - Current line count: 91 lines
  - Budget for agent specs: 50 lines
  - File is already over budget by 41 lines
  - Adding 3-4 lines would exceed further
- **Action**: SKIP per budget constraints

## Items Accepted (proceed to implementation)

### 1. Improve MCP tool error response documentation
- **File**: `.claude/rules/mcp-tools.md`
- **Filter checks**:
  - ✓ Deduplication: Concept exists (lines 40-47) but needs clarification
  - ✓ Recurrence: PR #285 demonstrates inconsistency in error patterns
  - ✓ Actionability: Concrete guidance on domain-specific error keys
  - ✓ Budget: 131 + 3 lines = ~134 lines (under 200-line limit)

### 2. Document MCP migration pattern (dual-path declarations)
- **File**: `.claude/rules/mcp-tools.md`
- **Filter checks**:
  - ✓ Deduplication: Not documented; only implied in PR #285 commit message
  - ✓ Recurrence: Pattern demonstrated and intentional in PR #285; expected to recur
  - ✓ Actionability: Concrete guidance on backwards-compatibility migration
  - ✓ Budget: 131 + 20 lines = ~151 lines (under 200-line limit)

## Result

- **Items analyzed**: 5 (3 High, 2 Medium, 1 Low from report)
- **Items accepted**: 2
- **Items filtered**: 3
- **Minimum threshold (2 items)**: ✓ Met
- **Status**: Proceed to implementation
