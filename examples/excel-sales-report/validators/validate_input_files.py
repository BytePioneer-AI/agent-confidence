def validate(expected_files: list[str], processed_files: list[str]) -> dict:
    expected = set(expected_files)
    processed = set(processed_files)
    missing = sorted(expected - processed)
    extra = sorted(processed - expected)
    passed = not missing and not extra
    return {
        "status": "PASS" if passed else "FAIL",
        "expected": sorted(expected),
        "actual": sorted(processed),
        "missing_files": missing,
        "extra_files": extra,
        "message": "Input file set matches" if passed else "Input file set mismatch",
    }
