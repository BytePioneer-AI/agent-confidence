def validate(claims: list[dict]) -> dict:
    mismatches = [
        claim.get("claim_id")
        for claim in claims
        if claim.get("claim_period") != claim.get("source_period")
    ]
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "mismatches": mismatches,
        "message": "Periods aligned" if not mismatches else "Period mismatch",
    }
