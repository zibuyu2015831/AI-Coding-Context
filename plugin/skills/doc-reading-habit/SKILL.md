---
name: doc-reading-habit
description: Use when the AI should load project docs on demand by frontmatter summary rather than reading everything — e.g. starting work in a documented repo, or the user says "use the docs properly" / "don't read everything".
---

# AICC On-Demand Doc Reading

How to use a `dev_docs/` tree without flooding context: decide by
frontmatter, read by need.

## The habit

1. **Index first**: read `dev_docs/AI_Coding_Context.md` — specifically
   its Documentation Index and Key Directories sections. That is the map.
2. **Frontmatter before body**: for any candidate sub-doc, read only its
   frontmatter block (first ~15 lines). `summary` states when the doc is
   worth reading; `scope` and `keywords` confirm relevance;
   `related_files` ties it to code paths.
3. **Read bodies only when**: the task touches the doc's `scope` or its
   `related_files`; the summary says it answers your current question; or
   another doc's `dependencies` names it.
4. **Trust by freshness**: check `verified_at`. Stale docs (>90 days) are
   leads, not facts — verify against code before relying on them, and
   mention staleness to the user.
5. **Max 3 docs per task**: if you think you need more, you are probably
   reading instead of searching. Re-check the index, narrow by
   `related_files` match against the files you're editing.

## Recommending docs to the user

When starting a task in a documented repo, surface at most 3 docs:
`path — why it matters for this task` (one line each). Skip the ritual
when the task plainly needs none.

## Spec

Format details: `${CLAUDE_PLUGIN_ROOT}/references/summary-format-spec.md`.
If a doc has no frontmatter, treat it as unindexed: read it only on direct
hit (filename/grep), and suggest /aicc:incremental-update to fix it.
