# framework_contracts 测试数据

- `valid_template.md`
  - 输入：满足主文档契约的最小模板
  - 预期：`framework_contract_checker --check-template` 通过

- `missing_sections_template.md`
  - 输入：缺少 `业务模块映射` 和 `常见任务速查`
  - 预期：报出 `missing_required_section`

- `spec_workflow_drift_case/`
  - 输入：spec 未收录 `review/`，workflow 却把它当成标准路径
  - 预期：报出 `workflow_path_drift`
