---
name: dev10x:work-plan
description: >
  View and customize work plan templates for the dev10x:work-on
  orchestrator. List available work types, inspect plan steps,
  edit templates through a guided flow, or reset to defaults.
user-invocable: true
invocation-name: dev10x:work-plan
allowed-tools:
  - Read(~/.claude/projects/**/memory/work-plans.yaml)
  - Write(~/.claude/projects/**/memory/work-plans.yaml)
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
---

# dev10x:work-plan — Work Plan Template Manager

## Overview

This skill manages the work plan templates used by `dev10x:work-on`
Phase 3. It provides a guided interface for viewing and customizing
plans so users never need to edit raw YAML.

Plans are stored per project at:
```
~/.claude/projects/<project>/memory/work-plans.yaml
```

The canonical schema with all defaults lives at:
```
${CLAUDE_PLUGIN_ROOT}/skills/work-plan/references/work-plans-schema.yaml
```

## Orchestration

**REQUIRED: Create a task at invocation.** Execute at startup:

1. `TaskCreate(subject="Manage work plans", activeForm="Managing plans")`

Mark completed when done: `TaskUpdate(taskId, status="completed")`

## Subcommands

Parse the arguments to determine the subcommand:

| Arguments | Subcommand | Action |
|-----------|-----------|--------|
| (none) or `list` | List | Show all work types with plan summaries |
| `view <type>` | View | Show full plan template for a work type |
| `edit <type>` | Edit | Guided editing of a plan template |
| `reset [<type>]` | Reset | Reset overrides to defaults |

If arguments don't match any subcommand, treat as a `list`.

---

## Subcommand: List

Show a summary of all available work types and their plan templates.

**Steps:**

1. Read the schema file at
   `${CLAUDE_PLUGIN_ROOT}/skills/work-plan/references/work-plans-schema.yaml`
