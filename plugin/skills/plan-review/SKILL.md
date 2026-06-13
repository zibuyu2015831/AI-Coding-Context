---
name: plan-review
description: Use when a single landed plan file on disk should be reviewed before it enters implementation — e.g. "review dev_docs/plans/active/2026-06-13_feature_export.md", "is this plan ready to implement?". The object is an addressable, re-enterable plan file (not an in-flight artifact — that's mutual-review; not the whole doc set — that's systematic-review).
---

# AICC Plan Review

Reviews **one named plan file that already sits on disk** (`dev_docs/plans/active/<plan>.md`)
as an addressable, re-enterable unit, before it enters implementation. This is the
missing middle grain between mutual-review (the artifact you *just* generated) and
systematic-review (the whole corpus): a plan may be weeks old, revised many times, or
written by another tool/session — you can still point at it and review it.

This skill owns only the **object semantics** (what to review, how to address it, what to
write back). It **delegates the actual reviewing** to /aicc:mutual-review's engine — do
not re-implement scoring, dimensions, or auto-fix here.

## Object and addressing

- **Object**: a single plan file at `<PLAN_PATH>` (e.g. `dev_docs/plans/active/2026-06-13_feature_export.md`).
- **Re-entrant**: any session can re-target the same path and re-review. Because review is
  decoupled from creation, "has this been reviewed?" cannot be known from chat — it must
  live on disk in the plan's frontmatter `review_status`.

## Two separate gates

`review_status: reviewed` means **the plan has been reviewed**. It does **not** mean the
user approved implementation. Those are two independent persisted states — never collapse
them. Reaching `reviewed` clears the "unreviewed" gate only; whether work starts still
needs the user's go-ahead.

## Trigger grading (don't double-review everything)

Pick depth by complexity, then force at least one round if any high-risk surface is touched:

| complexity | depth |
| --- | --- |
| trivial / simple | may `skipped` (must record a `review_reason`) |
| medium | one round |
| complex / critical | two rounds (round 2 builds on the round-1 revision; no restating) |

**High-risk surfaces** (any one forces ≥1 round, no `skipped`): `auth`, `payment`,
`data-schema`, `migration`, `external-API`, `privacy-secrets`, `concurrency`,
`breaking-change`. Project-specific surfaces come from the project's analysis report /
AI_RULES, not hardcoded here. Defaults are configurable under `aicc.planReview` in settings.

## Procedure

1. **Address** the plan at `<PLAN_PATH>` and read it from disk (not from memory).
2. **Grade** the trigger (table above). If `skipped`, record the reason and stop after step 5.
3. **Review** by delegating to /aicc:mutual-review with `agents/plan-reviewer.md` and the
   relevant standard — give the reviewer only the plan, the requirement it serves, and the
   standard, so the critique is independent. Use the graded depth (1 or 2 rounds).
4. **Disposition** findings P0/P1/P2/P3 (each: problem · evidence · impact · suggested
   change · blocking?). P0s must be fixed or explicitly rejected with evidence.
5. **Write back** to the plan file itself: fill the plan's self-review record block, set
   `review_status: reviewed | skipped`, bump `review_rounds`. Route any "future idea"
   findings to the plan's non-goals / residual-risk section or to `memos/` — never into the
   current implementation steps. A future idea must be re-distilled into a new plan and
   re-run through this protocol before it is implemented.
6. **Stop at the second gate**: report findings + disposition and state that `reviewed`
   ≠ approved; entering implementation still needs user confirmation.

## Enforcement boundary

Only one thing here is hook-enforced: at commit time, a plan committed into
`dev_docs/plans/done/` whose `review_status` is not `reviewed | skipped(with reason)` is a
**blocker** (`pre_commit_gate` → `doc_health.plan_done_without_review`; done is judged by
directory membership). The "review before implementing" gate is advisory/flow — a static
hook cannot intercept "the AI started writing code". Don't claim otherwise to the user.
