# Architecture

## Overview

`envctl` follows a small layered CLI architecture:

- **CLI layer**: Typer commands and exit handling. This layer translates command-line arguments into calls to the service layer, and passes any required callbacks (e.g., for confirmation prompts) to keep services framework-agnostic.
- **Service layer**: command-specific orchestration. Each service implements the core logic without depending on the CLI framework; it receives dependencies like configuration and confirmation functions as parameters.
- **Config layer**: XDG-aware default resolution and optional config loading.
- **Utility layer**: filesystem, permissions, path resolution, and output helpers.
- **Model layer**: immutable data structures passed between services.

The architecture is intentionally constrained. `envctl` is not a secret manager, a shell runtime, or a configuration framework. Its job is to manage the lifecycle of local environment files through explicit, deterministic workflows.

## Main concepts

### Vault

The vault is a local user directory that stores centralized `.env.local` files per project. It is created with restrictive permissions (`0700`) to protect secrets.

The vault is the only place where managed secret values live.

### Repository link

A repository does not own the real `.env.local` content. It contains a symlink pointing to the vault file.

This keeps secrets out of the repository while preserving the expected local developer workflow.

### Project context

A project context resolves:

- project name
- repository root
- repository `.env.local` path
- vault `.env.local` path

### Repository metadata

When a repository is initialized, `envctl` stores a local metadata file (`.envctl.json`) inside the repository root. This file links the repository to its vault entry and allows deterministic resolution of the managed environment file.

### Environment contract

A project may define an optional shared schema file, expected to be named `.envctl.schema.yaml`.

This file does **not** contain secrets and does **not** provide default values. It describes the expected environment contract for the project, for example:

- which variables should exist
- which variables are required
- optional human-readable notes or descriptions

The schema lives in the repository because it describes project requirements, not secret values.

## Command model

`envctl` is designed around clear command identities.

### `envctl init`

`init` is responsible for structure only:

- resolve project identity
- create vault directories
- create the managed vault file
- create repository metadata
- create the repository symlink when safe

`init` must remain deterministic. It must never prompt for secret values and must never mix structure creation with interactive configuration.

### `envctl doctor`

`doctor` answers:

> Is this machine and local envctl setup healthy enough to use the tool?

It checks local readiness such as:

- configuration loading
- vault path presence
- vault permissions
- Git repository detection
- symlink support

`doctor` is read-only.

### `envctl status`

`status` answers:

> Is this repository correctly connected to its vault entry?

It reports the state of the bridge between repository and vault:

- healthy
- broken
- not initialized
- missing vault env file

`status` is read-only.

### `envctl check` (planned)

`check` answers:

> Does the current vault env file satisfy the project's declared environment contract?

It compares the managed vault contents against `.envctl.schema.yaml`.

`check` must be read-only. It validates but never creates, repairs, or fills values.

### `envctl fill` (planned)

`fill` is the interactive onboarding command.

Its role is to:

- read `.envctl.schema.yaml`
- compare the current vault contents with the declared contract
- prompt the user only for missing required values
- write those values to the vault explicitly

`fill` exists to preserve the identity of `init`. It is intentionally separate from initialization.

### `envctl set`

`set` remains the lowest-level explicit mutation command:

- update one key
- write one value
- no inference
- no defaults
- no schema-driven behavior by itself

## Source-of-truth model

`envctl` is built around a strict separation of responsibilities:

- **Repository**: declares the need for environment variables
- **Vault**: stores the secret values
- **Metadata**: links repository and vault
- **Commands**: validate or mutate one concern at a time

This separation is deliberate.

The repository should describe the contract, but never hold the secret.
The vault should hold the secret, but never define the contract.

## Design constraints

- Local-only.
- Explicit and deterministic.
- Safe by default.
- No implicit remote synchronization.
- No encryption in v1.
- No default values provided by the tool.
- No hidden mutation during validation commands.

## Design rule

A useful way to think about the model is:

> The schema defines the need, the user provides the intent, and the vault stores the secret.

That rule keeps the architecture clean:

- `init` creates structure
- `status` validates the link
- `doctor` validates the local environment
- `check` validates the contract
- `fill` collects missing values
- `set` performs explicit manual mutation