# Architecture

## Overview

`envctl` follows a small layered CLI architecture:

- **CLI layer**: Typer commands and exit handling. This layer translates command-line arguments into calls to the service layer, and passes any required callbacks (e.g., for confirmation prompts) to keep services framework-agnostic.
- **Service layer**: command-specific orchestration. Each service implements the core logic without depending on the CLI framework; it receives dependencies like configuration and confirmation functions as parameters.
- **Config layer**: XDG-aware default resolution and optional config loading.
- **Utility layer**: filesystem, permissions, path resolution, and output helpers.
- **Model layer**: immutable data structures passed between services.

## Internal structure

The codebase is organized into explicit layers:

- **CLI (`cli/`)**
  - Handles command definitions, argument parsing, and output formatting
  - Delegates all logic to services

- **Services (`services/`)**
  - One module per command
  - Orchestrates operations using config, domain models, and repositories
  - Does not depend on CLI frameworks

- **Domain (`domain/`)**
  - Defines core data structures and result objects
  - Represents command outcomes explicitly

- **Repository (`repository/`)**
  - Handles metadata loading and project context resolution
  - Acts as the bridge between filesystem state and domain objects

- **Config (`config/`)**
  - Loads user configuration and resolves default paths

- **Utils (`utils/`)**
  - Pure helper functions (filesystem, parsing, symlinks, etc.)

This separation allows the system to remain deterministic, testable, and extensible.

## Main concepts

### Vault

The vault is a local user directory that stores centralized `.env.local` files per project. It is created with restrictive permissions (`0700`) to protect secrets.

### Repository link

A repository does not own the real `.env.local` content. It contains a symlink pointing to the vault file.

### Project context

A project context resolves:

- project name
- repository root
- repository `.env.local` path
- vault `.env.local` path

## Design constraints

- Local-only.
- Explicit and deterministic.
- Safe by default.
- No implicit remote synchronization.
- No encryption in v1.