---
title: V3.x Comprehensive Review — 复审验证进度（断点续审支持）
summary: 对 2026-04-25 V3.x Comprehensive Review 全部 35 项 Issue 的二次复审进度跟踪；记录每条 Issue 的核查状态、结论与方案处置；支持跨会话断点续审
keywords: re-review | verification | resumable | aicc | v3.x
scope: 复审本轮 35 项 Issue 的真实性、描述准确性与修复方案最优性
verified_at: 2026-04-26
---

# V3.x Comprehensive Review — 复审验证进度

> **本文档用途**：记录二次复审进度，支持跨会话断点续审。下次会话开启时仅需读本文件即可恢复上下文。

---

## 📌 元信息

| 字段 | 值 |
|---|---|
| 启动日期 | 2026-04-26 |
| 复审依据 | `Issue_Tracking.md` 全部 35 项 Issue |
| 复审深度 | 全量 35 项逐条核查 |
| 复审视角 | 系统架构师 |
| 已修复项处置 | 回放 git diff 验证修复确实落地 |
| 修复方案处置 | 评估 + 补充 + 对重大缺陷方案重写 |
| 主审 AI | Claude Opus 4.7 (1M context) |
| 报告输出 | `Review_Verification_Report.md`（本目录下） |
| 预期退出条件 | 35 项全部完成核查并写入报告 |

---

## 📦 5 批次规划

| 批次 | 主题 | Issue 集合 | 数量 | 状态 |
|---|---|---|:-:|:-:|
| **B1** | 命名一致性 + 路径/边界 | 016, 029, 032, 002, 003, 022, 010 | 7 | ✅ 已完成 |
| **B2** | 文档漂移 + SSOT | 001, 011, 012, 014, 015, 013, 018, 023 | 8 | ✅ 已完成（复审 + 修复） |
| **B3** | dogfood 自指 + 合规扫描 | 034, 027, 024, 025, 035, 021 | 6 | ✅ 已完成（复审） |
| **B4** | 实体缺失 + 工作流闭环 | 017, 020, 026, 019 | 4 | ⏳ 待启动 |
| **B5** | 用户旅程 + 已修复回放 + 卫生 | 028, 030, 031, 033, 004, 005, 006, 007, 008, 009 | 10 | ⏳ 待启动 |

**状态图例**：⏳ 待启动 / 🔵 进行中 / ✅ 已完成

---

## 🎯 复审输出标准

每条 Issue 的复审结论必须输出 4 个字段：

1. **真实性**：✅ 真实存在 / ❌ 不存在 / ⚠️ 部分存在
2. **描述准确性**：✅ 准确 / ⚠️ 偏差（具体哪里）/ ❌ 严重失实
3. **方案评估**：✅ 通过 / 🟡 需补充 / 🔴 重大缺陷需重写
4. **架构师补充/重写**：原方案问题 + 推荐新方案（如有）

---

## 📋 单条 Issue 复审状态表

