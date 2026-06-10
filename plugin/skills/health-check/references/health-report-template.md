# Health Check Report Template

Written to `dev_docs/_analysis/health_check_report.md` (or shown inline for
quick mode). Keep it compact — findings, not narration.

```markdown
---
title: Doc Health Report — <date>
summary: Health assessment of dev_docs/ — score, findings, and recommended follow-up.
keywords: aicc | health check | report
scope: dev_docs
related_files: ../AI_Coding_Context.md
dependencies: none
verified_at: <YYYY-MM-DD>
---

# Documentation Health Report

## Verdict
- Score: <n>/100 (<grade>), mode: <quick|standard|deep>
- Recommendation: <none | incremental-update | doc-fallacy-fix | regenerate | systematic-review>

## Machine checks (aicc-doc-health)
| check | result | issues |
| structure / frontmatter / staleness / links / code-syntax | pass or n issues | top items |

## AI judgment checks
| check | sample | finding |
e.g. code-example drift (3 of 5 samples match), architecture mapping
(1 undocumented module), ignored maintenance triggers (2 commits).

## Findings by severity
- P0 (docs assert something false about the code): ...
- P1 (drift: outdated but not wrong-direction): ...
- P2 (cosmetic/staleness): ...

## Accepted issues (if completing /aicc:init acceptance)
| issue | justification | accepted by |

## Next steps
Concrete ordered list, each mapped to a skill or a small inline fix.
```
