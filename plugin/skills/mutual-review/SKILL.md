---
name: mutual-review
description: Use when generated output (a plan, code, or doc) should be adversarially reviewed by a second AI reviewer before acceptance — e.g. "review this plan", "@review", "second opinion". Not for designing solutions (use design-thinking) or auditing the whole doc set (use systematic-review).
---

# AICC Mutual Review

Adversarial second-AI review of a concrete artifact (plan, code change, or
doc) before it is accepted. The reviewer's job is to find what's wrong, not
to congratulate.

## Mode selection

| mode | rounds | when |
| --- | --- | --- |
| skip | 0 | user says so, or the change is trivial (typo-class) |
| standard | 1 | default for medium changes |
| deep | 2 | complex or risky changes; second round verifies the fixes |
| ultra | 3 | user-forced (`@review:force`/"ultra") for high-risk work |

Choose by judgment when not directed: count of files touched, lines, core
modules (auth/payment/data) involved, breaking changes, and the semantic
riskiness of the logic. Lean up, not down, when core modules or breaking
changes are in play. State the chosen mode and why.

## Procedure

1. **Pick the reviewer**: launch this skill's subagent —
   `agents/plan-reviewer.md` for plans/designs, `agents/code-reviewer.md`
   for code and doc changes. Give it ONLY the artifact, the requirement it
   serves, and the relevant standard from
   [references/review-standards.md](references/review-standards.md) —
   not your own reasoning, so its review is independent.
2. **Reviewer reports** in the standard format: overall verdict
   (pass / needs-modification / fail), findings as P0 (blocking) /
   P1 (major) / P2 (minor), each with location, description, concrete
   suggestion, and the reviewer's confidence (high/medium/low).
3. **Disposition** (you, the generator):
   - P0 findings: must be fixed or explicitly rejected with evidence —
     never silently ignored.
   - Apply accepted P1/P2 fixes when they are clear improvements; defer
     the rest with one-line reasons.
   - Auto-fix without asking the user only when: no P0s, the reviewer is
     confident, and the fixes don't change scope or break compatibility.
     Otherwise present findings + your disposition to the user.
4. **Deep/ultra**: re-submit the revised artifact; the next round checks
   the fixes and hunts for what round 1 missed.
5. **Record**: append the review summary (mode, findings count by
   severity, disposition) to the artifact's progress/plan doc if one
   exists (e.g. `generation_progress.md` during /aicc:init).

## Honesty rules

- The reviewer must include at least one genuine concern or state
  explicitly that it searched and found none — "LGTM" without evidence of
  scrutiny is a failed review.
- Disagreements between generator and reviewer that survive one
  fix-round go to the user as a stated trade-off, not a silent override.
- A review changes the artifact or produces recorded reasons why not;
  reviews with zero effect are a smell worth telling the user about.

## Perspective option

For design-heavy artifacts you may instruct the reviewer to adopt a
perspective from /aicc:design-thinking's table (`pragmatist`,
`evolutionist`, `purist`) to sharpen the critique.
