# Skill Naming Convention

Rules for naming skill directories and invocation names in
this plugin.

## Directory Names

Use the plain feature name. No `dx-` prefix on directories.

**Good:**
```
skills/git-worktree/
skills/skill-audit/
skills/tasks-defer/
skills/linear/
```

**Bad:**
```
skills/dx-git-worktree/
skills/dx-skill-audit/
```

*Why?* The filesystem already scopes skills to this plugin's
`skills/` directory. Adding a redundant prefix clutters tab
completion and directory listings.

## Invocation Name (SKILL.md `name:` field)

Use the `dx:<feature-name>` format in the SKILL.md front matter.

**Good:**
```yaml
name: dx:git-worktree
name: dx:skill-audit
name: dx:defer
```

**Bad:**
```yaml
name: git-worktree
name: skill-audit
```

*Why?* The `dx:` namespace prefix identifies this plugin's skills
at invocation time. Without it, skills could collide with skills
from other plugins or built-in commands.

## Abbreviated Names

The `tasks-*` family uses shortened invocation names for ergonomics:

| Directory        | Invocation name |
|------------------|-----------------|
| `tasks/`         | `dx:tasks`      |
| `tasks-defer/`   | `dx:defer`      |
| `tasks-todo/`    | `dx:todo`       |
| `tasks-remind/`  | `dx:remind`     |
| `tasks-wrap-up/` | `dx:wrap-up`    |
| `tasks-discover/`| `dx:discover`   |

Other skills use the full directory name: `dx:git-worktree`,
`dx:skill-audit`, `dx:skill-create`.

## Sub-Namespace Families

Some skill families use a `dx:<family>:<skill>` double-colon format
to group related skills by domain:

| Directory             | Invocation name         |
|-----------------------|-------------------------|
| `ticket-from-commit/` | `dx:ticket:from-commit` |

Use the double-colon format when a skill belongs to a domain family
where future members are anticipated (e.g., `dx:ticket:create`,
`dx:ticket:branch`). If a family has only one member and no planned
additions, prefer the single-colon format for consistency.

## Evolving Patterns

When a PR introduces a new naming format variant (new separator,
prefix, or sub-namespace), `skill-naming.md` must be updated in
the same PR. Reviewers should flag the absence as WARNING.

Skills with vague descriptions get skipped by the router — the
`description:` field must explain when to trigger the skill.

## Rationale Summary

- **Directory**: plain name → clean filesystem, no redundant prefix
- **Invocation**: `dx:` prefix → namespace isolation at call time
- **Abbreviations**: allowed for frequently-used skill families
- **Sub-namespaces**: `dx:<family>:<skill>` for grouped families
