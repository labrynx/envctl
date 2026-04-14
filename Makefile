# =========================================
# envctl - Makefile
# =========================================

# -----------------------------------------
# Core tools
# -----------------------------------------

UV ?= uv
PYTHON ?= python3
COV_MIN ?= 85
IMPORTTIME_LOG_DIR ?= .importtime
ENVCTL_ENTRYPOINT ?= -m envctl
ENVCTL_TIME ?= /usr/bin/time

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
	sync sync-dev sync-full sync-locked sync-full \
	lint lint-fix format format-check typecheck security imports deadcode \
	test test-cov test-ci test-fast test-debug \
	validate check check-clean fix \
	clean clean-hard \
	build-package check-package publish-test publish-package \
	smoke-wheel smoke-sdist smoke-package \
	dist-checksums dist-sbom \
	run inspect \
	status commit push \
	pre-commit-install pre-commit-run pre-push-run \
	docs-install docs-check docs-build docs-serve docs-deploy \
	startup-version startup-help startup-vault-help \
	startup-importtime-clean startup-importtime-report \
	startup-timings startup-full

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

sync: ## Sync project environment
	$(UV) sync

sync-dev: ## Sync project environment with development dependencies
	$(UV) sync --dev

sync-full: ## Sync dev + docs
	$(UV) sync --dev --extra docs

sync-locked: ## Sync project environment with development dependencies from uv.lock without modifying it
	$(UV) sync --dev --locked

# -----------------------------------------
# Code quality
# -----------------------------------------

lint: ## Run Ruff checks
	$(UV) run ruff check .

lint-fix: ## Run Ruff checks with auto-fix
	$(UV) run ruff check . --fix

format: ## Format code with Ruff
	$(UV) run ruff format .

format-check: ## Check code formatting with Ruff
	$(UV) run ruff format --check .

typecheck: ## Run static type checking with mypy
	$(UV) run mypy .

security: ## Run security checks with bandit
	$(UV) run bandit -c pyproject.toml -r $(SRC)

imports: ## Check architectural import contracts
	$(UV) run lint-imports

deadcode: ## Run dead code detection with vulture
	$(UV) run vulture $(SRC) $(TESTS) --exclude .venv --min-confidence 80

# -----------------------------------------
# Test suite
# -----------------------------------------

test: ## Run test suite with readable output
	$(UV) run pytest $(PYTEST_BASE_ARGS)

test-cov: ## Run test suite with coverage
	$(UV) run pytest $(PYTEST_BASE_ARGS) $(PYTEST_DEBUG_ARGS) $(PYTEST_COV_ARGS)

test-ci: ## Run CI-oriented test suite with coverage threshold
	$(UV) run pytest $(PYTEST_BASE_ARGS) $(PYTEST_DEBUG_ARGS) $(PYTEST_COV_ARGS) --cov-fail-under=$(COV_MIN)

test-fast: ## Run tests quickly without coverage
	$(UV) run pytest -q --maxfail=1

test-debug: ## Run tests with maximum failure detail
	$(UV) run pytest -vv -ra --tb=long --showlocals --maxfail=1 --color=yes

# -----------------------------------------
# Composite workflows
# -----------------------------------------

validate: lint format-check typecheck security test-ci imports ## Validate code quality

