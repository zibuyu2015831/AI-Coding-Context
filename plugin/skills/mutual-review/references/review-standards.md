# Review Standards by Change Type

What each change type's review must additionally probe, beyond the
reviewer's base dimensions. Pass bars rise with blast radius: refactors
are judged hardest, features most leniently.

## Feature

- Architecture consistency: fits existing layering/patterns; no module
  boundary violations.
- Technical debt: no unnecessary complexity or speculative generality.
- Tests planned for new behavior incl. boundaries and error paths.
- Docs: which dev_docs need updating (maintenance triggers), API docs for
  new endpoints.

## Bugfix (stricter than feature)

- Root cause identified and stated — a fix without a root-cause analysis
  is a P0 finding by itself.
- True fix vs workaround; are sibling occurrences of the same bug fixed?
- Minimal change: nothing unrelated smuggled in.
- Regression evidence: a test that fails before and passes after.
- Knowledge capture: troubleshooting insight recorded (knowledge base or
  doc) when non-obvious.

## Refactor (strictest)

- Justification: stated benefit and cost; "cleaner" alone is not enough.
- Impact map: dependents enumerated; behavior-preservation argument.
- Rollback strategy exists and is realistic.
- Staged: large refactors land in independently-safe steps.
- ADR: structural decisions recorded (/aicc:adr) — its absence on an
  architecture-changing refactor is a P1.

## Doc change

- Accuracy first: every claim checked against code; quoted `file:line`
  references verified; examples runnable.
- Clarity and structure; consistent terminology with sibling docs.
- Frontmatter updated (verified_at only if claims were re-verified).
- Related docs: cross-references updated both directions.
