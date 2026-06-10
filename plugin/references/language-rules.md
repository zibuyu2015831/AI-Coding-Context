# Documentation Language Rules

How AICC decides which natural language generated docs use.

1. Priority: `aicc.documentLanguage` setting > explicit user request in the
   conversation > English default.
2. Confirm the language once, at the start of /aicc:init, before any scanning
   or generation; record the choice so it is never re-asked.
3. The choice applies to the whole doc set: main doc, sub-docs, AI_RULES,
   knowledge and plan docs. One generation cycle uses one language — never
   switch mid-run.
4. Frontmatter field NAMES stay English regardless of content language (the
   validators key on them).
5. Code identifiers follow the project's own conventions; comments inside
   generated examples follow the chosen doc language.
6. If the user later changes `aicc.documentLanguage`, new and updated docs
   use the new language; a full re-translation is a separate, explicit task.
