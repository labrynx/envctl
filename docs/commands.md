# Commands

## Global options

- `--version`, `-V`: Show the version and exit.

## envctl config init

Creates the default envctl config file in the user's XDG config directory.

- creates `~/.config/envctl/config.json`
- refuses to overwrite an existing config file unless future options explicitly allow it
- writes readable default values
- sets file permissions to `0600` when supported
- keeps configuration creation explicit

The config file controls local tool behavior only. It does not store project contracts or secrets.

## envctl init [PROJECT]

Initializes the current repository for `envctl` v2 workflows.

- `[PROJECT]` is optional
- if omitted, the repository directory name is used as the readable slug
- ensures the local vault structure exists when needed
- prepares the repository for contract-driven resolution workflows
- does not require a repository symlink
- does not require a repository metadata link file as a source of truth

Important:

- `init` does **not** ask for secret values
- `init` does **not** invent secrets
- `init` may create a starter contract or infer one from `.env.example` depending on the selected mode
- `init` does **not** materialize `.env.local` unless a future explicit flag says so
- `init` remains explicit and safe for repeated execution

## envctl add KEY VALUE

Creates or updates a variable in both the project contract and the local provider.

Expected behavior:

- writes the value into the local vault
- inserts the variable into `.envctl.schema.yaml` when missing
- may reuse the existing contract entry when already present
- infers metadata such as type, sensitivity, description, defaults, patterns, and choices where possible
- supports explicit overrides through flags
- supports an interactive review flow for inferred metadata

`add` is the main onboarding command when a variable does not yet exist in the contract.

## envctl set KEY VALUE

Creates or updates one explicit key/value pair in the local provider for the current repository.

- requires a valid project context
- writes one key at a time
- does not print the stored value back to the terminal
- does not modify the contract definition
- is intended as an explicit local value command

This command is useful when the contract already exists and only the local value needs to change.

## envctl unset KEY

Removes one key from the local provider only.

Expected behavior:

- removes the stored value from the local vault
- preserves the contract definition
- does not modify `.envctl.schema.yaml`

`unset` is useful when a value should be cleared locally without changing shared project requirements.

## envctl remove KEY

Removes one key from both the project contract and the local provider.

Expected behavior:

- removes the key from `.envctl.schema.yaml` when declared
- removes the stored value from the local vault when present
- may require explicit confirmation from the CLI layer
- keeps the removal explicit and visible

`remove` is intended for deleting variables from the shared model, not just clearing local state.

## envctl fill

Interactively fills missing values required by the project contract.

Expected behavior:

- reads `.envctl.schema.yaml` from the repository root
- compares the contract against the current locally available values
- prompts only for missing required keys
- uses contract metadata such as description, sensitivity, and defaults when prompting
- does not echo existing secret values back to the console
- writes only the values the user explicitly provides
- leaves already satisfied values unchanged

Unlike `set`, `fill` is contract-guided and only targets missing required values.

## envctl check

Validates the resolved environment against the project contract.

Expected behavior:

- reads `.envctl.schema.yaml` from the repository root
- resolves the current environment from supported sources
- reports missing required variables
- reports invalid values when type validation fails
- reports unknown keys in the vault where relevant
- exits non-zero when the contract is not satisfied
- never modifies files or stored values

`check` is a read-only validation command.

## envctl inspect

Displays the resolved environment in a human-readable form.

Expected behavior:

- shows which keys are currently resolved
- masks sensitive values
- may include whether a value is present, defaulted, or explicitly stored
- does not expose secret values in normal output

`inspect` is for visibility, not mutation.

## envctl explain KEY

Explains how one variable is resolved.

Expected behavior:

- identifies whether the key is declared in the contract
- shows whether the value is missing, defaulted, or explicitly provided
- explains the resolution path for that key
- does not print raw sensitive values unless a future explicit debug mode allows it

This command is useful for debugging confusing local setups.

## envctl sync

Materializes a derived environment file in the repository.

Expected behavior:

- resolves the current environment
- validates it before writing
- writes the target file (by default `.env.local`) as a generated artifact
- may include a generated header
- treats the generated file as a projection, not as a source of truth
- follows safe overwrite rules

`sync` exists for compatibility with tools that expect a real env file on disk.

## envctl export

Prints the resolved environment as shell export lines.

Expected behavior:

- resolves the current environment
- validates it before output
- prints shell-safe lines suitable for POSIX shells
- quotes values safely for shell consumption
- does not mutate files or stored state

This command is useful for manual shell workflows and integration with other local tooling.

## envctl run -- <command>

Runs a command with the resolved environment injected into the subprocess.

Expected behavior:

- resolves the current environment
- validates it before execution
- spawns the child process with the resolved values injected in memory
- does not require writing `.env.local` to disk
- returns the child process exit code

This is the cleanest projection mode when the target tool can consume environment variables directly.

## envctl status

Shows the current repository envctl status in a human-friendly format.

Typical output may include:

- whether a contract is present
- whether required values are missing
- whether the local provider has been initialized
- whether the repository is ready for `run`, `sync`, or `check`
- which next command is likely to help

`status` is a workflow-oriented summary command. It is broader than `check`, but should still avoid hidden mutation.

## envctl doctor

Runs read-only diagnostics for the local `envctl` environment.

Typical checks may include:

- configuration loading
- resolved vault path
- vault path permissions when the vault exists
- Git repository detection from the current working directory
- contract file detection
- local environment sanity checks

The command uses checklist-style output such as `[OK]`, `[WARN]`, and `[FAIL]`.

`doctor` is about host and local tool readiness, not about mutating project state.

## envctl vault edit

Opens the current local vault file in the configured editor.

Expected behavior:

- ensures the vault file exists
- opens it using the selected editor
- verifies it can still be read afterwards

This command is for explicit low-level inspection or manual editing.

## envctl vault check

Checks the current vault artifact as a physical file.

Expected behavior:

- reports whether the file exists
- reports whether it is parseable
- reports whether file permissions are private enough
- never mutates contract or values

## envctl vault path

Prints the current vault file path for the active project context.

## envctl vault show

Shows the raw stored values in the local vault.

Expected behavior:

- masks values by default
- allows raw output only through an explicit flag
- reflects stored local values, not the fully resolved environment

This differs from `inspect`, which shows resolved state.

## envctl vault prune

Removes keys from the local vault that are not declared in the contract.

Expected behavior:

- compares stored local values against the contract
- removes undeclared keys explicitly
- keeps declared keys untouched
- does not modify the contract

This is useful for cleaning up stale local state after contract changes.

## envctl help [COMMAND]

Shows help for envctl or for a specific command.

- `envctl help` shows the root help
- `envctl help init` shows help for `init`
- this is a convenience alias for Typer's built-in help output

## Command model summary

The v2.2 command model is centered on four responsibilities:

- **contract mutation**
  - `add`
  - `remove`

- **value mutation**
  - `set`
  - `unset`
  - `fill`

- **resolution and validation**
  - `check`
  - `inspect`
  - `explain`

- **projection**
  - `run`
  - `sync`
  - `export`

Supporting commands include:

- `init`
- `status`
- `doctor`
- `config init`
- `vault ...`

## Operational model summary

The main day-to-day distinction is:

- `add` → contract + value
- `set` → value only
- `unset` → remove value only
- `remove` → remove contract + value

That distinction is intentional and is one of the core behaviors of `envctl` v2.2.
