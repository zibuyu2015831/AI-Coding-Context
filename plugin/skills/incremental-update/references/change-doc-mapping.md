# Change -> Doc Mapping

Default mapping from code-change class to the docs that must be updated.
The project's own main-doc `Document Maintenance Triggers` table overrides
these defaults where they conflict.

| change class | detection signature | docs to update | strategy |
| --- | --- | --- | --- |
| new module/service | new top-level dir with several files | main doc (module mapping + index) + architecture doc | architecture (escalate) |
| new API endpoint | new route/handler | api doc | interface |
| signature change | params/return type changed | owning module doc | interface |
| DB schema change | migration / model change | database doc | interface |
| new dependency | lockfile/manifest change | main doc stack section + owning doc | interface |
| config/constants change | config files, .env.example | configuration doc (or main doc) | interface |
| internal optimization | same signature, new body | owning doc's code snippets | implementation |
| rename (local scope) | identifier rename | owning doc's code snippets | implementation |
| error-handling addition | new try/catch, validation | owning doc (brief note) | implementation |
| test addition | new test files | testing doc if present | implementation |
| framework upgrade | major version bump | main doc + every doc citing the framework | architecture (escalate) |
| directory restructure | files moved across dirs | main doc key-directories + all affected docs | architecture (escalate) |

Notes:

- "interface" strategy always bumps `verified_at`; "implementation" usually
  does not (content stayed true, only the snippet refreshed).
- Architecture-class changes also trigger /aicc:adr when a real decision was
  made (not just mechanical moves).
- A change class with no owning doc is a coverage gap — propose the doc,
  don't skip.
