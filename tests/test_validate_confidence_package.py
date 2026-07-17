import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "agent-confidence-designer" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_confidence_package import validate_package  # noqa: E402


class ValidateConfidencePackageTest(unittest.TestCase):
    def test_excel_example_has_no_findings(self) -> None:
        report = validate_package(ROOT / "examples" / "excel-sales-report")
        self.assertEqual([], report.errors)
        self.assertEqual([], report.warnings)

    def test_word_example_has_no_findings(self) -> None:
        report = validate_package(ROOT / "examples" / "word-management-report")
        self.assertEqual([], report.errors)
        self.assertEqual([], report.warnings)

    def test_unverified_high_and_missing_validator_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "invalid"
            shutil.copytree(ROOT / "examples" / "excel-sales-report", target)
            contract_path = target / "confidence-contract.yaml"
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            result = contract["result_units"][0]
            result["maximum_level_when_unverified"] = "high"
            result["required_validators"].append("missing-validator")
            contract_path.write_text(
                yaml.safe_dump(contract, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

            report = validate_package(target)
            codes = {finding.code for finding in report.errors}
            self.assertIn("unverified-high", codes)
            self.assertIn("unknown-validator", codes)

    def test_critical_result_must_have_deterministic_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "invalid"
            shutil.copytree(ROOT / "examples" / "word-management-report", target)
            contract_path = target / "confidence-contract.yaml"
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            causal = next(
                item for item in contract["result_units"] if item["id"] == "causal-analysis"
            )
            causal["required_validators"] = ["review-causal-support"]
            contract_path.write_text(
                yaml.safe_dump(contract, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )

            report = validate_package(target)
            codes = {finding.code for finding in report.errors}
            self.assertIn("no-deterministic-evidence", codes)


if __name__ == "__main__":
    unittest.main()
