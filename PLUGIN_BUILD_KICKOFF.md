# AICC Plugin Build — Kickoff (paste into a new Claude Code session / `/goal`)

> Copy everything in the fenced block below into a fresh session. It drives the conversion of AICC into a Claude Code **plugin**, on the long-lived `plugin` branch. It aims to complete the ENTIRE conversion in this run; resumability is only a safety net if the session hits its budget — re-paste to continue with zero rework.

```text
GOAL: Convert the AICC framework into a Claude Code plugin, IN FULL, this run.

THE BLUEPRINT IS dev/plan/plugin/03-execution-spec.md — read it FIRST and execute it
exactly (its sections §0 invariants, §0.5 build order, §1-§8 file-level specs, §9
checkpoints, §10 final gate). Read dev/plan/plugin/README.md for locked decisions D1-D7.
Do not re-derive or re-plan; the design work is done.

HARD INVARIANTS (also in 03 §0 — never violate):
- Branch: `git checkout plugin`; never commit to dev or master.
- First action: `git merge dev`. On conflict, STOP and report.
- English only under plugin/ (no CJK). Plan docs are Chinese; your OUTPUT is English.
- Migration = convergence: never copy assets 1:1; apply 03 §6 actions first
  (slim entry doc, merge template variants, de-boilerplate roles, fold personas into a
  parameter, delete unsubstantiated quantified claims). Can't converge -> omit + log
  in plugin/BUILD_NOTES.md.
- ADD plugin/ only; never delete/move core/ workflows/ agents/ tools/ templates/ guides/.
- Map only source files that actually exist on dev; log phantoms, don't invent.

SCOPE: ALL phases P0 -> P5 per 03 §9, one checkpoint commit per phase (acceptance
self-check in the commit body):
  P0   skeleton (plugin.json, hooks.json, build.py + lint, manifest) + smoke-test ONE
       real deny hook; record confirmed hook schema in BUILD_NOTES.md (03 §4).
  P1   session_inject.py (zero-paste) + skills init, health-check + bin wrappers
       + references/framework-boundary.md.
  P1.5 pre_commit_gate.py + dangerous_git_guard.py (live, commit_gate="ask")
       + skill incremental-update + settings.json + 2 dev-time agents.
  P2   design-thinking, mutual-review, adr + remaining agents.
  P3   doc-fallacy-fix, systematic-review, doc-reading-habit, knowledge-reuse;
       complexity-dashboard ONLY if it passes the 03 §6 ship gate. Record line budget.
  P3.5 post_tool_audit.py telemetry.
  P4   Codex flat projection dist/codex/ from the SAME sources (03 §7).
  P5   plugin/README.md + clone->plugin migration guide + finalize BUILD_NOTES + manifest.

RESUMABILITY (safety net, NOT a cap): first scan plugin/ and resume at the first unmet
checkpoint; never redo a committed phase. Do NOT stop before P5 while budget remains;
only if the session budget is nearly exhausted, finish the current phase, commit, and
end with "resume at P<n>" — re-pasting this kickoff continues with zero rework.

DONE = every box in 03 §10 passes (plugin loads with all /aicc:* skills; commit gate
denies a broken commit; zero-paste injection works; no CJK; trigger tests pass; Codex
package builds; source dirs intact; manifest complete; all checkpoint commits present).

Working style: before P0, post the P0->P5 task list + `git merge dev` result. If a
blueprint detail is ambiguous or a source is missing, log it in BUILD_NOTES.md and take
the safest convergent choice — do not stall. End with: what shipped, what was omitted
(why), and the exact resume point if (and only if) not fully complete.
```

---

**Notes for you (not part of the paste):**
- The plan is on the `plugin` branch under `dev/plan/plugin/`. If your new session opens on a different branch, run `git checkout plugin` first so the agent can read the plan.
- The run aims to finish the ENTIRE conversion (P0→P5). A large build may exceed one session's budget; if so it checkpoints and you re-paste the same block to continue to completion with no rework.
- The conversion baseline is `dev` (not `master`), per your note that dev isn't merged yet.
