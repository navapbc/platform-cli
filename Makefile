APP_NAME := nava-platform
PKG_NAME := nava-platform-cli

build: ## Build docker image
	docker build --tag $(PKG_NAME) .

check: ## Run checks
check: check-static test

check-static: ## Run static code checks
check-static: fmt lint

deps: ## Install dev dependencies
	poetry install

fmt: ## Run formatter
	poetry run ruff format

lint: ## Run linting
	poetry run mypy .
	poetry run ruff check --fix

test: ## Run tests
	poetry run pytest $(args)

help: ## Display this help screen
	@grep -Eh '^[[:print:]]+:.*?##' $(MAKEFILE_LIST) | \
	sort -d | \
	awk -F':.*?## ' '{printf "\033[36m%s\033[0m\t%s\n", $$1, $$2}' | \
	column -ts "$$(printf '\t')"
	@echo ""
	@echo "APP_NAME=$(APP_NAME)"
	@echo "PKG_NAME=$(PKG_NAME)"
