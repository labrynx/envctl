# Installation

Install `envctl`, verify that the CLI works, and then move straight into the quickstart.

## Option 1: install from PyPI

```bash
python3 -m pip install envctl
```

## Option 2: install from the repo for local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Verify that it works

Run:

```bash
envctl --version
```

If you see a version printed successfully, the CLI is installed and ready.

## What to do next

Once `envctl` is available in your shell, continue with the [Quickstart](quickstart.md).
