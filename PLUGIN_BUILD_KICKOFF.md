# AICC Plugin Build — Kickoff (paste into a new Claude Code session / `/goal`)

> Copy everything in the fenced block below into a fresh session. It drives the conversion of AICC into a Claude Code **plugin**, on the long-lived `plugin` branch, MVP-first and resumable. Re-paste it to continue where the previous run stopped.

```text
GOAL: Convert the AICC framework into a Claude Code plugin, following the approved blueprint. Build the MVP slice this run; the task is resumable — re-running this goal continues it.

=== READ FIRST (the plan is the source of truth — do not re-derive it) ===
1. dev/plan/plugin/README.md              — locked decisions D1–D7
2. dev/plan/plugin/01-plugin-architecture-and-enforcement.md
3. dev/plan/plugin/02-implementation-roadmap.md
4. dev/plan/plugin/03-execution-spec.md   — THE file-level blueprint; execute it
Also skim FRAMEWORK_REVIEW.md and FRAMEWORK_REVIEW_II.md for the WHY.

=== HARD INVARIANTS (never violate) ===
- BRANCH: work ONLY on `plugin`. First, ensure you are on it: `git checkout plugin`
  (create from dev if missing: `git checkout dev && git checkout -b plugin`).
  Never commit to `dev` or `master`.
- BASELINE = dev: FIRST action — `git merge dev` into `plugin`. If it conflicts, STOP and
  report; do not resolve a semantic merge yourself.
- ENGLISH ONLY: every file you create under `plugin/` (SKILL.md, descriptions, hook
  comments/messages, bin --help, settings keys, README) is English. The plan docs are
  Chinese; your OUTPUT is English. Lint: no CJK characters under `plugin/`.
- MIGRATION = CONVERGENCE: never copy a source asset 1:1. Apply its convergence action
  (03 §6) BEFORE it enters `plugin/`. Slim the 811-line entry doc, merge the 6 plan-template
  variants, de-boilerplate roles, delete unsubstantiated quantified claims, fold personas
  into a parameter. If an asset can't be converged in budget, leave it out and note it in
  plugin/BUILD_NOTES.md.
- DON'T BREAK CLONE FORM: you ADD `plugin/`. Never delete/move core/ workflows/ agents/
  tools/ templates/ guides/. Assert they still exist before finishing.
- REAL ASSETS ONLY: map only files that exist on dev; verify before mapping; log phantoms.

=== THIS RUN'S SCOPE (MVP slice — see 03 §0.5) ===
Resume rule: scan plugin/skills/* first; build the first item below that is missing or under
budget; checkpoint-commit each completed phase; stop after a clean commit when ~70% of the
session budget is used.

Build, in order, with a checkpoint commit per phase (acceptance result in the commit body):
  P0  Skeleton: .claude-plugin/plugin.json, hooks/hooks.json, build/build.py + lint stubs,
      manifest.generated.json. Smoke-test ONE real `pre_commit_gate` deny hook against the
      installed Claude Code (confirm matcher fires + deny honored); record the confirmed hook
      schema in plugin/BUILD_NOTES.md (03 §4 "Schema verification").
  P1  Zero-paste + first skills: hooks/session_inject.py; skills `init` and `health-check`;
      bin/aicc-doc-health, bin/aicc-scan, bin/aicc-summary-validate; references/framework-boundary.md.
  P1.5 Enforcement: hooks/pre_commit_gate.py + hooks/dangerous_git_guard.py (live, default
      git_safety.commit_gate="ask"); skill `incremental-update`; settings.json (03 §5).
  Agents: development-agents architecture-analyst + product-manager (converted to English,
      boilerplate stripped) — only if their sources exist under agents/development/.

DEFER to later runs (do NOT attempt this run): design-thinking, mutual-review, adr,
doc-fallacy-fix, systematic-review, doc-reading-habit, knowledge-reuse, complexity-dashboard
(only ship if made real — 03 §6 gate), post_tool_audit telemetry, Codex flat projection, the
clone→plugin migration guide.

=== ACCEPTANCE FOR THIS RUN (must pass before final commit) ===
- `claude --plugin-dir plugin` loads; `/aicc:init`, `/aicc:health-check`,
  `/aicc:incremental-update` are discoverable.
- pre_commit_gate returns deny on a deliberately broken-frontmatter commit (with
  commit_gate="deny"), allow otherwise.
- session_inject injects the skill catalog + project health snapshot with no user paste.
- No CJK under plugin/. No unsubstantiated quantified claim under plugin/.
- core/ workflows/ agents/ tools/ templates/ guides/ all still present.
- Each shipped skill passes the 3-positive / 2-negative trigger test (03 §9).
- Record measured plugin/ doc-line total in BUILD_NOTES.md.

=== WORKING STYLE ===
Plan-first: before P0, post a short ordered task list and the result of `git merge dev`.
Commit per phase. If anything in the blueprint is ambiguous or a source file is missing,
log it in BUILD_NOTES.md and proceed with the safest convergent choice — do not stall.
At the end, summarize what shipped, what deferred, and the exact next item to resume.
```

---

**Notes for you (not part of the paste):**
- The plan is on the `plugin` branch under `dev/plan/plugin/`. If your new session opens on a different branch, run `git checkout plugin` first so the agent can read the plan.
- A single run targets the MVP (enforcement + zero-paste + 3 core skills). Re-paste the same block to build the deferred skills; it detects existing work and continues.
- The conversion baseline is `dev` (not `master`), per your note that dev isn't merged yet.
