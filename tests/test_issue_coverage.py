import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "agent-confidence-designer" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_issue_coverage import analyze  # noqa: E402


class IssueCoverageTest(unittest.TestCase):
    def test_examples_have_complete_issue_coverage(self) -> None:
        for name in ("excel-sales-report", "word-management-report"):
            rows, failures = analyze(ROOT / "examples" / name)
            self.assertTrue(rows)
            self.assertEqual([], failures)

    def test_missing_detector_and_test_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "invalid"
            shutil.copytree(ROOT / "examples" / "excel-sales-report", target)
            risk_path = target / "known-risk-patterns.yaml"
            data = yaml.safe_load(risk_path.read_text(encoding="utf-8"))
            risk = data["risks"][0]
            risk["validator_id"] = "does-not-exist"
            risk["regression_tests"] = ["tests/does_not_exist.py"]
            risk_path.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

            _, failures = analyze(target)
            self.assertTrue(any("missing valid detector" in item for item in failures))
            self.assertTrue(any("missing regression test" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
