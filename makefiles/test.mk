.PHONY: test
test: ##@test Run full test suite with coverage for selected package(s)
test:
	${POETRY} run pytest -s --tb=native --durations=10 \
		$(COV_ARGS) \
		--cov-report=html \
		--ignore=tests/integration \
		tests
	${POETRY} run coverage report --fail-under=50

.PHONY: test-integration
test-integration: ##@test Run integration tests (requires live .v20.conf)
test-integration:
	${POETRY} run pytest -s --tb=native tests/integration

.PHONY: test-unit
test-unit: ##@test Run unit tests only
test-unit:
	${POETRY} run pytest -s --tb=native tests/unit
