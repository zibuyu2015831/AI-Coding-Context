---
name: doc-fallacy-fix
description: Use when documentation contains factual errors or claims contradicted by the code and the user wants them corrected — e.g. "the docs are wrong about X", "fix this doc error". Not for general staleness (use incremental-update) or assessment (use health-check).
---

# AICC Doc Fallacy Fix

Correct documentation that asserts something false, propagating the fix to
every doc that repeats the error.

## Step 1 — Intake and verify

Standardize the report: doc path, the claimed-wrong content, what the user
believes is correct, code evidence if given. Then VERIFY against the code
yourself — open the referenced source and confirm the doc is actually
wrong. A report that doesn't reproduce is a finding to return to the user,
not a fix to make.

Classify severity:

| level | meaning | examples |
| --- | --- | --- |
| P0 | actively misleads coding | wrong API/function names, broken code examples |
| P1 | wrong explanation | incorrect concept/process description |
| P2/P3 | cosmetic | formatting, spelling, dead anchors |

## Step 2 — Trace the blast radius

For P0/P1, find every doc repeating or depending on the false claim:

- grep dev_docs/ for the wrong identifier/claim text,
- follow frontmatter `dependencies` and `related_files` both directions,
- check the main doc's index/pattern sections (they quote sub-docs).

P2/P3: skip tracing unless asked; fix in place.

## Step 3 — Plan and confirm

Present: docs to change, exact locations, the corrected content (as
diffs), and risk notes. Offer: fix all affected docs / target doc only /
adjust / cancel. P0 fixes default to all-affected; never fix a P0 in one
doc while leaving the same falsehood elsewhere without saying so.

## Step 4 — Execute

- Apply the edits; re-quote corrected examples from the CURRENT code
  (`file:line`), redacted per the security rules.
- Bump `verified_at` on every corrected doc (the claims were re-verified
  by construction).
- Append an update record (date, error class, what was corrected, code
  evidence) to each touched doc.
- Commit separately (`doc(fix): ...` with WHAT/WHY/HOW) — the commit gate
  will validate the result; for many-doc fixes use a fix branch so the
  change is revertible in one step.

## Step 5 — Verify and close

`aicc-summary-validate --dir dev_docs/ --recursive` plus re-reading each
fix in context. Report: docs changed, severity, the commit hash, and the
one-command rollback (`git revert <hash>`). If the error suggests a
recurring cause (e.g. docs written from memory, no file:line discipline),
say so and recommend /aicc:systematic-review.
