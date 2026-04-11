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
BANDIT ?= bandit
IMPORT_LINTER ?= lint-imports
COV_MIN ?= 85
PYTEST ?= pytest
PRE_COMMIT ?= pre-commit
BUILD ?= $(PYTHON) -m build
TWINE ?= $(PYTHON) -m twine
CYCLONEDX ?= cyclonedx-py

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
	install install-dev bootstrap \
	lint lint-fix format format-check typecheck \
	test test-cov test-ci test-fast test-debug \
	check check-clean fix \
	clean clean-hard \
	build-package check-package publish-test publish-package \
	smoke-wheel smoke-sdist smoke-package \
	dist-checksums dist-sbom \
	run inspect \
	status commit push \
	pre-commit-install pre-commit-run pre-push-run \
	imports \
	docs-check

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

bootstrap: ## Bootstrap a local development environment
	$(PIP) install --upgrade pip
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
	$(MYPY)

security: ## Run security checks with bandit
	$(BANDIT) -c pyproject.toml -r $(SRC)

imports: ## Check architectural import contracts
	$(IMPORT_LINTER)

# -----------------------------------------
# Test suite
# -----------------------------------------

test: ## Run test suite with readable output
	$(PYTEST) $(PYTEST_BASE_ARGS)

test-cov: ## Run test suite with coverage
	$(PYTEST) $(PYTEST_BASE_ARGS) $(PYTEST_DEBUG_ARGS) $(PYTEST_COV_ARGS)

test-ci: ## Run CI-oriented test suite with coverage threshold
	$(PYTEST) $(PYTEST_BASE_ARGS) $(PYTEST_DEBUG_ARGS) $(PYTEST_COV_ARGS) --cov-fail-under=$(COV_MIN)

test-fast: ## Run tests quickly without coverage
	$(PYTEST) -q --maxfail=1

test-debug: ## Run tests with maximum failure detail
	$(PYTEST) -vv -ra --tb=long --showlocals --maxfail=1 --color=yes

# -----------------------------------------
# Composite workflows
# -----------------------------------------

validate: lint format-check typecheck security test-ci imports ## Validate code quality

check-package: build-package ## Validate built distribution metadata
	$(TWINE) check dist/*.whl dist/*.tar.gz

check: validate build-package check-package smoke-package ## Full validation including build

check-clean: clean check ## Run full validation suite from a clean workspace

fix: lint-fix format ## Auto-fix style and formatting issues

deadcode:
	vulture ${SRC} ${TESTS} --exclude .venv --min-confidence 80

# -----------------------------------------
# Build and publish
# -----------------------------------------

build-package: clean ## Build distribution artifacts
	$(BUILD)

smoke-wheel: build-package ## Install built wheel in a clean venv and verify import/CLI
	rm -rf .release-venv
	$(PYTHON) -m venv .release-venv
	./.release-venv/bin/python -m pip install --upgrade pip
	./.release-venv/bin/python -m pip install dist/*.whl
	./.release-venv/bin/python -m pip check
	./.release-venv/bin/python -c "import envctl; print(envctl.__name__)"
	./.release-venv/bin/envctl --version
	./.release-venv/bin/python -m envctl --version
	rm -rf .release-venv

smoke-sdist: build-package ## Install built sdist in a clean venv and verify import/CLI
	rm -rf .release-venv-sdist
	$(PYTHON) -m venv .release-venv-sdist
	./.release-venv-sdist/bin/python -m pip install --upgrade pip
	./.release-venv-sdist/bin/python -m pip install dist/*.tar.gz
	./.release-venv-sdist/bin/python -m pip check
	./.release-venv-sdist/bin/python -c "import envctl; print(envctl.__name__)"
	./.release-venv-sdist/bin/envctl --version
	./.release-venv-sdist/bin/python -m envctl --version
	rm -rf .release-venv-sdist

smoke-package: smoke-wheel smoke-sdist ## Run all package smoke tests

dist-checksums: dist-sbom ## Write SHA256SUMS for built distribution artifacts and SBOM
	cd dist && sha256sum *.whl *.tar.gz envctl-wheel.sbom.cdx.json > SHA256SUMS

dist-sbom: build-package ## Generate a CycloneDX SBOM for the built wheel
	rm -rf .sbom-venv
	$(PYTHON) -m venv .sbom-venv
	./.sbom-venv/bin/python -m pip install --upgrade pip
	./.sbom-venv/bin/python -m pip install cyclonedx-bom==7.3.0 dist/*.whl
	./.sbom-venv/bin/python -m cyclonedx_py environment --of JSON --output-file dist/envctl-wheel.sbom.cdx.json
	rm -rf .sbom-venv

publish-test: build-package check-package ## Upload package to TestPyPI
	$(TWINE) upload --repository testpypi dist/*.whl dist/*.tar.gz

publish-package: build-package check-package ## Upload package to PyPI
	$(TWINE) upload dist/*.whl dist/*.tar.gz

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
		site \
		.import_linter_cache
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	find . -type d -name "*.prof" -prune -exec rm -rf {} +

clean-hard: clean ## Remove additional local environment artifacts
	rm -rf .tox .nox .cache .sbom-venv .release-venv

# -----------------------------------------
# Git helpers
# -----------------------------------------

pre-commit-install: ## Install pre-commit hooks
	$(PRE_COMMIT) install
	$(PRE_COMMIT) install --hook-type pre-push

pre-commit-run: ## Run pre-commit on all files
	$(PRE_COMMIT) run --all-files

pre-push-run: ## Run pre-push hooks on all files
	$(PRE_COMMIT) run --hook-stage pre-push --all-files

status: ## Show git status
	git status

commit: ## Commit staged changes only (usage: make commit msg="message")
	@test -n "$(msg)" || (echo 'Error: use make commit msg="your message"' && exit 1)
	git commit -m "$(msg)"

push: ## Push current branch to origin
	git push

# -----------------------------------------
# CLI shortcuts
# -----------------------------------------

run: ## Run envctl CLI
	envctl

inspect: ## Run envctl inspect
	envctl inspect

# -----------------------------------------
# Documentation
# -----------------------------------------

DOCS_DEPS ?= pip install -e ".[docs]"

docs-install: ## Install documentation dependencies
	$(PIP) install -e ".[docs]"

docs-check: ## Build MkDocs site in strict mode for CI/local validation
	mkdocs build --strict

docs-build: ## Build MkDocs site locally
	mkdocs build --strict

docs-serve: docs-build ## Serve MkDocs site locally with live reload
	mkdocs serve

docs-deploy: ## Deploy MkDocs site to GitHub Pages (requires write access)
	mkdocs gh-deploy --force
