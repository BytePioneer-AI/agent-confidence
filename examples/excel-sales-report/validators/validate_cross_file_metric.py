def validate(excel_metric: dict, report_metric: dict) -> dict:
    keys = ("value", "period", "currency")
    differences = {key: (excel_metric.get(key), report_metric.get(key)) for key in keys if excel_metric.get(key) != report_metric.get(key)}
    passed = not differences
    return {
        "status": "PASS" if passed else "FAIL",
        "expected": excel_metric,
        "actual": report_metric,
        "differences": differences,
        "message": "Cross-file metric consistent" if passed else "Cross-file metric mismatch",
        "review_action": None if passed else "Check value, period and currency mapping",
    }
