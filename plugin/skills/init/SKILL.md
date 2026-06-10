---
name: init
description: Use when a project has no dev_docs/ AICC documentation yet and the user wants to generate the initial AI coding context (main doc + sub-docs + AI_RULES). Not for updating existing docs (use incremental-update) or assessing them (use health-check).
---

# AICC First Generation (init)

Generate a project's AI coding context from scratch: an analysis plan, a
main doc (`dev_docs/AI_Coding_Context.md`), tier-appropriate sub-docs, and
`dev_docs/rules/combined/AI_RULES.md`.

**Non-negotiables**

- Plan first, generate second: phase 1 produces a reviewed plan; phase 2
  generation starts only after explicit user approval of that plan.
- Every factual statement in the plan carries an evidence level (E1-E4
  below); never write speculation as fact.
- Every generated doc gets frontmatter per
  `${CLAUDE_PLUGIN_ROOT}/references/summary-format-spec.md`.
- Respect `${CLAUDE_PLUGIN_ROOT}/references/framework-boundary.md`: never
  analyze build artifacts, dependencies, or AICC's own files as project code.
- Apply `${CLAUDE_PLUGIN_ROOT}/references/security-rules.md` to every code
  example you quote.

## Phase 0 — Setup

1. If `dev_docs/` already exists, stop: route to /aicc:health-check (docs
   complete) or ask the user whether to repair vs regenerate (incomplete).
2. Confirm the documentation language per
   `${CLAUDE_PLUGIN_ROOT}/references/language-rules.md` (setting
   `aicc.documentLanguage`, default English). Ask once, never again.

## Phase 1 — Analyze and plan (ends at a hard user gate)

3. **Scan**: run `aicc-scan --json` (or
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/py/project_scan.py" --json`).
   It reports type signals, language/file/line counts, and a suggested
   complexity tier.
4. **Pick the complexity tier** — confirm or adjust the suggestion:

   | tier | typical shape | doc set |
   | --- | --- | --- |
   | trivial | single script, <~10 code files | main doc only |
   | simple | small CLI/lib, ~10-100 files | main doc + 0-1 sub-doc |
   | medium | standard app, ~100-500 files | main + 3-5 sub-docs + AI_RULES |
   | complex | large app/monorepo, ~500-2000 files | main + 5-8 sub-docs + AI_RULES |
   | critical | very large, multi-team | main + 8+ sub-docs by module + AI_RULES |

   Bump one tier for monorepo or microservices architecture; consider a bump
   when 3+ languages are mixed.
5. **Choose the sub-doc set** from the tier and the project type
   (`${CLAUDE_PLUGIN_ROOT}/references/project-types.md`). Prune to what the
   code actually contains.
6. **Write the analysis three-piece set** under `dev_docs/_analysis/` using
   [references/generation-plan-template.md](references/generation-plan-template.md):
   - `generation_plan.md` — strategy, tier, sub-doc list, batch plan,
     evidence inventory, open questions for the user
   - `project_analysis_report.md` — findings, risks, and every uncertainty,
     each with evidence level, `blocks_phase1` flag, and writeback target
   - `generation_progress.md` — status (`awaiting-user-review`), batch
     checklist, approval record (left empty for now)

   Evidence levels: **E1** = inferred, unverified; **E2** = single source
   (one file read); **E3** = corroborated (code + config/docs agree);
   **E4** = executed/verified (command output). Plan-level conclusions for
   medium+ tiers need E3 or better; anything weaker goes to the open
   questions list, not the plan body.
7. **Self-check gate**: `aicc-summary-validate --dir dev_docs/_analysis/ --strict`
   must pass. Fix and re-run until clean.
8. **Mutual review** (when `aicc.enableMutualReview` is true and tier is
   medium+): run /aicc:mutual-review on `generation_plan.md` and apply the
   accepted findings before showing the plan to the user.
9. **HARD GATE — user approval**: present a compact plan summary (tier,
   doc list, batches, open questions). STOP and wait for explicit approval.
   Record the user's approval verbatim in `generation_progress.md`. Only an
   explicit "skip review" instruction may bypass this gate, and that too is
   recorded.

## Phase 2 — Generate (only after approval)

10. Generate in batches sized by tier (trivial/simple: one pass; medium:
    2-3 batches; complex/critical: per-module batches). After each batch,
    update `generation_progress.md` before continuing — an interrupted
    session must be resumable from the progress record.
11. Content rules for every doc:
    - main doc follows [references/main-doc-template.md](references/main-doc-template.md);
      its required sections are enforced by the commit gate's contract check
    - code examples are real (quote `file:line`), runnable, and redacted per
      the security rules
    - sub-docs get frontmatter summaries; use the doc-summarizer subagent
      (this skill's `agents/doc-summarizer.md`) for consistent frontmatter
12. Generate `dev_docs/rules/combined/AI_RULES.md` (medium+ tiers) from
    [references/ai-rules-template.md](references/ai-rules-template.md),
    instantiated with the project's real stack, naming rules, and workflows.

## Phase 3 — Acceptance

13. Run `aicc-doc-health --mode deep` and
    `aicc-summary-validate --dir dev_docs/ --recursive`. Fix failures;
    record results and any explicitly-accepted issues (with justification)
    in `dev_docs/_analysis/health_check_report.md`.
14. Present the report; the run is complete only when checks pass (or
    residual issues are user-accepted) and the user confirms. Mark
    `generation_progress.md` status `completed` with the confirmation quoted.

## Failure handling

- Scanner/validator unavailable: degrade to manual inspection, note the
  degradation in `generation_progress.md`, continue.
- Budget/context exhaustion mid-generation: finish the current batch, update
  the progress record, and tell the user how to resume (re-invoke this skill;
  it must resume from `generation_progress.md`, never restart).
- Contradictory evidence: stop generating the affected doc, downgrade the
  claim to an open question, and surface it at the next user touchpoint.
