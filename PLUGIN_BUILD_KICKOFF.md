# AICC Plugin Build — Kickoff (paste into a new Claude Code session / `/goal`)

> Copy everything in the fenced block below into a fresh session. It drives the conversion of AICC into a Claude Code **plugin**, on the long-lived `plugin` branch. It aims to complete the ENTIRE conversion in this run; resumability is only a safety net if the session hits its budget — re-paste to continue with zero rework.

```text
GOAL: Convert the AICC framework into a Claude Code plugin in full, following the approved blueprint. Build the COMPLETE plugin (all phases P0→P5, to the §10 final gate) this run. The task is resumable: if you hit the session budget, checkpoint and stop cleanly, and re-running continues from there to completion.

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

=== SCOPE: build the COMPLETE plugin this run (03 §0.5 + §9) ===
Drive the whole conversion to the §10 final gate; do NOT stop at a partial slice while session
budget remains. Build in this order, one checkpoint commit per phase (acceptance in commit body):
  P0   Skeleton: .claude-plugin/plugin.json, hooks/hooks.json, build/build.py + lint stubs,
       manifest.generated.json. Smoke-test ONE real `pre_commit_gate` deny hook against the
       installed Claude Code (confirm matcher fires + deny honored); record the confirmed hook
       schema in plugin/BUILD_NOTES.md (03 §4 "Schema verification").
  P1   Zero-paste + first skills: hooks/session_inject.py; skills `init` and `health-check`;
       bin/aicc-doc-health, bin/aicc-scan, bin/aicc-summary-validate; references/framework-boundary.md.
  P1.5 Enforcement: hooks/pre_commit_gate.py + hooks/dangerous_git_guard.py (live, default
       git_safety.commit_gate="ask"); skill `incremental-update`; settings.json (03 §5);
       dev-time agents architecture-analyst + product-manager (English, boilerplate stripped).
  P2   Thinking skills: `design-thinking`, `mutual-review`, `adr` (+ remaining dev-time agents).
  P3   Remaining skills: `doc-fallacy-fix`, `systematic-review`, `doc-reading-habit`,
       `knowledge-reuse`, and `complexity-dashboard` ONLY IF it passes the 03 §6 ship gate
       (else omit + log). Verify and record the global doc-line budget (03 §6).
  P3.5 Telemetry: hooks/post_tool_audit.py; replace/withdraw ≥1 old quantified claim.
  P4   Codex flat projection: dist/codex/ from the SAME sources (03 §7).
  P5   Docs: plugin/README.md, clone→plugin migration guide, finalize BUILD_NOTES.md + manifest.

RESUMABILITY (safety net, not a cap): before building, scan plugin/ and resume at the first
unmet checkpoint; never redo a committed phase. Only if you are about to exhaust the session
budget: finish the current phase, commit it, and end with a one-line "resume at P<n>" note —
re-pasting this kickoff continues to completion with zero rework. Do not voluntarily stop short
of P5 while budget remains.

=== ACCEPTANCE: the conversion is DONE when ALL pass (03 §10) ===
- `claude --plugin-dir plugin` loads; all 10 guaranteed skills (+ complexity-dashboard iff it
  passed the §6 gate) discoverable as `/aicc:*`.
- pre_commit_gate denies a deliberately broken-frontmatter commit (with commit_gate="deny"),
  allows otherwise; dangerous-git guard blocks force-push/reset --hard unless permissive.
- session_inject injects the skill catalog + project health snapshot with no user paste.
- No CJK under plugin/. No unsubstantiated quantified claim under plugin/.
- core/ workflows/ agents/ tools/ templates/ guides/ all still present.
- Each shipped skill passes the 3-positive / 2-negative trigger test (03 §9).
- Codex flat package builds from the same sources.
- Global plugin/ doc-line total recorded in BUILD_NOTES.md; manifest covers every shipped file.
- All P0–P5 checkpoint commits present on branch `plugin`.

=== WORKING STYLE ===
Plan-first: before P0, post the full P0→P5 task list and the result of `git merge dev`.
Commit per phase. If anything in the blueprint is ambiguous or a source file is missing,
log it in BUILD_NOTES.md and proceed with the safest convergent choice — do not stall.
Keep going through P5; only stop early if the session budget forces it (then leave a
"resume at P<n>" line). At the end, summarize what shipped, anything omitted (with reason),
and — if not fully complete — the exact next checkpoint to resume.
```

---

**Notes for you (not part of the paste):**
- The plan is on the `plugin` branch under `dev/plan/plugin/`. If your new session opens on a different branch, run `git checkout plugin` first so the agent can read the plan.
- The run aims to finish the ENTIRE conversion (P0→P5). A large build may exceed one session's budget; if so it checkpoints and you re-paste the same block to continue to completion with no rework.
- The conversion baseline is `dev` (not `master`), per your note that dev isn't merged yet.
