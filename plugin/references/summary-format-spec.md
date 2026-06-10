# Frontmatter Summary Format

Every AICC-managed markdown doc starts with a YAML frontmatter block. This
is what lets an AI session decide whether to read a doc without opening it
(see the doc-reading-habit skill) and what `aicc-summary-validate` enforces.

## Required fields

```yaml
---
title: Short human-readable document title
summary: 1-3 sentences: what this doc covers and when to read it.
keywords: term1 | term2 | term3
scope: the code/dir/domain this doc describes
related_files: src/api/client.ts | src/api/interceptors.ts
dependencies: dev_docs/architecture_overview.md
verified_at: 2026-06-11
---
```

| field | rules |
| --- | --- |
| `title` | non-empty, one line |
| `summary` | 1-3 sentences; states content AND when to read it |
| `keywords` | 2+ terms, ` \| ` separated |
| `scope` | the area of the project this doc is authoritative for |
| `related_files` | ` \| ` separated repo paths, or `none`; paths must exist |
| `dependencies` | docs this doc builds on, ` \| ` separated, or `none` |
| `verified_at` | `YYYY-MM-DD` of the last human/AI verification against code |

## Staleness

A doc whose `verified_at` is more than 90 days old is flagged stale by the
validator and the health check. Update the content (or re-verify it) and bump
`verified_at` — never bump the date without re-verifying.

## Validation

```bash
aicc-summary-validate --file dev_docs/api_layer.md
aicc-summary-validate --dir dev_docs/ --recursive --strict
```

Strict mode (warnings fail too) is required for `dev_docs/_analysis/` docs
before the phase-1 review gate in /aicc:init.
