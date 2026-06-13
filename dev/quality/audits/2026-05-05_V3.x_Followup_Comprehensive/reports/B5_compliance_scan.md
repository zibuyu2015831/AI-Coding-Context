---
title: AICC V3.x Follow-up Comprehensive Review — B5 Compliance Scan
summary: B5 批量合规扫描结果，覆盖 frontmatter、双脚本对称、零依赖、Public→dev 边界泄漏与关键 frontmatter 完整性。
keywords: b5 | compliance | frontmatter | symmetry | boundary
scope: 2026-05-05 批量合规扫描
verified_at: 2026-05-05
dependencies: tools/py/summary_validator.py | tools/py/doc_health_checker.py | dev/quality/audits/2026-05-05_V3.x_Followup_Comprehensive/Issue_Tracking.md
---

# AICC V3.x Follow-up Comprehensive Review — B5 Compliance Scan

## 主要结果

### 1. Frontmatter dogfood 问题继续扩大证据面，但需区分真实缺陷与校验口径问题

新增扫描结果：

- `agents/`：`59 / 59` strict invalid，全部缺少 YAML frontmatter
- `config/`：`3 / 3` strict invalid
  - `config/README.md`、`config/MIGRATION_GUIDE.md`：无 frontmatter，属于真实缺陷
  - `config/CONFIG_TEMPLATE.md`：模板型配置文件，不满足 strict 必填字段要求，需单独界定验收口径
- `templates/`：`29 / 29` strict invalid
  - 多数为模板占位 `verified_at` 或占位路径，说明当前校验器不具备模板模式
  - `templates/rules/AI_RULES_STANDARD_TEMPLATE.md` 与 design_thinking prompts 无 frontmatter，这部分才更接近真实缺陷

关键补充证据：

- `workflows/complexity_alert_workflow.md` 虽有 frontmatter，但 `summary_validator --strict` 报缺 `related_files` 与 `dependencies`
- `guides/quick_start.md` 严格校验通过，说明并非整个 Public 层都未治理，而是治理分布极不均匀

结论：

- 这些结果不应粗暴视为同一种问题：
  - 可直接归入 `AICC-20260505-001` 的是 Public 非模板文档缺 frontmatter、以及字段缺失类问题
  - 需要单独定义修复策略的是模板文件与 `summary_validator --strict` 的口径冲突
- `034` 的当前问题不仅是“有没有 frontmatter”，还包括“frontmatter 是否满足 012 规则要求”，但模板文件是否必须 strict 通过需要先裁定

### 2. 双脚本主脚本对称保持稳定

统计结果：

- `tools/py` 主脚本：`34`
- `tools/js` 主脚本（排除 `*.test.js`）：`34`
- `tools/js` 额外测试文件：`3`

`comm -3` 结果为空，说明主脚本镜像集合一致。

### 3. 零依赖红线未见回退

扫描结果未发现实际引入外部库的代码使用：

- 未发现 `js-yaml` / `axios` / `requests` / `numpy` / `pandas` 等真实依赖导入
- `tools/js/aac_validator.js` 明确声明“不引入 js-yaml”
- `notifier.py` / `notifier.js` 仅在说明文案中提及未来可安装 `requests` / `axios`，非当前依赖

### 4. Public → dev/ 边界仍封闭

Public 层 markdown 死链 grep：

```bash
grep -rnE '\]\([^)]*dev/[^)]*\)' ...
```

结果为空，说明没有新的 Public→`dev/` markdown 链接泄漏。

## B5 裁定

- 没有发现新的边界泄漏、双脚本失衡或零依赖回退
- 本轮系统性主风险仍集中在 `AICC-20260505-001`：
  - `agents/`、`workflows/`、`guides/` 与 `config/` 中非模板说明文档存在真实 frontmatter 缺口
  - 个别工作流已开始补 frontmatter，但字段完整性仍不足
  - `templates/` 暴露出的是“模板占位符 vs strict 校验器”的设计缺口，应单独收口
- 到 B5 为止，本轮新增问题仍然只有：
  - `AICC-20260505-002`
  - `AICC-20260505-003`
  - 以及历史问题 `AICC-20260505-001` 的持续未闭合
