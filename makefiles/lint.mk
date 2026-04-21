.PHONY: bandit
bandit: ##@lint Run bandit security scan
bandit:
	${POETRY} run bandit -r -c .bandit $(SRC_DIRS)

.PHONY: black
black: ##@lint Run black formatter (check mode)
black:
	${POETRY} run black --check $(LINT_DIRS)

.PHONY: black-fix
black-fix: ##@lint Run black formatter (write mode)
black-fix:
	${POETRY} run black $(LINT_DIRS)

.PHONY: flake8
flake8: ##@lint Run flake8
flake8:
	${POETRY} run flake8 --config .flake8 $(LINT_DIRS)

.PHONY: isort
isort: ##@lint Run isort (check mode)
isort:
	${POETRY} run isort --diff --check-only --quiet $(LINT_DIRS)

.PHONY: isort-fix
isort-fix: ##@lint Run isort (write mode)
isort-fix:
	${POETRY} run isort $(LINT_DIRS)

.PHONY: mypy
mypy: ##@lint Run mypy type checker
mypy:
	${POETRY} run mypy $(MYPY_ARGS)

.PHONY: lint
lint: ##@lint Run all lint tools
lint: bandit black flake8 isort mypy

.PHONY: clean-imports
clean-imports: ##@lint Remove unused imports
clean-imports:
	${POETRY} run autoflake --in-place --remove-all-unused-imports --recursive $(LINT_DIRS)

.PHONY: reformat
reformat: ##@lint Auto-fix imports, isort, and black
reformat: clean-imports isort-fix black-fix
