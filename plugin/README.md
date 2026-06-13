# AICC — AI Coding Context (Claude Code plugin)

Generate, health-check, and incrementally maintain AI-facing project
documentation (`dev_docs/`), with enforced plan-first, mutual-review, and
git-safety gates.

The clone-form AICC framework asked you to paste an entry document and
trust the AI to follow rules. This plugin replaces that with mechanisms:
skills auto-trigger on intent, a SessionStart hook injects project doc
status with zero paste, and PreToolUse hooks actually gate commits and
block destructive git commands.

## Requirements

- Claude Code (hooks verified on 2.1.x) and `python3` (3.8+, stdlib only).

## Install

```bash
# from a local checkout
claude --plugin-dir /path/to/AI-Coding-Context/plugin

# or zip the plugin/ directory and use --plugin-url / the plugin manager
```

Optional: put `plugin/bin` on PATH for the `aicc-*` CLIs outside sessions.

## Skills

| skill | use when |
| --- | --- |
| `/aicc:init` | no `dev_docs/` yet — generate the initial AI coding context (plan-first, hard user gate before generation) |
| `/aicc:health-check` | assess existing docs: staleness, drift, score, routing |
| `/aicc:incremental-update` | code changed — sync the docs (commit-guided supported) |
| `/aicc:design-thinking` | complex/ambiguous task — 5-Why, multi-option, risk analysis |
| `/aicc:mutual-review` | adversarial second-AI review of an in-flight plan/code/doc you just generated |
| `/aicc:plan-review` | review one already-landed plan file before implementation — addressable + re-enterable; sets `review_status` (commit gate blocks a `plans/done/` plan that skipped it) |
| `/aicc:adr` | record an architecture decision |
| `/aicc:doc-fallacy-fix` | docs contradict the code — verify and correct everywhere |
| `/aicc:systematic-review` | multi-round audit of the whole doc set |
| `/aicc:doc-reading-habit` | load docs on demand by frontmatter summary |
| `/aicc:knowledge-reuse` | capture/reuse knowledge, optionally cross-project |

Dev-time subagents: architecture-analyst, product-manager, api-designer,
database-designer.

## Enforcement (hooks)

| hook | event | effect |
| --- | --- | --- |
| session_inject | SessionStart | injects skill catalog + `dev_docs/` health snapshot — no paste needed |
| pre_commit_gate | PreToolUse (git commit) | validates changed `dev_docs/**/*.md` (frontmatter + main-doc contract), and blocks a `plans/done/` plan whose `review_status` is not `reviewed`/`skipped(+reason)`; doc gate `aicc.git_safety.commit_gate` + plan gate `aicc.planReview.gate`, default `ask`, set `deny` to hard-block |
| dangerous_git_guard | PreToolUse (git) | denies force push, hard reset, history rewrite, protected-branch commits |
| post_tool_audit | PostToolUse | appends minimal JSONL telemetry under the plugin data dir |

## Settings

Defaults ship in the plugin; override per project in `.claude/settings.json`:

```json
{
  "aicc": {
    "documentLanguage": "en",
    "enableMutualReview": true,
    "enforceDesignThinking": false,
    "git_safety": {
      "mode": "standard",
      "commit_gate": "ask",
      "protected_branches": ["main", "master", "production"]
    }
  }
}
```

`git_safety.mode`: `standard` | `strict` (asks on commit/push too) |
`permissive` (disarms the guard). `commit_gate`: `ask` | `deny` | `off`.
If you work directly on `main`/`master`, trim `protected_branches`.

## CLI tools (`bin/`)

`aicc-scan` (project inventory + complexity tier), `aicc-doc-health`
(scored health check), `aicc-summary-validate` (frontmatter validator),
`aicc-contract-check` (main-doc sections), `aicc-git-safety` (red/yellow/
green classifier), `aicc-complexity` (raw size metrics), `aicc-knowledge`
(knowledge base, optional shared repo).

## Codex package

`python3 build/build.py --codex` emits `dist/codex/`: the same skills,
flat-named `aicc-*`, plus an `AGENTS.md` index and a self-contained
`.codex/` hooks bundle. Codex (>= v0.117) runs lifecycle hooks with a
stdin/stdout contract matching Claude Code's, so the commit gate and
git-safety guard enforce there too — install `.codex/` at your repo root
and trust it via `/hooks` (same hook scripts as the plugin, not a
reimplementation). Codex hook interception has gaps on some shell paths,
so the `bin/aicc-*` validators remain the advisory backstop.

## Migrating from the clone form

See [MIGRATION.md](MIGRATION.md).

## Development

`python3 build/build.py` = source-dir integrity check + lint (English-only,
description style, body budgets, reference depth, settings consumption) +
provenance manifest. Convergence decisions and deviations are logged in
[BUILD_NOTES.md](BUILD_NOTES.md).
