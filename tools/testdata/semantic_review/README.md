# semantic_review 测试数据

- `conflict_case/`
  - 目标：验证事实源冲突检查
  - 预期：`fact_conflict`

- `metric_drift_case/`
  - 目标：验证量化声明复核
  - 预期：`metric_drift`

- `test_topology_case/`
  - 目标：验证 `examples/**/tests/` 漏覆盖
  - 预期：`uncovered_test_topology`

- `combined_case/`
  - 目标：供 dogfood 同时运行 `doc_health_checker` 和 `semantic_review_checker`
  - 预期：
    - `doc_health_checker --full-check` 通过
    - `semantic_review_checker --full-check` 报出事实冲突、量化失真
    - `test_topology_case/` 单独用于验证嵌套测试目录漏覆盖

- `linguacafe_phase1_progress_only_case/`
  - 目标：复现 LinguaCafe 第三轮暴露的 Phase 1 progress-only PASS 漏检
  - 预期：`evidence_level_completeness`、`project_analysis_issue_status_missing`、`phase1_progress_only_review`、`confirmable_fact_misclassified`、`project_positioning_coverage_missing`

- `linguacafe_phase1_reviewed_case/`
  - 目标：验证修正后的 Phase 1 三件套可通过语义复查
  - 预期：`semantic_review_checker --full-check` 通过
