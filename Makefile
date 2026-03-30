# =========================================
# envctl - Makefile
# =========================================

# -----------------------------------------
# Core tools
# -----------------------------------------

PYTHON ?= python3
PIP ?= pip

RUFF ?= ruff
MYPY ?= mypy
PYTEST ?= pytest
BUILD ?= python -m build
TWINE ?= python -m twine

# -----------------------------------------
# Project paths
# -----------------------------------------

SRC ?= src
TESTS ?= tests
PACKAGE ?= envctl
COV_TARGET ?= src/envctl

# -----------------------------------------
# Pytest arguments
# -----------------------------------------

PYTEST_BASE_ARGS ?= -ra -vv --tb=short --color=yes
PYTEST_DEBUG_ARGS ?= --showlocals --durations=10
PYTEST_COV_ARGS ?= --cov=$(COV_TARGET) --cov-report=term-missing:skip-covered --cov-report=html --cov-report=xml

# -----------------------------------------
# Defaults
# -----------------------------------------

.DEFAULT_GOAL := help

.PHONY: \
	help \
	install install-dev \
	lint lint-fix format format-check typecheck \
	test test-cov test-fast test-debug \
	check fix \
	clean clean-hard \
	build-package check-package publish-package \
	run doctor \
	status commit push

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
# Environment setup
# -----------------------------------------

install: ## Install package in editable mode
	$(PIP) install -e .

install-dev: ## Install package with development dependencies
	$(PIP) install -e ".[dev]"

# -----------------------------------------
# Code quality
# -----------------------------------------

lint: ## Run Ruff checks
	$(RUFF) check .

lint-fix: ## Run Ruff checks with auto-fix
	$(RUFF) check . --fix

format: ## Format code with Ruff
	$(RUFF) format .

format-check: ## Check code formatting with Ruff
	$(RUFF) format --check .

typecheck: ## Run static type checking with mypy
	$(MYPY) $(SRC)

# -----------------------------------------
# Test suite
# -----------------------------------------

test: ## Run test suite with readable output
	$(PYTEST) $(PYTEST_BASE_ARGS)

test-cov: ## Run test suite with coverage
	$(PYTEST) $(PYTEST_BASE_ARGS) $(PYTEST_DEBUG_ARGS) $(PYTEST_COV_ARGS)

test-fast: ## Run tests quietly without coverage
	$(PYTEST) -q

test-debug: ## Run tests with maximum failure detail
	$(PYTEST) -vv -ra --tb=long --showlocals --maxfail=1 --color=yes

# -----------------------------------------
# Composite workflows
# -----------------------------------------

check: lint format-check typecheck test-cov ## Run full CI-like validation suite

fix: lint-fix format ## Auto-fix style and formatting issues

# -----------------------------------------
# Build and publish
# -----------------------------------------

build-package: clean ## Build distribution artifacts
	$(BUILD)

check-package: ## Validate built distribution metadata
	$(TWINE) check dist/*

publish-package: build-package check-package ## Upload package to PyPI
	$(TWINE) upload dist/*

# -----------------------------------------
# Cleanup
# -----------------------------------------

clean: ## Remove caches, coverage files, and build artifacts
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
		.eggs \
		codereview
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

clean-hard: clean ## Remove additional local environment artifacts
	rm -rf .tox .nox .cache

# -----------------------------------------
# Git helpers
# -----------------------------------------

status: ## Show git status
	git status

commit: ## Commit all changes (usage: make commit msg="message")
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