# Commands Reference

This page describes command behavior.

If you want practical examples, see the workflow guides. If you want the model behind the commands, see the concepts section.

## Global options

Available global options:

- `--version`, `-V`
- `--profile`, `-p`
- `--group`, `-g`
- `--set`
- `--var`
- `--json`

Profile selection precedence is:

1. `--profile`
2. `ENVCTL_PROFILE`
3. config `default_profile`
4. `local`

Named profiles must be created explicitly before use with `envctl profile create <name>`.

Contract scope selectors:

- `--group LABEL` targets variables whose normalized `groups` include `LABEL`
- `--set NAME` targets one named contract set
- `--var KEY` targets one explicit variable

These selectors are mutually exclusive. When none is provided, envctl uses the full contract.

Legacy `group` is still accepted in contract files for compatibility, but it is deprecated and treated as `groups: [value]`. Legacy `required` is also accepted, but ignored functionally.

## Command groups

Commands are grouped by responsibility.

### Contract mutation

These commands change the shared project contract `.envctl.schema.yaml`:

- `add`
- `remove`

### Value mutation

These commands change local environment values only:

- `set`
- `unset`
- `fill`

### Resolution

These commands inspect or validate resolved state:

- `check`
- `inspect`
- `explain`

### Projection

These commands expose resolved state to other tools:

- `run`
- `sync`
- `export`

### Identity

These commands manage project binding and recovery:

- `project bind`
- `project unbind`
- `project rebind`
- `project repair`

### Profiles

These commands manage local value namespaces:

- `profile ...`

### Vault

These commands inspect or maintain physical local vault files:

- `vault ...`

## Core commands

### `add`

```bash
envctl add KEY VALUE
```

Behavior:

* updates the contract
* stores the value in the active profile
* may infer metadata for the contract entry
* does not initialize other profiles implicitly

Useful options:

* `--type` to set variable type explicitly
* `--format` to set semantic string format (`json`, `url`, `csv`) when `--type string`
* `--required` / `--optional`
* `--sensitive` / `--non-sensitive`
* `--description`, `--default`, `--example`, `--pattern`, `--choice`

Use `add` when the project itself now requires a new variable.

### `set`

```bash
envctl set KEY VALUE
```

Behavior:

* updates the value only
* does not modify the contract
* fails fast if the selected explicit profile does not exist

Use `set` when the contract already exists and you only want to change the active-profile value.

### `unset`

```bash
envctl unset KEY
```

Behavior:

* removes the value from the active profile
* keeps the contract definition
* fails fast if the selected explicit profile does not exist

Use `unset` when you want to clear a local value without removing the variable from the project.

### `remove`

```bash
envctl remove KEY
```

Behavior:

* removes the contract definition
* removes the value from all persisted profiles
* reports which persisted profiles were inspected and changed

Use `remove` when the variable should no longer be part of the shared project model.

### `fill`

```bash
envctl fill
```

Behavior:

* prompts for missing required values
* uses contract metadata when available
* fails fast if the selected explicit profile does not exist

Use `fill` when the contract is valid but the active profile is missing required values.

### `check`

```bash
envctl check
```

Behavior:

* validates the resolved environment
* validates placeholder expansion and reference errors
* placeholder expansion is contract-only: unknown `${VAR}` references are invalid
* validates semantic string formats when declared in the contract (`format`)
* `--group LABEL`, `--set NAME`, and `--var KEY` validate only the active contract scope
* exits non-zero on failure
* fails fast if the selected explicit profile does not exist

Use `check` when you want a clear pass/fail answer for contract satisfaction.

### `inspect`

```bash
envctl inspect
```

Behavior:

* shows resolved state
* shows the effective expanded values
* indicates expansion state when relevant
* masks sensitive values
* `--group LABEL`, `--set NAME`, and `--var KEY` show only the active contract scope
* fails fast if the selected explicit profile does not exist

Use `inspect` when you want to understand what the runtime view looks like.

### `explain`

```bash
envctl explain KEY
```

Behavior:

* explains how one key was resolved
* includes expansion metadata for the resolved key
* fails fast if the selected explicit profile does not exist

Use `explain` when one variable is confusing, missing, or coming from a different source than expected.

### `run`

```bash
envctl run -- command
```

Behavior:

* injects the resolved environment in memory into the subprocess
* uses the final expanded values
* affects the immediate subprocess only
* only contract-declared keys are resolved and projected
* `--group LABEL`, `--set NAME`, and `--var KEY` inject only the active contract scope
* placeholder expansion remains contract-only and does not read undeclared host variables
* when projection is blocked, explains the filtered missing, invalid, or unknown keys and suggests next debugging steps
* fails fast if the selected explicit profile does not exist

Use `run` when the target tool can receive environment variables directly and you do not want to create `.env.local`.

If `run` cannot project the environment safely, prefer `envctl check` for the full report and `envctl explain KEY` for one confusing key.

For `docker run` and `docker compose run`, Docker does not inherit the full host process environment into the container automatically. Forward required variables explicitly with `-e`, `--env`, or `--env-file`. For container workflows, prefer an explicit env-file handoff such as `docker run --env-file <(envctl export --format dotenv) my-image`.

### `sync`

```bash
envctl sync
envctl sync --output-path PATH
```

Behavior:

* writes `.env.local`
* writes the final expanded values, not the original `${...}` expressions
* writes `.env.<profile>` for named profiles
* `--output-path PATH` writes the generated dotenv file to an explicit location instead
* unknown contract-missing placeholder references block projection before any file is written
* when projection is blocked, explains the filtered missing, invalid, or unknown keys and suggests next debugging steps
* fails fast if the selected explicit profile does not exist

Use `sync` when another tool requires an env file on disk.

### `export`

```bash
envctl export
envctl export --format shell
envctl export --format dotenv
```

Behavior:

* default output prints shell export lines
* `--format shell` matches the default output
* `--format dotenv` prints dotenv `KEY=value` lines to stdout
* prints the final expanded values
* placeholder expansion is contract-only and does not read undeclared host variables
* when projection is blocked, explains the filtered missing, invalid, or unknown keys and suggests next debugging steps
* fails fast if the selected explicit profile does not exist

Use `export` for shell-oriented workflows.

### `status`

```bash
envctl status
```

Behavior:

* shows a readiness summary
* shows the active profile
* surfaces structured diagnostics when config, contract loading, persisted state, or project binding recovery fail before readiness can be computed
* fails fast if the selected explicit profile does not exist

Use `status` when you want a quick view of what is ready and what still needs attention.

Across commands, when `envctl` can classify a failure it now preserves a stable machine-readable JSON envelope and adds structured `error.details` only for supported error families such as projection validation, contract loading, config loading, persisted state, and project binding or repository discovery.

### `doctor`

```bash
envctl doctor
```

Behavior:

* runs diagnostics

Use `doctor` when you want to check config, storage, and general local readiness.

## Profile commands

```bash
envctl profile list
envctl profile create NAME
envctl profile copy SRC DST
envctl profile remove NAME
envctl profile path [NAME]
```

These commands manage explicit local profiles.

## Vault commands

```bash
envctl vault check
envctl vault show
envctl vault path
envctl vault edit
envctl vault prune
```

These commands inspect or maintain physical vault files.

## Project commands

```bash
envctl project bind ID
envctl project unbind
envctl project rebind
envctl project repair
```

These commands manage repository identity and local binding continuity.