2. Read the user's plan file at
   `~/.claude/projects/<project>/memory/work-plans.yaml`
   (may not exist — that's fine, use defaults only)
3. For each work type in defaults, display:

```
## Work Plan Templates

| Type | Steps | Customized? | Description |
|------|-------|-------------|-------------|
| feature | 10 | No | New functionality or enhancement |
| bugfix | 10 | Yes | Broken behavior with reproduction |
| pr-continuation | 7 | No | Existing PR with review comments |
| local-only | 9 | No | No ticket, decision to PR deferred |
| investigation | 4 | No | Understanding, not fixing |
```

4. Note which types have overrides in the user's plan file
5. Mention: "Use `/dev10x:work-plan view <type>` to inspect a
   plan, or `/dev10x:work-plan edit <type>` to customize."

---

## Subcommand: View

Show the full plan template for a specific work type.

**Steps:**

1. Read both the schema file and user's plan file
2. Resolve the plan for the requested type:
   - Check user overrides first
   - Fall back to defaults
3. Display the plan as a numbered tree:

```
## Feature Plan Template

**Prompt:** Use when a ticket describes new functionality...

| # | Type | Step | Skills | Children |
|---|------|------|--------|----------|
| 1 | detailed | Set up workspace | dev10x:ticket-branch | — |
| 2 | detailed | Draft Job Story | dev10x:jtbd | — |
| 3 | epic | Design implementation approach | — | 3 children |
|   |   | ├─ Read relevant code | — | |
|   |   | ├─ Identify affected components | — | |
|   |   | └─ Propose approach | — | |
| 4 | epic | Implement changes | — | — |
| ... | | | | |

**Source:** defaults (no user override)
```

4. If an override exists, show both the override and the default
   so the user can compare.

---

## Subcommand: Edit

Guided editing of a plan template. This is the core value — users
describe what they want to change in natural language rather than
editing YAML.

**Steps:**

1. Show the current plan (same as View)
2. **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
   Options:
   - **Add step** — Insert a new step at a specific position
   - **Remove step** — Remove a step by number
   - **Reorder steps** — Move a step to a different position
   - **Edit step** — Change a step's subject, type, prompt, or skills

3. Based on the user's choice, gather details:

   **Add step:**
   - Ask: position (before/after which step), subject, type
     (detailed/epic), skills (optional), prompt (optional)
   - If epic: ask if it should have pre-templated children

   **Remove step:**
   - Confirm which step to remove (by number)
   - Warn if removing a step that other skills depend on

   **Reorder steps:**
   - Ask which step to move and where

   **Edit step:**
   - Show the current step details
   - Ask what to change

4. Preview the modified plan as a numbered tree
5. **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
   Options:
   - **Save** — Write the override to the user's plan file
   - **Continue editing** — Make more changes (loop back to step 2)
   - **Discard** — Abandon changes

6. If Save:
   - Read the user's plan file (create if absent)
   - Add/update the override entry for this work type
   - Set `persist: true` and `added: <today's date>`
   - Write the updated YAML file

**Override format in user's plan file:**

```yaml
overrides:
  - work_type: feature
    persist: true
    added: 2026-03-11
    steps:
      - subject: Set up workspace
        type: detailed
        skills: [dev10x:ticket-branch]
      # ... full step list
```

---

## Subcommand: Reset

Reset a work type's override to the default template.

**Steps:**

1. Read the user's plan file
2. If no overrides exist, inform the user: "No customizations
   found. All plans use defaults."
3. If `<type>` is specified:
   - Check if an override exists for that type
   - **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
     Options:
     - **Reset** — Remove the override for this work type
     - **Cancel** — Keep the current override
   - If Reset: remove the override entry and write the file
4. If no `<type>` specified:
   - Show all overrides
   - **REQUIRED: Call `AskUserQuestion`** (do NOT use plain text).
     Options:
     - **Reset all** — Remove all overrides
     - **Select specific** — Choose which types to reset
     - **Cancel** — Keep all overrides

---

## Plan File Management

**File location:** `~/.claude/projects/<project>/memory/work-plans.yaml`

**Creating the file:** Only create the file when the user saves
their first customization. The file starts with the full defaults
section copied from the schema, plus an empty overrides list.

**Schema reference:** The canonical schema with all defaults and
field documentation lives at:
`${CLAUDE_PLUGIN_ROOT}/skills/work-plan/references/work-plans-schema.yaml`

**Resolution order** (used by both this skill and `dev10x:work-on`):
1. User overrides with `persist: false` — use once, then remove
2. User overrides with `persist: true` — reuse across sessions
3. Defaults from user's plan file
4. Defaults from the schema reference file (hardcoded fallback)

---

## Integration with work-on

The `dev10x:work-on` skill loads plans during Phase 3 using the
same resolution order above. When presenting the plan to the
supervisor, it notes: "Customize plans with `/dev10x:work-plan`."

If a user asks to customize their plan during a `work-on` session,
the orchestrator can delegate to this skill mid-flight and then
reload the updated plan.

---

## Examples

### Example 1: List plans

**User:** `/dev10x:work-plan`

Shows the summary table of all 5 work types with step counts
and whether each has been customized.

### Example 2: View a specific plan

**User:** `/dev10x:work-plan view bugfix`

Shows the full bugfix plan template with all steps, children,
prompts, and skill delegations in a readable tree format.

### Example 3: Add a step to the feature plan

**User:** `/dev10x:work-plan edit feature`

1. Shows current feature plan (10 steps)
2. User selects "Add step"
3. User says: "Add a 'Run e2e tests' step after Verify"
4. Skill creates the step: `{subject: "Run e2e tests", type: detailed, skills: [tt:e2e-debug]}`
5. Shows preview with 11 steps
6. User selects "Save"
7. Writes override to plan file

### Example 4: Reset all customizations

**User:** `/dev10x:work-plan reset`

Shows all overrides, confirms reset, removes them from the file.
