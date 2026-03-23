# Proposed Changes for PR #406 Lessons Learned Implementation

## Overview
2 items from the PR #406 lessons learned report pass the Value Filter. Both target `.claude/rules/skill-gates.md`.

## Change 1: Skill() Delegation Assertion Patterns

**Location**: `.claude/rules/skill-gates.md`, after line 69 (after AskUserQuestion example)

**Proposed Content**:

```markdown
### Assertion Patterns for Skill Delegation

When a skill has `**REQUIRED: Call Skill(...)**` enforcement markers, use
the same assertion pattern with the Skill() tool. See
`references/eval-schema.md` Example 2 for complete delegation assertion
structure:

```json
{
  "check": "tool_called",
  "tool": "Skill",
  "assertion": "fixup_uses_skill_tool",
  "signal": "Skill(Dev10x:gh-pr-fixup) is called"
}
```

Include negative signal assertions to detect regressions:
```json
{
  "type": "plain_text",
  "assertion": "no_inline_fixup_delegation",
  "signal": "No inline text-based delegation before Skill() call"
}
```
```

**Rationale**: PR #404 introduced 5+ skill delegations with `**REQUIRED: Call Skill(...)**` markers. eval-schema.md now documents Example 2 (Skill() assertions), but skill-gates.md only covers AskUserQuestion. This creates a gap where skill authors adding delegation markers have no reference in skill-gates.md.

**Lines Added**: ~15

---

## Change 2: Anti-Pattern Signals Documentation

**Location**: `.claude/rules/skill-gates.md`, after Change 1

**Proposed Content**:

```markdown
### Anti-Pattern Signals

Use negative signals (`✗`) to catch enforcement violations:

- `✗ no-inline-*`: Skill not invoked via plain-text delegation ("Call the fixup skill")
- `✗ gate*-no-plain-text`: AskUserQuestion not replaced with inline question ("Do you want to proceed?")
- `✗ no-auto-*`: State not auto-resolved without user confirmation
- `✗ *-silent-defaults`: No defaults silently accepted instead of requiring user choice

Negative signals are **regression detection checks** — they ensure agents
don't fall back to text-based delegation or auto-progression when tool
calls are required. Every assertion pattern should include both positive
signal (tool is called) and negative signal (no text fallback).
```

**Rationale**: PR #406 introduces negative signals in eval-schema.md (lines 84-92) as a regression-prevention strategy. However, skill-gates.md (the authoritative enforcement pattern guide) doesn't explain when/how to use negative signals. This guidance helps skill authors and reviewers understand the dual-signal pattern.

**Lines Added**: ~10

---

## Impact

- **File**: `.claude/rules/skill-gates.md` (86 lines → ~111 lines)
- **Budget**: 111 / 200 line limit ✓
- **Breaking Changes**: None (additive only)
- **Cross-References**: Links eval-schema.md for complete examples

---

## Value Filter Summary

| Criterion | Item 1 | Item 2 |
|-----------|--------|--------|
| Deduplication | ✓ PASS (Skill() not documented) | ✓ PASS (no signal guidance) |
| Recurrence | ✓ PASS (5+ skills, pattern recurs) | ✓ PASS (foundational for future) |
| Actionability | ✓ PASS (concrete examples) | ✓ PASS (concrete patterns) |
| Budget | ✓ PASS (101 lines) | ✓ PASS (96 lines) |
| **Decision** | **PASS** | **PASS** |

Minimum threshold (2 items) met.