| ID | 主题 | 严重 | 视角 | Batch | 真实性 | 描述 | 方案 | 报告锚 |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| 001 | FRAMEWORK_CONTEXT vs PROGRESS 漂移 | 主要 | B | B2 | ✅ 真实 | ⚠️ 项数细节偏差 | ✅ 通过（统领条目） | B2#001 ✅ 已修复 |
| 002 | Public→dev/ 死链 | 主要 | A | B1 | ✅ 真实 | ✅ 准确 | ✅ 通过 | B1#002 ✅ 已修复 |
| 003 | audit_metadata.py 孤儿文件 | 次要 | C+A | B1 | ✅ 真实 | ✅ 准确 | 🟡 需补充判据→重写为"删除" | B1#003 ✅ 已修复 |
| 004 | dev/quality 编码乱码 | 次要 | C | B5 | ⏳ | - | - | - |
| 005 | Framework_Review_Guidelines 自相矛盾 | 主要 | B | B5 | ⏳ | - | - | - |
| 006 | 基础设施长期缺失 | 主要 | B+C | B5 | ⏳ | - | - | - |
| 007 | BY_DOCUMENT_TYPE 被引用但缺失 | 次要 | B | B5 | ⏳ | - | - | - |
| 008 | PROGRESS.md 末尾乱码+重复 | 次要 | C | B5 | ⏳ | - | - | - |
| 009 | dev/ 内部悬空引用 | 次要 | C | B5 | ⏳ | - | - | - |
| 010 | 文件位置疑似错误 | 建议 | C | B1 | ✅ 真实 | ✅ 准确 | 🟡 需补充更优目标位置 | B1#010 ✅ 已修复 |
| 011 | FRAMEWORK_CONTEXT 顶部摘要严重过时 | 主要 | B+A | B2 | ✅ 真实 | ✅ 准确 | 🟡 需补充（与 015 联动改分母） | B2#011 ✅ 已修复 |
| 012 | PROGRESS 自身内部不一致 | 次要 | B | B2 | ✅ 真实 | ✅ 准确 | ✅ 通过 | B2#012 ✅ 已修复 |
| 013 | 路径引用错误 | 次要 | B+C | B2 | ✅ 真实 | ✅ 准确 | ✅ 通过 | B2#013 ✅ 已修复 |
| 014 | 同一文档自相矛盾 | 建议 | B | B2 | ✅ 真实 | ✅ 准确 | ✅ 基本通过（措辞优化） | B2#014 ✅ 已修复 |
| 015 | 已完成但未登记（019） | 建议 | B+C | B2 | ✅ 真实 | ⚠️ 实体描述错误 | 🔴 重大缺陷已重写 | B2#015 ✅ 已修复 |
| 016 | AI_RULES.md 大小写不一致 | 主要 | A+B | B1 | ✅ 真实 | ⚠️ 漏报 .kiro/real_case 中 lowercase | 🟡 需补充 | B1#016 ✅ 已修复 |
| 017 | doc_health_checker 工具实体缺失 | 主要 | A+B | B4 | ⏳ | - | - | - |
| 018 | 路径假设错误 | 次要 | B | B2 | ✅ 真实 | ✅ 准确 | 🟡 需补充（"两层修复"思路） | B2#018 ✅ 已修复 |
| 019 | 端到端工作流缺失 | 主要 | A+B | B4 | ⏳ | - | - | - |
| 020 | complexity --check-doc-errors 参数不存在 | 次要 | A+B | B4 | ⏳ | - | - | - |
| 021 | 默认配置路径假设需明示 | 建议 | B+C | B3 | ✅ 真实 | ✅ 准确 | 🟡 需补充（推荐 fallback 选 B 覆盖 A + 双脚本对称） | B3#021 ✅ 已修复 |
| 022 | 目录命名规范不一致 | 主要 | B+C | B1 | ✅ 真实 | ✅ 准确 | ✅ 通过 | B1#022 ✅ 已修复 |
| 023 | README 索引覆盖率缺口 | 次要 | B+C | B2 | ✅ 真实 | ⚠️ language_specific 数字 5 实为 6 | 🟡 需补充 | B2#023 ✅ 已修复 |
| 024 | SOP 过度承诺 | 次要 | B | B3 | ✅ 真实 | ✅ 准确 | ✅ 通过（推荐选项 A，删除 2 项 + 重排序号 + 对齐 README） | B3#024 ✅ 已修复 |
| 025 | 措辞与策略不一致 | 建议 | B | B3 | ✅ 真实 | ✅ 准确 | ✅ 通过（重写 L44-L58，对齐 v2.0 三级口径） | B3#025 ✅ 已修复 |
| 026 | architecture_analyzer 工具不存在 | 次要 | B+C | B4 | ⏳ | - | - | - |
| 027 | 005 walkthrough 未提升至 Public | 建议 | A+B | B3 | ✅ 真实 | ⚠️ 源路径未对齐 B1#022 重命名 | 🟡 需补充（路径对齐 + frontmatter 联动 + 工具索引细化） | B3#027 ✅ 已修复（同步关闭 019） |
| 028 | quick_start 结构错乱+步骤跳号 | 严重 | A | B5 | ⏳ | - | - | - |
| 029 | AI_RULES.md 路径多版本不一致 | 主要 | A+B | B1 | ✅ 真实 | ⚠️ 误称权威源 + 错估 majority | 🔴 重大缺陷已重写 | B1#029 ✅ 已修复 |
| 030 | quick_start 过时框架名残留 | 主要 | A | B5 | ⏳ | - | - | - |
| 031 | README "3 步"计数错误 | 主要 | A | B5 | ⏳ | - | - | - |
| 032 | 主文档名 ai_coding_context 大小写 | 次要 | A+B | B1 | ✅ 真实 | ⚠️ 漏 workflows/generation_workflow.md L493 | 🟡 需补充 | B1#032 ✅ 已修复 |
| 033 | quick_start 推荐 find/cloc 与 V3.0 脱节 | 次要 | A | B5 | ⏳ | - | - | - |
| 034 | V3.0 强制 frontmatter 14% 自指 | 严重 | A+B | B3 | ✅ 真实 | ⚠️ templates 分母过期（B1#022 后 5/12 而非 5/29） | 🟡 需补充（验收双层门槛+CI gate 同步+dogfood 闭环验证） | B3#034 🟡 P0 已完成（10 文件 strict 通过；P1/P2 待后续） |
| 035 | 工具头部 docstring 不规范 | 建议 | C | B3 | ✅ 真实 | ✅ 准确 | ✅ 通过（直接使用 JSDoc 模板，参考 .py 内容质量） | B3#035 ✅ 已修复 |

