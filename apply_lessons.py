#!/usr/bin/env python3
"""Apply lessons learned from PR #737 analysis."""

import re
import sys

def apply_h2_skill_orchestration_format():
    """Add Mixed-Tool Sequences section to skill-orchestration-format.md"""
    filepath = '.claude/rules/skill-orchestration-format.md'

    with open(filepath, 'r') as f:
        content = f.read()

    new_section = """## Mixed-Tool Sequences & Batching Optimization

When a skill runs validation checks or steps using **different tool types**
(GraphQL queries, shell scripts, git commands), agents may attempt to batch
commands of the same type for efficiency. This can cause checks to run out
of order or be skipped entirely if not explicitly forbidden.

**Pattern: Critical sequence that requires separate steps**

When checks use different tools and sequencing is critical:

1. Run Check 1 (GraphQL batch — may combine with other GraphQL checks)
2. **DO NOT batch Check 1b with Check 2** — Check 1b uses shell script
   and MUST complete after Check 1. Result visibility depends on
   prior GraphQL output; skipping causes silent failures.
3. After Check 1b completes, run Checks 2+ (remaining checks may batch by type)

**Enforcement signals:**
- Different tool types (GraphQL → shell → git) require sequential isolation
- Explicit "DO NOT batch" or "MUST run after" in step heading
- Rationale in parentheses explains why the constraint is real (not arbitrary)

**Why this matters:** Agents optimize batching automatically. Without
explicit "DO NOT" markers, skills mixing tool types silently skip
critical checks, causing hard-to-debug false passes (e.g., missing
review findings, undetected merge conflicts).

"""

    # Insert after "This distinction arises naturally..." section
    pattern = r'(This distinction arises naturally.*?\n\n)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r'\1' + new_section, content, count=1, flags=re.DOTALL)
        with open(filepath, 'w') as f:
            f.write(content)
        print("✓ H2: Updated skill-orchestration-format.md")
        return True
    else:
        print("✗ H2: Could not find insertion point")
        return False

def apply_m1_claude_md():
    """Expand External Tool Declarations section in CLAUDE.md"""
    filepath = 'CLAUDE.md'

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find "Missing declarations cause..." line and insert after it
    insert_idx = -1
    for i, line in enumerate(lines):
        if 'Missing declarations cause' in line:
            # Find the period at end of paragraph
            for j in range(i, min(i + 3, len(lines))):
                if lines[j].strip().endswith('.'):
                    insert_idx = j + 2  # After blank line
                    break
            break

    if insert_idx > 0:
        new_text = """**Validation sequences:** When a skill validation section runs checks using
different tools (e.g., GraphQL then shell scripts), use explicit enforcement
markers ("REQUIRED:", "DO NOT proceed") to prevent agents from batching checks
out of order. See `.claude/rules/skill-orchestration-format.md` § Mixed-Tool
Sequences for the pattern.

"""
        lines.insert(insert_idx, new_text)
        with open(filepath, 'w') as f:
            f.writelines(lines)
        print("✓ M1: Updated CLAUDE.md")
        return True
    else:
        print("✗ M1: Could not find insertion point")
        return False

def apply_m2_task_orchestration():
    """Add Pattern 2 to references/task-orchestration.md"""
    filepath = 'references/task-orchestration.md'

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find "## Pattern 1: Out-of-Order Execution" and insert before it
    insert_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('## Pattern 1: Out-of-Order Execution'):
            insert_idx = i
            break

    if insert_idx > 0:
        new_pattern = """## Pattern 2: Validation Check Ordering

When a skill performs multi-step validation (especially with mixed tool types),
document sequential dependencies explicitly. Skills with 5+ checks spanning
multiple tool types (GraphQL, shell, git) should annotate which checks may
batch together and which must run separately.

**Pattern: Sequential checks where order matters**

Document checks using different tool types with explicit ordering:

```markdown
### Step 3: Run validation checks

Checks 1-4 (GraphQL): may batch together
- Check 1: unresolved threads (GraphQL)
- Check 2: CI passing (gh pr checks)
- Check 3: not draft (GraphQL)
- Check 4: mergeable (GraphQL)

**Check 1b: REQUIRED as separate step after Check 1**
- Check 1b: no automated review comments (shell script)
- Reason: top-level comments invisible to GraphQL (GH-728)
- Do NOT batch with Check 2

Checks 5-7 (git): may batch together
- Check 5: clean working copy (git status)
- Check 6: no fixup commits (git log)
- Check 7: approved (gh pr view)
```

**Enforcement principle:** When tool types change (GraphQL → shell → git),
explicitly document which checks may batch and which must run separately.
Enforcement markers ("DO NOT batch", "MUST run after") prevent silent
skipping by optimization agents.

"""
        lines.insert(insert_idx, new_pattern)
        with open(filepath, 'w') as f:
            f.writelines(lines)
        print("✓ M2: Updated references/task-orchestration.md")
        return True
    else:
        print("✗ M2: Could not find insertion point")
        return False

if __name__ == '__main__':
    results = [
        apply_h2_skill_orchestration_format(),
        apply_m1_claude_md(),
        apply_m2_task_orchestration(),
    ]

    if all(results):
        print("\n✅ All changes applied successfully")
        sys.exit(0)
    else:
        print("\n⚠️ Some changes failed")
        sys.exit(1)
