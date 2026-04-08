# Layers

`envctl` is deliberately split into layers so that orchestration, domain rules, persistence, and infrastructure do not collapse into one hard-to-maintain blob.

The point of the layers is not ceremony.

The point is to make the codebase easier to change without breaking the product model.

## The layer model

At a high level, `envctl` is organized like this:

```text
CLI
-> Services
-> Domain / Repository / Config / Adapters
-> Utils
```

Not every layer depends on every other layer, but the direction is intentional:

* outer layers orchestrate
* inner layers define stable rules or data access
* lower-level utilities stay generic

## CLI

The CLI layer owns:

* Typer commands
* argument and selector validation
* interactive prompts
* presentation decisions
* JSON vs terminal output routing

In other words, the CLI is where the user-facing command shape lives.

What it should **not** own:

* core resolution rules
* persistence logic
* reusable domain semantics

The CLI should stay thin.

## Services

Services own use-case orchestration.

That includes workflows such as:

* building resolved runtime state
* validating the environment
* coordinating projection
* combining repository reads with domain logic

Services are where “do this product workflow” belongs.

What they should **not** become:

* a second domain layer
* a dumping ground for formatting logic
* a place for direct CLI concerns

## Domain

The domain layer owns the stable concepts and rules of the product.

That includes things like:

* contract semantics
* resolution rules
* result models
* normalization logic

If a rule is part of what `envctl` means rather than how one command is wired, it probably belongs here.

What the domain should **not** know about:

* Typer
* terminal formatting
* repository-specific orchestration
* infrastructure details

## Repository

The repository layer owns persisted project and contract state.

That includes reading and writing the things the product treats as durable state, such as:

* contract data
* local persisted values
* related project state

Repository code is where storage-facing coordination belongs.

What it should **not** become:

* a hidden service layer
* a place to embed user interaction
* a home for business rules that belong in domain

## Config

The config layer owns user-level tool configuration.

That keeps machine-local tool behavior separate from:

* project contract data
* local vault values
* command presentation logic

This separation matters because config is upstream of many workflows, but is still not the same thing as project state.

## Adapters

Adapters talk to the outside world.

Examples include:

* Git integration
* dotenv parsing or writing
* editor launching
* other IO-heavy integration points

Adapters exist so the rest of the product does not have to pretend external tools and formats are pure domain concepts.

## Utils

Utils are the small generic helpers that other layers can share without dragging in higher-level meaning.

They should stay boring.

If a helper starts expressing product semantics, it probably no longer belongs in `utils`.

## Dependency direction

The important architectural rule is directional:

* CLI can depend on services
* services can depend on domain, repository, config, adapters, and utils
* deeper layers must not reach back upward into CLI concerns

This is exactly the kind of rule that import-linter can enforce well.

## Why this matters in practice

When layers stay clean:

* command modules stay smaller
* product semantics remain testable outside the CLI
* infrastructure changes do not leak everywhere
* architectural regressions become easier to spot

In short, the layers exist so the codebase keeps matching the product model instead of eroding into convenience shortcuts.

## Read next

Go deeper from architectural shape into architectural limits and implementation detail:

<div class="grid cards envctl-read-next" markdown>

-   **Boundaries**

    See the product and codebase limits that keep the layers honest.

    [Read about boundaries](boundaries.md)

-   **Internals (advanced)**

    Follow the maintainer-facing view of how the current repository is organized.

    [Read the internal architecture guide](../internals/architecture.md)

</div>