---

## 🔁 断点续审协议

**若会话中断，下次会话开启需执行**：

1. 读取本文件 (`Review_Verification_Progress.md`) 获取批次状态
2. 读取已产出的 `Review_Verification_Report.md`
3. 找到第一条状态为 ⏳/🔵 的 Batch，从未完成的 Issue 继续
4. 完成单 Issue 后立即更新本文件的 Issue 状态表
5. 完成单 Batch 后立即更新批次状态为 ✅

**当前会话起点**：B1 启动前

---

## 📝 复审日志

> 简明记录每批次完成时间、关键发现、跨批次的系统性洞察。

### 启动期
- **2026-04-26**：复审计划设定 — 5 批次 / 全 35 项 / 评估+补充+必要重写 / 不动被审文件

### B1（命名一致性 + 路径/边界）
- 启动：2026-04-26
- 复审完成：2026-04-26
- **修复完成：2026-04-26** ✅
- **关键发现**：
  1. **029 方案有重大缺陷**：原推荐"统一为 dev_docs/AI_RULES.md"是少数派路径（仅 1 处）；实际仓库主流（17 处）使用 `dev_docs/rules/combined/AI_RULES.md`；按原方案修复将需改 17+ 文档而非 4。已重写：统一为 deep path，仅需改 2 处 + 新增 AI_ENTRY_POINT 术语表 1 行。
  2. **016/029 共同误判**：原 Issue 称"AI_ENTRY_POINT.md 术语表 L306 为权威源"，但术语表 L300-L310 **无 AI_RULES 行**，权威源不存在。需在 `core/framework_spec.md` 新建"标准产物路径"章节作为真正 SSOT。
  3. **016/032 漏报现象**：lowercase 形式在 .kiro/、dev/real_case/、workflows/generation_workflow.md L493 还有 3+ 处遗漏，原方案未覆盖。
  4. **003 应明确选 C 删除**：实读 audit_metadata.py 发现脚本检测的 `importance:` 字段不属框架标准、硬编码路径过时、无 main guard、违反 V3.0 双脚本红线 + docstring 红线。功能已被 summary_validator 取代。
  5. **002 自验 regex 漏洞**：原 Issue 验证命令的 `\.{0,2}` 仅匹配 ≤2 个点号，**漏 `../../dev/` 形式**。已补正确 regex。
  6. **010 更优归位**：advanced-audit-report 实为 010 优化点的资深审查报告。最佳归位是 `confirmed/010-cross-project-knowledge/senior_review_report.md`（与同优化点其他子文档并列），优于原方案 reference/ 或 quality/audits/。
  7. **横切洞察**：本批次的"权威源不存在"问题和 029 的 majority 误判共同指向 — **AICC 框架缺乏对"产物路径"的单一真相源（SSOT）**，这是命名一致性集群的根因。已在修复阶段完成 SSOT 建立。

- **修复成果汇总**（2026-04-26）：
  - 删除：`audit_metadata.py`（仓库根孤儿）
  - 重命名（git mv）：3 个目录（004/005/006-*.md/ → 去 .md 后缀）+ 1 个文件迁移（advanced-audit-report → confirmed/010/senior_review_report.md）
  - 新增章节：`core/framework_spec.md` 新增 "🗂️ 标准产物路径（SSOT）" 章节（命名规范集群的根因治理）；同步修复 framework_spec.md 标准目录结构未闭合代码块
  - 修订路径/大小写：8 文件共 9 处（path_a / generation_workflow / quick_start / templates/AI_RULES_TEMPLATE / templates/rules_README_TEMPLATE / .kiro/QUICK_START / AI_ENTRY_POINT × 2）
  - 死链清理：5 处真泄漏链接全部转为带"dev 分支可见"边界声明的文字描述（agents/_progress / workflows/doc_error_fix_workflow / core/SUMMARY_FORMAT_SPEC / core/design_decisions × 1）
  - 索引更新：`010-cross-project-knowledge.md` 子文档索引追加 senior_review_report 行；senior_review_report 头部加归位历史
  - **回归通过**：lowercase ai_rules.md / ai_coding_context.md 已清除（仅反例文档保留）；confirmed/.md/ 目录归零；仓库根 .py 归零；Public→dev/ 链接形式真泄漏归零

