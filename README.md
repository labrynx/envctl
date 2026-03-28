# envctl v2

`envctl` is a local environment control plane.

Instead of linking `.env.local` files with symlinks, v2 resolves environment state from a
project contract and projects that state explicitly:

- `envctl check` validates a contract
- `envctl fill` completes missing values
- `envctl inspect` shows resolved values with masking
- `envctl explain KEY` shows where a value came from
- `envctl run -- <command>` injects the resolved environment in memory
- `envctl sync` materializes `.env.local` as a generated artifact
- `envctl export` prints shell-safe exports

## Contract file

The repository contract lives in:

```text
<repo-root>/.envctl.schema.yaml
```

Example:

```yaml
version: 1
variables:
  APP_NAME:
    type: string
    required: true
    description: Application name
  PORT:
    type: int
    required: true
    default: 3000
  DATABASE_URL:
    type: url
    required: true
    sensitive: true
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .[dev]

envctl config init
envctl init
envctl fill
envctl check
envctl run -- python app.py
```
