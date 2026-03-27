# Architecture

## Overview

`envctl` follows a small layered CLI architecture:

- **CLI layer**: Typer commands and exit handling.
- **Service layer**: command-specific orchestration.
- **Config layer**: XDG-aware default resolution and optional config loading.
- **Utility layer**: filesystem, permissions, path resolution, and output helpers.
- **Model layer**: immutable data structures passed between services.

## Main concepts

### Vault

The vault is a local user directory that stores centralized `.env.local` files per project.

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
