# Contract

The contract is the shared description of what a project expects from its environment.

It tells the repository what must exist, what shape those values should have, and how that shared intent is organized.

It does **not** store the real local values.

That boundary is the most important thing to understand in `envctl`.

!!! danger "Do not put real secret values in the contract"
    The contract is shared, versioned project intent. Secrets and machine-local values belong in the vault, not in repository-tracked contract files.

## What the contract is

The contract is:

* shared
* versioned with the repository
* reviewable like any other project change
* about requirements, not personal machine state

If you want one sentence:

> the contract defines what the project needs, not what your machine currently has

## What the contract is not

The contract is not:

* a secret store
* a profile file
* a machine-local config file
* a generated artifact
* a dump of the current resolved environment

If those concerns get mixed together, the system becomes harder to trust and harder to debug.

## Where the contract lives

The root contract is discovered at the repository root in this order:

```text
<repo-root>/.envctl.yaml
<repo-root>/.envctl.schema.yaml  # legacy fallback
```

If both files exist, `envctl` prefers `.envctl.yaml`.

That location matters because the contract belongs to the project itself. It should live with the repository, be visible in reviews, and evolve with the codebase.

## What the contract describes

A contract can describe:

* which variables exist
* types
* optional semantic string formats such as `json`, `url`, or `csv`
* optional descriptions
* sensitivity flags
* non-secret defaults
* validation rules
* allowed choices
* optional groups
* named reusable sets

Example:

```yaml
version: 1
variables:
  DATABASE_URL:
    type: url
    sensitive: true
    description: Primary database connection
    groups:
      - Database
      - Secrets

  PORT:
    type: int
    default: 3000
    groups:
      - Runtime

  APP_URL:
    type: string
    default: http://${APP_NAME}:${PORT}
    groups:
      - Application

sets:
  docker_runtime:
    description: Variables needed to run the app in a container
    groups:
      - Application
      - Runtime
    variables:
      - DATABASE_URL
```

This is enough to explain shared intent without committing live secrets.

## Contract vs local values

The clean split in `envctl` looks like this:

* the **contract** says what should exist
* the **vault** stores what this machine actually has
* the **profile** selects one local value set
* **resolution** decides the effective runtime value
* **projection** exposes that resolved result to tools

This is why `envctl` is not just a prettier `.env` wrapper.

It separates shared requirements from local truth.

## Defaults are still contract data

Defaults live in the contract because they are part of shared intent.

That makes them very different from local values:

* a default is visible to the whole team
* a default is reviewable
* a default should be safe to commit
* a default is not a personal secret

In practice, defaults are for non-sensitive fallback behavior, not for hiding local setup inside the repo.

## Contract composition and imports

A root contract may import other contract files:

```yaml
imports:
  - ./contracts/shared.yaml
  - ./contracts/backend.yaml
```

Imports are resolved relative to the file that declares them. `envctl` loads them recursively and builds one composed contract.

The important model is:

* imported files help organize the contract
* they do not create separate namespaces
* they do not override one another implicitly
* the final result is still one project contract and one global variable namespace

That keeps modularity without introducing precedence puzzles.

## Groups and sets

Groups and sets are organization tools inside the contract.

### Groups

Variables may declare optional human-facing `groups` such as `Database`, `Runtime`, or `Application`.

Groups are:

* optional
* non-hierarchical
* useful for selection and presentation

Groups are not:

* namespaces
* dependency boundaries
* a resolution rule

### Sets

Contracts may also define named `sets`.

A set is a reusable subset built from:

* explicit variables
* one or more groups
* other sets

Sets are useful when the project wants to talk about a meaningful slice of the contract without duplicating lists of keys.

## How the contract changes

Only two commands change the contract directly:

* [`add`](../reference/commands/add.md)
* [`remove`](../reference/commands/remove.md)

Commands such as `set`, `unset`, and `fill` operate on local values only.

That distinction matters because it separates “the project changed” from “my local machine changed”.

## What problem the contract avoids

Without a contract, environment setup tends to drift:

* required keys are implied rather than declared
* secrets leak into example files
* different developers infer different rules
* generated `.env.local` files quietly become the real source of truth

The contract avoids that by making the shared requirements explicit.

## Why this matters

When the contract is clean:

* onboarding gets easier
* validation gets more trustworthy
* local values can stay local
* the project can evolve its environment model intentionally

In short, the contract answers:

> what does this project require?

It does not answer:

> what does this one machine happen to have right now?

## Read next

Continue from shared requirements into local state and runtime behavior:

<div class="grid cards envctl-read-next" markdown>

-   **Vault**

    See where machine-local values actually live.

    [Read about the vault](vault.md)

-   **Profiles**

    Learn how one contract can support more than one local value set.

    [Read about profiles](profiles.md)

-   **Resolution**

    See how contract data becomes the effective runtime environment.

    [Read about resolution](resolution.md)

</div>
