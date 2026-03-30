# Architecture

## Overview

`envctl` is a local environment control plane.

Its purpose is not to manage one physical `.env.local` file inside a repository. Its purpose is to:

- define what environment a project needs
- resolve values from explicit local sources
- validate the resulting state against a shared contract
- project that resolved state into developer workflows

The tool follows a small layered architecture:

- **CLI layer**: Typer commands, argument parsing, exit handling, and terminal rendering
- **Service layer**: command-specific orchestration and workflow sequencing
- **Config layer**: XDG-aware defaults and optional user configuration
- **Repository layer**: contract loading, local state access, and project context reconstruction
- **Adapters layer**: focused integrations for dotenv parsing, editor launching, and Git access
- **Utility layer**: small helpers for filesystem operations, shell output, masking, permissions, and paths
- **Domain layer**: typed models representing contracts, inferred metadata, resolved environments, diagnostics, and command results

This separation keeps the system deterministic, testable, and extensible.

## Internal structure

The codebase is organized into explicit layers:

- **CLI (`cli/`)**
  - Handles command definitions, argument parsing, and output formatting
  - Delegates workflow logic to services

- **Services (`services/`)**
  - One module per command or workflow family
  - Orchestrates operations using config, repositories, domain models, adapters, and utilities
  - Does not depend on the CLI framework directly

- **Domain (`domain/`)**
  - Defines contracts, inference models, resolution results, status reports, diagnostics, and operation results
  - Represents workflow outcomes explicitly

- **Repository (`repository/`)**
  - Handles contract loading and local state access
  - Reconstructs project context from the current repository and configuration
  - Bridges persisted local state and domain objects

- **Config (`config/`)**
  - Loads user configuration and resolves default paths

- **Adapters (`adapters/`)**
  - Encapsulates external interactions such as dotenv parsing, editor invocation, and Git queries

- **Utils (`utils/`)**
  - Pure helper functions for focused technical tasks

## Main concepts

### Contract

A project contract defines what environment variables the project expects.

The contract lives in the repository as:

```text
<repo-root>/.envctl.schema.yaml
````

The contract may define:

* required and optional variables
* descriptions
* basic types
* non-sensitive defaults
* sensitivity flags
* validation patterns
* allowed choices
* provider hints for future extensibility

The contract must not contain secrets.

### Local values

The default storage backend is local and user-owned.

By default, `envctl` stores values outside repositories under a private vault directory. That location is configured at the user level and is not meant to be committed to source control.

Local values are a source of data, not the project contract.

### Resolved environment

A resolved environment is the result of combining:

* the project contract
* local stored values
* explicit defaults allowed by the contract
* process-level environment overrides when relevant

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
* repository slug
* repository fingerprint
* contract path
* target env filename
* resolved local vault location

The repository does not need a mandatory link file to its local environment state.

## Variable operations

In v2.2, `envctl` distinguishes clearly between contract mutation and value mutation.

* **add**: adds a variable to the contract and stores a local value
* **set**: updates a local value only
* **unset**: removes a local value only
* **remove**: removes both the contract definition and the local value

This separation is intentional.

The contract defines what exists.
The local vault defines what is currently set.

That keeps shared project requirements and machine-local state from drifting into each other.

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

The long-term direction of `envctl` is based on four ideas:

* **contract**: what the project needs
* **value management**: how local values are added, updated, or removed
* **resolution**: how values are obtained and validated
* **projection**: how the resolved environment is used

This keeps responsibilities clear:

* repositories declare requirements
* local storage provides machine-specific values
* `envctl` resolves and validates state
* commands project that state into concrete workflows

## Why this matters

This model prevents the tool from drifting back into “just manipulate one file” thinking.

Instead of treating `.env.local` as the system, `envctl` treats it as one optional projection of a larger, explicit model:

* contract
* local values
* resolution
* projection

That is the core architectural idea behind v2.2.
