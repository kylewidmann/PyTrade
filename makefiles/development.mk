.PHONY: venv
venv: ##@development Set up virtual environment
venv:
	${POETRY} install

.PHONY: infrastructure
infrastructure: ##@development Set up infrastructure for tests
infrastructure:
	@echo "Skipping..."

.PHONY: clean
clean: ##@development Clean up any dependencies
clean:
	@echo "Skipping..."

.PHONY: ci
ci: ##@development Run CI pipeline
ci: clean infrastructure lint test clean
