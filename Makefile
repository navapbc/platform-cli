APP_NAME := nava-platform
PKG_NAME := nava-platform-cli

PY_SRCS := nava tests

PY_RUN ?= uv run --frozen


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
check: check-static test test-e2e

check-static: ## Run static code checks
check-static: fmt lint

clean: ## Remove intermediate, cache, or build artifacts
clean: clean-docs
	find . -type f -name '*.py[cod]' -delete
	find . -type d -name __pycache__ -print -exec rm -r {} +
	find . -type d -name '*.egg-info' -print -exec rm -r {} +
	find . -type d -name .mypy_cache -print -exec rm -r {} +
	find . -type d -name .pytest_cache -print -exec rm -r {} +
	$(PY_RUN) ruff clean
	-docker image rm $(PKG_NAME)

clean-docs: ## Remove generated doc files
	rm -f docs/index.md

	rm -rf $(REFERENCE_DOC_DIR)
	mkdir -p $(REFERENCE_DOC_DIR)
	touch $(REFERENCE_DOC_DIR)/.keep

	rm -rf site/

clean-venv: ## Remove active virtualenv
	rm -rf ./.venv/

deps: ## Install dev dependencies
	uv sync --dev --frozen

.PHONY: docs
docs: ## Generate documentation
docs: docs/index.md docs-reference
	$(PY_RUN) mkdocs build

docs-watch: ## Start local server that will re-generate docs on file change
docs-watch: docs-reference
	$(PY_RUN) mkdocs serve

docs/index.md: README.md
	cp -f $< $@
	sed -ri 's|\./docs/||g' $@

REFERENCE_DOC_DIR := ./docs/reference

python_module_files := $(shell find nava -type f -name '*.py')
python_module_doc_files := $(patsubst %.py,$(REFERENCE_DOC_DIR)/%.md,$(python_module_files))

docs-reference: $(python_module_doc_files)
	find $(REFERENCE_DOC_DIR) -name '__init__.md' -print -exec bash -c 'mv $$0 $${0/__init__/index}' {} \;

define python_module_name_from_file_name
$(shell echo $(1) | sed 's/__init__.py//' | sed 's/.py//' | sed 's|/|\.|g' | sed 's/\.$$//')
endef

$(REFERENCE_DOC_DIR)/%.md: %.py
	mkdir -p $(@D)
	echo "::: $(call python_module_name_from_file_name, $<)" > $@

fmt: ## Run formatter
	$(PY_RUN) ruff format $(FMT_ARGS) $(PY_SRCS)

lint: ## Run linting
lint: lint-mypy lint-ruff lint-uv

lint-mypy: ## Run mypy
	$(PY_RUN) mypy $(args) $(PY_SRCS)

lint-ruff: ## Run ruff linting with auto-fixes
	$(PY_RUN) ruff check $(LINT_ARGS) $(args) $(PY_SRCS)

lint-uv: ## Run uv checks
	uv lock --check

setup-tooling: ## Install build/development tools
	curl -LsSf https://astral.sh/uv/install.sh | sh

test: ## Run tests
	$(PY_RUN) pytest $(args)

test-e2e: ## Run "e2e" tests, requires that the tool is installed
	./bin/test-e2e $(args)

update-container-digest: ## Update container digests to latest
	./bin/update-container-digest Dockerfile

help: ## Display this help screen
	@grep -Eh '^[[:print:]]+:.*?##' $(MAKEFILE_LIST) | \
	sort -d | \
	awk -F':.*?## ' '{printf "\033[36m%s\033[0m\t%s\n", $$1, $$2}' | \
	column -ts "$$(printf '\t')"
	@echo ""
	@echo "APP_NAME=$(APP_NAME)"
	@echo "PKG_NAME=$(PKG_NAME)"
	@echo "PY_RUN=$(PY_RUN)"
