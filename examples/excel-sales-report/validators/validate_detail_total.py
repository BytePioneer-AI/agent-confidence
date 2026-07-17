def validate(detail_amounts: list[float], reported_total: float, tolerance: float = 0.01) -> dict:
    expected = round(sum(detail_amounts), 2)
    actual = round(reported_total, 2)
    difference = round(actual - expected, 2)
    passed = abs(difference) <= tolerance
    return {
        "status": "PASS" if passed else "FAIL",
        "expected": expected,
        "actual": actual,
        "difference": difference,
        "message": "Detail and total reconcile" if passed else "Detail and total do not reconcile",
    }
