def validate(required_sections: list[str], document_sections: dict[str, str]) -> dict:
    missing = [section for section in required_sections if section not in document_sections]
    empty = [section for section in required_sections if section in document_sections and not document_sections[section].strip()]
    passed = not missing and not empty
    return {
        "status": "PASS" if passed else "FAIL",
        "missing_sections": missing,
        "empty_sections": empty,
        "message": "Required sections present" if passed else "Required section failure",
    }
