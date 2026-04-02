# Contract

The contract defines what a project expects from its environment.

It is the shared description of the project’s needs. It is **not** where real values live.

That is the most important thing to understand on this page.

## Where the contract lives

The contract lives in the repository:

```text
<repo-root>/.envctl.schema.yaml
```

Because it lives with the project, it can be versioned, reviewed, and shared with the rest of the team.

## What the contract describes

A contract can describe things like:

* required and optional variables
* types
* optional semantic string formats (`json`, `url`, `csv`)
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
    required: true
    sensitive: true
    description: Primary database connection

  PORT:
    type: int
    required: true
    default: 3000

  TEST_JSON:
    type: string
    format: json
    required: false
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
