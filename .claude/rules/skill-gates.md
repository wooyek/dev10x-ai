# Skill Decision Gates

Pattern for defining blocking decision points in skills.

## What is a Decision Gate?

A decision gate is a user choice that **affects execution flow** and
**requires blocking** until the user responds. Gates differ from information
questions (which can use plain text):

| Type | Example | Tool Required |
|------|---------|---------|
| Decision Gate | "Resolve thread or leave open?" | AskUserQuestion ✓ |
| Information Question | "What's the PR title?" | Plain text OK |

## Marking Decision Gates

In SKILL.md, mark every decision gate with an explicit enforcement marker:

```markdown
**REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
This blocks execution until the user responds. Options:
- Option 1
- Option 2
```

This replaces soft guidance ("Use AskUserQuestion") which allows agents to
substitute plain text instead.

## Why This Matters

Plain text questions:
- Don't block execution (agents can auto-proceed)
- Lack structured options (no clickable buttons)
- Break the skill's documented orchestration contract

Tool calls ensure:
- User response is mandatory
- Options are presented clearly
- Skill flow is respected

## Evaluation Assertions

When a skill has decision gates, include assertions in `evals/evals.json`:

1. **Gate enforcement** — Verify AskUserQuestion tool calls (not text)
2. **Option correctness** — Check documented options match gate
3. **No auto-resolve** — Confirm user interaction is required
4. **Task tracking** — Validate orchestration state updates

Example signal for detection:
```json
{
  "check": "tool_called",
  "tool": "AskUserQuestion",
  "assertion": "gate1_uses_tool",
  "signal": "AskUserQuestion is called at thread resolution point"
}
```

## When Not to Use AskUserQuestion

Skip tool calls for:
- Clarifying information (e.g., filename, description)
- Confirmations that don't affect workflow
- Optional preferences (user can proceed with defaults)

Reserve gates for choices that **change execution path**.
