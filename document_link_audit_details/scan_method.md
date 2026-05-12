# Scan Method

Generated: 2026-05-12

## Scope

- Markdown files scanned: 253.
- Source discovery used repository-local `*.md` files, excluding VCS/editor/system folders and the generated audit report files.
- Public layer, `dev/`, `dev/reference/`, and historical `dev/quality/audits/` Markdown files are included.
- External URLs are ignored; only repository-internal document links are classified.

## Extracted Link Forms

- Markdown inline links: `[text](target)`.
- Markdown image links: `![alt](target)`.
- Reference definitions: `[id]: target`.
- Frontmatter `related_files` and `dependencies`, split on `|`.

## Exclusions

- Fenced code blocks are ignored.
- Inline code spans are ignored for Markdown link extraction.
- `http://`, `https://`, `mailto:`, `tel:`, `javascript:`, `data:`, and `file:` targets are ignored.
- Pure same-document anchors such as `#section` are ignored in this audit because they do not point to other documents.
- Non-document targets with extensions other than `.md` / `.markdown` are ignored.

## Resolution Rules

- Relative targets are resolved from the source file directory.
- Targets beginning with `/` are resolved from the repository root.
- Targets beginning with repository top-level document roots such as `core/`, `guides/`, `templates/`, `agents/`, `workflows/`, `config/`, `tools/`, or `dev/` are resolved from the repository root.
- Directory links are valid only when the directory exists and contains `README.md`.
- `target.md#heading` validates both file existence and heading anchor existence.

## Issue Types

- `missing_target`: resolved target does not exist and does not match template/example heuristics.
- `missing_anchor`: target document exists, but the requested heading anchor was not found.
- `case_mismatch`: the path does not exist with exact casing, but a case-insensitive repository path exists.
- `directory_without_readme`: the target is a directory without `README.md`.
- `release_boundary_risk`: a public-layer document points into `dev/`, which is expected to be excluded from release artifacts.
- `example_or_template_reference`: the target looks like an illustrative placeholder or template path rather than a repository document.

## Raw Counts

- Internal document links identified: 894.
- Files with at least one internal document link: 188.
