def validate(source_record_ids: list[str]) -> dict:
    passed = bool(source_record_ids) and all(bool(item) for item in source_record_ids)
    return {
        "status": "PASS" if passed else "FAIL",
        "source_record_ids": source_record_ids,
        "message": "Sources traceable" if passed else "Missing source record references",
    }
