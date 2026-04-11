# Layers

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Architecture</span>
  <p class="envctl-section-intro__body">
    This page describes the main codebase layers and what each one owns.
    It is maintainer-facing: the goal is to keep the implementation aligned with the product model rather than letting responsibilities blur together.
  </p>
</div>

## The layer model

At a high level, `envctl` is organized like this:

```text
CLI
-> Services
-> Domain / Repository / Config / Adapters
-> Utils
```

## Why the layers matter

The point of the layers is not ceremony. The point is to make the codebase easier to change without collapsing orchestration, domain semantics, persistence, and IO into one hard-to-maintain blob.

## Layer ownership

### CLI

Owns:

- Typer commands
- argument and selector validation
- prompts and output routing
- terminal vs JSON presentation choices

Should not own:

- core resolution rules
- persistence logic
- reusable domain semantics

### Services

Own:

- use-case orchestration
- workflow coordination
- command-to-domain glue

Should not become:

- a second domain layer
- a formatting layer
- a dumping ground for CLI concerns

### Domain

Owns:

- contract semantics
- resolution rules
- stable product models
- normalization logic

Should not know about:

- Typer
- terminal presentation
- repository-specific orchestration

### Repository / Config / Adapters

Own:

- stored project and vault state
- user config
- external IO and integrations

Should not become:

- hidden service logic
- interactive CLI flows
- a second domain layer

### Utils

Own:

- small generic helpers
- shared low-level utilities

If a helper starts expressing product semantics, it probably no longer belongs here.

## Dependency direction

The important rule is directional:

- CLI can depend on services
- services can depend on domain, repository, config, adapters, and utils
- deeper layers must not depend upward on CLI concerns

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Boundaries

See the product and codebase boundaries that keep these layers honest.

[Read about boundaries](boundaries.md)
</div>

<div class="envctl-doc-card" markdown>
### Internal architecture

Switch from the conceptual layer model to the repository’s current maintainer view.

[Read internal architecture](../internals/architecture.md)
</div>

<div class="envctl-doc-card" markdown>
### Concepts

Go back to the product model the implementation is supposed to reinforce.

[Open concepts](../concepts/index.md)
</div>

</div>
