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
- generic hook-management features unrelated to envctl-owned protection

## Code of Conduct

This project follows a simple principle: be respectful, provide constructive feedback, and keep discussions focused on technical improvements.

## Development setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/labrynx/envctl.git
   cd envctl
   ```

2. **Sync the development environment**

   ```bash
   uv sync --dev
   ```

3. **Run the canonical local validation flow**

   ```bash
   make validate
   ```

This is the supported baseline workflow for contributors.

### Official local workflow policy

The repository uses `uv` as the canonical dependency manager.

```bash
uv sync --dev
make validate
```

This ensures:

* deterministic dependency resolution via `uv.lock`
* consistent environments across contributors and CI
* no drift between local and CI execution

`uv.lock` is part of the repository contract and must be updated whenever dependencies change.

### Docs workflow

If you are editing documentation or site overrides:

```bash
uv sync --extra docs
make docs-check
```

Documentation must build cleanly in strict mode.

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

## Observability guidance

`envctl` uses one structured observability layer for technical diagnostics. It is the only supported internal diagnostics model.

Rules to keep that boundary clean:

* Emit lifecycle through `observe_span(...)`
* Use `record_event(...)` only for cross-cutting point events such as handled/unhandled errors
* Keep user-facing messaging in presenters and serializers
* Prefer stable event families plus `operation` and sanitized `fields`
* Prefer counts, booleans, states, and selection metadata over free-form messages
* Never emit secret values, raw vault payloads, master-key material, or unredacted command arguments
* The JSONL event contract is the source of truth; the human renderer is only a derived view

You can enable observability locally with:

```bash
envctl --trace check
envctl --trace --trace-format human check
envctl --trace --trace-format jsonl --trace-output file check
```

## Managed hooks contribution guidance

`envctl` now owns a very small managed hooks subsystem. Keep its boundary tight.

Rules:

* do not turn it into a generic hooks framework
* do not add support for arbitrary hook names without a clear product reason
* keep hook wrappers minimal and POSIX-compatible
* keep product logic in Python, not in shell scripts
* do not reintroduce `.githooks` as the active product mechanism
* do not make `--force` bypass the repository-perimeter safety rule

If you change managed hook behavior:

* update `docs/reference/commands/hooks.md`
* update `docs/reference/commands/init.md` and `guard.md` when behavior changes there too
* add or adjust cross-platform tests, especially the real `sh`-executed wrapper path

## Running tests

* Run the full suite:

  ```bash
  uv run pytest
  ```

* Run a specific test file:

  ```bash
  uv run pytest tests/test_init.py
  ```

* Run with coverage:

  ```bash
  uv run pytest --cov=envctl
  ```

* Run the canonical validation flow:

  ```bash
  make validate
  ```

* Run strict docs validation when touching docs:

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

For release structure and changelog conventions, see `.github/release-playbook.md`.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for helping make `envctl` better.
