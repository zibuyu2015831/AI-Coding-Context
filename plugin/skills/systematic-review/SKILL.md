---
name: systematic-review
description: Use when the user wants a structured multi-round audit of the whole documentation set — e.g. "audit the docs", "full documentation review". Not for one doc error (use doc-fallacy-fix) or a quick score (use health-check).
---

# AICC Systematic Review

A planned, recorded, multi-round audit of an entire doc set. Heavier than
/aicc:health-check (which scores); this produces a tracked issue list and
an improvement roadmap.

## Phase 1 — Prepare

1. Scope with the user: comprehensive | priority-only (P0/P1 docs) |
   component (one doc family) | security/accuracy focus.
2. Create the audit workspace `dev_docs/_analysis/audits/<YYYY-MM-DD>/`
   with three files: `review_plan.md` (scope, rounds, baseline),
   `issue_tracking.md` (the table below), `review_log.md` (chronological
   record).
3. Baseline: `aicc-doc-health --mode deep --json` output + doc inventory
   (count, staleness distribution) recorded in the plan.

## Phase 2 — Rounds

| round | focus | method |
| --- | --- | --- |
| 1 — accuracy | claims vs code; quoted examples; API/identifier names | sample by risk: entry doc, most-depended-on docs, docs whose scope changed recently |
| 2 — consistency | terminology, cross-references both directions, format/frontmatter compliance, index completeness | full sweep, mostly mechanical (use the bin tools) |
| 3+ — deep dives (optional) | one component family per round (architecture docs, rules, knowledge base) chosen from round 1-2 findings | targeted re-read with code open |

Record every finding immediately in `issue_tracking.md`:

```text
| id | type | severity | doc(s) | location | description | evidence | proposed fix |
```

id format `AUD-YYYYMMDD-NNN`; severity: severe / major / minor /
suggestion; evidence = file:line or command output, never "seems".

## Phase 3 — Report and route

1. Summarize in `review_plan.md`: issues by severity and type, doc-set
   verdict, top systemic causes (not just instances).
2. Route the issues: factual errors -> /aicc:doc-fallacy-fix (can batch);
   drift -> /aicc:incremental-update; structural decay -> targeted
   rewrite proposals; process causes -> recommendations (e.g. enable
   commit gate `deny`, adopt /aicc:doc-reading-habit).
3. Get user sign-off on the roadmap; the audit is done when every issue
   is either fixed, routed with an owner skill, or explicitly accepted.

## Exit criteria

All planned rounds executed; every recorded issue triaged (no "open"
rows); report filed in the audit workspace; follow-ups routed. Partial
audits end with a resume note in `review_log.md` so a later session can
continue from the last completed round.
