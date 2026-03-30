# Contract

The contract defines what a project expects from its environment.

It is the **source of truth for requirements**, not for values.

## Location

```text
<repo-root>/.envctl.schema.yaml
```

## What the contract defines

A contract may describe:

* required and optional variables
* types
* descriptions
* sensitivity flags
* non-sensitive defaults
* validation rules
* allowed choices

Example:

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
```

## What the contract does NOT do

The contract must not:

* store secret values
* store machine-specific paths
* define profile-specific values
* act as a local configuration file

## Contract vs values

* the contract defines what exists
* the vault defines what is set

This distinction is fundamental.

## Contract mutation

Only two commands modify the contract:

* `add`
* `remove`

Everything else operates on local values only.

## Why this matters

Keeping the contract separate ensures:

* reproducibility across machines
* explicit project requirements
* no accidental secret leakage
* clear onboarding for new developers

## See also

* [Profiles](profiles.md)
* [Resolution](resolution.md)