check-package: build-package ## Validate built distribution metadata
	$(UV) run python -m twine check dist/*.whl dist/*.tar.gz

check: validate build-package check-package smoke-package ## Full validation including build

check-clean: clean check ## Run full validation suite from a clean workspace

fix: lint-fix format ## Auto-fix style and formatting issues

# -----------------------------------------
# Build and publish
# -----------------------------------------

build-package: clean ## Build distribution artifacts
	$(UV) build

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
	$(UV) run python -m twine upload --repository testpypi dist/*.whl dist/*.tar.gz

publish-package: build-package check-package ## Upload package to PyPI
	$(UV) run python -m twine upload dist/*.whl dist/*.tar.gz

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
	rm -rf .tox .nox .cache .sbom-venv .release-venv .release-venv-sdist

# -----------------------------------------
# Git helpers
# -----------------------------------------

pre-commit-install: ## Install pre-commit hooks
	$(UV) run pre-commit install
	$(UV) run pre-commit install --hook-type pre-push

pre-commit-run: ## Run pre-commit on all files
	$(UV) run pre-commit run --all-files

pre-push-run: ## Run pre-push hooks on all files
	$(UV) run pre-commit run --hook-stage pre-push --all-files

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
	$(UV) run envctl

inspect: ## Run envctl inspect
	$(UV) run envctl inspect

# -----------------------------------------
# Documentation
# -----------------------------------------

docs-install: ## Install documentation dependencies
	$(UV) sync --extra docs

docs-check: ## Build MkDocs site in strict mode for CI/local validation
	$(UV) run mkdocs build --strict

docs-build: ## Build MkDocs site locally
	$(UV) run mkdocs build --strict

docs-serve: ## Serve MkDocs site locally with live reload
	$(UV) run mkdocs serve

docs-deploy: ## Deploy MkDocs site to GitHub Pages (requires write access)
	$(UV) run mkdocs gh-deploy --force

# -----------------------------------------
# Startup and import-time analysis
# -----------------------------------------

startup-importtime-clean: ## Remove import-time analysis artifacts
	rm -rf $(IMPORTTIME_LOG_DIR)

startup-version: ## Profile import/startup time for `envctl --version`
	mkdir -p $(IMPORTTIME_LOG_DIR)
	$(UV) run python -X importtime $(ENVCTL_ENTRYPOINT) --version 2> $(IMPORTTIME_LOG_DIR)/version.importtime.log
	@echo ""
	@echo "Saved import-time log to $(IMPORTTIME_LOG_DIR)/version.importtime.log"
	@echo ""
	@grep 'envctl\|cryptography' $(IMPORTTIME_LOG_DIR)/version.importtime.log || true

startup-help: ## Profile import/startup time for `envctl --help`
	mkdir -p $(IMPORTTIME_LOG_DIR)
	$(UV) run python -X importtime $(ENVCTL_ENTRYPOINT) --help 2> $(IMPORTTIME_LOG_DIR)/help.importtime.log
	@echo ""
	@echo "Saved import-time log to $(IMPORTTIME_LOG_DIR)/help.importtime.log"
	@echo ""
	@grep 'envctl\|cryptography' $(IMPORTTIME_LOG_DIR)/help.importtime.log || true

startup-vault-help: ## Profile import/startup time for `envctl vault --help`
	mkdir -p $(IMPORTTIME_LOG_DIR)
	$(UV) run python -X importtime $(ENVCTL_ENTRYPOINT) vault --help 2> $(IMPORTTIME_LOG_DIR)/vault-help.importtime.log
	@echo ""
	@echo "Saved import-time log to $(IMPORTTIME_LOG_DIR)/vault-help.importtime.log"
	@echo ""
	@grep 'envctl\|cryptography' $(IMPORTTIME_LOG_DIR)/vault-help.importtime.log || true

startup-importtime-report: ## Show the heaviest envctl/cryptography imports from collected logs
	@echo ""
	@for file in $(IMPORTTIME_LOG_DIR)/*.log; do \
		[ -f "$$file" ] || continue; \
		echo "==> $$file"; \
		grep 'envctl\|cryptography' "$$file" | tail -n 40 || true; \
		echo ""; \
	done

startup-timings: ## Measure wall-clock and memory for common startup paths
	@echo ""
	@echo "==> envctl --version"
	@$(ENVCTL_TIME) -f "elapsed=%E maxrss=%MKB" $(UV) run python $(ENVCTL_ENTRYPOINT) --version >/dev/null
	@echo ""
	@echo "==> envctl --help"
	@$(ENVCTL_TIME) -f "elapsed=%E maxrss=%MKB" $(UV) run python $(ENVCTL_ENTRYPOINT) --help >/dev/null
	@echo ""
	@echo "==> envctl vault --help"
	@$(ENVCTL_TIME) -f "elapsed=%E maxrss=%MKB" $(UV) run python $(ENVCTL_ENTRYPOINT) vault --help >/dev/null

startup-full: startup-version startup-help startup-vault-help startup-importtime-report startup-timings ## Run all startup/import-time analysis tasks
