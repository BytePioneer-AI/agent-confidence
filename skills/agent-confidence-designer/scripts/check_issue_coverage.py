#!/usr/bin/env python3
"""Report whether every known test issue has a detector/manual gate and regression test."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required. Install it with: python -m pip install PyYAML") from exc


def load_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing required file: {path}") from exc
    except yaml.YAMLError as exc:
        raise SystemExit(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected YAML mapping in {path}")
    return value


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def analyze(package_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    risks_data = load_mapping(package_dir / "known-risk-patterns.yaml")
    validators_data = load_mapping(package_dir / "validator-spec.yaml")
    validator_ids = {
        item.get("id")
        for item in as_list(validators_data.get("validators"))
        if isinstance(item, dict) and nonempty(item.get("id"))
    }

    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for risk in as_list(risks_data.get("risks")):
        if not isinstance(risk, dict):
            failures.append("Risk entry is not a mapping")
            continue
        risk_id = risk.get("id", "<missing-id>")
        detectability = risk.get("detectability")
        validator_id = risk.get("validator_id")
        manual_gate = risk.get("manual_gate")
        tests = as_list(risk.get("regression_tests"))

        detector_ok = False
        detector_label = "missing"
        if detectability in {"deterministic", "semantic_assist"}:
            detector_ok = nonempty(validator_id) and validator_id in validator_ids
            detector_label = str(validator_id or "missing")
        elif detectability == "manual":
            detector_ok = nonempty(manual_gate)
            detector_label = str(manual_gate or "missing")

        existing_tests = [
            test for test in tests if nonempty(test) and (package_dir / test).is_file()
        ]
        test_ok = bool(tests) and len(existing_tests) == len(tests)

        row = {
            "id": risk_id,
            "severity": risk.get("severity", "unknown"),
            "source": risk.get("source", "unknown"),
            "detector": detector_label,
            "detector_ok": detector_ok,
            "tests_ok": test_ok,
        }
        rows.append(row)

        if not detector_ok:
            failures.append(f"{risk_id}: missing valid detector or manual gate")
        if not tests:
            failures.append(f"{risk_id}: no regression test declared")
        elif not test_ok:
            missing = [test for test in tests if not (package_dir / str(test)).is_file()]
            failures.append(f"{risk_id}: missing regression test file(s): {', '.join(map(str, missing))}")

    return rows, failures


def print_report(rows: list[dict[str, Any]], failures: list[str]) -> None:
    print("Known issue coverage")
    print("=" * 88)
    print(f"{'Risk':<28} {'Severity':<10} {'Source':<18} {'Detector':<20} {'Tests':<8}")
    print("-" * 88)
    for row in rows:
        detector = "OK" if row["detector_ok"] else "MISSING"
        tests = "OK" if row["tests_ok"] else "MISSING"
        detector_value = f"{row['detector']} ({detector})"
        print(
            f"{str(row['id']):<28} {str(row['severity']):<10} "
            f"{str(row['source']):<18} {detector_value:<20} {tests:<8}"
        )
    print("-" * 88)
    if failures:
        print("Coverage failures:")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("All known issues have a detector/manual gate and existing regression tests.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check known issue coverage")
    parser.add_argument("package_dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package_dir = args.package_dir.resolve()
    if not package_dir.is_dir():
        print(f"ERROR: package directory does not exist: {package_dir}")
        return 1
    rows, failures = analyze(package_dir)
    print_report(rows, failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
