import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PY_CHECKER = ROOT / "tools" / "py" / "framework_contract_checker.py"
VALID_TEMPLATE = ROOT / "tools" / "testdata" / "framework_contracts" / "valid_template.md"
MAIN_TEMPLATE = ROOT / "templates" / "AI_Coding_Context_TEMPLATE.md"
MISSING_TEMPLATE = ROOT / "tools" / "testdata" / "framework_contracts" / "missing_sections_template.md"
DRIFT_SPEC = ROOT / "tools" / "testdata" / "framework_contracts" / "spec_workflow_drift_case" / "spec.md"
DRIFT_WORKFLOW = ROOT / "tools" / "testdata" / "framework_contracts" / "spec_workflow_drift_case" / "workflow.md"


def run_json(args):
    result = subprocess.run(
        ["python3", str(PY_CHECKER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, json.loads(result.stdout)


class TestFrameworkContractCheckerPython(unittest.TestCase):
    def test_help_mentions_core_flags(self):
        result = subprocess.run(
            ["python3", str(PY_CHECKER), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--self-check", result.stdout)
        self.assertIn("--check-template", result.stdout)
        self.assertIn("--check-workflow", result.stdout)

    def test_valid_template_passes(self):
        result, payload = run_json(["--check-template", str(VALID_TEMPLATE)])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["summary"]["passed"])
        self.assertEqual(payload["checks"]["template"]["issues"], [])

    def test_missing_sections_are_reported(self):
        result, payload = run_json(["--check-template", str(MISSING_TEMPLATE)])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["template"]["issues"]}
        self.assertIn("missing_required_section", issue_types)

    def test_workflow_drift_is_reported(self):
        result, payload = run_json([
            "--check-workflow",
            str(DRIFT_WORKFLOW),
            "--spec",
            str(DRIFT_SPEC),
        ])
        self.assertEqual(result.returncode, 1)
        issue_types = {issue["type"] for issue in payload["checks"]["workflow"]["issues"]}
        self.assertIn("workflow_path_drift", issue_types)

    def test_plan_lifecycle_paths_are_enforced_by_self_check(self):
        result, payload = run_json(["--self-check"])
        self.assertEqual(result.returncode, 0, payload)

        spec_paths = payload["checks"]["spec_paths"]
        self.assertIn("dev_docs/plans/active/", spec_paths["standard_paths"])
        self.assertIn("dev_docs/plans/done/", spec_paths["standard_paths"])
        self.assertIn("dev_docs/plans/archive/", spec_paths["standard_paths"])
        self.assertIn("dev_docs/memos/", spec_paths["standard_paths"])

        workflow_paths = payload["checks"]["workflow"]["seen_standard_paths"]
        self.assertIn("dev_docs/plans/active/", workflow_paths)
        self.assertIn("dev_docs/memos/", workflow_paths)

        forbidden_paths = {
            issue["path"]
            for issue in payload["checks"]["workflow"]["issues"]
            if issue["type"] == "obsolete_standard_path"
        }
        self.assertNotIn("dev_docs/plans/features/", forbidden_paths)
        self.assertNotIn("dev_docs/plans/bugfixes/", forbidden_paths)

    def test_main_template_explains_memo_workflow(self):
        template = MAIN_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("备忘录", template)
        self.assertIn("主动阅读", template)
        self.assertIn("避免重复", template)
        self.assertIn("主动将合适的内容沉淀为备忘录", template)


if __name__ == "__main__":
    unittest.main()
