# Boundaries

Architectural boundaries matter in `envctl` because the product itself is built around boundaries.

The tool stays understandable only if it keeps clear lines between:

* contract and local values
* resolution and projection
* product logic and external tooling

This page is about those limits and why they are intentional.

## Boundary 1: contract is not local state

`envctl` does not treat the repository contract as a place to store real machine values.

Why that boundary exists:

* shared intent should be reviewable
* secrets should stay local
* profiles should not mutate the project definition

If contract and local state get mixed together, the project loses its clean source of shared truth.

## Boundary 2: resolution is not host-environment inheritance

`envctl` does not treat the whole current shell environment as part of resolution.

Why that boundary exists:

* hidden host dependence makes behavior harder to reproduce
* debugging becomes guesswork
* CI and local behavior diverge more easily

That is why placeholder expansion is contract-only and why undeclared host variables do not quietly become part of the model.

## Boundary 3: projection is not source of truth

`envctl` does not treat generated outputs such as `.env.local` as the canonical state of the system.

Why that boundary exists:

* generated files can go stale
* people start editing artifacts by hand
* the team loses track of whether the contract, the vault, or the file is the truth

Projection is downstream of resolution on purpose.

## Boundary 4: profiles are not alternate contracts

Profiles exist to select different local values for the same contract.

They do not redefine:

* which variables exist
* what is required
* validation rules
* the shape of the shared environment model

Why that boundary exists:

* one contract can support multiple local contexts
* profile switching stays predictable
* the project definition does not fragment by machine

## Boundary 5: `envctl` is not Docker, your shell, or CI

`envctl` resolves and projects environment state, but it does not own the full behavior of downstream tools.

That means:

* Docker still decides how containers receive env vars
* shells still decide how command chaining behaves
* CI still decides how pipeline steps are orchestrated

Why that boundary exists:

* downstream tools have their own interfaces and rules
* pretending otherwise creates confusing failures
* the correct fix is usually explicit handoff, not hidden coupling

## Boundary 6: CLI is not the domain

The CLI is how users interact with `envctl`, but it is not where the product semantics should live.

Why that boundary exists:

* command modules should stay thin
* domain rules should remain testable outside Typer
* orchestration and presentation should not become inseparable

This is one of the key codebase boundaries, not just a documentation preference.

## What these boundaries prevent

These boundaries collectively prevent a few recurring failure modes:

* treating `.env.local` as the real state store
* relying on undeclared shell variables
* smuggling secrets into the repository contract
* letting one profile behave like a hidden fallback for another
* writing command-specific convenience logic directly into core semantics

## Why the boundaries matter

Without these limits, `envctl` would be easier to use incorrectly and harder to explain correctly.

With them, the system becomes more explicit:

* shared intent lives in the contract
* local truth lives in the vault
* resolution determines effective state
* projection exposes it in the right shape
* downstream tools consume that shape through explicit interfaces

That is what keeps the product model coherent.

## Read next

Connect these limits back to the product model and the codebase structure:

<div class="grid cards envctl-read-next" markdown>

-   **Contract**

    Revisit the boundary between shared requirements and machine-local state.

    [Read about the contract](../concepts/contract.md)

-   **Resolution**

    See why undeclared host state stays outside the runtime model.

    [Read about resolution](../concepts/resolution.md)

-   **Layers**

    Go back to the codebase structure that enforces these boundaries.

    [Read about layers](layers.md)

</div>
