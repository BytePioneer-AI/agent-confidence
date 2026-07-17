#!/usr/bin/env python3
"""Validate a business-specific Agent confidence design package."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install it with: python -m pip install PyYAML") from exc

REQUIRED_FILES = (
    "confidence-contract.yaml",
    "known-risk-patterns.yaml",
    "validator-spec.yaml",
)
VALID_LEVELS = {"high", "medium", "low"}
VALID_CRITICALITIES = {"critical", "high", "medium", "low"}
VALID_VALIDATOR_TYPES = {"deterministic", "semantic_assist", "manual_gate"}
VALID_IMPLEMENTATION_STATUS = {"planned", "implemented", "verified", "deprecated"}
VALID_RISK_SOURCES = {"development_test", "user_self_test"}
VALID_DETECTABILITY = {"deterministic", "semantic_assist", "manual"}
MANDATORY_HIGH_REQUIREMENTS = {
    "all_required_validators_pass",
    "no_critical_risk_detected",
    "within_supported_scope",
    "evidence_traceable",
}
MANDATORY_DOWNGRADES = {
    "any_critical_validator_fail": "low",
    "required_validator_unavailable": "medium",
    "outside_supported_scope": "low",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


@dataclass
class ValidationReport:
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

    def print(self) -> None:
        if not self.findings:
            print("Validation passed with no findings.")
            return
        for finding in self.findings:
            print(f"{finding.severity} [{finding.code}] {finding.message}")
        print(f"Summary: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_yaml(path: Path, report: ValidationReport) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.error("missing-file", f"Required file is missing: {path.name}")
        return {}
    except yaml.YAMLError as exc:
        report.error("invalid-yaml", f"Cannot parse {path.name}: {exc}")
        return {}
    if not isinstance(value, dict):
        report.error("invalid-root", f"{path.name} must contain a YAML mapping")
        return {}
    return value


def unique_index(items: list[Any], label: str, report: ValidationReport) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(items):
        if not isinstance(item, dict):
            report.error("invalid-entry", f"{label}[{position}] must be a mapping")
            continue
        item_id = item.get("id")
        if not nonempty_string(item_id):
            report.error("missing-id", f"{label}[{position}] must have a non-empty id")
            continue
        if item_id in result:
            report.error("duplicate-id", f"Duplicate {label} id: {item_id}")
            continue
        result[item_id] = item
    return result


def validate_policy(contract: dict[str, Any], report: ValidationReport) -> None:
    policy = contract.get("grading_policy")
    if not isinstance(policy, dict):
        report.error("grading-policy", "confidence-contract.yaml must define grading_policy")
        return
    high_requires = set(as_list(policy.get("high_requires")))
    missing = MANDATORY_HIGH_REQUIREMENTS - high_requires
    if missing:
        report.error("high-requirements", "Missing high requirements: " + ", ".join(sorted(missing)))

    mappings: dict[str, str] = {}
    for position, rule in enumerate(as_list(policy.get("downgrade_rules"))):
        if not isinstance(rule, dict):
            report.error("downgrade-rule", f"downgrade_rules[{position}] must be a mapping")
            continue
        condition = rule.get("condition")
        level = rule.get("level")
        if not nonempty_string(condition):
            report.error("downgrade-condition", f"downgrade_rules[{position}] needs condition")
        if level not in VALID_LEVELS:
            report.error("downgrade-level", f"downgrade_rules[{position}] has invalid level: {level}")
        if nonempty_string(condition) and level in VALID_LEVELS:
            mappings[condition] = level
    for condition, level in MANDATORY_DOWNGRADES.items():
        if mappings.get(condition) != level:
            report.error("mandatory-downgrade", f"grading_policy must map {condition} to {level}")

    aggregation = policy.get("aggregation")
    if not isinstance(aggregation, dict):
        report.error("aggregation", "grading_policy.aggregation must be a mapping")
    elif aggregation.get("use_numeric_average") is not False:
        report.error("numeric-average", "use_numeric_average must be false")


def detect_cycle(results: dict[str, dict[str, Any]]) -> list[str] | None:
    active: list[str] = []
    done: set[str] = set()

    def visit(node: str) -> list[str] | None:
        if node in active:
            start = active.index(node)
            return active[start:] + [node]
        if node in done:
            return None
        active.append(node)
        for dependency in as_list(results[node].get("dependencies")):
            if dependency in results:
                cycle = visit(dependency)
                if cycle:
                    return cycle
        active.pop()
        done.add(node)
        return None

    for node in results:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def validate_package(package_dir: Path) -> ValidationReport:
    report = ValidationReport()
    for file_name in REQUIRED_FILES:
        if not (package_dir / file_name).is_file():
            report.error("missing-file", f"Required file is missing: {file_name}")
    if report.errors:
        return report

    contract = load_yaml(package_dir / "confidence-contract.yaml", report)
    risks_data = load_yaml(package_dir / "known-risk-patterns.yaml", report)
    validators_data = load_yaml(package_dir / "validator-spec.yaml", report)
    if report.errors:
        return report

    for file_name, data in (
        ("confidence-contract.yaml", contract),
        ("known-risk-patterns.yaml", risks_data),
        ("validator-spec.yaml", validators_data),
    ):
        if str(data.get("schema_version", "")) != "1.0":
            report.error("schema-version", f"{file_name} must set schema_version to '1.0'")

    agent = contract.get("agent")
    if not isinstance(agent, dict):
        report.error("agent", "confidence-contract.yaml must define agent")
    else:
        for key in ("id", "name", "version", "owner", "description"):
            if not nonempty_string(agent.get(key)):
                report.error("agent-field", f"agent.{key} must be a non-empty string")

    scope = contract.get("supported_scope")
    if not isinstance(scope, dict):
        report.error("supported-scope", "confidence-contract.yaml must define supported_scope")
    else:
        for key in ("inputs", "outputs", "assumptions", "exclusions"):
            if not isinstance(scope.get(key), list):
                report.error("supported-scope-field", f"supported_scope.{key} must be a list")

    validate_policy(contract, report)

    results = unique_index(as_list(contract.get("result_units")), "result_units", report)
    validators = unique_index(as_list(validators_data.get("validators")), "validators", report)
    risks = unique_index(as_list(risks_data.get("risks")), "risks", report)
    if not results:
        report.error("result-units", "At least one result unit is required")
    if not validators:
        report.error("validators", "At least one validator is required")
    if not risks:
        report.warning("no-known-risks", "No known test risks have been recorded")

    for validator_id, validator in validators.items():
        validator_type = validator.get("type")
        status = validator.get("implementation_status")
        if validator_type not in VALID_VALIDATOR_TYPES:
            report.error("validator-type", f"Validator {validator_id} has invalid type: {validator_type}")
        if status not in VALID_IMPLEMENTATION_STATUS:
            report.error("validator-status", f"Validator {validator_id} has invalid status: {status}")
        elif status == "planned":
            report.warning("validator-planned", f"Validator {validator_id} is still planned")
        elif status == "deprecated":
            report.warning("validator-deprecated", f"Validator {validator_id} is deprecated")

        applies_to = as_list(validator.get("applies_to"))
        if not applies_to:
            report.error("validator-target", f"Validator {validator_id} must apply to a result")
        for result_id in applies_to:
            if result_id not in results:
                report.error("unknown-result", f"Validator {validator_id} targets unknown result: {result_id}")

        for field_name in ("fail_effect", "unavailable_effect"):
            if validator.get(field_name) not in VALID_LEVELS:
                report.error("validator-level", f"Validator {validator_id} has invalid {field_name}")
        if validator.get("unavailable_effect") == "high":
            report.error("unavailable-high", f"Validator {validator_id} cannot map unavailable to high")

        implementation = validator.get("implementation")
        if status in {"implemented", "verified"}:
            if not nonempty_string(implementation):
                report.error("implementation-path", f"Validator {validator_id} has no implementation path")
            elif not (package_dir / implementation).is_file():
                report.error("implementation-missing", f"Missing implementation for {validator_id}: {implementation}")

        tests = as_list(validator.get("regression_tests"))
        if not tests:
            report.warning("validator-no-tests", f"Validator {validator_id} has no regression tests")
        for test_path in tests:
            if nonempty_string(test_path) and not (package_dir / test_path).is_file():
                report.warning("test-missing", f"Validator {validator_id} references missing test: {test_path}")

    for result_id, result in results.items():
        criticality = result.get("criticality")
        if criticality not in VALID_CRITICALITIES:
            report.error("criticality", f"Result {result_id} has invalid criticality: {criticality}")
        if result.get("maximum_level_when_unverified") == "high":
            report.error("unverified-high", f"Result {result_id} cannot be high when unverified")
        elif result.get("maximum_level_when_unverified") not in {"medium", "low"}:
            report.error("unverified-level", f"Result {result_id} needs medium or low unverified cap")

        required = as_list(result.get("required_validators"))
        optional = as_list(result.get("optional_validators"))
        if criticality in {"critical", "high"} and not required:
            report.error("critical-without-validator", f"Result {result_id} needs required validators")
        for validator_id in required + optional:
            if validator_id not in validators:
                report.error("unknown-validator", f"Result {result_id} references unknown validator: {validator_id}")
        deterministic = [
            validator_id for validator_id in required
            if validator_id in validators and validators[validator_id].get("type") == "deterministic"
        ]
        if criticality in {"critical", "high"} and not deterministic:
            report.error("no-deterministic-evidence", f"Critical/high result {result_id} needs deterministic evidence")

        for dependency in as_list(result.get("dependencies")):
            if dependency not in results:
                report.error("unknown-dependency", f"Result {result_id} references unknown dependency: {dependency}")
        for validator_id in required:
            if validator_id in validators and result_id not in as_list(validators[validator_id].get("applies_to")):
                report.error("validator-target-mismatch", f"Validator {validator_id} does not apply to {result_id}")

    cycle = detect_cycle(results)
    if cycle:
        report.error("dependency-cycle", "Result dependency cycle: " + " -> ".join(cycle))

    for risk_id, risk in risks.items():
        source = risk.get("source")
        severity = risk.get("severity")
        detectability = risk.get("detectability")
        if source not in VALID_RISK_SOURCES:
            report.error("risk-source", f"Risk {risk_id} has invalid source: {source}")
        if severity not in VALID_CRITICALITIES:
            report.error("risk-severity", f"Risk {risk_id} has invalid severity: {severity}")
        if detectability not in VALID_DETECTABILITY:
            report.error("risk-detectability", f"Risk {risk_id} has invalid detectability: {detectability}")

        affected = as_list(risk.get("affected_result_units"))
        if not affected:
            report.error("risk-target", f"Risk {risk_id} must affect a result")
        for result_id in affected:
            if result_id not in results:
                report.error("unknown-result", f"Risk {risk_id} references unknown result: {result_id}")

        validator_id = risk.get("validator_id")
        manual_gate = risk.get("manual_gate")
        if detectability in {"deterministic", "semantic_assist"}:
            if not nonempty_string(validator_id) or validator_id not in validators:
                report.error("unknown-validator", f"Risk {risk_id} needs a valid validator_id")
            elif validators[validator_id].get("type") != detectability:
                report.error("detector-type", f"Risk {risk_id} detectability and validator type differ")
        elif detectability == "manual" and not nonempty_string(manual_gate):
            report.error("manual-gate", f"Manual risk {risk_id} needs manual_gate")

        for field_name in ("on_detected", "on_unverified"):
            if risk.get(field_name) not in VALID_LEVELS:
                report.error("risk-level", f"Risk {risk_id} has invalid {field_name}")
        if risk.get("on_unverified") == "high":
            report.error("unverified-high", f"Risk {risk_id} cannot be high when unverified")
        if not nonempty_string(risk.get("issue_reference")):
            report.error("issue-reference", f"Risk {risk_id} needs issue_reference")
        if not as_list(risk.get("trigger_conditions")):
            report.error("trigger-condition", f"Risk {risk_id} needs trigger_conditions")

        regression_tests = as_list(risk.get("regression_tests"))
        if not regression_tests:
            report.error("risk-no-regression-test", f"Risk {risk_id} needs a regression test")
        for test_path in regression_tests:
            if nonempty_string(test_path) and not (package_dir / test_path).is_file():
                report.warning("test-missing", f"Risk {risk_id} references missing test: {test_path}")

        if (
            severity in {"critical", "high"}
            and validator_id in validators
            and validators[validator_id].get("implementation_status") != "verified"
        ):
            report.warning("critical-risk-detector-not-verified", f"Risk {risk_id} detector is not verified")

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an Agent confidence design package")
    parser.add_argument("package_dir", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package_dir = args.package_dir.resolve()
    if not package_dir.is_dir():
        print(f"ERROR: package directory does not exist: {package_dir}")
        return 1
    report = validate_package(package_dir)
    report.print()
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
