---
name: dx:work-on
description: >
  Start work on any input — ticket URL, PR link, Slack thread,
  Sentry issue, or free text. Classifies inputs, gathers context
  in parallel, builds a supervisor-approved task list, and executes
  adaptively with pause/resume support.
user-invocable: true
invocation-name: dx:work-on
allowed-tools:
  - Bash(~/.claude/skills/gh/scripts/*:*)
  - Bash(~/.claude/skills/jira/scripts/*:*)
---

# dx:work-on — Adaptive Work Orchestrator

## Overview

This skill turns any combination of inputs into a structured,
supervisor-approved work plan. It runs in four phases:

1. **Parse & Classify** — identify what each input is
2. **Gather** — fetch context from all sources in parallel
3. **Plan** — build a task list for supervisor approval
4. **Execute** — work through tasks, expanding epics on demand

The supervisor sees progress via `TaskList`, can approve/edit
the plan, and can pause at any point with `dx:wrap-up`.

## Prerequisites

| Capability | Required for | Tool |
|------------|-------------|------|
| GitHub CLI | GitHub issues, PRs | `gh` CLI |
| Linear MCP | Linear tickets | `mcp__claude_ai_Linear__*` |
| JIRA | JIRA tickets | `dx:jira` plugin + `JIRA_TENANT` env var + keyring |
| Sentry MCP | Sentry issues | `mcp__sentry__*` |
| Slack MCP | Slack threads | `mcp__claude_ai_Slack__*` |

Not all are required — only those matching the input types.

## When to Use

- User provides any combination of: ticket URL/ID, PR link, Slack
  thread, Sentry link, or free text description
- User wants to start structured work with progress tracking
- User wants comprehensive context before starting

---

## Phase 1: Parse & Classify

Accept the user's arguments as a space-separated list. Each
argument is classified independently:

| Pattern | Type | Action |
|---------|------|--------|
| `https://github.com/.../issues/N` | `github-issue` | Extract repo + issue number |
| `https://github.com/.../pull/N` | `github-pr` | Extract repo + PR number |
| `https://linear.app/.../issue/XXX-N/...` | `linear-ticket` | Extract ticket ID (e.g., `TEAM-133`) |
| `https://.*slack.com/archives/C.../p...` | `slack-thread` | Store channel + timestamp |
| `https://sentry.io/.../issues/N` | `sentry-issue` | Extract issue ID |
| `https://*.sentry.io/issues/N` | `sentry-issue` | Extract issue ID |
| `https://...atlassian.net/browse/XX-N` | `jira-ticket` | Extract ticket ID |
| `GH-N` | `github-issue` | Route to `detect-tracker.sh` |
| `TEAM-N` (Linear prefix) | `linear-ticket` | Route to `detect-tracker.sh` |
| `TT-N` | `jira-ticket` | Route to `detect-tracker.sh` |
| `#N` (bare number) | `github-pr` | Resolve against current repo |
| Anything else | `note` | Store as free-text context |

For ticket IDs, run the tracker detector (from `dx:gh` skill):
```bash
~/.claude/skills/gh/scripts/detect-tracker.sh "$TICKET_ID"
```
Parse `TRACKER`, `TICKET_NUMBER`, and `FIXES_URL` from output.

Each classified input becomes a **source** entry with its type and
extracted identifiers. Collect all sources into a list for Phase 2.

---

## Phase 2: Gather (Quick & Parallel)

Fetch context from all sources **in parallel** — no supervisor
interaction needed. Use parallel tool calls or Agent subagents.

### Fetch Dispatch

| Source type | Fetch method |
|-------------|-------------|
| `github-issue` | `dx:gh` script: `gh-issue-get.sh "$NUMBER" "$REPO"` |
| `github-pr` | `gh pr view $NUMBER --repo $REPO --json title,body,headRefName,state,mergedAt,reviews` |
| `linear-ticket` | `mcp__claude_ai_Linear__get_issue(issueId: "$ID")` — extract title, body, parent, relations, comments |
| `jira-ticket` | `dx:jira` script: `jira-get.sh "$ID"` |
| `slack-thread` | `mcp__claude_ai_Slack__slack_read_thread(channelId, threadTs)` |
| `sentry-issue` | `mcp__sentry__get_issue_details(issueId)` — extract error, frequency, stack trace |
| `note` | No fetch needed — pass through |

### Cross-Reference Expansion (One Level)

After the initial fetch, scan all gathered text for references
to other sources. Add them to the sources list and fetch:

- **PR body** mentions `Fixes: GH-N` or `Fixes: TEAM-N` → fetch that ticket
- **Ticket body** contains Sentry URL → fetch that Sentry issue
- **Ticket body** mentions PR `#N` or branch name → fetch that PR
- **Linear ticket** has parent or relations → fetch related tickets
- **Ticket comments** contain any of the above patterns → fetch

Do NOT expand beyond one level — keep the gathering phase fast.

### Output: Context Summary

Present a structured summary of everything gathered:

```markdown
## Context Summary

### Sources (N gathered)
- [github-issue] GH-15: Title here (OPEN)
- [slack-thread] #channel-name: 5 messages
- [sentry-issue] #12345: ErrorType — 145 events in 7 days
- [note] "check the retry logic"

### Cross-References Found
- [sentry-issue] #67890 (from ticket body)
- [github-pr] #42: PR title (merged)

### Key Details
[Brief synthesis: what the work is about, who reported it,
severity if applicable, related context from Slack/Sentry]
```

---

## Phase 3: Plan (Lightweight Steps)

Build a **high-level task list** using `TaskCreate`. The plan is
adapted based on what was gathered — not a fixed template.

### Step Types

- **Detailed** — small, immediately executable (2-5 min).
  Created with `metadata: {"type": "detailed"}`.
- **Epic** — placeholder for a phase expanded when reached.
  Created with `metadata: {"type": "epic"}`. Description says
  what the phase accomplishes, not how.

### Generating the Plan

Examine the gathered context and construct a task list. Use these
heuristics to decide which tasks to include:

**Always include (if a ticket was found):**
- Set up workspace (branch or worktree) — detailed
- Draft Job Story — detailed

**Include based on context:**

| Context signal | Tasks to add |
|---------------|-------------|
| Ticket with implementation work | Design approach (epic), Implement (epic), Verify (epic) |
| Sentry issue found | Reproduce issue (detailed), Investigate root cause (epic) |
| PR already exists | Fetch PR context (detailed), Address review comments (epic) |
| Multiple related tickets | Synthesize requirements (detailed) |
| Slack thread with discussion | Summarize key decisions (detailed) |

**Always include at the end:**
- Create PR & ensure CI passes — epic
- Self-review & request human review — epic

### Example Plans

**Feature from ticket:**
```
1. [detailed] Set up workspace (branch, worktree)
2. [detailed] Draft Job Story
3. [epic]     Design implementation approach
4. [epic]     Implement changes
5. [epic]     Verify (tests, lint)
6. [epic]     Create PR & ensure CI passes
7. [epic]     Self-review & request human review
```

**Bug fix from Sentry + ticket:**
```
1. [detailed] Set up workspace
2. [detailed] Reproduce the issue locally
3. [epic]     Investigate root cause
4. [epic]     Implement fix
5. [epic]     Verify fix (tests, regression)
6. [epic]     Create PR & ensure CI passes
```

**PR continuation:**
```
1. [detailed] Fetch PR and review context
2. [epic]     Address review comments
3. [epic]     Verify changes pass CI
4. [epic]     Request re-review
```

**Local-only work (no ticket, no PR):**
```
1. [detailed] Summarize the work from gathered context
2. [epic]     Implement changes
3. [epic]     Verify
4. [detailed] Decide: create ticket, create PR, or done
```

### Supervisor Approval Gate

Present the plan as a numbered list. Then use `AskUserQuestion`:

- **Approve (Recommended)** — start execution
- **Edit** — describe what to change (add/remove/reorder steps)

After approval, set task dependencies where appropriate (use
`TaskUpdate` with `addBlockedBy`). Mark the first task as
`in_progress` and begin Phase 4.

---

## Phase 4: Execute (Adaptive)

Work through the approved task list. Update task status via
`TaskUpdate` as work progresses.

### Executing Detailed Tasks

Run the task directly. Common detailed tasks delegate to skills:

| Task | Delegated to |
|------|-------------|
| Set up workspace (branch) | `dx:ticket-branch` skill |
| Set up workspace (worktree) | `dx:git-worktree` skill |
| Draft Job Story | `dx:jtbd` skill (attended mode) |
| Update ticket status | Linear MCP (see references/team-info.md) |
| Fetch PR context | `gh pr view` + `gh pr diff` |
| Create PR | `dx:gh-pr-create` skill |
| Monitor CI | `dx:gh-pr-monitor` skill |

After completing a detailed task, mark it `completed` via
`TaskUpdate` and move to the next task.

### Expanding Epic Tasks

When reaching an epic task:

1. **Read the epic description** and the gathered context
2. **Generate sub-tasks** — break the epic into detailed steps.
   This may involve:
   - Reading code to understand scope
   - `AskUserQuestion` for A/B decisions (e.g., "approach X
     vs approach Y?")
   - Follow-up information gathering
3. **Present sub-tasks** to the supervisor for approval
4. **Check for parallelism** — if sub-tasks are independent,
   ask the supervisor before launching parallel agents
5. **Execute sub-tasks**, marking each completed as they finish
6. **Mark the epic completed** when all sub-tasks are done

### Parallelism Policy

| Phase | Parallelism | Approval needed? |
|-------|------------|-----------------|
| Phase 2 (Gather) | Auto-parallel | No |
| Phase 4 (detailed tasks) | Sequential | No |
| Phase 4 (epic sub-tasks) | Parallel if independent | Yes — ask supervisor |

When asking about parallelism, present which tasks would run
concurrently and why they're independent:

```
Tasks 4a and 4b are independent (different files, no shared state).
Run them in parallel?
- Yes, launch parallel agents (Recommended)
- No, run sequentially
```

### Skill Delegation During Execution

**Workspace setup:**
- If in main repo (`.git` is directory): offer "Work here" or
  "New worktree" via `AskUserQuestion`
- If in worktree (`.git` is file): offer "Work here" or
  "New worktree"
- For worktree path: compute branch name, invoke `dx:git-worktree`
  skill. Do NOT invoke `dx:ticket-branch` first — `dx:git-worktree`
  creates the branch internally; calling `dx:ticket-branch` first
  creates a duplicate branch in the main repo.
- For work-here path: delegate to `dx:ticket-branch` skill

**Job Story drafting:**
- MUST invoke `Skill(dx:jtbd)` explicitly — never draft inline
- Pass gathered context to avoid redundant API calls
- If approved, write back to the ticket:

| Tracker | Write-back |
|---------|-----------|
| GitHub | `gh issue comment` |
| Linear | Prepend to description via `save_issue` |
| JIRA | `jira-update.sh` |

**Ticket status update (Linear only):**
1. Get statuses: `list_issue_statuses(teamId)` from
   references/team-info.md
2. Find "In Progress" (type `started`)
3. Update: `save_issue(id, stateId)`
4. Skip if already "In Progress"; warn if "Done"/"Canceled"

---

## Pause/Resume

At any pause signal ("wrap up", "pause", "that's enough for
today", end-of-session):

1. Invoke `dx:wrap-up` — it reads `TaskList` and discovers all
   open tasks automatically
2. `dx:wrap-up` handles routing each open item (PR bookmark,
   TODO.md, Slack DM, etc.)
3. The task list itself serves as resume context — when the user
   resumes work, they can invoke `dx:discover` to find deferred
   items and `dx:tasks` to see the saved task list

No custom bookmarking needed — leverage existing `dx:wrap-up`
and `dx:defer` infrastructure.

---

## Important Notes

- Always verify ticket exists before creating a branch
- If ticket is "Done"/"Canceled" (Linear) or "closed" (GitHub),
  warn the user before proceeding
- Handle errors gracefully — if a fetch fails, continue with
  what was gathered and note the failure in the context summary
- Linear team UUID is in `references/team-info.md` (template)
- After completing work, use `dx:gh-pr-create` to create the PR
- Do not modify ticket description or add comments unless the
  user explicitly approves (e.g., Job Story write-back)

## Resources

### references/team-info.md

Linear team configuration template: UUID, status mappings,
branch naming, Sentry integration patterns.

---

## Examples

### Example 1: Single Ticket URL

**User:** `/dx:work-on https://github.com/org/repo/issues/15`

**Phase 1:** Classify → `github-issue`, repo=`org/repo`, number=15

**Phase 2:** Fetch issue. Body mentions Sentry URL → fetch Sentry
issue. Body mentions PR #42 → fetch PR. Produce context summary.

**Phase 3:** Build plan:
```
1. [detailed] Set up workspace
2. [detailed] Draft Job Story
3. [epic]     Design implementation approach
4. [epic]     Implement changes
5. [epic]     Verify
6. [epic]     Create PR & ensure CI passes
```
Supervisor approves.

**Phase 4:** Execute tasks 1-6, expanding epics as reached.

### Example 2: Multiple Inputs

**User:** `/dx:work-on TEAM-133 https://slack.com/archives/C123/p456 "check the retry logic"`

**Phase 1:** Classify →
- `linear-ticket` TEAM-133
- `slack-thread` C123/p456
- `note` "check the retry logic"

**Phase 2:** Fetch all three in parallel. Linear ticket links to
Sentry issue → fetch that too. Produce context summary with 4
sources.

**Phase 3:** Build plan (adapted — Sentry issue means
"Reproduce" task added):
```
1. [detailed] Set up workspace
2. [detailed] Reproduce the Sentry error locally
3. [detailed] Draft Job Story
4. [epic]     Investigate root cause
5. [epic]     Implement fix
6. [epic]     Verify fix
7. [epic]     Create PR & ensure CI passes
```

### Example 3: PR Continuation

**User:** `/dx:work-on https://github.com/org/repo/pull/42`

**Phase 1:** Classify → `github-pr`, number=42

**Phase 2:** Fetch PR. Body has `Fixes: GH-15` → fetch issue.
PR has 3 review comments → note them.

**Phase 3:** Build plan:
```
1. [detailed] Fetch review comments and understand feedback
2. [epic]     Address review comments
3. [epic]     Verify CI passes
4. [epic]     Request re-review
```

### Example 4: Mid-Workflow Pause

User is at task 4 of 7 and says "let's wrap up for today".

1. Skill detects pause signal
2. Invokes `dx:wrap-up`
3. `dx:wrap-up` reads `TaskList` — sees 3 pending tasks
4. Routes each via `dx:defer` (e.g., PR bookmark, TODO.md)
5. Session ends with bookmark saved

Next session: user runs `dx:discover` to find bookmarks and
resume where they left off.
