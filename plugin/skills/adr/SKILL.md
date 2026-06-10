---
name: adr
description: Use when a significant architecture or design decision is made and should be recorded as an Architecture Decision Record — e.g. "record this decision", "write an ADR". Not for making the decision itself (use design-thinking).
---

# AICC Architecture Decision Records

Record decisions that future sessions must not silently undo.

## When an ADR is required

- A new architectural principle or cross-module constraint is adopted.
- A technical direction is chosen among real alternatives (framework,
  storage, protocol, pattern).
- An existing pattern is deliberately broken or superseded.
- A high-risk/high-cost approach is accepted with reasons worth keeping.

Local, single-module choices need no ADR unless they contradict an
existing one.

## Procedure

1. **Search first**: scan the ADR directory (default
   `dev_docs/architecture/decisions/`, or the project's existing ADR
   location if it has one) for duplicates, conflicts, and prerequisite
   ADRs. A conflict means: adjust scope, supersede the old ADR
   explicitly, or stop.
2. **Write** the record from
   [references/adr-template.md](references/adr-template.md):
   number it `ADR-###` (next free number, zero-padded), filename
   `ADR-###-kebab-case-title.md`, status `Proposed`.
3. **Substance checks** (the template's pre-flight checklist, enforced):
   - 2+ real alternatives with honest "why rejected" reasoning
   - both positive AND negative impacts stated
   - the Decision section is prescriptive (a rule to follow, checkable in
     review), not a narrative
4. **Review**: for consequential ADRs run /aicc:mutual-review on the
   draft; then have the user accept it (status -> `Accepted`).
5. **Wire it in**: add the ADR to the doc index in the main doc; if the
   decision constrains code patterns, reflect it in AI_RULES so reviews
   can cite it ("per ADR-012...").

## Lifecycle

- Statuses: Proposed -> Accepted -> (Deprecated | Superseded by ADR-YYY).
- Never edit an Accepted ADR's decision content — supersede it with a new
  one and cross-link both directions.
- Reviews (mutual-review's code reviewer) treat Active ADR violations as
  P0 findings; that only works if ADRs stay findable and current — bump
  `verified_at` when re-confirmed.