### B2（文档漂移 + SSOT）
- 启动：2026-04-26
- 复审完成：2026-04-26
- **修复完成：2026-04-26** ✅
- **关键发现**：
  1. **015 实体描述重大错误**：原 Issue 称"019 实体不存在 confirmed/ 档案，需创建"，但 `dev/V3.0/confirmed/019-systematic-review-framework.md` **单文件实体已存在**（24KB，符合 022 修复后的"单文件用 NNN-name.md"命名规范）。已重写：仅做 PROGRESS 登记，不重组实体。
  2. **011 与 015 联动**：011 修复推荐分母 (12/18)，但 015 落地后总数应为 19。修复时需先决策 015，再统一调整 011 的分母为 (13/19)。
  3. **014 措辞错误**：原方案推荐措辞列了"剩余 015"，但 015 实为已归档（PROGRESS L19），不应在"剩余"列出。已重写更精确表述。
  4. **001 项数细节偏差**：Issue 称顶部"8 项 P0 + 019 共 9 项"，实际仅 8 项总数（含 019）。本条作为统领可保留。
  5. **023 数字偏差**：Issue 称 language_specific 实际"5 项 + base/"，实测为 6 项；examples 21 vs 18 数字 ✓ 正确。
  6. **横切洞察 1：架构升级机会**。011/012/014/015 共同根因是"FRAMEWORK_CONTEXT 与 PROGRESS 双轨独立维护"。建议从根本上**改为层级关系（概览 + 详情）**：FRAMEWORK_CONTEXT 顶部摘要彻底简化为指针式（不再罗列编号），PROGRESS 作为单一详细清单。这是治理漂移集群的根本方案。
  7. **横切洞察 2：CI 防漂移**。建议加入 frontmatter 字段 `progress_synced_at`，并在 CI 校验"FRAMEWORK_CONTEXT 与 PROGRESS 的优化点编号集合 diff 应为空"。这与 B1 SSOT 章节配套，形成完整的漂移防御。
  8. **018 工具实体缺失暴露**：原文档假设的 doc_error/doc_fix 测试**根本不存在于任何位置**。改路径只能让命令"形式可执行"但仍无效。需"两层修复"：短期诚实记录、长期补全测试。
  9. **023 → 自指连锁**：dev/quality/README.md 自身索引数字与实际不符，是 dogfood 失败的另一证据（与 B3 的 034 frontmatter 14% 自指失败同源）— 索引数字也属"框架自己的产物自己应一致"。

- **修复成果汇总**（2026-04-26）：
  - 文档层级化：FRAMEWORK_CONTEXT 顶部 L11-L23 + 底部 L703-L716 + L25-L28 全部重写为 P0/P1/P2/V3.0+ 分组的进度概览，明示"以 PROGRESS 为 SSOT"
  - PROGRESS 漂移修正：L15-L19 总数 18→19；L18 已完成 11→13 项（加 011 + 019）；L34 P1 计数 011 🟢→✅（5 项全 ✅）+ 新增 V3.0+ 后期增益 1 项；L16 confirmed 13→14
  - 019 后期增益登记：PROGRESS 末尾追加专门小节，登记来源/实体/纳入说明
  - 路径修订：FRAMEWORK_CONTEXT L539-L540 reference/→core/
  - frontmatter 增强：FRAMEWORK_CONTEXT 新增 `progress_synced_at: 2026-04-26` 字段（漂移防御）；verified_at 同步刷新
  - 测试命令诚实化：doc_error_fix_workflow.md L484-L495 改为反映实际覆盖 + 明示 doc_error/doc_fix 测试待补全
  - README 索引修正：dev/quality/README.md agents 索引段补 _templates/（2 项）+ examples 21→18 + language_specific 7→6 + personas 加注口径
  - **附带发现（推迟到 B5 卫生批次）**：PROGRESS L86 误把已归档的 015-质量保证体系集成列为 P1 milestone 待办，与 L19 已归档 + L35 P2 矛盾。本批次仅严守 B2 复审范围，未顺手清理。同样 PROGRESS L282-L312 末尾段重复（与 008 同性质），亦推迟至 B5。
  - **回归通过**：FRAMEWORK_CONTEXT 与 PROGRESS 已完成项编号集合一致 = {001, 003, 004, 005, 006, 011, 012, 013, 014, 016, 017, 018, 019}（13 项）；分母 19 一致；011 状态全 ✅

