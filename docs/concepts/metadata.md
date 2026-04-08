# Metadata and Local State

This page exists to answer one narrower question than the core concepts:

> what local metadata does `envctl` keep around, and why does it not become part of the source of truth?

## The main idea

`envctl` keeps a clean split between:

* the contract in the repository
* local values in storage
* generated artifacts such as `.env.local`
* local metadata that helps identity and recovery

That last category matters, but it is still secondary.

Metadata helps `envctl` reconnect a checkout to the right local state. It does not redefine the contract, replace the vault, or become the source of truth for secrets.

## What local metadata is for

Local metadata supports things like:

* project identity
* recovery after a repository move or clone
* continuity across checkouts
* known local paths and related recovery hints

In other words, metadata exists so that `envctl` can answer “which local project state belongs to this checkout?” more reliably.

## What metadata is not

Metadata is not:

* the contract
* the secret store
* the resolved runtime environment
* a replacement for profiles

If metadata started doing those jobs, it would become a second hidden model and make the system harder to trust.

## Relation to binding

Most of the important metadata story is really about binding.

Binding connects a repository checkout to the correct local project identity. Metadata helps that process stay recoverable.

If you care mainly about how the current checkout finds the right local project state, read [Binding](binding.md) first.

## Relation to local values

Local values are still the real local truth.

Metadata may describe or support that truth operationally, but it does not replace it. That is why generated files and helper state remain safe to delete and regenerate, while local values themselves remain the meaningful stored state.

## Why this matters

Keeping metadata secondary helps avoid a common failure mode:

* a helper file quietly becomes the real system model

`envctl` avoids that by keeping metadata in a support role only.

## Read next

Keep metadata in its support role by connecting it back to the main model:

<div class="grid cards envctl-read-next" markdown>

-   **Binding**

    Start with the identity model that metadata supports.

    [Read about binding](binding.md)

-   **Vault**

    Revisit the actual local storage layer that metadata never replaces.

    [Read about the vault](vault.md)

-   **Resolution**

    See where metadata stops and the runtime model begins.

    [Read about resolution](resolution.md)

</div>
