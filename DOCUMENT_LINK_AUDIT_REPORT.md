# Document Link Audit Report

Generated: 2026-05-12

## Executive Summary

- Markdown files scanned: **253**
- Internal document links identified: **894**
- Issue records: **51**
- Real breakage / release-risk records excluding template examples: **28**
- Files with real breakage / release-risk records: **20**

## Issue Counts

| Type | Count |
|---|---:|
| `missing_target` | 9 |
| `missing_anchor` | 10 |
| `case_mismatch` | 0 |
| `directory_without_readme` | 6 |
| `release_boundary_risk` | 3 |
| `example_or_template_reference` | 23 |

## Severe Issues

This section excludes `example_or_template_reference` so template placeholders do not hide actionable breakage.

| Type | Source | Line | Target | Resolved |
|---|---|---:|---|---|
| `missing_target` | `agents/_progress/implementation_progress.md` | 7 | `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md` | `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md` |
| `missing_target` | `core/project_types.md` | 6 | `core/project_types/*.md` | `core/project_types/*.md` |
| `missing_target` | `core/SUMMARY_FORMAT_SPEC.md` | 6 | `dev/V3.0/confirmed/012-mandatory-doc-summary` | `dev/V3.0/confirmed/012-mandatory-doc-summary` |
| `missing_target` | `dev/architecture/decisions/002-layered-documentation.md` | 6 | `AI_Coding_Context.md` | `dev/architecture/decisions/AI_Coding_Context.md` |
| `missing_target` | `dev/architecture/decisions/002-layered-documentation.md` | 6 | `dev_docs/*` | `dev/architecture/decisions/dev_docs/*` |
| `missing_target` | `dev/architecture/decisions/002-layered-documentation.md` | 7 | `001-markdown-as-first-class-doc` | `dev/architecture/decisions/001-markdown-as-first-class-doc` |
| `missing_target` | `dev/architecture/evolution.md` | 6 | `dev_docs/architecture/decisions/*.md` | `dev/architecture/dev_docs/architecture/decisions/*.md` |
| `missing_target` | `dev/reference/ai-coding-prompt-java-main/README.md` | 471 | `LICENSE` | `dev/reference/ai-coding-prompt-java-main/LICENSE` |
| `missing_target` | `workflows/complexity_alert_workflow.md` | 7 | `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` | `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` |
| `missing_anchor` | `agents/personas/README.md` | 202 | `../README.md#角色索引` | `agents/README.md` |
| `missing_anchor` | `AI_ENTRY_POINT.md` | 597 | `./workflows/detection_workflow.md#环境预检` | `workflows/detection_workflow.md` |
| `missing_anchor` | `guides/documentation_maintenance.md` | 320 | `../templates/GENERATION_PLAN_TEMPLATE.md#质量检查清单` | `templates/GENERATION_PLAN_TEMPLATE.md` |
| `missing_anchor` | `templates/HEALTH_CHECK_REPORT_TEMPLATE.md` | 540 | `../AI_ENTRY_POINT.md#场景4-文档健康度检查` | `AI_ENTRY_POINT.md` |
| `missing_anchor` | `workflows/document_health_check.md` | 1411 | `../AI_ENTRY_POINT.md#场景4-文档健康度检查` | `AI_ENTRY_POINT.md` |
| `missing_anchor` | `workflows/path_a_first_generation.md` | 338 | `./decision_workflow.md#复杂度检测` | `workflows/decision_workflow.md` |
| `missing_anchor` | `workflows/path_a_first_generation.md` | 930 | `../AI_ENTRY_POINT.md#路由索引` | `AI_ENTRY_POINT.md` |
| `missing_anchor` | `workflows/path_b_health_check.md` | 722 | `../AI_ENTRY_POINT.md#路由索引` | `AI_ENTRY_POINT.md` |
| `missing_anchor` | `workflows/path_c_incremental_update.md` | 618 | `../AI_ENTRY_POINT.md#路由索引` | `AI_ENTRY_POINT.md` |
| `missing_anchor` | `workflows/path_d_specific_tasks.md` | 693 | `../AI_ENTRY_POINT.md#路由索引` | `AI_ENTRY_POINT.md` |
| `directory_without_readme` | `core/SUMMARY_FORMAT_SPEC.md` | 405 | `../guides/examples/summary_examples/` | `guides/examples/summary_examples` |
| `directory_without_readme` | `dev/FRAMEWORK_CONTEXT.md` | 6 | `dev/plan/` | `dev/plan` |
| `directory_without_readme` | `dev/FRAMEWORK_CONTEXT.md` | 722 | `./plan/` | `dev/plan` |
| `directory_without_readme` | `guides/generation_workflow.md` | 605 | `../templates/` | `templates` |
| `directory_without_readme` | `workflows/generation_workflow.md` | 1100 | `../templates/` | `templates` |
| `directory_without_readme` | `workflows/shared/README.md` | 27 | `../` | `workflows` |
| `release_boundary_risk` | `agents/_progress/implementation_progress.md` | 7 | `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md` | `dev/V3.0/confirmed/001-ai-agent-library/001-ai-agent-library.md` |
| `release_boundary_risk` | `core/SUMMARY_FORMAT_SPEC.md` | 6 | `dev/V3.0/confirmed/012-mandatory-doc-summary` | `dev/V3.0/confirmed/012-mandatory-doc-summary` |
| `release_boundary_risk` | `workflows/complexity_alert_workflow.md` | 7 | `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` | `dev/V3.0/confirmed/005-complexity-dashboard/walkthrough.md` |

