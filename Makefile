# Check if .env exists
ifeq (,$(wildcard .env))
$(error .env file is missing at .env. Please create one based on .env.example)
endif

# Load environment variables from .env
include .env

.PHONY: help clean ruff mypy create-roles zip-lambdas add-s3-trigger test

# Default target
.DEFAULT_GOAL := help

# All tasks
all: ruff mypy clean

# Create IAM roles
create-roles: ## Create IAM roles
	@echo "✅ Executing create_roles.sh..."
	chmod +x ./scripts/create_roles.sh
	./scripts/create_roles.sh

# Zip Lambda functions
zip-lambdas: ## Zip lambda functions
	@echo "✅ Executing zip_lambdas.sh..."
	chmod +x ./scripts/zip_lambdas.sh
	./scripts/zip_lambdas.sh

# Deploy state machine
deploy: ## Deploy state machine
	uv run deploy.py

# Run pytest tests
test: ## Run pytest tests
	@echo "Running pytest tests..."
	uv run pytest
	@echo "pytest tests complete."

# Run Ruff linter
ruff: ## Run Ruff linter
	@echo "Running Ruff linter..."
	uv run ruff check . --fix --exit-non-zero-on-fix
	@echo "Ruff linter complete."

# Run MyPy static type checker
mypy: ## Run MyPy static type checker
	@echo "Running MyPy static type checker..."
	uv run mypy
	@echo "MyPy static type checker complete."

# Clean up cached generated files
clean: ## Clean up cached generated files
	@echo "Cleaning up generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Cleanup complete."

# Display help message
help: ## Display this help message
	@echo "Default target: $(.DEFAULT_GOAL)"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
