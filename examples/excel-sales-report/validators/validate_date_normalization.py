def validate(records: list[dict]) -> dict:
    invalid_ids = [record.get("record_id") for record in records if not record.get("parsed_date")]
    return {
        "status": "PASS" if not invalid_ids else "FAIL",
        "target": "normalized-sales-detail",
        "invalid_record_ids": invalid_ids,
        "message": "All dates normalized" if not invalid_ids else "Unparsed dates found",
    }
