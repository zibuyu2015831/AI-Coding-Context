# Commit-Guided Doc Sync

Structured commits let doc updates be derived from intent, not just diffs.
This merges the clone-form quick-start and migration guides.

## Commit format

```text
<prefix>(<type>): <subject>

WHAT: core action and object
WHY: business motivation or requirement id
HOW: implementation strategy and key decisions
```

- prefixes: `doc`, `ai`, `prompt` (equivalent); plain conventional-commit
  prefixes (`feat`, `fix`, ...) work too — WHAT/WHY/HOW lines are what matter.
- types: feature | fix | refactor | doc | perf | test | architecture

## Sync procedure

1. Collect commits since the docs' newest `verified_at`:
   `git log --since=<date> --pretty=full`.
2. For structured commits: WHAT names the change object, HOW names modules
   touched — map straight to owning docs (frontmatter `related_files`,
   then the change-doc mapping table).
3. For unstructured commits: fall back to the diff
   (`git show --stat <id>`), classify per the mapping table.
4. Draft per-doc updates; show the user the proposal (doc -> section ->
   change) before applying.
5. After applying, commit docs separately with a structured message, e.g.:

```text
doc(sync): update api_layer for pagination change

WHAT: api_layer.md examples and parameter table refreshed
WHY: commits a1b2c3..d4e5f6 changed the list endpoints' paging contract
HOW: re-quoted handlers from src/api/list.ts; bumped verified_at
```

## Integrity rule

Before committing, check the message against the staged diff: every file
class the message claims must appear in the diff and vice versa. A mismatch
means the message (or the staging) is wrong — fix it, don't hand-wave.

## When commit-guided beats diff-guided

- Many small commits with good messages: parse messages, batch by module.
- One huge unstructured diff: ignore messages, work from the diff and the
  mapping table.
- Mixed history: structured commits first, then sweep the remainder by diff.
