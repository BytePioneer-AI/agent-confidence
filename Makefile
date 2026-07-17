PYTHON ?= python3
SKILL_DIR := skills/agent-confidence-designer
VALIDATOR := $(SKILL_DIR)/scripts/validate_confidence_package.py
COVERAGE := $(SKILL_DIR)/scripts/check_issue_coverage.py

.PHONY: test validate-examples

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-examples:
	$(PYTHON) $(VALIDATOR) examples/excel-sales-report --strict
	$(PYTHON) $(COVERAGE) examples/excel-sales-report
	$(PYTHON) $(VALIDATOR) examples/word-management-report --strict
	$(PYTHON) $(COVERAGE) examples/word-management-report
