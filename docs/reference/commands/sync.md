# sync

```bash
envctl sync
envctl sync --output-path PATH
```

## Purpose

`sync` is file-based projection.

Use it when another tool expects a dotenv file on disk rather than an in-memory subprocess environment.

## What it does

* resolves the active environment first
* writes `.env.local` by default
* writes `.env.<profile>` for named profiles
* writes to an explicit path with `--output-path PATH`
* writes the final expanded values, not the original `${...}` expressions
* respects global selectors such as `--group`, `--set`, and `--var`
* fails fast if the selected explicit profile does not exist

## What `sync` does not do

`sync` does not turn the generated file into the source of truth.

The generated dotenv file is an artifact. It is safe to delete and regenerate because the underlying source of truth remains the contract plus local values.

## When to use it

Use `sync` when another tool really needs an env file on disk.

Typical examples include older tooling, explicit Docker handoff, or integration points that cannot consume direct subprocess injection.

## When not to use it

Do not use `sync` as your default workflow if `run` is enough. Writing secrets to disk is often less clean than direct in-memory projection.

If you only need stdout-oriented projection, use [`export`](export.md) instead.

## Typical examples

```bash
envctl sync
envctl sync --output-path /tmp/app.env
envctl --group Database sync
```

## Related commands

* use [`run`](run.md) for in-memory subprocess injection
* use [`export`](export.md) for stdout-oriented workflows
* use [`check`](check.md) if you only need validation before projection
