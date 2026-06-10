# AICC Plugin — Build Notes

Convergence log for the plugin build (spec: `dev/plan/plugin/03-execution-spec.md`).
Everything dropped, deferred, or adapted from the dev-tree sources is recorded here.

## Confirmed hook schema (P0, Claude Code 2.1.170)

- Plugin hooks live in `hooks/hooks.json` under a top-level `"hooks"` key:
  `{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "..."}]}]}}`.
- The spec's draft used an `"if": "Bash(git commit*)"` field; that field does
  **not** exist in the installed hooks schema. `matcher` is a regex over the
  tool name only. Command-pattern filtering (git commit / dangerous git) is
  therefore done inside each hook script, which exits with no output for
  non-matching commands.
- `${CLAUDE_PLUGIN_ROOT}` expands in hook commands; hook scripts also fall
  back to a path-relative root so they are testable outside a session.
- Stdin event JSON carries `tool_name`, `tool_input.command`, `cwd`.
- PreToolUse decision output (verified honored):
  `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"|"deny"|"ask", "permissionDecisionReason": "..."}}`.
- On a **pass**, the commit gate emits no output (no opinion) instead of
  `"allow"`: an explicit allow would auto-approve the Bash call and bypass the
  user's own permission settings, which is not the gate's job.

## Robustness contract (all hooks)

- PreToolUse gates fail safe: internal error => `ask` (or `deny` when the gate
  is configured to deny); never crash the session.
- SessionStart / PostToolUse hooks fail open: any error => no-op, exit 0.

## Decisions and deviations

- **Validator scope**: the commit gate validates only `dev_docs/**/*.md`
  (the AICC-managed tree per the framework boundary), not every `.md` in the
  commit — validating arbitrary project markdown (README, vendored docs)
  against AICC frontmatter rules would be all false positives.
- **English reimplementation of tools**: the dev-tree tools under `tools/py`
  are stdlib-only but their docstrings, comments, and user-facing messages are
  Chinese. The English-only mandate (D5) makes a 1:1 copy impossible, so
  `scripts/py/*` are compact English rewrites of just the capabilities the
  plugin consumes (summary validation, contract check, doc health, project
  scan, git safety, complexity metrics). Each counts as converged (>=30%
  smaller, same rule set). The remaining ~30 dev-tree tools are not consumed
  by any skill/hook/bin and are not shipped.
- **JS tool variants and `fallback/` command docs not shipped**: the planned
  `scripts/js` + `scripts/fallback` mirrors would duplicate every shipped tool
  in a second language (and the fallback docs are Chinese). The plugin requires
  `python3` (declared in README); JS fallback is dropped per the
  cannot-converge-within-budget rule. `scripts/` therefore contains `py/` only.
- **Main-doc contract**: `core/contracts/main_doc_contract.yaml` encodes
  Chinese, project-specific section titles (including a hard-coded project
  name). The plugin ships contract v1 in `scripts/py/contract_check.py` —
  seven English, project-agnostic required sections that the `/aicc:init`
  template generates. The dev-tree yaml is not shipped.
- **complexity-dashboard skill omitted** (spec §6 ship gate):
  `dev/complexity/data/` holds only an 837-byte mock `test.json`; metrics are
  not real and thresholds are not scale-calibrated. Deferred: scaffolding
  only. `bin/aicc-complexity` (real static scan) ships; the dashboard skill
  does not.
- **build.py role**: convergence of prose is editorial, so the converged
  English artifacts are authored and committed; `build.py` verifies (source
  dirs intact, lint, budgets), generates the provenance manifest, and projects
  the Codex package. It does not regenerate skill prose from Chinese sources.

## Phantom / unusable source references

- `core/contracts/main_doc_contract.yaml` — exists but unusable as-is (see
  above): Chinese + hard-coded to one project ("Brainary").
- `dev/complexity/data/` — mock data only; fails the §6 ship gate.
