#!/usr/bin/env python3
"""Static validation for a business confidence design package.

This script validates design structure and references only. It does not calculate
runtime confidence and does not require a universal validator interface.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FILES = (
    "confidence-contract.yaml",
    "known-risk-patterns.yaml",
    "confidence-logic.yaml",
    "confidence-review-report.md",
)
VALID_SHAPES = {"scalar", "field", "record", "text", "collection", "document", "decision"}
VALID_IMPACTS = {"critical", "high", "medium", "low"}
VALID_LEVELS = {"high", "medium", "low"}
ROOT_CAUSES = {
    "implementation_error",
    "rule_gap",
    "new_rule_candidate",
    "case_specific_info",
    "external_system_field",
    "business_confirmation_needed",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def error(self, code: str, message: str) -> None:
        self.findings.append(Finding("ERROR", code, message))

    def warning(self, code: str, message: str) -> None:
        self.findings.append(Finding("WARNING", code, message))

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "WARNING"]


def load_yaml(path: Path, report: Report) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        report.error("invalid-yaml", f"Cannot read {path.name}: {exc}")
        return {}
    if not isinstance(value, dict):
        report.error("invalid-root", f"{path.name} must contain a mapping")
        return {}
    return value


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def index_items(items: list[Any], label: str, report: Report) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for pos, item in enumerate(items):
        if not isinstance(item, dict):
            report.error("invalid-entry", f"{label}[{pos}] must be a mapping")
            continue
        item_id = item.get("id")
        if not nonempty(item_id):
            report.error("missing-id", f"{label}[{pos}] needs id")
            continue
        if item_id in result:
            report.error("duplicate-id", f"Duplicate {label} id: {item_id}")
            continue
        result[item_id] = item
    return result


def validate_package(package_dir: Path) -> Report:
    report = Report()
    for name in REQUIRED_FILES:
        if not (package_dir / name).is_file():
            report.error("missing-file", f"Missing required file: {name}")
    if report.errors:
        return report

    contract = load_yaml(package_dir / "confidence-contract.yaml", report)
    risks_data = load_yaml(package_dir / "known-risk-patterns.yaml", report)
    logic_data = load_yaml(package_dir / "confidence-logic.yaml", report)
    if report.errors:
        return report

    for file_name, data in (
        ("confidence-contract.yaml", contract),
        ("known-risk-patterns.yaml", risks_data),
        ("confidence-logic.yaml", logic_data),
    ):
        if str(data.get("schema_version")) != "2.0":
            report.error("schema-version", f"{file_name} must use schema_version 2.0")

    agent = contract.get("agent")
    if not isinstance(agent, dict):
        report.error("agent", "confidence-contract.yaml needs agent")
    else:
        for key in ("id", "name", "version", "owner", "description"):
            if not nonempty(agent.get(key)):
                report.error("agent-field", f"agent.{key} must be non-empty")

    context = contract.get("business_context")
    if not isinstance(context, dict):
        report.error("business-context", "confidence-contract.yaml needs business_context")
    else:
        for key in (
            "users",
            "downstream_actions",
            "business_stages",
            "authoritative_sources",
            "supported_scope",
            "exclusions",
        ):
            if not isinstance(context.get(key), list):
                report.error("business-context-field", f"business_context.{key} must be a list")

    results = index_items(as_list(contract.get("result_units")), "result_units", report)
    risks = index_items(as_list(risks_data.get("risks")), "risks", report)
    logic_items = index_items(as_list(logic_data.get("logic_items")), "logic_items", report)
    if not results:
        report.error("result-units", "At least one result unit is required")
    if not logic_items:
        report.error("logic-items", "At least one confidence logic item is required")

    for result_id, result in results.items():
        if result.get("result_shape") not in VALID_SHAPES:
            report.error("result-shape", f"{result_id} has invalid result_shape")
        if result.get("business_impact") not in VALID_IMPACTS:
            report.error("business-impact", f"{result_id} has invalid business_impact")
        if not nonempty(result.get("business_stage")):
            report.error("business-stage", f"{result_id} needs business_stage")
        meaning = result.get("confidence_meaning")
        if not isinstance(meaning, dict):
            report.error("confidence-meaning", f"{result_id} needs confidence_meaning")
        else:
            for key in ("evaluates", "high_proves", "high_does_not_prove"):
                if not nonempty(meaning.get(key)):
                    report.error("confidence-meaning-field", f"{result_id}.{key} must be non-empty")
        for key in ("high_conditions", "medium_conditions", "low_conditions"):
            if not as_list(result.get(key)):
                report.error("level-conditions", f"{result_id} needs {key}")
        policy = result.get("review_policy")
        if not isinstance(policy, dict):
            report.error("review-policy", f"{result_id} needs review_policy")
        else:
            for level in VALID_LEVELS:
                if not nonempty(policy.get(level)):
                    report.error("review-policy-level", f"{result_id}.review_policy.{level} is required")
        for dep in as_list(result.get("dependencies")):
            if dep not in results:
                report.error("unknown-dependency", f"{result_id} references unknown dependency {dep}")

    for logic_id, logic in logic_items.items():
        applies_to = as_list(logic.get("applies_to"))
        if not applies_to:
            report.error("logic-target", f"{logic_id} needs applies_to")
        for result_id in applies_to:
            if result_id not in results:
                report.error("unknown-result", f"{logic_id} references unknown result {result_id}")
        for key in ("dimensions", "hard_rules", "evidence_requirements", "required_inputs"):
            if not as_list(logic.get(key)):
                report.error("logic-field", f"{logic_id} needs {key}")
        for key in ("suggested_method", "suggested_location", "review_action"):
            if not nonempty(logic.get(key)):
                report.error("logic-field", f"{logic_id} needs {key}")

    for risk_id, risk in risks.items():
        if risk.get("root_cause_category") not in ROOT_CAUSES:
            report.error("root-cause", f"{risk_id} has invalid root_cause_category")
        affected = as_list(risk.get("affected_result_units"))
        if not affected:
            report.error("risk-target", f"{risk_id} needs affected_result_units")
        for result_id in affected:
            if result_id not in results:
                report.error("unknown-result", f"{risk_id} references unknown result {result_id}")
        if not as_list(risk.get("trigger_conditions")):
            report.error("risk-trigger", f"{risk_id} needs trigger_conditions")
        generalization = risk.get("generalization")
        if not isinstance(generalization, dict):
            report.error("generalization", f"{risk_id} needs generalization")
        else:
            if not isinstance(generalization.get("reusable"), bool):
                report.error("generalization-reusable", f"{risk_id}.reusable must be boolean")
            if not isinstance(generalization.get("business_confirmed"), bool):
                report.error("generalization-confirmed", f"{risk_id}.business_confirmed must be boolean")
            if not nonempty(generalization.get("basis")):
                report.error("generalization-basis", f"{risk_id}.basis is required")
        if risk.get("level_effect") not in VALID_LEVELS:
            report.error("risk-level", f"{risk_id} has invalid level_effect")
        if not nonempty(risk.get("suggested_action")):
            report.error("risk-action", f"{risk_id} needs suggested_action")

    covered = {result_id for logic in logic_items.values() for result_id in as_list(logic.get("applies_to"))}
    for result_id in results:
        if result_id not in covered:
            report.warning("result-without-logic", f"{result_id} has no confidence logic item")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a confidence design package")
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = validate_package(args.package_dir.resolve())
    if not report.findings:
        print("Validation passed with no findings.")
    else:
        for finding in report.findings:
            print(f"{finding.severity} [{finding.code}] {finding.message}")
        print(f"Summary: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
