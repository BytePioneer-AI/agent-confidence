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


class WordConfidenceValidatorsTest(unittest.TestCase):
    def test_missing_required_section_is_detected(self) -> None:
        validator = load("validate_required_sections")
        result = validator.validate(
            ["执行摘要", "经营分析", "行动建议"],
            {"执行摘要": "ok", "经营分析": "ok"},
        )
        self.assertEqual("FAIL", result["status"])
        self.assertEqual(["行动建议"], result["missing_sections"])

    def test_metric_source_mismatch_is_detected(self) -> None:
        validator = load("validate_report_metrics")
        result = validator.validate(
            [{"metric_id": "revenue", "value": 110, "period": "2026-06", "unit": "CNY"}],
            {"revenue": {"value": 100, "period": "2026-06", "unit": "CNY"}},
        )
        self.assertEqual("FAIL", result["status"])
        self.assertEqual("revenue", result["mismatches"][0]["metric_id"])

    def test_unsupported_causal_claim_is_detected(self) -> None:
        validator = load("review_causal_support")
        result = validator.validate([
            {
                "claim_id": "claim-3",
                "review_status": "unsupported",
                "risk_type": "unsupported_causal_claim",
                "reason": "No customer-demand evidence",
            }
        ])
        self.assertEqual("FAIL", result["status"])
        self.assertEqual("claim-3", result["risky_claims"][0]["claim_id"])

    def test_evidence_links_can_pass(self) -> None:
        validator = load("validate_evidence_links")
        result = validator.validate([
            {"claim_id": "claim-1", "evidence_refs": ["metric:revenue:2026-06"]}
        ])
        self.assertEqual("PASS", result["status"])


if __name__ == "__main__":
    unittest.main()
