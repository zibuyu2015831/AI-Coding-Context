# Main Doc Template — dev_docs/AI_Coding_Context.md

The project's AI entry point. Sections marked **required** are enforced by
the commit gate's contract check (`scripts/py/contract_check.py`); keep
their headings recognizable (emoji/numbering allowed, key words intact).
Length guidance: small projects ~100-200 lines; never exceed what the
project's real complexity justifies.

```markdown
---
title: AI Coding Context — <project name>
summary: Entry point for AI coding sessions: project shape, doc index, core patterns, and rules.
keywords: <project> | ai context | entry point
scope: whole project
related_files: <key source dirs>
dependencies: none
verified_at: <YYYY-MM-DD>
---

# AI Coding Context — <project name>

## How to Read This Document
First-session reading order; which sections answer which question types.

## Project Overview                                    [required]
Type, purpose, tech stack with versions (from lockfiles, E3+), scale in one
paragraph. No marketing language.

## Key Directories                                     [required]
5-10 rows: directory -> what lives there -> when an AI session needs it.

## Documentation Index                                 [required]
Every dev_docs/ sub-doc with a one-line "read this when..." trigger.
This is the on-demand loading map (see /aicc:doc-reading-habit).

## Core Architecture Features                          (if distinctive)
1-3 patterns that make this codebase different, each with file:line evidence.

## Development Workflow                                [required]
Plan-first rules, branch/PR conventions, test expectations — the project's
real workflow as evidenced by CONTRIBUTING/CI config, not aspirations.

## Core Code Patterns                                  (medium+)
Real, redacted code excerpts (file:line) for: API calls, state, error
handling, naming — the patterns a new change must follow.

## Naming Conventions                                  (medium+)
File, symbol, and module naming rules actually observed in the code.

## Business Module Mapping                             (medium+)
module -> directories -> key files -> owning docs.

## Common Tasks                                        [required]
task -> step sequence -> docs to read first. Cover the project's actual
frequent tasks (add endpoint, add screen, fix bug class, ...).

## Document Maintenance Triggers                       [required]
code change class -> which doc(s) must be updated (drives /aicc:incremental-update).

## AI Coding Taboos                                    [required]
Explicit do-nots with the reason: never skip the plan gate, never touch
generated dirs, project-specific footguns (each with evidence).
```
