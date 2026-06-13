import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PY_CHECKER = ROOT / "tools" / "py" / "doc_health_checker.py"
JS_CHECKER = ROOT / "tools" / "js" / "doc_health_checker.js"


MAIN_DOC_BASE = """---
title: 示例
summary: 示例摘要，长度足够用于通过 frontmatter 检查。
keywords: example | test | aicc
scope: test
related_files: core/framework_spec.md
dependencies: 无
verified_at: 2026-05-12
---

# AI 编码上下文

## 📊 项目概览
## 📂 关键目录速查
## 🎯 场景快速导航
## 🚀 文档索引
## 🛠️ 开发流程规范
## 💻 核心代码模式
## 📋 命名规范
## 🏢 业务模块映射
## ⚠️ AI 编码禁忌
## 🔧 常见任务速查
"""

GENERATION_PLAN_BASE = """# 文档生成方案模板

## 🎯 任务复杂度评估 (Complexity Assessment)

## ⚠️ 风险点与注意事项

## 🤝 交互策略 (Interaction Strategy)

## 📚 第三阶段：子文档规划（待审核）

## 📊 质量保证措施

## 🧾 证据与验证记录

## 🔎 Phase 1 方案复查清单
"""

GENERATION_PROGRESS_BASE = """# 文档生成进度记录

> **开始时间**: 2026-05-12 10:00
> **最后更新**: 2026-05-12 10:30
> **当前状态**: 生成中
> **流程阶段进度**: Step 4/8，当前处于方案生成
> **产物完成度**: 1/3，已完成部分 _analysis 产物
> **当前 gate**: Phase 1 自检
> **下一步动作**: 继续生成
> **正式生成授权**: 未授权

## 🎯 总体步骤进度

## 📝 逐文档完成状态

## 📊 统计信息

- **总任务数**: 3
- **已完成数**: 1
"""

PHASE1_CONFIRMED_RECORD = """
## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-12 10:30
- **review_completed_at**: 2026-05-12 10:40
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **manual_review_summary**: 已复查
- **writeback_summary**: 已更新 generation_plan.md
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过
- **user_confirmation_status**: confirmed
- **formal_generation_authorization**: user_confirmed
- **authorization_source_summary**: 用户确认方案审核通过

### machine_checks

| phase | tool | implementation | command | exit_code | issue_count | status | required | disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| phase1_review | summary_validator | python | `python3 tools/py/summary_validator.py --dir dev_docs/_analysis --recursive --strict` | 0 | 0 | PASS | yes | verified |
| phase1_review | doc_health_checker | python | `python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | 0 | 0 | PASS | yes | verified |
| phase1_review | doc_health_checker | js | `node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | 0 | 0 | PASS | yes | verified |
| phase1_review | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | yes | verified |
| phase1_review | semantic_review_checker | js | `node tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | yes | verified |

### phase1_review_verdict

| field | value |
| --- | --- |
| verdict | USER_APPROVED_FORMAL_GENERATION |
| reason | 用户已确认方案 |
| can_generate_formal_docs | yes |
| user_confirmation_required | yes |
| next_action | 执行正式生成 |
"""

HEALTH_REPORT_BASE = """# 首版文档质量验收报告

## 总体结论

- **最终 verdict**: PASS

## machine_checks

| round | tool | implementation | command | exit_code | issue_count | status | disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | summary_validator | python | `python3 tools/py/summary_validator.py --dir dev_docs --recursive --strict` | 0 | 0 | PASS | metadata-only |
| 1 | doc_health_checker | python | `python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | 0 | 0 | PASS | verified |
| 1 | doc_health_checker | js | `node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | 0 | 0 | PASS | verified |
| 1 | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | verified |
| 1 | semantic_review_checker | js | `node tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | verified |

## accepted_issues

无 accepted issue
"""


def _run_json(cmd):
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    return result, payload


class TestDocHealthCheckerCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="doc-health-checker-"))
        self.dev_docs = self.tmpdir / "dev_docs"
        (self.dev_docs / "_analysis").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _write_valid_bundle(self):
        (self.dev_docs / "AI_Coding_Context.md").write_text(MAIN_DOC_BASE, encoding="utf-8")
        (self.dev_docs / "_analysis" / "generation_plan.md").write_text(GENERATION_PLAN_BASE, encoding="utf-8")
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(GENERATION_PROGRESS_BASE, encoding="utf-8")

    def _write_valid_first_release_bundle(self):
        self._write_valid_bundle()
        progress = GENERATION_PROGRESS_BASE.replace(
            "> **当前状态**: 生成中",
            "> **当前状态**: 首版建议通过",
        ).replace(
            "> **产物完成度**: 1/3，已完成部分 _analysis 产物",
            "> **产物完成度**: 正式文档 1/1，_analysis 产物 4/4，总文件数 4",
        ).replace(
            "> **当前 gate**: Phase 1 自检",
            "> **当前 gate**: 首版质量验收",
        ).replace(
            "> **下一步动作**: 继续生成",
            "> **下一步动作**: 等待用户确认首版验收",
        ) + "\n## 🔎 首版质量验收记录\n\n首版验收 verdict = PASS\n"
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        (self.dev_docs / "_analysis" / "health_check_report.md").write_text(HEALTH_REPORT_BASE, encoding="utf-8")

    def test_help_mentions_new_checks_python(self):
        result = subprocess.run(
            ["python3", str(PY_CHECKER), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--check-required-sections", result.stdout)
        self.assertIn("--check-template-residue", result.stdout)
        self.assertIn("--check-run-record-integrity", result.stdout)
        self.assertIn("--check-plan-review", result.stdout)

    def test_required_sections_passes_for_complete_main_doc(self):
        self._write_valid_bundle()
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-required-sections",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["summary"]["passed"])
        self.assertIn("required_sections", payload["checks"])
        self.assertEqual(payload["checks"]["required_sections"]["issues"], [])

    def test_missing_required_sections_are_reported(self):
        self._write_valid_bundle()
        broken = MAIN_DOC_BASE.replace("## 🏢 业务模块映射\n", "")
        broken = broken.replace("## 🔧 常见任务速查\n", "")
        (self.dev_docs / "AI_Coding_Context.md").write_text(broken, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-required-sections",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["required_sections"]["issues"]}
        self.assertIn("missing_required_section", issue_types)

    def test_template_residue_is_reported(self):
        self._write_valid_bundle()
        residue_doc = MAIN_DOC_BASE + "\nTODO: [PROJECT_NAME]\n"
        (self.dev_docs / "AI_Coding_Context.md").write_text(residue_doc, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-template-residue",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["template_residue"]["issues"]}
        self.assertIn("template_residue", issue_types)

    def test_template_residue_scanner_command_is_not_reported(self):
        self._write_valid_bundle()
        command_doc = MAIN_DOC_BASE + """
| check | command |
| --- | --- |
| residue | `rg -n "<marker:T-O-D-O>|<marker:T-B-D>|待补充" dev_docs` |

- `rg -n "<marker:T-O-D-O>|<marker:T-B-D>|待补充" dev_docs`

```bash
rg -n "<marker:T-O-D-O>|<marker:T-B-D>|待补充" dev_docs
```
"""
        (self.dev_docs / "AI_Coding_Context.md").write_text(command_doc, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-template-residue",
        ])
        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["checks"]["template_residue"]["issues"], [])

    def test_template_residue_plain_body_marker_is_still_reported(self):
        self._write_valid_bundle()
        residue_doc = MAIN_DOC_BASE + "\n正文仍然待补充。\n"
        (self.dev_docs / "AI_Coding_Context.md").write_text(residue_doc, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-template-residue",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["template_residue"]["issues"]}
        self.assertIn("template_residue", issue_types)

    def test_run_record_integrity_is_reported(self):
        self._write_valid_bundle()
        broken_progress = """# 文档生成进度记录

> **开始时间**: 2026-05-12 10:00
"""
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(broken_progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("run_record_integrity", issue_types)

    def test_phase1_pass_requires_plan_review_record(self):
        self._write_valid_bundle()
        progress = GENERATION_PROGRESS_BASE.replace(
            "> **当前状态**: 生成中",
            "> **当前状态**: 等待人工审核",
        ).replace(
            "> **下一步动作**: 继续生成",
            "> **下一步动作**: Phase 1 PASS，可进入正式文档生成",
        )
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("phase1_pass_without_plan_review_record", issue_types)
        self.assertIn("phase1_pass_before_user_confirmation", issue_types)

    def test_phase1_review_record_requires_writeback_summary(self):
        self._write_valid_bundle()
        progress = GENERATION_PROGRESS_BASE.replace(
            "> **当前状态**: 生成中",
            "> **当前状态**: 等待人工审核",
        ).replace(
            "> **下一步动作**: 继续生成",
            "> **下一步动作**: Phase 1 建议通过，等待用户确认",
        ) + """

## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-12 10:30
- **review_completed_at**: 2026-05-12 10:40
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **machine_checks**: doc_health_checker=PASS, semantic_review_checker=PASS
- **manual_review_summary**: 已复查
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过，等待用户确认
- **user_confirmation_status**: pending
- **formal_generation_authorization**: none
- **authorization_source_summary**: 未授权
"""
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("phase1_plan_review_writeback_missing", issue_types)

    def test_phase1_review_record_requires_structured_machine_checks(self):
        self._write_valid_bundle()
        progress = GENERATION_PROGRESS_BASE.replace(
            "> **当前状态**: 生成中",
            "> **当前状态**: 等待人工审核",
        ).replace(
            "> **下一步动作**: 继续生成",
            "> **下一步动作**: Phase 1 建议通过，等待用户确认",
        ) + """

## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-12 10:30
- **review_completed_at**: 2026-05-12 10:40
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **machine_checks**: doc_health_checker=PASS, semantic_review_checker=PASS
- **manual_review_summary**: 已复查
- **writeback_summary**: 已更新 generation_plan.md
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过，等待用户确认
- **user_confirmation_status**: pending
- **formal_generation_authorization**: none
- **authorization_source_summary**: 未授权
"""
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("machine_check_table_missing", issue_types)

    def test_phase1_review_record_accepts_structured_machine_checks(self):
        self._write_valid_bundle()
        progress = GENERATION_PROGRESS_BASE.replace(
            "> **当前状态**: 生成中",
            "> **当前状态**: 等待人工审核",
        ).replace(
            "> **下一步动作**: 继续生成",
            "> **下一步动作**: Phase 1 建议通过，等待用户确认",
        ) + """

## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-12 10:30
- **review_completed_at**: 2026-05-12 10:40
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **manual_review_summary**: 已复查
- **writeback_summary**: 已更新 generation_plan.md
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过，等待用户确认
- **user_confirmation_status**: pending
- **formal_generation_authorization**: none
- **authorization_source_summary**: 未授权

### machine_checks

| phase | tool | implementation | command | exit_code | issue_count | status | required | disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| phase1_review | summary_validator | python | `python3 tools/py/summary_validator.py --dir dev_docs/_analysis --recursive --strict` | 0 | 0 | PASS | yes | verified |
| phase1_review | doc_health_checker | python | `python3 tools/py/doc_health_checker.py --full-check --doc-dir dev_docs` | 0 | 0 | PASS | yes | verified |
| phase1_review | doc_health_checker | js | `node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | 0 | 0 | PASS | yes | verified |
| phase1_review | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | yes | verified |
| phase1_review | semantic_review_checker | js | `node tools/js/semantic_review_checker.js --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | yes | verified |

### phase1_review_verdict

| field | value |
| --- | --- |
| verdict | READY_FOR_USER_REVIEW |
| reason | 必需检查通过 |
| can_generate_formal_docs | no |
| user_confirmation_required | yes |
| next_action | 等待用户审核 |
"""
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["checks"]["run_record_integrity"]["issues"], [])

    def test_progress_duplicate_last_updated_is_reported(self):
        self._write_valid_bundle()
        broken_progress = GENERATION_PROGRESS_BASE + "\n**最后更新**: 2026-05-12 11:00\n"
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(broken_progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("progress_metadata_mismatch", issue_types)

    def test_unlabeled_multiple_percentages_are_reported(self):
        self._write_valid_bundle()
        broken_progress = GENERATION_PROGRESS_BASE + "\n**进度**: 40%\n**进度**: 60%\n"
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(broken_progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("ambiguous_progress_percentage", issue_types)

    def test_stale_review_conclusion_is_reported(self):
        self._write_valid_bundle()
        plan = GENERATION_PLAN_BASE + """
依赖锁文件: Package.resolved 待确认

## 复查记录

| 事实 | 新状态 |
| --- | --- |
| Package.resolved 已存在 | ✅ 已确认 |
"""
        (self.dev_docs / "_analysis" / "generation_plan.md").write_text(plan, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("stale_review_conclusion", issue_types)

    def test_analysis_docs_do_not_require_frontmatter(self):
        self._write_valid_bundle()
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--full-check",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["checks"]["frontmatter"]["issues"], [])

    def test_analysis_docs_with_frontmatter_are_strictly_checked(self):
        self._write_valid_bundle()
        (self.dev_docs / "_analysis" / "generation_plan.md").write_text(
            "---\nsummary: 缺少必填字段。\n---\n\n# 文档生成方案模板\n",
            encoding="utf-8",
        )
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--full-check",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["frontmatter"]["issues"]}
        self.assertIn("frontmatter", issue_types)

    def test_completed_count_does_not_trigger_health_report_requirement(self):
        self._write_valid_bundle()
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["checks"]["run_record_integrity"]["issues"], [])

    def test_formal_docs_without_health_report_are_reported(self):
        self._write_valid_bundle()
        (self.dev_docs / "architecture").mkdir()
        (self.dev_docs / "architecture" / "overview.md").write_text("# 架构概览\n", encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("formal_docs_without_health_report", issue_types)

    def test_subdirectory_formal_docs_use_dev_docs_analysis_health_report(self):
        self._write_valid_first_release_bundle()
        review_dir = self.dev_docs / "review"
        review_dir.mkdir()
        (review_dir / "README.md").write_text("# 文档审查入口\n", encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(review_dir),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["checks"]["run_record_integrity"]["issues"], [])

    def test_formal_docs_without_phase1_confirmation_are_reported(self):
        self._write_valid_first_release_bundle()
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("formal_docs_generated_without_phase1_confirmation", issue_types)

    def test_formal_docs_with_phase1_confirmation_and_health_report_pass_run_record_gate(self):
        self._write_valid_first_release_bundle()
        progress = (self.dev_docs / "_analysis" / "generation_progress.md").read_text(encoding="utf-8")
        progress += PHASE1_CONFIRMED_RECORD
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["checks"]["run_record_integrity"]["issues"], [])

    def test_summary_only_validation_misrepresented_is_reported(self):
        self._write_valid_bundle()
        progress = GENERATION_PROGRESS_BASE + """
## 验证记录

summary_validator PASS，验证已通过。
"""
        (self.dev_docs / "_analysis" / "generation_progress.md").write_text(progress, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("summary_only_validation_misrepresented", issue_types)

    def test_legacy_quick_mode_still_works(self):
        self._write_valid_bundle()
        result = subprocess.run(
            ["python3", str(PY_CHECKER), "--doc-dir", str(self.dev_docs), "--mode", "quick"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn(result.returncode, (0, 1))
        payload = json.loads(result.stdout)
        self.assertIn("file_paths", payload["checks"])

    def test_health_report_pass_conflicting_with_machine_check_failure_is_reported(self):
        self._write_valid_first_release_bundle()
        report = HEALTH_REPORT_BASE.replace(
            "| 1 | doc_health_checker | js | `node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | 0 | 0 | PASS | verified |",
            "| 1 | doc_health_checker | js | `node tools/js/doc_health_checker.js --full-check --doc-dir dev_docs` | 1 | 6 | FAIL | accepted |",
        )
        (self.dev_docs / "_analysis" / "health_check_report.md").write_text(report, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("health_report_verdict_conflicts_with_checks", issue_types)
        self.assertIn("health_report_accepted_issue_missing_detail", issue_types)

    def test_health_report_accepted_issue_requires_detail(self):
        self._write_valid_first_release_bundle()
        report = HEALTH_REPORT_BASE.replace(
            "无 accepted issue",
            """| issue_id | tool | implementation | file | issue_type | original_status | accepted_reason | residual_risk | follow_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| js-esm-1 | doc_health_checker | js | frontend.md | js_esm_parse_false_positive | FAIL | 解析器误报 |  | 修复 JS parser |""",
        ).replace("PASS\n\n## machine_checks", "PASS_WITH_ACCEPTED_ISSUES\n\n## machine_checks")
        (self.dev_docs / "_analysis" / "health_check_report.md").write_text(report, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("health_report_accepted_issue_missing_detail", issue_types)

    def test_health_report_disallows_accepted_sensitive_issue(self):
        self._write_valid_first_release_bundle()
        report = HEALTH_REPORT_BASE.replace(
            "| 1 | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | 0 | 0 | PASS | verified |",
            "| 1 | semantic_review_checker | python | `python3 tools/py/semantic_review_checker.py --full-check --doc-dir dev_docs --repo-root .` | 1 | 1 | FAIL | accepted |",
        ).replace(
            "无 accepted issue",
            """| issue_id | tool | implementation | file | issue_type | original_status | accepted_reason | residual_risk | follow_up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| secret-1 | semantic_review_checker | python | deployment.md | sensitive_default_value_repeated | FAIL | 开源默认值 | 低 | 无 |""",
        ).replace("PASS\n\n## machine_checks", "PASS_WITH_ACCEPTED_ISSUES\n\n## machine_checks")
        (self.dev_docs / "_analysis" / "health_check_report.md").write_text(report, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("health_report_accepted_issue_not_allowed", issue_types)

    def test_artifact_count_mismatch_is_reported(self):
        self._write_valid_first_release_bundle()
        report = HEALTH_REPORT_BASE.replace("## 总体结论", "## 总体结论\n\n- **检查范围**: 全部 3 个产物")
        (self.dev_docs / "_analysis" / "health_check_report.md").write_text(report, encoding="utf-8")
        result, payload = _run_json([
            "python3",
            str(PY_CHECKER),
            "--doc-dir",
            str(self.dev_docs),
            "--check-run-record-integrity",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["run_record_integrity"]["issues"]}
        self.assertIn("artifact_count_mismatch", issue_types)

    def test_javascript_esm_code_samples_are_accepted_by_js_checker(self):
        self._write_valid_bundle()
        (self.dev_docs / "AI_Coding_Context.md").write_text(MAIN_DOC_BASE + """
```javascript
import { defineConfig } from "vite";
export default defineConfig({});
```
""", encoding="utf-8")
        result = subprocess.run(
            ["node", str(JS_CHECKER), "--doc-dir", str(self.dev_docs), "--check-code-samples"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["checks"]["code_samples"]["issues"], [])


    def _write_done_plan(self, name, frontmatter):
        done = self.dev_docs / "plans" / "done"
        done.mkdir(parents=True, exist_ok=True)
        (done / name).write_text("---\n%s\n---\n# %s\n" % (frontmatter, name), encoding="utf-8")

    def test_plan_done_without_review_is_blocker(self):
        self._write_done_plan("2026-06-13_feature_x.md", "title: x\nreview_status: not_reviewed")
        result, payload = _run_json([
            "python3", str(PY_CHECKER), "--doc-dir", str(self.dev_docs), "--check-plan-review",
        ])
        self.assertEqual(result.returncode, 1, payload)
        issues = payload["checks"]["plan_review"]["issues"]
        match = [i for i in issues if i["type"] == "plan_done_without_review"]
        self.assertTrue(match and match[0]["severity"] == "blocker", payload)

    def test_plan_done_reviewed_passes_and_skipped_needs_reason(self):
        self._write_done_plan("2026-06-13_feature_ok.md", "title: ok\nreview_status: reviewed")
        self._write_done_plan("2026-06-13_feature_s.md", "title: s\nreview_status: skipped\nreview_reason: trivial typo fix")
        result, payload = _run_json([
            "python3", str(PY_CHECKER), "--doc-dir", str(self.dev_docs), "--check-plan-review",
        ])
        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["checks"]["plan_review"]["issues"], [])

    def test_plan_skipped_without_reason_is_blocker(self):
        self._write_done_plan("2026-06-13_feature_s.md", "title: s\nreview_status: skipped\nreview_reason:")
        result, payload = _run_json([
            "python3", str(PY_CHECKER), "--doc-dir", str(self.dev_docs), "--check-plan-review",
        ])
        self.assertEqual(result.returncode, 1, payload)
        issues = payload["checks"]["plan_review"]["issues"]
        self.assertTrue(any(i["type"] == "plan_skipped_without_reason" for i in issues), payload)

    def test_active_plan_missing_review_status_is_warning(self):
        active = self.dev_docs / "plans" / "active"
        active.mkdir(parents=True, exist_ok=True)
        (active / "2026-06-13_feature_a.md").write_text("---\ntitle: a\n---\n# a\n", encoding="utf-8")
        result, payload = _run_json([
            "python3", str(PY_CHECKER), "--doc-dir", str(self.dev_docs), "--check-plan-review",
        ])
        issues = payload["checks"]["plan_review"]["issues"]
        match = [i for i in issues if i["type"] == "plan_active_missing_review_status"]
        self.assertTrue(match and match[0]["severity"] == "warning", payload)


class TestDocHealthCheckerJSSmoke(unittest.TestCase):
    def test_help_mentions_new_checks_js(self):
        result = subprocess.run(
            ["node", str(JS_CHECKER), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--check-required-sections", result.stdout)
        self.assertIn("--check-template-residue", result.stdout)
        self.assertIn("--check-run-record-integrity", result.stdout)
        self.assertIn("--check-plan-review", result.stdout)


if __name__ == "__main__":
    unittest.main()
