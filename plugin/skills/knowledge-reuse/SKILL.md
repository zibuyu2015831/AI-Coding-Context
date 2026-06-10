---
name: knowledge-reuse
description: Use when the user wants to capture reusable engineering knowledge or pull cross-project knowledge/patterns from a shared knowledge base — e.g. "save this solution for reuse", "check the knowledge base".
---

# AICC Knowledge Reuse

Sediment hard-won solutions into `dev_docs/knowledge/` and reuse them —
locally and, optionally, across projects via a git-backed shared repo.

## When to capture

Capture when a solution: took real effort to find, is non-obvious or
non-standard, will recur (here or in sibling projects), or encodes a
measured improvement. Do NOT capture restated official docs or one-off
trivia.

## Capturing

1. Write the entry to `dev_docs/knowledge/<category>/<kebab-case-name>.md`
   using [references/knowledge-entry-template.md](references/knowledge-entry-template.md).
   Categories: troubleshooting | patterns | performance | integration |
   tooling (extend as needed).
2. Frontmatter per the summary spec (it is a dev_docs doc; the commit
   gate validates it).
3. Add one line to `dev_docs/knowledge/README.md`'s index.

## Reusing

1. Before solving a gnarly problem, search:
   `aicc-knowledge search "<terms>"` (greps local and, if enabled, the
   shared cache) — or grep `dev_docs/knowledge/` directly.
2. Adapt, don't paste: knowledge entries state context and caveats; check
   they hold in the current project.
3. After use, if the entry was wrong or incomplete, fix it — reuse that
   degrades the base is worse than no reuse.

## Cross-project sharing (optional)

A shared knowledge repo is just a git repo of entries:

- `aicc-knowledge status` — local/shared state
- `aicc-knowledge enable-shared <git-url>` — clone to
  `.aicc-cache/shared-knowledge/` (gitignored) and include it in searches
- `aicc-knowledge update` — pull the shared repo
- Publishing: copy/promote a local entry into the shared repo clone and
  push it from there (normal git flow; the guard hook's red-zone rules
  still apply).

Search order is local-first; a shared entry that contradicts local
experience is a flag to reconcile, not silently prefer.
