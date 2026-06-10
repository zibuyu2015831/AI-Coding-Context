# ADR Template

File: `dev_docs/architecture/decisions/ADR-###-kebab-case-title.md`

```markdown
---
title: "ADR-###: <decision title>"
summary: <one sentence: the decision and its driving context>
keywords: adr | architecture | <topic>
scope: <system/module boundary this decision governs>
related_files: <key code paths affected, ' | ' separated, or none>
dependencies: <prerequisite ADR files, or none>
verified_at: <YYYY-MM-DD>
---

> Pre-flight (delete after passing):
> - [ ] searched existing ADRs — no duplicate topic
> - [ ] dependencies listed above are all still Accepted
> - [ ] no conflict with an Accepted ADR (or the conflict is resolved in
>       "Alternatives" by superseding it explicitly)

# ADR-###: <decision title>

## 1. Decision info
- Date: <YYYY-MM-DD>
- Status: Proposed | Accepted | Deprecated | Superseded by ADR-YYY
- Participants: <people and/or AI roles involved>

## 2. Context
Why this decision is needed: the pain point, constraint, or pressure —
grounded in this project's reality, with evidence (file paths, incidents,
measurements) where it exists.

## 3. Decision
Prescriptive statement of the rule(s) now in force. Specific enough that
a reviewer can check a change against it.

## 4. Alternatives considered
- **<Option A>**: <one-line description>
  - Why rejected: <the concrete trade-off that disqualified it here>
- **<Option B>**: ...

## 5. Impact
- Positive: <what improves, quantified only with real measurements>
- Negative: <honest costs: migration, boilerplate, learning curve>

## 6. Enforcement notes (optional)
Machine-checkable constraints implied by this decision (forbidden
patterns, required dependencies, module boundaries) — what a linter, CI
check, or AI reviewer should flag. Mark each as enforced or aspirational.
```