### B3（dogfood 自指 + 合规扫描）
- 启动：2026-04-26
- 复审完成：2026-04-26
- **修复完成：2026-04-26** ✅（5 项 🟢 全闭环 + 034 P0 完成转 🟡 修复中）
- **关键发现**：
  1. **034 主体数据完全吻合**：实测 Public 总计 20/138=14% 与 Issue 完全一致；顶层入口、core/、workflows/、guides/、agents/、config/ 各项数字 100% 匹配。仅 templates 行实测 5/12=41%（Issue 5/29=17%）— B1#022 删除 .md/ 子目录后分母从 29 降至 12，结论方向不变（仍偏低）但数字过期需修订。
  2. **034 工具支持完备**：summary_validator.py 与 summary_extractor.py 双语言版本均存在并可用（CLI --help 通过）；`--strict --recursive` 模式可直接作 CI gate。
  3. **034 最讽刺自指失败**：`core/SUMMARY_FORMAT_SPEC.md`（规范源）自身**不带 frontmatter** — 规范不自证。补全此条具备符号意义。
  4. **027 源路径已被 B1#022 重命名连锁影响**：Issue 引用 `005-complexity-dashboard.md/walkthrough.md` 已过期，真实路径为 `005-complexity-dashboard/walkthrough.md`。这是首次出现"前批次修复对后批次 Issue 描述的连锁影响"，提示 B4/B5 复审时需特别注意。
  5. **021 双脚本对称问题**：JS 镜像 `tools/js/complexity_scanner.js` 同样硬编码 `dev_docs/complexity/config.yaml`，按 V3.0 红线必须双版本同步修复。
  6. **021 推荐覆盖原方案**：原推荐选项 A（仅文档说明）成本低但增加 dogfood 摩擦；推荐改为选项 B（fallback：dev_docs/ → dev/ → 内置默认），对治理 dogfood 集群是杠杆点。
  7. **024 同步 README 漂移**：dev/quality/README.md L62-L73 已用"5 件套"，Framework_Review_Guidelines.md L443-L504 仍列 10 项 — 自指连锁。修复时需对齐为"必需 5 件套 + 可选附加"分组。
  8. **025 v2.0 三级口径已存在**：dev/quality/README.md L18 + L110-L118 已宣告分级策略，但 L44-L58 contexts 章节未同步措辞。修复方案是用三级语境重写。
  9. **035 双脚本对称 32/33**：仅 aac_validator.js 缺规范 docstring；建议参考 .py 版的实际内容质量（含功能说明/使用方法/输出/退出码/零依赖红线说明）而非 Issue 的精简模板。
  10. **027 段落名修正**（精修阶段发现）：原 Issue 称需在"工作流路由"段补索引，但 AI_ENTRY_POINT.md 实际**无此段名**。当前真实段为 L317"工具脚本标准"、L371"🗺️ 工作流全景图"、L439"📁 框架文件索引"。修复时需对齐到实际段落。
  11. **021 内部隐性 bug**（精修阶段实地核查发现）：`tools/py/complexity_scanner.py` L520-L585 的 `load_config()` 已含"file 不存在 → fallback 内置默认"逻辑（仅对 path != ""）；但 L363、L434 等内部调用点直接传**空字符串** `load_config("")`，意味着 `args.config` 的 CLI 值**根本未流入这些调用点**。这是与 021 同源但更深的结构性问题，修复方案已扩展为 fallback + 内部调用点统一。
  12. **024 当前结构观察**（精修阶段发现）：Guidelines L445 章节是**平铺 10 项**清单，并非"必需 + 可选"二级结构。仅删除 5/6 两项后仍是平铺，与 README L62-L73"5 件套+可选附加"不一致。修复方案已扩展为重组为二级结构。
  13. **横切洞察 1：dogfood 失败集群**。034 + 027 + 021 + 035 共同指向"AICC 框架对自身的 dogfood 能力薄弱"，是 R5（自指一致性）的本质性问题。建议在 SSOT 章节追加"框架自审 mode"约定。
  14. **横切洞察 2：dev_docs/ vs dev/ 二元结构未在工具行为中显式处理**。021 暴露的根因 — 二元约定仅在文档层存在，工具默认值单方向硬编码。fallback 是治理点。
  15. **横切洞察 3：SOP 与策略漂移集群**。024 + 025 共同指向"SOP 文档随策略迭代时未同步"，与 B2 的 014 同源（R2 V3.0 一致性）。建议把"策略变更必须同步刷新 SOP 引用"列入 quality 体系的 verification 清单。
  16. **横切洞察 4：B1 修复连锁**。027 是首条因前批次修复而过期的 Issue，需在最终系统性发现章节中归并这类"修复链"问题，避免被遗漏。

