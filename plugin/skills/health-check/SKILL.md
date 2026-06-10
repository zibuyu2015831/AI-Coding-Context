---
name: health-check
description: Use when dev_docs/ already exists and the user wants to assess documentation health, staleness, or drift before relying on it. Not for generating docs (use init) or applying updates (use incremental-update).
---

# AICC Documentation Health Check

Assess whether an existing `dev_docs/` doc set can be trusted, score it,
and route to the right follow-up. Read-only: this skill never edits docs.

## Modes

Pick by how much confidence the user needs (escalate on demand):

| mode | adds | machine support |
| --- | --- | --- |
| quick | structure completeness, frontmatter validity, staleness | `aicc-doc-health --mode quick` |
| standard | + internal link/file-path accuracy, code-sample spot check | `aicc-doc-health --mode standard` |
| deep | + architecture-vs-code drift, coverage gaps, code-block syntax | `aicc-doc-health --mode deep` |

## Procedure

1. Run `aicc-doc-health --mode <mode> --json` (wrapper over
   `${CLAUDE_PLUGIN_ROOT}/scripts/py/doc_health.py`). It returns a 0-100
   score, grade, and issue list for the machine-checkable part.
2. Add the AI-judgment checks the tool cannot do:
   - **standard**: open 3-5 code examples from the docs and diff them
     against the current source (`file:line` references make this fast).
   - **deep**: compare the main doc's architecture/module mapping against
     the real directory tree; list undocumented modules and documented
     ghosts; check whether `Document Maintenance Triggers` fired for recent
     commits but were ignored (`git log` since the docs' `verified_at`).
3. Merge tool + judgment findings into a report per
   [references/health-report-template.md](references/health-report-template.md).
4. Grade bands (from the tool): >=90 excellent, 70-89 good, 50-69 fair,
   30-49 poor, <30 critical.

## Routing (present these options, let the user choose)

| situation | recommend |
| --- | --- |
| excellent / good | no action, or fix the listed small issues inline |
| fair, drift from recent code changes | /aicc:incremental-update |
| factual errors found (docs contradict code) | /aicc:doc-fallacy-fix |
| poor with broad drift | /aicc:incremental-update first; regenerate only if it can't converge |
| critical, docs structurally broken or obsolete | regenerate via /aicc:init (archive old dev_docs/ first) |
| user wants a full multi-round audit | /aicc:systematic-review |

Always show the score, the top findings, and the recommendation — then
stop. Executing the follow-up is the chosen skill's job, not this one's.

## Notes

- A stale `verified_at` with an unchanged code area is a re-verify task
  (bump the date after checking), not a rewrite.
- If `dev_docs/` exists but the main doc is missing, that is structural
  damage: recommend repair via /aicc:init rather than scoring around it.
- Never bulk-load all docs to "check" them; sample by risk (entry doc,
  most-referenced sub-docs, docs whose scope saw recent commits).
