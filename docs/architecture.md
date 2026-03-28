# Architecture

## Overview

`envctl` is a local environment control plane.

Its purpose is not to manage one physical `.env.local` file inside a repository. Its purpose is to:

- define what environment a project needs
- resolve values from explicit local sources
- validate the resulting state against a shared contract
- project that resolved state into developer workflows

The tool follows a small layered CLI architecture:

- **CLI layer**: Typer commands and exit handling. This layer translates command-line arguments into calls to the service layer and keeps framework-specific behavior isolated.
- **Service layer**: command-specific orchestration. Each service coordinates one workflow without depending on the CLI framework directly.
- **Config layer**: XDG-aware default resolution and optional config loading.
- **Repository layer**: project contract loading, local state access, and repository context resolution.
- **Utility layer**: focused helpers for filesystem operations, shell output, masking, parsing, and path handling.
- **Domain layer**: immutable models that represent contracts, resolved environments, diagnostics, and command results.

This separation keeps the system deterministic, testable, and extensible.

## Internal structure

The codebase is organized into explicit layers:

- **CLI (`cli/`)**
  - Handles command definitions, argument parsing, and output formatting
  - Delegates all logic to services

- **Services (`services/`)**
  - One module per command or workflow
  - Orchestrates operations using config, repositories, domain models, and utilities
  - Does not depend on CLI frameworks

- **Domain (`domain/`)**
  - Defines contracts, resolution results, status reports, and diagnostics
  - Represents command outcomes explicitly

- **Repository (`repository/`)**
  - Handles contract loading and local state access
  - Reconstructs project context from the current repository and configuration
  - Acts as the bridge between persisted local state and domain objects

- **Config (`config/`)**
  - Loads user configuration and resolves default paths

- **Utils (`utils/`)**
  - Pure helper functions for focused technical tasks

## Main concepts

### Contract

A project contract defines what environment variables the project expects.

The contract lives in the repository as:

```text
<repo-root>/.envctl.schema.yaml
```

The contract may define:

* required and optional variables
* descriptions
* basic types
* non-sensitive defaults
* sensitivity flags
* provider hints for future extensibility

The contract must not contain secrets.

### Local provider

The default storage backend is local and user-owned.

By default, `envctl` stores resolved values outside repositories under a private vault directory. That location is configured at the user level and is not meant to be committed to source control.

The local provider is a source of values, not the project contract.

### Resolved environment

A resolved environment is the result of combining:

* the project contract
* local stored values
* explicit defaults allowed by the contract
* interactive values when the user chooses to provide them

The resolved environment is the central runtime concept in v2.

### Projection

Once an environment has been resolved and validated, it can be projected in different ways:

* **run**: inject values into a subprocess environment in memory
* **sync**: materialize a derived `.env.local` file in the repository
* **export**: emit shell export lines

Projected files are artifacts, not sources of truth.

### Project context

A project context resolves the current repository as an execution unit.

A project context typically includes:

* repository root
* repository name or slug
* repository fingerprint
* contract path
* target env filename
* resolved vault location for local storage

The repository does not need a mandatory link file to its local environment state.

## Design constraints

`envctl` is intentionally conservative.

Core constraints:

* local-first
* explicit behavior
* deterministic resolution
* safe by default
* no implicit remote synchronization
* no hidden background processes
* no secret values stored in repository contracts
* no encryption-at-rest by default in the core model

## Architectural direction

The long-term direction of `envctl` is based on three ideas:

* **contract**: what the project needs
* **resolution**: how values are obtained and validated
* **projection**: how the resolved environment is used

This keeps responsibilities clear:

* repositories declare requirements
* local or external sources provide values
* `envctl` resolves and validates state
* commands project that state into concrete workflows
