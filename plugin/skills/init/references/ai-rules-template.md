# AI_RULES Template — dev_docs/rules/combined/AI_RULES.md

A single rules file the user can paste into any IDE assistant (Cursor,
Windsurf, Copilot instructions) or let Claude Code pick up. Generated for
medium+ tiers; instantiate every section with project-specific content —
delete sections that would only restate generic best practice.

```markdown
---
title: AI Rules — <project name>
summary: Binding rules for AI coding sessions in this project: stack, standards, workflows, and prohibitions.
keywords: <project> | ai rules
scope: whole project
related_files: ../../AI_Coding_Context.md
dependencies: ../../AI_Coding_Context.md
verified_at: <YYYY-MM-DD>
---

# AI Rules — <project name>

## Documentation Entry
Read dev_docs/AI_Coding_Context.md first; load sub-docs on demand via their
frontmatter summaries (do not bulk-read dev_docs/).

## Core Specifications (must obey)
Tech-stack versions, API-call pattern, state-management pattern, error
handling, naming — each rule cites its source doc or file:line.

## Document Reading Triggers
| task type | read first |
Mirrors the main doc's Documentation Index; keeps IDE assistants honest.

## Workflow Standards
- New feature: plan -> user approval -> code -> update docs
- Bug fix: reproduce -> analyze -> fix -> record in knowledge base
- Any code change: check Document Maintenance Triggers; update affected docs
  in the same change (or run /aicc:incremental-update after committing)

## Git Safety
- Red zone (never): force push, hard reset, history rewrite on shared
  branches, branch/tag deletion, committing to protected branches
- Yellow zone (ask first): commit, push, new branches
- Green zone (free): status, log, diff, add, local checkout
The AICC plugin enforces the red zone via hooks when installed.

## Prohibitions
Project-specific do-nots (from the main doc's AI Coding Taboos), each with
its reason. No generic filler.

## Rule Update Triggers
Stack upgrade, new sub-doc, naming change, workflow change -> update this
file and bump verified_at.
```
