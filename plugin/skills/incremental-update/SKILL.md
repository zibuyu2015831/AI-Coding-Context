---
name: incremental-update
description: Use when code changed (or a structured commit is provided) and the existing dev_docs/ must be updated to match — includes commit-guided sync and git-safety rules. Not for first generation (use init) or pure assessment (use health-check).
---

# AICC Incremental Update

Keep `dev_docs/` synchronized with code changes. Merges three clone-form
workflows: incremental update, commit-guided update, and git safety.

**Git safety is enforced, not advisory**: the plugin's hooks deny red-zone
git operations (force push, hard reset, history rewrite, protected-branch
commits) per `aicc.git_safety.mode`, and gate `git commit` on doc validity
per `aicc.git_safety.commit_gate`. This skill works WITH those hooks; never
try to talk the user around them.

## Step 1 — Detect what changed

Preferred order (degrade gracefully, note which source you used):

1. Structured commits: `git log --since=<last doc verified_at>` — commits
   whose body carries `WHAT:`/`WHY:`/`HOW:` lines are parsed directly (see
   [references/commit-guided.md](references/commit-guided.md)).
2. Plain git diff: `git diff --stat <last-sync>..HEAD` for changed files.
3. No git: file mtimes, or ask the user what changed.

If the number of unsynced commits is large (rule of thumb: more than ~10,
or the diff touches most modules), stop and recommend a fuller pass:
/aicc:health-check first, possibly regeneration via /aicc:init.

## Step 2 — Map changes to docs

For each changed file, find owning docs by:
1. frontmatter `related_files` match (exact path > parent dir),
2. the main doc's `Document Maintenance Triggers` table,
3. the mapping table in [references/change-doc-mapping.md](references/change-doc-mapping.md).

No match for a significant change → that is a coverage gap; propose a new
sub-doc or a main-doc section rather than silently skipping.

## Step 3 — Classify each change, pick the update strategy

| change class | strategy |
| --- | --- |
| implementation detail (internals, renames, optimizations) | refresh affected code snippets only |
| interface/logic (signatures, endpoints, schema, config) | update descriptions + snippets, bump `verified_at` |
| architecture (new module, framework change, restructure) | escalate: design first (/aicc:design-thinking — mandatory when `aicc.enforceDesignThinking` is true), update architecture docs + main doc, consider /aicc:adr |

## Step 4 — Apply updates

- Edit only the affected sections; keep surrounding prose intact.
- Updated snippets must be re-quoted from the CURRENT code (`file:line`),
  redacted per `${CLAUDE_PLUGIN_ROOT}/references/security-rules.md`.
- Bump `verified_at` only on docs whose claims you actually re-verified.
- Append an update record to each touched doc:
  date, trigger (commit id or change description), change class, sections
  touched.

## Step 5 — Verify and commit

1. `aicc-summary-validate --dir dev_docs/ --recursive` and
   `aicc-doc-health --mode quick` must be clean — the commit gate will run
   the same checks and block/ask on failure.
2. Show the user a compact summary: changed files -> updated docs ->
   change classes. Get confirmation before committing.
3. Commit docs with a structured message (`doc(sync): ...` with
   WHAT/WHY/HOW), respecting the yellow-zone rules in
   [references/commit-guided.md](references/commit-guided.md): never on a
   protected branch, no force operations — the guard hook enforces this.

## Git safety quick reference (enforced by hooks)

- **Red (denied)**: force push, `reset --hard`, `clean -f`, `rebase`,
  `branch -D`, remote branch/tag deletion, commit/push on protected
  branches (`aicc.git_safety.protected_branches`).
- **Yellow (your judgment + user confirmation; "strict" mode makes the
  hook ask)**: commit, push, branch creation.
- **Green (free)**: status, log, diff, add, pull, local checkout.
- Modes: `standard` (default), `strict`, `permissive` — set
  `aicc.git_safety.mode`. The commit gate (`commit_gate`: `ask`/`deny`/`off`)
  additionally validates changed dev_docs before any commit.
