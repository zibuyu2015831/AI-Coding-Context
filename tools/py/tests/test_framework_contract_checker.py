import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PY_CHECKER = ROOT / "tools" / "py" / "framework_contract_checker.py"
VALID_TEMPLATE = ROOT / "tools" / "testdata" / "framework_contracts" / "valid_template.md"
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


if __name__ == "__main__":
    unittest.main()
