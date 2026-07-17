PYTHON ?= python3
SKILL_DIR := skills/agent-confidence-designer
VALIDATOR := $(SKILL_DIR)/scripts/validate_confidence_package.py
COVERAGE := $(SKILL_DIR)/scripts/check_issue_coverage.py
EXAMPLES := pba-so-contract-agent ecs-uat-automation-agent supplier-questionnaire-integration

.PHONY: test validate-examples

test:
	$(PYTHON) -m unittest discover -s tests -v

validate-examples:
	@for example in $(EXAMPLES); do \
		$(PYTHON) $(VALIDATOR) examples/$$example --strict || exit 1; \
		$(PYTHON) $(COVERAGE) examples/$$example || exit 1; \
	done
