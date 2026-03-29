# =========================================
# envctl - Makefile
# =========================================

PYTHON ?= python3
PIP ?= pip
SRC ?= src
TESTS ?= tests

RUFF ?= ruff
MYPY ?= mypy
PYTEST ?= pytest

PACKAGE ?= envctl
COV_TARGET ?= src/envctl

.DEFAULT_GOAL := help

.PHONY: \
	help \
	install install-dev \
	lint lint-fix format format-check typecheck \
	test test-cov test-fast \
	check fix \
	clean clean-hard \
	status commit push \
	run doctor

# -----------------------------------------
# Help
# -----------------------------------------

help: ## Show available commands
	@echo ""
	@echo "envctl - available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""

# -----------------------------------------
# Setup
# -----------------------------------------

install: ## Install package in editable mode
	$(PIP) install -e .

install-dev: ## Install package with development dependencies
	$(PIP) install -e ".[dev]"

# -----------------------------------------
# Quality
# -----------------------------------------

lint: ## Run Ruff checks
	$(RUFF) check .

lint-fix: ## Run Ruff with auto-fix
	$(RUFF) check . --fix

format: ## Format code with Ruff
	$(RUFF) format .

format-check: ## Check formatting with Ruff
	$(RUFF) format --check .

typecheck: ## Run static type checking with mypy
	$(MYPY) $(SRC)

# -----------------------------------------
# Tests
# -----------------------------------------

test: ## Run test suite
	$(PYTEST)

test-cov: ## Run tests with coverage report
	$(PYTEST) --cov=$(COV_TARGET) --cov-report=term-missing

test-fast: ## Run tests quietly without coverage
	$(PYTEST) -q

# -----------------------------------------
# Combined workflows
# -----------------------------------------

check: lint format-check typecheck test-cov ## Run all checks (CI-like)

fix: lint-fix format ## Auto-fix code style issues

# -----------------------------------------
# Clean
# -----------------------------------------

clean: ## Remove Python, pytest, Ruff, mypy and build artifacts
	@echo "Cleaning artifacts..."
	rm -rf \
		.pytest_cache \
		.ruff_cache \
		.mypy_cache \
		.coverage \
		htmlcov \
		dist \
		build \
		*.egg-info \
		.eggs
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

clean-hard: clean ## Full clean including local virtual environment
	rm -rf .venv

# -----------------------------------------
# Git helpers
# -----------------------------------------

status: ## Show git status
	git status

commit: ## Commit changes (usage: make commit msg="message")
	@test -n "$(msg)" || (echo 'Error: use make commit msg="your message"' && exit 1)
	git add .
	git commit -m "$(msg)"

push: ## Push current branch to origin
	git push

# -----------------------------------------
# CLI shortcuts
# -----------------------------------------

run: ## Run envctl CLI
	$(PYTHON) -m envctl

doctor: ## Run envctl doctor
	$(PYTHON) -m envctl doctor