# Contributing to envctl

Thank you for considering contributing to `envctl`. This document outlines the process for setting up the development environment, running tests, and submitting changes.

## Project philosophy

Before adding features, preserve the core model:

- local-first
- explicit operations
- deterministic initialization
- one responsibility per command
- repository declares the contract, vault stores the secret

Features that blur those boundaries should be treated with caution.

Examples of things to avoid unless strongly justified:

- defaults provided by the tool for project variables
- interactive logic inside `init`
- read-only commands that mutate state
- schema files that become alternate secret stores

## Code of Conduct

This project follows a simple principle: be respectful, provide constructive feedback, and keep discussions focused on technical improvements.

## Development setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/labrynx/envctl.git
   cd envctl
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install development dependencies**

   ```bash
   pip install -U pip
   pip install -e .[dev]
   ```

4. **Run the canonical local validation flow**

   ```bash
   make validate
   ```

This is the supported baseline workflow for contributors today.

### Official local workflow policy

The repository currently supports one canonical local development path:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
make validate
```

This is the path that contributors should use first when checking whether the repo is healthy locally.

`uv.lock` is still tracked intentionally, but its role is narrower:

- it records one tested dependency resolution state
- it supports optional local `uv` workflows for contributors who already use `uv`
- it is not yet the canonical CI input or the primary contributor contract

Until that policy changes explicitly, contributor docs and CI expectations should treat `.venv` + editable `pip install -e ".[dev]"` as the source of truth for local setup.

### Docs workflow

If you are editing documentation or site overrides, install docs extras too:

```bash
pip install -e ".[dev,docs]"
make docs-check
```

Documentation is expected to build cleanly with strict MkDocs validation.

## Project structure

```text
envctl/
├── docs/               # User and contributor documentation
├── src/envctl/         # Main package
│   ├── cli/            # Typer CLI (commands, presenters, serializers, callbacks)
│   ├── config/         # XDG config handling
│   ├── domain/         # Core domain models and result objects
│   ├── repository/     # Metadata and project context resolution
│   ├── services/       # Command orchestration (business logic)
│   ├── adapters/       # External integrations (git, editor, dotenv)
│   ├── utils/          # Generic helpers and internal support
│   ├── constants.py
│   ├── errors.py
│   └── __main__.py
├── tests/              # Test suite
└── README.md
```

### Architectural note

The project follows a layered structure:

* **CLI layer** → handles user input/output (Typer)
* **Service layer** → orchestrates command behavior
* **Domain layer** → defines structured data and results
* **Repository layer** → resolves project metadata and context
* **Config layer** → loads and resolves configuration
* **Utils layer** → pure helpers (filesystem, parsing, etc.)

This separation ensures that business logic remains testable and independent from the CLI framework.

## Adding a new command

1. **Define the service** in `src/envctl/services/new_service.py`

   * Implement a function `run_new(...)` with explicit inputs and outputs.
   * Return a clear result object where appropriate.
   * Raise domain exceptions (`EnvctlError` subclasses) for user-facing errors.

2. **Add the CLI command** in the relevant command module under `src/envctl/cli/commands/`

   * Create or extend the relevant command module.
   * Use `typer.Option` and `typer.Argument` as needed.
   * Pass prompt callbacks only when the command is meant to be interactive.
   * Keep service orchestration out of presenters and serializers.

3. **Update documentation**

   * Add or update the relevant page under `docs/reference/commands/`.
   * Update architecture docs under `docs/architecture/` or `docs/internals/` if the command changes boundaries or lifecycle story.
   * Update `README.md` if the command affects user-facing workflows.
   * Run `make docs-check` when documentation or overrides change.

4. **Write tests**

   * Add targeted unit and/or integration tests under the existing `tests/unit/` and `tests/integration/` layout.
   * Cover success paths, failure modes, and user-visible diagnostics when relevant.

## Special guidance for schema-based features

Planned features such as `.envctl.yaml`, `check`, and `fill` should follow these rules:

* the schema declares requirements, not values
* the schema must never store secrets
* `check` must be read-only
* `fill` may be interactive, but only for missing values
* `init` must remain structural and deterministic

A good litmus test is:

> Does this feature keep structure, validation, and secret entry separated?

If not, it probably needs redesign.

## Code style

* Use `ruff format` for formatting
* Use `ruff check` for linting
* Run `lint-imports` as part of normal local validation, not only in CI
* Keep functions small and focused
* Prefer explicit control flow over hidden convenience
* Docstrings should describe behavior, side effects, and failure conditions when useful

## Internal logging guidance

`envctl` uses internal logging for debugging implementation details. It is not a second user-facing output channel.

Rules to keep that boundary clean:

* Use `src/envctl/utils/logging.py` for logger creation and safe helpers
* Keep user-facing messaging in presenters and serializers
* Prefer `DEBUG` for normal execution tracing and developer-facing diagnostics in services/repositories
* Use `INFO` only for key operational milestones such as persistent writes or external process execution
* Use `WARNING` only for unusual but recoverable situations
* Use `ERROR` when the command is about to fail or has failed
* Never log secret values, raw vault payloads, or unredacted sensitive command arguments
* Prefer summaries and counts over full dumps of resolved environments

You can enable tracing locally with:

```bash
ENVCTL_LOG_LEVEL=DEBUG envctl check
ENVCTL_LOG_LEVEL=INFO envctl sync
```

## Running tests

* Run the full suite:

  ```bash
  pytest
  ```

* Run a specific test file:

  ```bash
  pytest tests/test_init.py
  ```

* Run with coverage:

  ```bash
  pytest --cov=envctl
  ```

* Run the canonical validation flow:

  ```bash
  make validate
  ```

* Run strict docs validation when touching docs or overrides:

  ```bash
  make docs-check
  ```

The test suite creates temporary directories and sets environment variables to avoid affecting your real system.

## Submitting changes

1. Create a new branch from `main` with a descriptive name.
2. Make your changes, ensuring tests pass and formatting is correct.
3. Commit with a clear imperative message.
4. Open a pull request explaining what changed and why.

When a change alters command identity or the lifecycle model, explain that explicitly in the pull request.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for helping make `envctl` better.
