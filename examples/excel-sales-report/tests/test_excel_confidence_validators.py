import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    path = ROOT / "validators" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExcelConfidenceValidatorsTest(unittest.TestCase):
    def test_mixed_date_formats_issue_is_detected(self) -> None:
        validator = load("validate_date_normalization")
        result = validator.validate([
            {"record_id": "A", "parsed_date": "2026-01-01"},
            {"record_id": "B", "parsed_date": None},
        ])
        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["B"], result["invalid_record_ids"])

    def test_hidden_row_omission_is_detected_by_record_count(self) -> None:
        validator = load("validate_record_count")
        result = validator.validate(100, 98)
        self.assertEqual("FAIL", result["status"])
        self.assertEqual(-2, result["difference"])

    def test_report_number_mismatch_is_detected(self) -> None:
        validator = load("validate_cross_file_metric")
        result = validator.validate(
            {"value": 100, "period": "2026-06", "currency": "CNY"},
            {"value": 90, "period": "2026-06", "currency": "CNY"},
        )
        self.assertEqual("FAIL", result["status"])
        self.assertIn("value", result["differences"])

    def test_detail_total_can_pass(self) -> None:
        validator = load("validate_detail_total")
        result = validator.validate([10.0, 20.0, 30.0], 60.0)
        self.assertEqual("PASS", result["status"])


if __name__ == "__main__":
    unittest.main()
