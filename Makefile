build: ## Build docker image
	docker build --tag platform .

deps: ## Install dev dependencies
	poetry install

lint: ## Run linting
	poetry run mypy .

test: ## Run tests
	poetry run pytest $(args)

help: ## Display this help screen
	@grep -Eh '^[[:print:]]+:.*?##' $(MAKEFILE_LIST) | \
	sort -d | \
	awk -F':.*?## ' '{printf "\033[36m%s\033[0m\t%s\n", $$1, $$2}' | \
	column -ts "$$(printf '\t')"
