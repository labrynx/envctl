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

PYTEST_BASE_ARGS ?= -ra -vv --tb=short --color=yes
PYTEST_DEBUG_ARGS ?= --showlocals --durations=10
PYTEST_COV_ARGS ?= --cov=$(COV_TARGET) --cov-report=term-missing:skip-covered --cov-report=html --cov-report=xml

.DEFAULT_GOAL := help

.PHONY: \
	help \
	install install-dev \
	lint lint-fix format format-check typecheck \
	test test-cov test-fast test-debug \
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

test: ## Run test suite with readable output
	$(PYTEST) $(PYTEST_BASE_ARGS)

test-cov: ## Run tests with detailed coverage and readable failures
	$(PYTEST) $(PYTEST_BASE_ARGS) $(PYTEST_DEBUG_ARGS) $(PYTEST_COV_ARGS)

test-fast: ## Run tests quietly without coverage
	$(PYTEST) -q

test-debug: ## Run tests with maximum failure context
	$(PYTEST) -vv -ra --tb=long --showlocals --maxfail=1 --color=yes

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
		coverage.xml \
		dist \
		build \
		*.egg-info \
		.eggs
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	rm -rf codereview

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