## Directory Summary

| Directory | Total Issues | missing_target | missing_anchor | case_mismatch | release_boundary_risk | directory_without_readme | example_or_template_reference |
|---|---:|---:|---:|---:|---:|---:|---:|
| `.` | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| `agents` | 7 | 1 | 1 | 0 | 1 | 0 | 4 |
| `core` | 4 | 2 | 0 | 0 | 1 | 1 | 0 |
| `dev/FRAMEWORK_CONTEXT.md` | 2 | 0 | 0 | 0 | 0 | 2 | 0 |
| `dev/architecture` | 6 | 4 | 0 | 0 | 0 | 0 | 2 |
| `dev/quality` | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| `dev/reference` | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `guides` | 2 | 0 | 1 | 0 | 0 | 1 | 0 |
| `templates` | 9 | 0 | 1 | 0 | 0 | 0 | 8 |
| `workflows` | 13 | 1 | 6 | 0 | 1 | 2 | 3 |

## Highest-Impact Source Files

| Source | Real Issue Records |
|---|---:|
| `core/SUMMARY_FORMAT_SPEC.md` | 3 |
| `dev/architecture/decisions/002-layered-documentation.md` | 3 |
| `agents/_progress/implementation_progress.md` | 2 |
| `dev/FRAMEWORK_CONTEXT.md` | 2 |
| `workflows/complexity_alert_workflow.md` | 2 |
| `workflows/path_a_first_generation.md` | 2 |
| `agents/personas/README.md` | 1 |
| `AI_ENTRY_POINT.md` | 1 |
| `core/project_types.md` | 1 |
| `dev/architecture/evolution.md` | 1 |
| `dev/reference/ai-coding-prompt-java-main/README.md` | 1 |
| `guides/documentation_maintenance.md` | 1 |
| `guides/generation_workflow.md` | 1 |
| `templates/HEALTH_CHECK_REPORT_TEMPLATE.md` | 1 |
| `workflows/document_health_check.md` | 1 |
| `workflows/generation_workflow.md` | 1 |
| `workflows/path_b_health_check.md` | 1 |
| `workflows/path_c_incremental_update.md` | 1 |
| `workflows/path_d_specific_tasks.md` | 1 |
| `workflows/shared/README.md` | 1 |

## Recommended Fix Order

1. Fix `missing_target` in public-layer and workflow/core documents first, because those links are visible to release users and AI entry flows.
2. Fix `case_mismatch` next; these links may work on case-insensitive local filesystems but fail on GitHub or Linux.
3. Fix `missing_anchor` after path fixes, because anchors are easiest to validate once target files are stable.
4. Decide whether public-layer links into `dev/` should be removed, copied into release documentation, or intentionally documented as non-release references.
5. Review `example_or_template_reference` only for clarity; these were not counted as real breakage.

## Detail Files

- `document_link_audit_details/all_links.md`: all identified internal document links.
- `document_link_audit_details/issues.md`: every issue record with source file, line, raw link, resolved target, and classification.
- `document_link_audit_details/scan_method.md`: scan scope, extraction rules, and classification definitions.
- `document_link_audit_details/review.md`: strict post-audit review notes, verification commands, classification caveats, and feasible fix guidance.

## Strict Review Status

This report was rechecked against the current repository on 2026-05-12. The review found one inaccurate `Raw Link` transcription in `issues.md` and one misclassified reference-import `LICENSE` link. Both were corrected; the total issue-record count did not change, while `missing_target`, `example_or_template_reference`, and non-template issue totals changed accordingly. See `document_link_audit_details/review.md` for the verification evidence and remediation notes.
