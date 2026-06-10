# Generation Plan Template (parametric, all tiers)

One template for all five complexity tiers. Sections tagged
`[medium+]` / `[complex+]` are included only at that tier or above;
everything else applies to all tiers. This replaces the six per-tier
templates of the clone-form framework.

The phase-1 output is a three-piece set under `dev_docs/_analysis/`:
`generation_plan.md` (this template), `project_analysis_report.md`,
`generation_progress.md`. All three need valid frontmatter (strict).

---

## 1. generation_plan.md

```markdown
---
title: Generation Plan — <project name>
summary: AICC phase-1 plan: complexity tier, doc set, batch strategy, and evidence inventory for first generation.
keywords: aicc | generation plan | <project type>
scope: dev_docs/_analysis
related_files: ./project_analysis_report.md | ./generation_progress.md
dependencies: none
verified_at: <YYYY-MM-DD>
---

# Generation Plan

## Project metadata
- Name, repo root, primary language(s), detected type signals (from aicc-scan)
- Documentation language (confirmed with user)

## Complexity assessment
- Tier: <trivial|simple|medium|complex|critical> — rationale in one
  paragraph: code size, architecture signals (monorepo? microservices?
  multi-language?), risk factors
- Scan numbers quoted from `aicc-scan --json` output (E4 evidence)

## Doc set
| doc | priority | rationale | content sources |
| --- | --- | --- | --- |
| dev_docs/AI_Coding_Context.md | P0 | entry point | scan + code reading |
| <sub-doc>.md | P0/P1/P2 | <why this project needs it> | <dirs/files> |

[medium+] Include AI_RULES (dev_docs/rules/combined/AI_RULES.md) as P0.

## Core code patterns to extract
For each pattern (API calls, state, routing, components, error handling —
pick what the project actually has): source `file:line`, one-line pattern
description. Patterns must be quoted from real code during generation.

[medium+] ## Project positioning constraints
| constraint | evidence | doc impact | status |
e.g. privacy/local-first/offline/no-backend promises found in README or
product docs — these constrain what generated docs may recommend.

[medium+] ## AI / external service boundaries
| boundary | evidence | data sent | doc impact |
Which external services the code calls, what data crosses the boundary,
where credentials live. Drives security-rule application.

## Redaction checklist
Sensitive values expected in this codebase (keys, domains, IPs, PII) and
the replacement strategy per references/security-rules.md.

## Batch plan
| batch | docs | depends on |
trivial/simple: one batch. medium: 2-3. complex/critical: per-module.

## Evidence inventory
| fact | level (E1-E4) | source | verification |
Every load-bearing fact in this plan. [medium+] Plan-body conclusions
need E3+; E1/E2 items belong in open questions instead.

## Open questions for the user
For each: current conservative assumption, evidence checked, why the code
cannot answer it, blocks_phase1 (true/false), writeback target doc.

## Acceptance criteria
- All docs have valid strict frontmatter
- Main doc passes the contract check (required sections)
- aicc-doc-health deep mode: no errors, accepted issues justified
```

---

## 2. project_analysis_report.md

```markdown
---
title: Project Analysis Report — <project name>
summary: Phase-1 findings, risks, and uncertainties with evidence levels feeding the generation plan.
keywords: aicc | analysis | findings
scope: dev_docs/_analysis
related_files: ./generation_plan.md
dependencies: ./generation_plan.md
verified_at: <YYYY-MM-DD>
---

# Project Analysis Report

## Findings
| # | finding | evidence (file:line) | level | feeds |
Architecture facts, module map, stack versions — only what generation needs.

## Risks
| # | risk | impact on docs | mitigation |
e.g. large generated dirs that could pollute scans, ambiguous module
boundaries, undocumented build steps.

## Uncertainties
| # | question | conservative assumption | level | blocks_phase1 | writeback target |
Everything not answerable from the repo. blocks_phase1=true items must be
resolved before the user gate; false items carry into generation as marked
assumptions.
```

---

## 3. generation_progress.md

```markdown
---
title: Generation Progress — <project name>
summary: Execution state of AICC first generation: batch checklist, approvals, and resume point.
keywords: aicc | progress | resume
scope: dev_docs/_analysis
related_files: ./generation_plan.md
dependencies: ./generation_plan.md
verified_at: <YYYY-MM-DD>
---

# Generation Progress

## Status
One of: planning | awaiting-user-review | generating | awaiting-acceptance
| completed

## Approval record
- Plan approved by: <user>, quoted verbatim: "<approval message>"
- Review-skip (if any): quoted verbatim, with who authorized it

## Batch checklist
| batch | docs | status | notes |

## Writeback log
When any fact changes after review, list every doc updated to match —
sync the full set (plan tables, report rows, summaries), never just append.

## Resume note
If a session ends mid-generation: the next session reads this file and
continues from the first unchecked batch. Never regenerate completed docs.
```
