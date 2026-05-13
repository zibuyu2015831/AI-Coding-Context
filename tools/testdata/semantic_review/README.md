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
