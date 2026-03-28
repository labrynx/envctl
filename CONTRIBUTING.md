# Contributing to envctl

Thank you for considering contributing to `envctl`! This document outlines the process for setting up the development environment, running tests, and submitting changes.

## Code of Conduct

This project follows a simple principle: be respectful, provide constructive feedback, and keep discussions focused on technical improvements.

## Development setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-org/envctl.git
   cd envctl
   ```

2. **Create a virtual environment**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**  
   ```bash
   pip install -U pip
   pip install -e .[dev]
   ```

   This installs `envctl` in editable mode along with `pytest`, `typer`, and other required packages.

4. **Run the tests** to verify everything works:  
   ```bash
   pytest
   ```

## Project structure

```
envctl/
├── docs/               # User and contributor documentation
├── scripts/            # Development helper scripts
├── src/envctl/         # Main package
│   ├── cli.py          # Typer CLI entry points
│   ├── config/         # XDG config handling
│   ├── services/       # Core logic (each command one service)
│   ├── utils/          # Filesystem, permissions, output helpers
│   └── models.py       # Immutable data structures
├── tests/              # Test suite (mirrors src structure)
└── README.md
```

## Adding a new command

1. **Define the service** in `src/envctl/services/new_service.py`  
   - Implement a function `run_new(...)` that takes necessary dependencies (e.g., `confirm` callback) and returns a result dataclass.
   - Raise domain exceptions (`EnvctlError` subclasses) for user‑facing errors.

2. **Add the CLI command** in `src/envctl/cli.py`  
   - Create a new function decorated with `@app.command()`.
   - Use `typer.Option` and `typer.Argument` as needed.
   - Call the service function, passing any required dependencies (e.g., `_typer_confirm` for prompts).
   - Handle output using `print_*` helpers.

3. **Update documentation**  
   - Add the command to `docs/commands.md`.
   - If the command introduces new concepts, update `docs/architecture.md` or create a new doc.

4. **Write tests**  
   - Create `tests/test_new.py` covering success paths, edge cases, and error handling.
   - Use the `isolated_env` and `repo_dir` fixtures to simulate filesystem isolation.

## Code style

- Use `black` for formatting: `black src tests`.
- Use `isort` for import sorting: `isort src tests`.
- Use `mypy` for type checking: `mypy src` (strict mode optional but encouraged).
- Keep functions small and focused; docstrings should describe behavior, exceptions, and side effects.

## Running tests

- Run the full suite: `pytest`
- Run a specific test file: `pytest tests/test_init.py`
- Run with coverage: `pytest --cov=envctl`

The test suite creates temporary directories and sets environment variables to avoid affecting your real system.

## Submitting changes

1. Create a new branch from `main` with a descriptive name (e.g., `feature/add-list-command`).
2. Make your changes, ensuring all tests pass and code is formatted.
3. Commit with a clear message (use imperative style, e.g., "Add list command").
4. Push the branch and open a pull request. Include a description of what the change does and why.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

Thank you for helping make `envctl` better!
