# Internal Architecture

This document explains how `envctl` is organized internally today.

It is written for maintainers and contributors. The goal is not to describe an ideal architecture in the abstract, but the actual structure of this repository and the responsibilities each layer is expected to keep.

## Product model first

`envctl` revolves around a small set of concepts:

- **contract** — the shared project declaration in `.envctl.schema.yaml`
- **profile values** — local persisted values stored in the vault
- **project context** — the resolved project identity, binding source, and vault paths
- **resolution** — the deterministic runtime view built from contract + profile values
- **inspection** — human or JSON diagnostics over resolved state
- **projection** — safe export of resolved values to subprocesses or generated files

The code should reinforce that model.

## Layering

The repository is intentionally split into these layers:

```text
CLI -> Services -> Domain / Repository / Config / Adapters / Utils
```

The CLI talks to services. Services orchestrate workflows. The deeper layers should not depend on Typer or presentation concerns.

## CLI

The CLI layer owns:

- Typer commands
- argument and selector validation
- command-specific output choices
- alias and deprecation messaging

Examples in this repo:

- `check` is a compact validation command
- `inspect` is the detailed diagnostic command
- `inspect KEY` is the focused single-variable view
- `doctor` and `explain` are deprecated aliases that delegate to `inspect` and `inspect KEY`

The CLI should stay thin. If a command starts accumulating diagnostic-building logic, that logic probably belongs in a service helper instead.

## Services

Services coordinate workflows and return structured results to the CLI.

Important examples in this repo:

- `resolution_service` builds the resolved runtime state
- `check_service` returns a compact `CheckResult`
- `inspect_service` returns `InspectResult` or `InspectKeyResult`
- `resolution_diagnostics.py` converts a `ResolutionReport` into reusable problems and summaries
- projection-related services enforce that invalid or unsafe state does not leak into `run`, `sync`, or `export`

A service should not know how the terminal output is formatted.

## Domain

The domain layer defines the core concepts and stable result models.

Examples:

- `Contract`, `VariableSpec`, and `SetSpec`
- `ProjectContext`
- `ResolutionReport` and `ResolvedValue`
- `CheckResult`, `InspectResult`, `InspectKeyResult`, `DiagnosticProblem`, and `DiagnosticSummary`

This is the layer where semantics should live. If a concept matters to users or to the product model, it probably deserves a domain model instead of an ad-hoc dictionary.

## Repository

The repository layer reconstructs persisted project state and contract state.

Examples:

- loading and validating the contract
- resolving vault profile paths
- reconstructing project binding and recovery state
- reading and writing persisted local state

This layer answers questions like “what exists on disk?” and “what project does this repo belong to?”

## Config

The config layer deals with user-level tool configuration:

- runtime mode
- default profile
- encryption settings
- config file validation

This is not project contract state. It is local tool configuration.

## Adapters

Adapters isolate external integrations and file-format specifics.

Examples:

- dotenv parsing and rendering
- git access
- editor launching
- interactive input helpers

Adapters should keep those concerns from leaking into services or domain code.

## Utils

Utilities exist for narrow, reusable helpers such as:

- atomic writes
- masking
- filesystem helpers
- path normalization
- projection rendering

`utils` should stay small and boring. If meaningful business logic starts to accumulate there, the code is probably hiding a missing domain or service concept.

## Error and diagnostics model

`envctl` does not only return success values. It also exposes structured diagnostics.

There are two important families:

- **structured errors** — config, contract, repository, state, and projection failures surfaced through diagnostics objects
- **command diagnostics** — summaries and actionable problems returned by `check` and `inspect`

That separation matters:

- structured errors explain why a command could not proceed
- command diagnostics explain the state that was inspected successfully but needs action

## Current transition state

The repo is in a controlled transition around diagnostics commands.

The intended model is:

- `check` = short validation
- `inspect` = full diagnostics
- `inspect KEY` = one variable in detail
- `doctor` = deprecated alias of `inspect`
- `explain` = deprecated alias of `inspect KEY`

Compatibility shims still exist in a few places, especially for legacy JSON fields and alias behavior. Those should be treated as transitional, not as the target architecture.

## What to avoid

The main anti-patterns in this repo are:

- business logic inside CLI commands
- new command behavior implemented by reviving legacy presenters
- growing compatibility payloads without explicit removal plans
- hiding reusable diagnostic logic inside one command service instead of shared builders

## Practical summary

A good way to read the current architecture is:

- CLI chooses the interaction shape
- services orchestrate workflows
- domain defines stable semantics
- repository reconstructs persisted project state
- config manages local tool settings
- adapters isolate external systems
- utils support, but should not lead

That is the structure that should guide future work on `envctl`.
