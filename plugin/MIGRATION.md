# Migrating from the AICC clone form to the plugin

The clone form (master/dev branches: `core/`, `workflows/`, `templates/`,
`agents/`, `tools/`, `guides/` copied or referenced in your repo, entry via
pasting `AI_ENTRY_POINT.md`) keeps working. The plugin replaces its manual
steps with automatic ones.

## What replaces what

| clone-form habit | plugin replacement |
| --- | --- |
| paste `AI_ENTRY_POINT.md` each session | nothing — SessionStart hook injects skills + doc health automatically |
| follow `workflows/path_a_first_generation.md` | `/aicc:init` (triggers on "set up AI docs" intent) |
| follow `path_b_health_check.md` | `/aicc:health-check` |
| follow `path_c` / commit-guided / git-safety docs | `/aicc:incremental-update` + enforcing hooks |
| `@think` via `path_d` + persona files | `/aicc:design-thinking` (`perspective` parameter) |
| `@review` via review-workflow + reviewer roles | `/aicc:mutual-review` (bundled reviewer subagents) |
| `python tools/py/doc_health_checker.py ...` | `aicc-doc-health` (and the other `bin/aicc-*` CLIs) |
| `config/user_config.md` | `aicc` block in `.claude/settings.json` |
| git safety as a rules document | `dangerous_git_guard` hook — denied, not advised |
| commit hygiene by convention | `pre_commit_gate` hook (`ask` by default, `deny` when you trust it) |

## Migration steps

1. **Install the plugin** (see README). Open a session in your project —
   you should see the AICC context injected without pasting anything.
2. **Keep `dev_docs/` as is.** The doc format (frontmatter summaries, main
   doc, AI_RULES) is unchanged; existing docs validate as before. Run
   `/aicc:health-check` once to see where you stand.
3. **Move config**: translate your `config/user_config.md` choices into the
   `aicc` settings block (README "Settings"). Keys the plugin no longer
   uses can be dropped — the plugin only reads what its skills/hooks
   consume.
4. **Remove the framework copy** (optional, recommended): if your repo
   vendored the framework (an `ai_coding_context/` dir or similar), delete
   it once the plugin covers your workflows — your `dev_docs/` does not
   depend on it. Keep it if other tooling still points there.
5. **Calibrate the gates**: defaults are `commit_gate: "ask"` and
   `mode: "standard"`. After a week of clean asks, set
   `commit_gate: "deny"` for real enforcement. If you commit straight to
   `main`/`master`, edit `protected_branches` first or the guard will deny
   those commits.

## Differences worth knowing

- **Plugin docs are English-first**; generated doc language follows
  `aicc.documentLanguage` — set it to your previous `documentLanguage`.
- **Old quantified claims are gone**: the plugin makes no efficiency
  percentage claims; telemetry (`post_tool_audit`) exists to ground such
  claims in data eventually.
- **Complexity dashboard is not shipped** (its data layer was a mock);
  `aicc-complexity` gives raw metrics instead.
- **The main-doc contract is the plugin's English contract v1** (seven
  required sections, see `scripts/py/contract_check.py`). Docs generated
  by the clone form with different section names will fail
  `aicc-contract-check` until their main doc adopts the required headings
  (or you keep the gate at `ask` and accept the warning).
