# run

```bash
envctl run -- command
```

## Purpose

`run` is ephemeral projection.

It injects the resolved environment into one subprocess in memory, without generating a dotenv file on disk.

## What it does

* resolves the active environment first
* injects the final expanded values into the immediate subprocess
* affects only that subprocess tree
* projects only contract-declared keys
* respects global selectors such as `--group`, `--set`, and `--var`
* fails fast if the selected explicit profile does not exist

## Scope and selectors

Global selectors change what gets projected:

* `--group LABEL` injects only variables whose normalized `groups` include `LABEL`
* `--set NAME` injects one named contract set
* `--var KEY` injects one explicit variable

When none is provided, `run` injects the full contract scope.

## What `run` does not do

`run` does not:

* create `.env.local`
* treat host environment variables as fallback resolution inputs
* bypass invalid or missing values
* magically inject values into a container launched by Docker unless Docker is told to forward them

Placeholder expansion remains contract-only. Unknown `${VAR}` references are invalid earlier in resolution and block projection.

## When to use it

Use `run` when the target tool can consume environment variables directly and you do not want to write secrets to disk for that workflow.

For many local workflows, `run` is the cleanest default projection mode.

## When not to use it

Do not use `run` when another tool explicitly requires a dotenv file on disk. Use [`sync`](sync.md) instead.

Do not use `run` when you need stdout-oriented piping into another shell command. Use [`export`](export.md) instead.

## Docker note

If the immediate subprocess is `docker run` or `docker compose run`, `envctl` only injects variables into the Docker client process. Docker still needs explicit forwarding such as `-e`, `--env`, or `--env-file`.

For container workflows, prefer an explicit env-file handoff such as:

```bash
docker run --env-file <(envctl export --format dotenv) my-image
```

## Typical examples

```bash
envctl run -- python app.py
envctl --profile dev run -- pytest
envctl --group Runtime run -- make serve
```

## Related commands

* use [`check`](check.md) for the quick preflight answer
* use [`inspect`](inspect.md) or `envctl inspect KEY` when projection is blocked and you need the full runtime picture
* use [`sync`](sync.md) for file-based projection
* use [`export`](export.md) for stdout-oriented projection