- **修复优先级与执行顺序**（架构师推荐）：
  1. **021** + **035**（独立 + tools/ 卫生）：先扫平工具 dogfood 阻碍
  2. **025** + **024**（同源 SOP 漂移）：可同批
  3. **027**（含创建 workflows/complexity_alert_workflow.md，自带 frontmatter，作为 #034 工程的样板）
  4. **034 P0**（含顶层入口 + core/）：最后启动，避开与 027 对 AI_ENTRY_POINT.md 的并发编辑
  - 原因：避免重复编辑同一文件（AI_ENTRY_POINT.md 在 027 中需补索引，在 034 P0 中需加 frontmatter）+ 让 034 修复期间的 dogfood 操作（频繁调用 summary_validator/complexity_scanner）能依赖 021/035 的修复成果

- **修复成果汇总**（2026-04-26）：
  - **021**：`tools/py/complexity_scanner.py` + `tools/js/complexity_scanner.js` 双脚本 `load_config` 改为 fallback 链（CLI → dev_docs/ → dev/ → 内置）；CLI default 改为空字符串以触发 fallback；--help 文本同步；框架仓库根直跑无需 --config 参数。
  - **035**：`tools/js/aac_validator.js` 添加完整 JSDoc 块（参考 .py 内容质量：功能/用法/参数/输出/退出码/零依赖红线说明）；JS 主脚本 docstring 合规率 100%。
  - **025**：`dev/quality/README.md` L44-L58 重写为"按需生成"语境；删除"每个 🔴 文档对应一份"承诺；引用 v2.0 三级策略章节。
  - **024**：`dev/quality/Framework_Review_Guidelines.md` 重组为"必需 5 件套（Plan/Issue_Tracking/Progress_Tracking/Review_Log/Review_Checklist）+ 可选附加（4 项）"二级结构；删除 Review_Data.zip / Assessment_Dashboard.html；与 README L62-L73 完全同口径。
  - **027**：新建 `workflows/complexity_alert_workflow.md`（带完整 frontmatter，作为 workflows/ 第 2 个样板）；从 005 walkthrough.md 提取场景 A-E 转写为面向 AI 的 SOP；`AI_ENTRY_POINT.md` 工具表补 5 行（complexity_scanner.py/.js + report_generator.py/.js + notifier.py）+ 框架文件索引补 1 行；`workflows/path_d_specific_tasks.md` 任务索引表 + 末尾 @complexity 章节（含简化执行链 + fallback 说明）。**同步关闭 019**（端到端工作流缺失）。
  - **034 P0**（10 文件）：3 顶层入口（AI_ENTRY_POINT/README/CONTRIBUTING）+ 7 个 core/（SUMMARY_FORMAT_SPEC/framework_spec/design_decisions/language_rules/security_rules/update_triggers/project_types/README）补 frontmatter；全 10 文件 strict 校验通过；core/ 合规率 66%→100%；Public 总计 14%→22%（20/138 → 31/139）；顶层入口 0/3 → 3/3；规范源 `core/SUMMARY_FORMAT_SPEC.md` 自带示范级 frontmatter 实现自证。
  - **回归通过**：B3 全 6 项目标项全部 PASS（21 双脚本直跑、24/25 措辞与结构、027 三处索引 + frontmatter、034 P0 strict 校验、35 JSDoc 100% 合规）

### B4（实体缺失 + 工作流闭环）
- 启动：—
- 完成：—
- 关键发现：—

### B5（用户旅程 + 已修复回放 + 卫生）
- 启动：—
- 完成：—
- 关键发现：—

---

**文档版本**：v1.0
**创建日期**：2026-04-26
**维护者**：复审主审（Claude Opus 4.7）
