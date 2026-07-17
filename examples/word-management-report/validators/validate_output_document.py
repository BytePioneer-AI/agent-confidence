from pathlib import Path


def validate(document_path: str) -> dict:
    path = Path(document_path)
    passed = path.is_file() and path.stat().st_size > 0
    return {
        "status": "PASS" if passed else "FAIL",
        "path": document_path,
        "message": "Document exists and is non-empty" if passed else "Document missing or empty",
    }
