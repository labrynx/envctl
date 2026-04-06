# Contract

The contract defines what a project expects from its environment.

It is the shared description of the project’s needs. It is **not** where real values live.

That is the most important thing to understand on this page.

## Where the contract lives

The root contract lives at the repository root and is discovered in this order:

```text
<repo-root>/.envctl.yaml
<repo-root>/.envctl.schema.yaml  # legacy fallback
```

If both files exist, `envctl` uses `.envctl.yaml` and warns that `.envctl.schema.yaml` should be migrated or removed.

Because the root contract lives with the project, it can be versioned, reviewed, and shared with the rest of the team.


## Contract composition and imports

A root contract may import other contract files:

```yaml
imports:
  - ./contracts/shared.yaml
  - ./contracts/backend.yaml
```

Imports are resolved relative to the file that declares them. `envctl` loads them recursively and builds one composed contract.

A few rules are strict on purpose:

* imported contracts do not create separate namespaces
* one variable key may be declared only once across the full resolved graph
* imported contracts do not override one another
* the final result is one contract, one global variable namespace, and one project vault
* the root contracts `.envctl.yaml` and `.envctl.schema.yaml` are reserved and cannot be imported by child contracts

This keeps composition explicit and deterministic. Modular files are allowed. Implicit precedence is not.

## What the contract describes

A contract can describe things like:

* declared variables
* types
* optional semantic string formats (`json`, `url`, `csv`)
* optional human-facing groups
* named reusable sets
* descriptions
* sensitivity flags
* non-sensitive defaults
* validation rules
* allowed choices

For example:

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

  TEST_JSON:
    type: string
    format: json

  APP_URL:
    type: string
    groups:
      - Application
    default: http://${APP_NAME}:${PORT}

sets:
  docker_runtime:
    description: Variables needed to run the app in a container
    groups:
      - Application
      - Runtime
    variables:
      - DATABASE_URL
```

This file tells the project what should exist and what shape those values should have. It does not provide the real secret values themselves.

## What the contract does NOT do

The contract must not:

* store secret values
* store machine-specific paths
* define profile-specific values
* act as a personal local config file

If it did those things, it would stop being a clean shared description and start becoming a confusing mix of shared requirements and local state.

## Contract vs values

A good way to think about it is this:

* the **contract** defines what exists
* the **vault** defines what is currently set

That separation is one of the core ideas behind `envctl`.

The contract is shared with the project. Values stay local to the machine.

## Groups and sets

Groups and sets are global across the resolved contract graph. If different imported files contribute variables to the same set or group name, `envctl` merges the membership by union and keeps the result stable and deduplicated.


Variables may declare optional `groups` such as `Database`, `Observability`, or `Docker runtime`. A variable may belong to more than one group.

Groups are:

* optional
* human-facing
* non-hierarchical
* used only for selection and presentation

They are not:

* a namespace
* a dependency boundary
* a prefix or dotted matching system
* a rule that changes resolution behavior

Contracts may also define named `sets`. A set is a reusable subset built from:

* other sets
* one or more groups
* explicit variables

Set resolution is recursive, duplicates are removed, and the final variable list is normalized alphabetically. Cycles between sets are invalid.

Legacy `group` is still accepted for compatibility, but it is deprecated and normalized to `groups: [value]`. Legacy `required` is also accepted for compatibility, but it no longer affects validation. Validation now follows the active contract scope: full contract, `--group`, `--set`, or `--var`.

## How the contract changes

Only two commands change the contract:

* `add`
* `remove`

Everything else works on local values only.

That means commands like `set`, `unset`, and `fill` do not change the shared project definition. They only affect the values stored on the current machine.

## Why this matters

Keeping the contract separate from local values makes a few important things easier:

* new developers can see what the project needs
* secrets stay out of version control
* project requirements stay explicit
* the same repository can be used on different machines without guessing

In short, the contract answers:

> “What does this project need to run?”

It does not answer:

> “What secrets do I personally have on this machine right now?”

## See also

* [Profiles](profiles.md)
* [Resolution](resolution.md)
