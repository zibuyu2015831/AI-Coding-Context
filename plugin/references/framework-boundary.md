# Framework Boundary

What AICC may and may not treat as user-project content.

## Never analyze as project code

- The AICC plugin's own files (everything under the plugin install dir).
- Legacy clone-form framework dirs if present in the repo:
  `ai_coding_context/`, `core/`, `workflows/`, `templates/`, `agents/`,
  `tools/`, `guides/`, `config/` (detect via an `AI_ENTRY_POINT.md` file).
- AICC analysis artifacts: `dev_docs/_analysis/` (generation plan, analysis
  report, progress record) — these describe the docs, not the project.
- Build artifacts and dependencies: `node_modules/`, `venv/`, `.venv/`,
  `dist/`, `build/`, `target/`, `__pycache__/`, coverage output.
- VCS and IDE metadata: `.git/`, `.svn/`, `.idea/`, `.vscode/`, editor swap
  files.

## Always treat as project content

- Source dirs (`src/`, `lib/`, `app/`, `api/`, `services/`, ...).
- Project config (`package.json`, `pyproject.toml`, `go.mod`, `pom.xml`,
  `.env.example`, CI config).
- Project docs (`README.md`, `docs/`, `CONTRIBUTING.md`, `CHANGELOG.md`).
- Generated AICC docs themselves: `dev_docs/*.md`, `dev_docs/rules/`,
  `dev_docs/knowledge/`, `dev_docs/plans/`.

## Ownership

- AICC owns `dev_docs/` layout and frontmatter format; it never rewrites
  project source as part of doc generation.
- The commit gate validates only `dev_docs/**/*.md`; other markdown in the
  repo is the project's own business.
- When a boundary is ambiguous, list the candidates, ask the user, and record
  the decision in `dev_docs/_analysis/generation_plan.md`.
