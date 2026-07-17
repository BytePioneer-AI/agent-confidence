from pathlib import Path


def validate(output_paths: list[str]) -> dict:
    missing = [path for path in output_paths if not Path(path).is_file()]
    empty = [path for path in output_paths if Path(path).is_file() and Path(path).stat().st_size == 0]
    passed = not missing and not empty
    return {
        "status": "PASS" if passed else "FAIL",
        "missing_files": missing,
        "empty_files": empty,
        "message": "Output files present" if passed else "Output file integrity failure",
    }
