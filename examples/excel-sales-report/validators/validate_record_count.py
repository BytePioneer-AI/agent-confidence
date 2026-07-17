def validate(expected_business_record_count: int, output_record_count: int) -> dict:
    difference = output_record_count - expected_business_record_count
    return {
        "status": "PASS" if difference == 0 else "FAIL",
        "expected": expected_business_record_count,
        "actual": output_record_count,
        "difference": difference,
        "message": "Record count conserved" if difference == 0 else "Record count mismatch",
    }
