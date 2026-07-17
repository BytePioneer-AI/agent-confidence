def validate(structured_semantic_review: list[dict]) -> dict:
    risky = [
        item
        for item in structured_semantic_review
        if item.get("review_status") != "supported"
    ]
    return {
        "status": "PASS" if not risky else "FAIL",
        "risky_claims": risky,
        "message": "No unsupported causal claims found" if not risky else "Unsupported causal claims found",
        "review_action": None if not risky else "Review the cited evidence or weaken the causal wording",
    }
