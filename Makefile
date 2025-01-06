APP_NAME := nava-platform
PKG_NAME := nava-platform-cli

PY_SRCS := nava tests

PY_RUN ?= poetry run


ifdef CI
FMT_ARGS :=--check
LINT_ARGS :=
else
FMT_ARGS :=
LINT_ARGS :=--fix
endif

build: ## Build docker image
	docker build --tag $(PKG_NAME) .

check: ## Run checks
check: check-static test

check-static: ## Run static code checks
check-static: fmt lint

clean: ## Remove intermediate, cache, or build artifacts
	find . -type f -name '*.py[cod]' -delete
	find . -type d -name __pycache__ -print -exec rm -r {} +
	find . -type d -name '*.egg-info' -print -exec rm -r {} +
	find . -type d -name .mypy_cache -print -exec rm -r {} +
	find . -type d -name .pytest_cache -print -exec rm -r {} +
	$(PY_RUN) ruff clean
	-docker image rm $(PKG_NAME)

clean-venv: ## Remove active poetry virtualenv
	rm -rf $(shell poetry env info --path)

deps: ## Install dev dependencies
	poetry install

fmt: ## Run formatter
	$(PY_RUN) ruff format $(FMT_ARGS) $(PY_SRCS)

lint: ## Run linting
lint: lint-mypy lint-ruff lint-poetry

lint-mypy: ## Run mypy
	$(PY_RUN) mypy $(args) $(PY_SRCS)

lint-ruff: ## Run ruff linting with auto-fixes
	$(PY_RUN) ruff check $(LINT_ARGS) $(args) $(PY_SRCS)

lint-poetry: ## Run poetry checks
	poetry check --lock

setup-tooling: ## Install build/development tools
	pipx install 'poetry>=1.2.0,<2.0'

test: ## Run tests
	$(PY_RUN) pytest $(args)

test-e2e: ## Run "e2e" tests, requires that the tool is installed
	./bin/test-e2e $(args)

help: ## Display this help screen
	@grep -Eh '^[[:print:]]+:.*?##' $(MAKEFILE_LIST) | \
	sort -d | \
	awk -F':.*?## ' '{printf "\033[36m%s\033[0m\t%s\n", $$1, $$2}' | \
	column -ts "$$(printf '\t')"
	@echo ""
	@echo "APP_NAME=$(APP_NAME)"
	@echo "PKG_NAME=$(PKG_NAME)"
	@echo "PY_RUN=$(PY_RUN)"
