# Internal Architecture

This document explains how envctl is structured internally.

## Layers

- CLI
- Services
- Domain
- Repository
- Config
- Adapters
- Utils

## Dependency flow

```text
CLI -> Services -> Domain/Repository/Config/Adapters/Utils
```

## Key principles

* explicit behavior
* deterministic flows
* no hidden mutation
* CLI separated from logic

## CLI

* Typer
* argument parsing
* output

## Services

* orchestration
* workflows
* no CLI dependency

## Domain

* dataclasses
* result models
* contracts
* resolution

## Repository

* contract loading
* project context
* state reconstruction

## Config

* user config
* defaults

## Adapters

* dotenv
* git
* editor

## Utils

* filesystem
* atomic writes
* masking
* paths

## Core model

* contract
* values
* profiles
* resolution
* projection

## Anti-patterns

* fat utils
* logic in CLI
* hidden state
* mixing contract and values

## Summary

* CLI talks
* services orchestrate
* domain defines
* repository loads
* config configures
* adapters integrate
* utils help
