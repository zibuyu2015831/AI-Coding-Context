# Knowledge Entry Template

File: `dev_docs/knowledge/<category>/<kebab-case-name>.md`
(e.g. `troubleshooting/websocket-reconnect-storm.md`)

```markdown
---
title: <short, problem-shaped title>
summary: <the problem and the proven solution in 1-2 sentences — this is what search hits>
keywords: <tech> | <symptom> | <pattern name>
scope: <where this applies: stack, versions, project shape>
related_files: <code that implements/demonstrates it here, or none>
dependencies: none
verified_at: <YYYY-MM-DD>
---

# <title>

## Problem
Symptoms and context: what was observed, in what environment, what made
it non-obvious.

## Root cause
The actual mechanism — not just "what fixed it".

## Solution
The working approach, with the essential code (redacted, runnable):

```<lang>
<minimal working core>
```

## Key points & caveats
- Why this works; what it depends on.
- Where it does NOT apply (versions, scales, constraints).
- Side effects worth knowing.

## References
Links to issues, docs, or the commit where this landed.
```

Index line for `dev_docs/knowledge/README.md`:
`- [<title>](<category>/<file>.md) — <one-line trigger>`
