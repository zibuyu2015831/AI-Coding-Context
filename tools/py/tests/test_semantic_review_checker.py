import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PY_CHECKER = ROOT / "tools" / "py" / "semantic_review_checker.py"
SEMANTIC_ROOT = ROOT / "tools" / "testdata" / "semantic_review"


def run_json(args):
    result = subprocess.run(
        ["python3", str(PY_CHECKER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, json.loads(result.stdout)


class TestSemanticReviewCheckerPython(unittest.TestCase):
    def _make_phase1_case(self, *, plan_extra="", report_extra="", contributing=""):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-phase1-"))
        dev_docs = tmpdir / "dev_docs" / "_analysis"
        dev_docs.mkdir(parents=True)
        (tmpdir / "tests" / "Feature").mkdir(parents=True)
        (tmpdir / "tests" / "Feature" / "ExampleTest.php").write_text("<?php\n", encoding="utf-8")
        if contributing:
            (tmpdir / "CONTRIBUTING.md").write_text(contributing, encoding="utf-8")
        (dev_docs / "generation_plan.md").write_text(f"""# 文档生成方案

## 🎯 项目定位与愿景理解

LinguaCafe 是 Laravel + Vue 语言学习应用，文档方案需覆盖主应用、开源维护与队列边界。

## 🧾 证据与验证记录

| 结论 | 证据等级 | 证据文件 | 验证方式 |
| --- | --- | --- | --- |
| 测试目录存在 | E1 | tests/Feature/ExampleTest.php | 读取目录 |

## 等待用户审核的问题

1. 部署环境边界
   - 当前保守结论: 暂按 Docker 与本地环境并存记录。
   - 已检查证据: docker-compose.yml 未覆盖真实生产拓扑。
   - 为什么代码或仓库文档无法回答: 生产部署策略属于团队运维决策，仓库只包含示例配置。
   - blocks_phase1: false
   - 回写目标: deployment.md

## 🔎 Phase 1 方案复查清单

- [x] 证据表包含 `证据等级`
{plan_extra}
""", encoding="utf-8")
        (dev_docs / "project_analysis_report.md").write_text(f"""# 项目分析报告

## 架构分析

已覆盖 tests/Feature/ExampleTest.php。

## 复查记录

| 事项 | 证据等级 | 当前状态 | blocks_phase1 | 回写目标 |
| --- | --- | --- | --- | --- |
| 部署环境边界 | E2 | 待用户确认 | false | deployment.md |

## 待确认问题

- 部署环境边界

{report_extra}
""", encoding="utf-8")
        (dev_docs / "generation_progress.md").write_text("""# 文档生成进度记录

## 🔎 Phase 1 方案复查记录

- **review_trigger**: 用户要求审核 _analysis
- **review_started_at**: 2026-05-18 10:00
- **review_completed_at**: 2026-05-18 10:10
- **reviewed_files**: generation_plan.md, project_analysis_report.md, generation_progress.md
- **machine_checks**: doc_health_checker=PASS, semantic_review_checker=PASS
- **manual_review_summary**: 已复查
- **writeback_summary**: 已更新 generation_plan.md
- **blocker_count**: 0
- **warning_count**: 0
- **waived_issue_count**: 0
- **phase1_recommendation**: 建议通过，等待用户确认
- **user_confirmation_status**: pending
""", encoding="utf-8")
        return tmpdir

    def _make_first_release_case(self, *, docs_extra="", ai_rules="", package_json=None, dockerfile="", contributing="", vuex_modules=None):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-first-release-"))
        dev_docs = tmpdir / "dev_docs"
        (dev_docs / "_analysis").mkdir(parents=True)
        (dev_docs / "rules" / "combined").mkdir(parents=True)
        (tmpdir / "resources" / "js" / "vuex").mkdir(parents=True)
        (tmpdir / "docker").mkdir(parents=True)
        (tmpdir / "routes").mkdir(parents=True)
        package_json = package_json or {
            "dependencies": {
                "vue": "^2.6.12",
                "vuex": "^3.6.2",
            }
        }
        (tmpdir / "package.json").write_text(json.dumps(package_json), encoding="utf-8")
        (tmpdir / "docker" / "PhpDockerfile").write_text(dockerfile or "FROM php:8.2-apache\nCOPY ./docker/vhost.conf /etc/apache2/sites-available/000-default.conf\n", encoding="utf-8")
        (tmpdir / "routes" / "web.php").write_text("<?php\nRoute::get('/books', 'BookController@index');\n", encoding="utf-8")
        (tmpdir / "routes" / "api.php").write_text("<?php\n", encoding="utf-8")
        for module in vuex_modules or ["Shared", "InteractiveText", "HoverVocabularyBox", "VocabularyBox"]:
            (tmpdir / "resources" / "js" / "vuex" / f"{module}.js").write_text("export default {}\n", encoding="utf-8")
        if contributing:
            (tmpdir / "CONTRIBUTING.md").write_text(contributing, encoding="utf-8")
        (dev_docs / "_analysis" / "generation_plan.md").write_text("Phase 1 脱敏要求: 不复述密码、Token、完整密钥或个人联系信息。\n", encoding="utf-8")
        (dev_docs / "architecture_overview.md").write_text(docs_extra or "Web 层为 Nginx/PHP-FPM。\n", encoding="utf-8")
        (dev_docs / "deployment_guide.md").write_text("DB_PASSWORD 默认值为 `linguacafe`，PUSHER_APP_KEY 为 `wjp2pou6ebgibtwccqsj`。\n", encoding="utf-8")
        (dev_docs / "rules" / "combined" / "AI_RULES.md").write_text(ai_rules or "前端框架: Vue 2 + Vuex 4\n状态管理模块: `user_storage`, `shared`, `theme`\n部署: Nginx/PHP-FPM\n", encoding="utf-8")
        return tmpdir

    def test_help_mentions_core_flags(self):
        result = subprocess.run(
            ["python3", str(PY_CHECKER), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--check-fact-conflicts", result.stdout)
        self.assertIn("--check-metrics", result.stdout)
        self.assertIn("--check-test-topology", result.stdout)

    def test_fact_conflicts_are_reported(self):
        case_root = SEMANTIC_ROOT / "conflict_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--check-fact-conflicts",
        ])
        self.assertEqual(result.returncode, 1)
        self.assertTrue(payload["checks"]["fact_conflicts"])
        self.assertEqual(payload["checks"]["fact_conflicts"][0]["type"], "fact_conflict")

    def test_generated_file_rule_rephrasing_is_not_fact_conflict(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-rule-rephrasing-"))
        try:
            dev_docs = tmpdir / "dev_docs"
            dev_docs.mkdir()
            (tmpdir / "CONTRIBUTING.md").write_text("Generated output `*.g.dart` should not be edited by hand.\n", encoding="utf-8")
            (dev_docs / "AI_Coding_Context.md").write_text("不要手改 `*.g.dart`。\n", encoding="utf-8")
            result, payload = run_json([
                "--doc-dir", str(dev_docs),
                "--repo-root", str(tmpdir),
                "--check-fact-conflicts",
            ])
            self.assertEqual(result.returncode, 0, payload)
            self.assertEqual(payload["checks"]["fact_conflicts"], [])
        finally:
            shutil.rmtree(tmpdir)

    def test_generated_file_opposite_rule_is_fact_conflict(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-rule-conflict-"))
        try:
            dev_docs = tmpdir / "dev_docs"
            dev_docs.mkdir()
            (tmpdir / "CONTRIBUTING.md").write_text("Generated output `*.g.dart` should not be edited by hand.\n", encoding="utf-8")
            (dev_docs / "AI_Coding_Context.md").write_text("建议直接编辑 `*.g.dart`。\n", encoding="utf-8")
            result, payload = run_json([
                "--doc-dir", str(dev_docs),
                "--repo-root", str(tmpdir),
                "--check-fact-conflicts",
            ])
            self.assertEqual(result.returncode, 1)
            issue_types = {issue["type"] for issue in payload["checks"]["fact_conflicts"]}
            self.assertIn("rule_conflict", issue_types)
        finally:
            shutil.rmtree(tmpdir)

    def test_sensitive_keyword_attention_is_not_fact_conflict_authority(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-sensitive-attention-"))
        try:
            dev_docs = tmpdir / "dev_docs"
            docs = tmpdir / "docs"
            dev_docs.mkdir()
            docs.mkdir()
            (docs / "pr-policy-preflight.en.md").write_text(
                "| Sensitive keyword | Added lines include keywords such as `UserStorage`, `GlobalEventBus` | These words are not necessarily wrong, but AI or reviewers should notice them. |\n",
                encoding="utf-8",
            )
            (dev_docs / "AI_Coding_Context.md").write_text("新增数据偏好时优先使用 `UserStorage`。\n", encoding="utf-8")
            result, payload = run_json([
                "--doc-dir", str(dev_docs),
                "--repo-root", str(tmpdir),
                "--check-fact-conflicts",
            ])
            self.assertEqual(result.returncode, 0, payload)
            self.assertEqual(payload["checks"]["fact_conflicts"], [])
        finally:
            shutil.rmtree(tmpdir)

    def test_mixed_rule_line_applies_negative_polarity_to_actual_negative_anchor_only(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-mixed-rule-"))
        try:
            dev_docs = tmpdir / "dev_docs"
            dev_docs.mkdir()
            (tmpdir / "AGENTS.md").write_text(
                "Do not scatter Drift `query.watch()` streams across services; centralize change observation through `TableChangeNotifier`.\n",
                encoding="utf-8",
            )
            (dev_docs / "AI_Coding_Context.md").write_text("文件/数据库层变更：优先统一到 `TableChangeNotifier`。\n", encoding="utf-8")
            result, payload = run_json([
                "--doc-dir", str(dev_docs),
                "--repo-root", str(tmpdir),
                "--check-fact-conflicts",
            ])
            self.assertEqual(result.returncode, 0, payload)
            self.assertEqual(payload["checks"]["fact_conflicts"], [])
        finally:
            shutil.rmtree(tmpdir)

    def test_metric_drift_is_reported(self):
        case_root = SEMANTIC_ROOT / "metric_drift_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--check-metrics",
        ])
        self.assertEqual(result.returncode, 1)
        self.assertTrue(payload["checks"]["metrics"])
        self.assertEqual(payload["checks"]["metrics"][0]["type"], "metric_drift")

    def test_uncovered_test_topology_is_reported(self):
        case_root = SEMANTIC_ROOT / "test_topology_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--check-test-topology",
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["test_topology"]}
        self.assertIn("uncovered_test_topology", issue_types)

    def test_virtualenv_site_packages_tests_are_excluded_from_topology(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-venv-topology-"))
        try:
            dev_docs = tmpdir / "dev_docs"
            dev_docs.mkdir()
            (tmpdir / "tests" / "unit").mkdir(parents=True)
            (tmpdir / ".venv" / "lib" / "python3.11" / "site-packages" / "numpy" / "tests").mkdir(parents=True)
            (tmpdir / "tests" / "unit" / "test_real.py").write_text("def test_real(): pass\n", encoding="utf-8")
            (tmpdir / ".venv" / "lib" / "python3.11" / "site-packages" / "numpy" / "tests" / "test_vendor.py").write_text("def test_vendor(): pass\n", encoding="utf-8")
            (dev_docs / "testing_guide.md").write_text("测试目录覆盖 `tests/`。\n", encoding="utf-8")

            result, payload = run_json([
                "--doc-dir", str(dev_docs),
                "--repo-root", str(tmpdir),
                "--check-test-topology",
            ])

            self.assertEqual(result.returncode, 0, payload)
            self.assertEqual(payload["checks"]["test_topology"], [])
        finally:
            shutil.rmtree(tmpdir)

    def test_memex_style_test_topology_requires_all_test_roots(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="semantic-memex-topology-"))
        try:
            dev_docs = tmpdir / "dev_docs"
            dev_docs.mkdir()
            (tmpdir / "test" / "agent").mkdir(parents=True)
            (tmpdir / "tests" / "tools").mkdir(parents=True)
            (tmpdir / "ios" / "RunnerTests").mkdir(parents=True)
            (tmpdir / "test" / "agent" / "agent_test.dart").write_text("void main() {}\n", encoding="utf-8")
            (tmpdir / "tests" / "tools" / "test_tool.py").write_text("def test_tool(): pass\n", encoding="utf-8")
            (tmpdir / "ios" / "RunnerTests" / "RunnerTests.swift").write_text("import XCTest\n", encoding="utf-8")
            (dev_docs / "testing_guide.md").write_text("仅记录 `test/`。\n", encoding="utf-8")
            result, payload = run_json([
                "--doc-dir", str(dev_docs),
                "--repo-root", str(tmpdir),
                "--check-test-topology",
            ])
            self.assertEqual(result.returncode, 1)
            uncovered = {issue["path"] for issue in payload["checks"]["test_topology"]}
            self.assertIn("tests/", uncovered)
            self.assertIn("ios/RunnerTests/", uncovered)
        finally:
            shutil.rmtree(tmpdir)

    def test_swift_xcode_tests_are_counted(self):
        case_root = SEMANTIC_ROOT / "dayflow_like_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--check-metrics",
            "--check-test-topology",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["checks"]["metrics"], [])
        self.assertEqual(payload["checks"]["test_topology"], [])

    def test_non_swift_tests_suffix_falls_back_to_all_files(self):
        case_root = SEMANTIC_ROOT / "non_swift_tests_suffix_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--check-metrics",
            "--check-test-topology",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["checks"]["metrics"], [])
        self.assertEqual(payload["checks"]["test_topology"], [])

    def test_second_review_semantic_issues_are_reported(self):
        case_root = SEMANTIC_ROOT / "dayflow_second_review_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--full-check",
        ])
        self.assertEqual(result.returncode, 1)
        issues = []
        for check_issues in payload["checks"].values():
            issues.extend(check_issues)
        issue_types = {issue["type"] for issue in issues}
        self.assertIn("summary_question_count_mismatch", issue_types)
        self.assertIn("unevidenced_strong_conclusion", issue_types)
        self.assertIn("invalid_evidence_path", issue_types)

    def test_linguacafe_phase1_progress_only_case_is_blocked(self):
        case_root = SEMANTIC_ROOT / "linguacafe_phase1_progress_only_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--full-check",
        ])
        self.assertEqual(result.returncode, 1)
        issues = []
        for check_issues in payload["checks"].values():
            issues.extend(check_issues)
        issue_types = {issue["type"] for issue in issues}
        self.assertTrue({"evidence_level_completeness", "evidence_table_level_column_missing"} & issue_types)
        self.assertIn("project_analysis_issue_status_missing", issue_types)
        self.assertIn("phase1_progress_only_review", issue_types)
        self.assertIn("confirmable_fact_misclassified", issue_types)
        self.assertIn("project_positioning_coverage_missing", issue_types)

    def test_linguacafe_phase1_reviewed_case_passes(self):
        case_root = SEMANTIC_ROOT / "linguacafe_phase1_reviewed_case"
        result, payload = run_json([
            "--doc-dir", str(case_root / "dev_docs"),
            "--repo-root", str(case_root),
            "--full-check",
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["summary"]["passed"])

    def test_embedded_aicc_symlink_is_excluded_from_project_scan(self):
        case_root = self._make_phase1_case()
        try:
            (case_root / "AI-Coding-Context").symlink_to(ROOT, target_is_directory=True)
            result, payload = run_json([
                "--doc-dir", str(case_root / "dev_docs"),
                "--repo-root", str(case_root),
                "--full-check",
            ])
            self.assertEqual(result.returncode, 0, payload)
            self.assertTrue(payload["summary"]["passed"])
        finally:
            shutil.rmtree(case_root)

    def test_evidence_table_requires_level_column_even_when_checklist_mentions_it(self):
        case_root = self._make_phase1_case()
        (case_root / "dev_docs" / "_analysis" / "generation_plan.md").write_text("""
# 文档生成方案

## 🎯 项目定位与愿景理解

LinguaCafe 是 Laravel + Vue 语言学习应用。

## 🧾 证据与验证记录

| 结论 | 证据文件 | 验证方式 |
| --- | --- | --- |
| 测试目录存在 | tests/Feature/ExampleTest.php | 读取目录 |

## 等待用户审核的问题

1. 部署环境边界
   - 当前保守结论: 暂按 Docker 与本地环境并存记录。
   - 已检查证据: docker-compose.yml 未覆盖真实生产拓扑。
   - 为什么代码或仓库文档无法回答: 生产部署策略属于团队运维决策，仓库只包含示例配置。
   - blocks_phase1: false
   - 回写目标: deployment.md

## 🔎 Phase 1 方案复查清单

- [x] 证据表包含 `证据等级`
""", encoding="utf-8")
        try:
            result, payload = run_json([
                "--doc-dir", str(case_root / "dev_docs"),
                "--repo-root", str(case_root),
                "--full-check",
            ])
            self.assertEqual(result.returncode, 1)
            issues = [issue for check_issues in payload["checks"].values() for issue in check_issues]
            issue_types = {issue["type"] for issue in issues}
            self.assertIn("evidence_table_level_column_missing", issue_types)
        finally:
            shutil.rmtree(case_root)

    def test_user_confirmation_items_require_rationale_and_writeback_target(self):
        case_root = self._make_phase1_case()
        (case_root / "dev_docs" / "_analysis" / "generation_plan.md").write_text("""
# 文档生成方案

## 🎯 项目定位与愿景理解

LinguaCafe 是 Laravel + Vue 语言学习应用。

## 🧾 证据与验证记录

| 结论 | 证据等级 | 证据文件 | 验证方式 |
| --- | --- | --- | --- |
| 测试目录存在 | E1 | tests/Feature/ExampleTest.php | 读取目录 |

## 等待用户审核的问题

1. 部署环境边界
   - 当前保守结论: 暂按 Docker 与本地环境并存记录。
   - 已检查证据: docker-compose.yml 未覆盖真实生产拓扑。

## 🔎 Phase 1 方案复查清单

- [x] 证据表包含 `证据等级`
""", encoding="utf-8")
        try:
            result, payload = run_json([
                "--doc-dir", str(case_root / "dev_docs"),
                "--repo-root", str(case_root),
                "--full-check",
            ])
            self.assertEqual(result.returncode, 1)
            issues = [issue for check_issues in payload["checks"].values() for issue in check_issues]
            issue_types = {issue["type"] for issue in issues}
            self.assertIn("user_confirmation_rationale_missing", issue_types)
            self.assertIn("user_confirmation_blocks_phase1_missing", issue_types)
            self.assertIn("user_confirmation_writeback_missing", issue_types)
        finally:
            shutil.rmtree(case_root)

    def test_test_recommendation_conflicting_with_contributing_is_reported(self):
        case_root = self._make_phase1_case(
            report_extra="后续优先补核心 Service 与队列 Job 的回归测试。",
            contributing="Currently I don't use tests neither for Javascript, Python or PHP, please do not write any for PR-s.\n",
        )
        try:
            result, payload = run_json([
                "--doc-dir", str(case_root / "dev_docs"),
                "--repo-root", str(case_root),
                "--full-check",
            ])
            self.assertEqual(result.returncode, 1)
            issues = [issue for check_issues in payload["checks"].values() for issue in check_issues]
            issue_types = {issue["type"] for issue in issues}
            self.assertIn("test_recommendation_conflicts_with_contributing", issue_types)
        finally:
            shutil.rmtree(case_root)

    def test_first_release_runtime_ai_rules_and_sensitive_conflicts_are_reported(self):
        case_root = self._make_first_release_case(
            contributing="Currently I don't use tests neither for Javascript, Python or PHP, please do not write any for PR-s.\n",
        )
        try:
            result, payload = run_json([
                "--doc-dir", str(case_root / "dev_docs"),
                "--repo-root", str(case_root),
                "--full-check",
            ])
            self.assertEqual(result.returncode, 1)
            issues = [issue for check_issues in payload["checks"].values() for issue in check_issues]
            issue_types = {issue["type"] for issue in issues}
            self.assertIn("runtime_stack_conflict", issue_types)
            self.assertIn("ai_rules_dependency_version_conflict", issue_types)
            self.assertIn("ai_rules_state_module_conflict", issue_types)
            self.assertIn("ai_rules_runtime_stack_conflict", issue_types)
            self.assertIn("sensitive_policy_declared_but_violated", issue_types)
            self.assertIn("secret_like_value_in_docs", issue_types)
        finally:
            shutil.rmtree(case_root)

    def test_first_release_correct_docs_pass_without_docker_false_positive(self):
        case_root = self._make_first_release_case(
            docs_extra="Web 层为 Apache + Laravel + Supervisor。\n",
            ai_rules="前端框架: Vue 2 + Vuex 3\n状态管理模块: `shared`, `interactiveText`, `hoverVocabularyBox`, `vocabularyBox`\n部署: Apache\n",
        )
        try:
            (case_root / "dev_docs" / "deployment_guide.md").write_text("只列变量名：`DB_PASSWORD`、`PUSHER_APP_KEY`，生产环境必须改写。\n", encoding="utf-8")
            result, payload = run_json([
                "--doc-dir", str(case_root / "dev_docs"),
                "--repo-root", str(case_root),
                "--full-check",
            ])
            self.assertEqual(result.returncode, 0, payload)
        finally:
            shutil.rmtree(case_root)


if __name__ == "__main__":
    unittest.main()
