import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "agent-confidence-designer" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from scaffold_confidence_package import scaffold  # noqa: E402


class ScaffoldConfidencePackageTest(unittest.TestCase):
    def test_scaffold_creates_expected_files_and_replaces_agent_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "confidence"
            created = scaffold("invoice-agent", "Invoice Agent", target)

            expected_files = {
                "confidence-contract.yaml",
                "known-risk-patterns.yaml",
                "validator-spec.yaml",
                "confidence-review-report.md",
                "validators/validate_replace_me.py",
                "tests/test_replace_me_risk.py",
                "README.md",
            }
            actual_files = {
                str(path.relative_to(target))
                for path in target.rglob("*")
                if path.is_file()
            }
            self.assertTrue(expected_files.issubset(actual_files))
            self.assertEqual(len(created), len(expected_files))

            contract = (target / "confidence-contract.yaml").read_text(encoding="utf-8")
            self.assertIn('id: "invoice-agent"', contract)
            self.assertIn('name: "Invoice Agent"', contract)
            self.assertNotIn("{{AGENT_ID}}", contract)
            self.assertNotIn("{{AGENT_NAME}}", contract)

    def test_scaffold_refuses_to_overwrite_nonempty_directory_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "confidence"
            target.mkdir()
            (target / "existing.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                scaffold("invoice-agent", "Invoice Agent", target)


if __name__ == "__main__":
    unittest.main()
