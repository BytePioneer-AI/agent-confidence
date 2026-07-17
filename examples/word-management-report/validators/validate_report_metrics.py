def validate(report_claims: list[dict], source_metrics: dict[str, dict]) -> dict:
    mismatches = []
    for claim in report_claims:
        metric_id = claim.get("metric_id")
        source = source_metrics.get(metric_id)
        if source is None:
            mismatches.append({"claim": claim, "reason": "missing_source"})
            continue
        differences = {
            key: (source.get(key), claim.get(key))
            for key in ("value", "period", "unit")
            if source.get(key) != claim.get(key)
        }
        if differences:
            mismatches.append({"metric_id": metric_id, "differences": differences})
    passed = not mismatches
    return {
        "status": "PASS" if passed else "FAIL",
        "mismatches": mismatches,
        "message": "Report metrics match sources" if passed else "Report metric mismatch",
        "review_action": None if passed else "Check metric_id, value, period and unit",
    }
