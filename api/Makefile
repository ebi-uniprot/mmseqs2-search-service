SHELL := /bin/bash
.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))
VERSION := $$(grep '^version' pyproject.toml | head -1 | sed 's%version = "\(.*\)"%\1%')
APP_NAME := $$(grep '^name' pyproject.toml | head -1 | sed 's%name = "\(.*\)"%\1%')

.DEFAULT_GOAL := help

version: ## display version and exit
	@echo $(VERSION)

dev: ## setup development environment
	$(shell echo $$SHELL) ./setup.sh

test: ## run unit tests
	@echo "Running tests..."
	@uv run --frozen pytest

lint: ## run linting
	@echo "Running linting tools..."
	@uv run --frozen ruff check --fix --select I src/$(APP_NAME) tests
	@uv run --frozen pydoclint --config=pyproject.toml src tests

type-check: ## run mypy and check types
	@echo "Running type checks..."
	@uv run --frozen mypy --install-types --non-interactive src/$(APP_NAME)

format: ## run formatting
	@echo "Running formatting tools..."
	@uv run --frozen ruff format src/$(APP_NAME) tests

dep-check: ## check for outdated dependencies
	@echo "Running dependencies checks..."
	@uv run --frozen deptry . --known-first-party $(APP_NAME)

build: ## build distributions
	@echo "Building distributions..."
	@uv build

check: lint format test type-check dep-check ## run all checks

help: ## This is help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build-docker: ## build docker image
	docker build -t $(APP_NAME):$(VERSION) --no-cache -f Dockerfile .

test-api: ## Test the API
	uv run api
