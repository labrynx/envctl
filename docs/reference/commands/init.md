# init

```bash
envctl init
envctl init PROJECT
envctl init --contract ask|example|starter|skip
```

## Purpose

`init` prepares a repository for `envctl`.

It is the bootstrap command that establishes local project state and helps you get to a usable starting point.

## What it does

* initializes the current project in the local vault
* can bootstrap a missing contract depending on `--contract`
* establishes or repairs the local project binding when needed
* is safe to think of as “prepare this repository for envctl”

## Key option

### `--contract`

Controls how `envctl` handles a missing contract:

* `ask`
* `example`
* `starter`
* `skip`

The exact choice changes how much scaffolding `init` performs when the repository does not already have a contract.

## When to use it

Use `init`:

* the first time a repository adopts `envctl`
* after cloning a project that already expects envctl-managed local state
* when local binding or vault setup needs to be re-established

## When not to use it

Do not use `init` as a substitute for filling missing values. Once the project is initialized, use [`fill`](fill.md), [`check`](check.md), and [`run`](run.md) for normal workflows.

## Typical examples

```bash
envctl init
envctl init --contract starter
```

## Related commands

* use [`config`](config.md) to create your user-level config first
* use [`project`](project.md) when you need lower-level binding operations
* use [`fill`](fill.md) after initialization to add missing required values
