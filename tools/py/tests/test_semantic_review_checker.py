import json
import subprocess
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


if __name__ == "__main__":
    unittest.main()
