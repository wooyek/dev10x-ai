# Dev10x Claude Plugin

Stop babysitting your AI. Start supervising it.

---

A Claude Code plugin that gives your AI pre-approved workflows,
self-correcting guardrails, and a complete scope-to-merge pipeline —
so you can supervise in 5-minute windows instead of hovering over
every command.

## The problem with AI coding assistants

**Permission friction kills autonomy.** Every ad-hoc bash command
triggers a permission prompt. Every prompt pulls you back to the
terminal. Your AI can write code, but it can't ship a commit
without asking you 15 times.

**Progress is invisible.** You walk away for 10 minutes and come
back to a wall of terminal output. Or a stalled session waiting
for approval. No way to tell at a glance if things are on track.

**Attention doesn't batch.** You want to give 5 minutes of
direction, check in during coffee, and move on. Instead you're
hovering — approving every shell command, every file write, every
git operation.

## How dev10x solves this

### Pre-approved workflows, not ad-hoc scripts

40 skills encapsulate complete dev workflows as slash commands.
`/commit` handles gitmoji, ticket reference, and benefit-focused
title — all through pre-approved tool calls that never trigger
permission prompts.

When Claude uses `/dev10x:gh-pr-create` instead of raw `gh` commands, every
step matches an allow rule. Zero interruptions.

### Guardrails that teach, not just block

8 hooks intercept dangerous patterns *before* they execute — and
redirect the AI toward the approved path:

- **`detect-and-chaining`** catches `mkdir && script.sh` that
  breaks allow rules → teaches separate calls
- **`block-python3-inline`** blocks `python3 -c "..."` →
  teaches `uv run --script`
- **`validate-commit-jtbd`** blocks "Add retry logic" → teaches
  "Enable automatic retry on failure"

The hooks carry educational messages. The AI learns from each
block. By mid-session, it stops triggering them entirely.

### A complete scope-to-merge pipeline

Every step produces a precise, artifact-quality message — readable
by the next agent in the chain or a human reviewer glancing at
their phone:

| Step | Skill | Output |
|------|-------|--------|
| Scope | `dev10x:ticket-scope` | Architecture research, ticket update |
| Branch | `dev10x:work-on` | Named branch, gathered context |
| Commit | `dev10x:git-commit` | Atomic commits with benefit-focused titles |
| Groom | `dev10x:git-groom` | Clean history, no fixup commits |
| PR | `dev10x:gh-pr-create` | Job Story description, ticket links |
| Monitor | `dev10x:gh-pr-monitor` | Background CI + review watch |
| Respond | `dev10x:gh-pr-respond` | Batched review responses, minimal noise |
| Review | `dev10x:gh-pr-review` | Domain-routed review across 5 agents |

No step produces wall-of-text. Each output is sized for a Slack
preview, a PR comment, or a task list glance.

### Learning loops that calibrate to you

Code review findings, commit conventions, and PR feedback flow
back into CLAUDE.md rules and session memory. The more you
course-correct, the less you need to.

After a few sessions, the AI produces commits, PR descriptions,
and code that look like *you* wrote them — because it learned your
preferences, not generic defaults.

## Supervise, don't babysit

The plugin is designed around batched attention windows:

1. **Scope** — point at a ticket, let the AI research and plan
2. **Walk away** — skills and hooks keep the pipeline moving
3. **Check in** — task list shows where the session stands
4. **Course-correct** — give 2 minutes of guidance, walk away again
5. **Ship** — come back to a groomed branch, clean PR, ready for
   review

When you pop in during a coffee break, you see a task list — not
a wall of terminal output. Each artifact (commit message, PR body,
review comment) is concise enough to evaluate in seconds.

## Skill families

| Family | Skills | What it automates |
|--------|--------|-------------------|
| **Git** | `git-commit`, `git-commit-split`, `git-fixup`, `git-groom`, `git-promote`, `git-worktree`, `git`, `git-alias-setup` | Atomic commits, clean history, workspace isolation |
| **PR** | `gh-pr-create`, `gh-pr-review`, `gh-pr-respond`, `gh-pr-monitor`, `gh-pr-triage`, `gh-pr-fixup`, `gh-pr-request-review`, `gh-pr-bookmark`, `gh-context` | Full PR lifecycle, domain-routed review |
| **Tickets** | `ticket-create`, `ticket-branch`, `ticket-scope`, `ticket-jtbd`, `work-on`, `linear` | Issue tracker integration, ticket scoping |
| **Park** | `park`, `park-todo`, `park-remind`, `park-discover` | Deferred work parking |
| **Scoping** | `scope`, `jtbd`, `adr` | Architecture decisions, Job Story format |
| **QA** | `qa-scope`, `qa-self`, `playwright` | Test planning, self-review, browser testing |
| **Session** | `session-tasks`, `wrap-up` | In-session work tracking |
| **Tooling** | `py-uv`, `slack` | Python packaging, Slack notifications |
| **Meta** | `skill-create`, `skill-audit`, `skill-index` | Create, audit, and discover skills |

All skills use the `dev10x:` prefix — type `/dev10x:git-commit` in the Claude
Code CLI to run it. Run `/dev10x:skill-index` for the full reference.

## Installation

```
/plugin marketplace add WooYek/Dev10x-AI
/plugin install Dev10x@WooYek
```

[Full installation guide →](docs/installation.md) — prerequisites,
dependencies, manual clone, develop branch, and verification.

## Codex Skills

A Codex-native pack is available in `codex-skills/` for use outside
Claude Code.

[Codex skills guide →](docs/codex.md)

## Community

The [Dev10x community on Skool](https://www.skool.com/dev10x-1892)
is where plugin users get assistance, request features, and share
workflows. If you already have access to this repository, you do not
need to join Skool — it is a support and discussion hub, not a
gatekeeper for repo access.

## Development

[Development guide →](docs/development.md)
