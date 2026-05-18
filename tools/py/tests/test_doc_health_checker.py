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
## 💻 核心代码模式
## 🛠️ 开发流程规范
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
"""

GENERATION_PROGRESS_BASE = """# 文档生成进度记录

> **开始时间**: 2026-05-12 10:00
> **最后更新**: 2026-05-12 10:30
> **当前状态**: 生成中
> **流程阶段进度**: Step 4/8，当前处于方案生成
> **产物完成度**: 1/3，已完成部分 _analysis 产物
> **当前 gate**: Phase 1 自检
> **下一步动作**: 继续生成

## 🎯 总体步骤进度

## 📝 逐文档完成状态

## 📊 统计信息

- **总任务数**: 3
- **已完成数**: 1
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
数据库技术: SQLite/Core Data / SwiftData (待确认)

## 复查记录

| 事实 | 新状态 |
| --- | --- |
| 数据库技术为 GRDB | ✅ 已确认 |
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


if __name__ == "__main__":
    unittest.main()
