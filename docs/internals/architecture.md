# Internal Architecture

This document explains how `envctl` is organized internally.

It is mainly for contributors, maintainers, or anyone who wants to understand how the code is structured behind the CLI.

## The big picture

`envctl` is built in layers.

The goal of that structure is simple: keep command-line concerns separate from business logic, keep domain rules separate from file access, and avoid hiding important behavior in random helper functions.

The main layers are:

- CLI
- Services
- Domain
- Repository
- Config
- Adapters
- Utils

## Dependency flow

The dependency direction looks like this:

```text
CLI -> Services -> Domain/Repository/Config/Adapters/Utils
```

That means the CLI talks to services, and services orchestrate the rest. The deeper layers should not depend on the CLI.

## Key principles

A few principles shape the architecture:

* explicit behavior
* flows that stay consistent and easy to trace
* no hidden mutation
* CLI kept separate from application logic

Those principles matter because `envctl` is a tool about visibility and trust. If the code hides behavior in the wrong places, the product starts to feel more magical than it should.

## CLI

The CLI layer is responsible for things like:

* Typer command definitions
* argument parsing
* output formatting

The CLI should focus on interaction, not on business rules.

## Services

Services coordinate workflows.

They are responsible for things like:

* command orchestration
* combining domain rules with repository access
* returning structured results to the CLI

A service should not depend on Typer or other CLI-specific details.

## Domain

The domain layer holds the core concepts of the tool.

That includes things like:

* dataclasses
* result models
* contract semantics
* resolution rules

If you want to understand what `envctl` means by “contract”, “profile”, or “resolved state”, this is the layer where those ideas should live.

## Repository

The repository layer is responsible for reading and reconstructing project-related state.

Typical responsibilities include:

* loading contracts
* resolving project context
* reconstructing persisted local state

This layer should answer questions like “what data exists?” rather than “what should the CLI print?”

## Config

The config layer handles user-level configuration and defaults.

Typical responsibilities include:

* loading user config
* applying defaults
* validating config structure

This is local tool configuration, not project contract state.

## Adapters

Adapters are the integration points with external systems or formats.

Examples include:

* dotenv handling
* Git access
* editor launching

They keep those integrations from leaking all over the rest of the codebase.

## Utils

Utils support the rest of the system with small reusable helpers.

Examples include:

* filesystem helpers
* atomic writes
* masking
* path handling

Utilities should stay focused. If business logic starts piling up here, that is usually a sign something belongs in a more explicit layer.

## Core model

Even inside the architecture, the same conceptual model still matters:

* contract
* values
* profiles
* resolution
* projection

The code structure should reinforce that model, not blur it.

## Anti-patterns

Some patterns are especially worth avoiding:

* oversized utils modules
* business logic in the CLI layer
* hidden state changes
* mixing contract definitions with local values

Those patterns make the code harder to trust and harder to maintain.

## Summary

A simple way to read the architecture is:

* CLI talks
* services orchestrate
* domain defines
* repository loads
* config configures
* adapters integrate
* utils support

That separation keeps the system easier to extend without turning it into a tangle.
