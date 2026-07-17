def validate(claims: list[dict]) -> dict:
    missing = [claim.get("claim_id") for claim in claims if not claim.get("evidence_refs")]
    return {
        "status": "PASS" if not missing else "FAIL",
        "items_without_evidence": missing,
        "message": "Evidence links complete" if not missing else "Claims without evidence",
        "review_action": None if not missing else "Attach evidence or route the claim to review",
    }
