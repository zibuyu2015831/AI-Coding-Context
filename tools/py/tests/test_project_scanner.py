import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PY_SCANNER = ROOT / "tools" / "py" / "project_scanner.py"
DAYFLOW_LIKE = ROOT / "tools" / "testdata" / "semantic_review" / "dayflow_like_case"


class TestProjectScannerPython(unittest.TestCase):
    def test_swift_xcode_manifests_are_reported(self):
        result = subprocess.run(
            ["python3", str(PY_SCANNER), str(DAYFLOW_LIKE), "--format", "json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        data = payload["data"]
        self.assertIn(
            "Dayflow/Dayflow.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved",
            data["dependency_manifest_candidates"],
        )
        self.assertIn("Dayflow/Dayflow.xcodeproj/project.pbxproj", data["xcode_project_files"])
        self.assertIn("Dayflow/Dayflow/Info.plist", data["platform_config_files"])
        self.assertIn("Dayflow/Dayflow/Dayflow.entitlements", data["platform_config_files"])

    def test_standard_exclude_skips_embedded_aicc_symlink(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="project-scanner-aicc-"))
        try:
            (tmpdir / "app.txt").write_text("app\n", encoding="utf-8")
            (tmpdir / "AI-Coding-Context").symlink_to(ROOT, target_is_directory=True)
            result = subprocess.run(
                ["python3", str(PY_SCANNER), str(tmpdir), "--format", "json", "--exclude-standard", "--follow-symlinks"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("app.txt", result.stdout)
            self.assertNotIn("AI_ENTRY_POINT.md", result.stdout)
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()
