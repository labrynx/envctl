# Mental Model

If you understand this page, you understand `envctl`.

Everything else is a consequence of this model.

## The five parts

Think of `envctl` as five explicit parts:

- **contract**
- **vault**
- **profile**
- **resolution**
- **projection**

## Contract

The contract defines what the project needs.

It lives in the repository:

```text
<repo-root>/.envctl.schema.yaml
```

It may define:

* which variables exist
* whether they are required
* their type
* whether they are sensitive
* optional non-secret defaults
* optional validation rules

The contract must not contain secrets.

## Vault

The vault stores local machine-owned values outside the repository.

This is where real values live.

The vault is local by design.
It is not meant to be shared through version control.

## Profile

A profile selects one local value namespace for the same contract.

Examples:

* `local`
* `dev`
* `staging`
* `ci`

A profile changes only stored values.

A profile does **not** change:

* which variables exist
* which variables are required
* types
* descriptions
* sensitivity flags

## Resolution

Resolution is how `envctl` decides what value each variable gets.

The effective model is:

```text
process environment
-> active profile values
-> contract defaults
```

This is explicit and deterministic.

There is no hidden profile inheritance.

## Projection

Projection is how resolved state becomes usable.

Main projection modes:

* `run` → inject values into a subprocess
* `sync` → generate `.env.local`
* `export` → emit shell export lines

Projected files are artifacts.
They are not the source of truth.

## The most important distinction

The contract defines what exists.

The profile vault defines what is currently set.

The resolved environment defines what actually runs.

That distinction explains almost every command.

## Why command semantics look the way they do

* `add` → contract + active-profile value
* `set` → active-profile value only
* `unset` → remove active-profile value only
* `remove` → remove contract + all persisted profile values

This is intentional.

It prevents shared requirements and local state from collapsing into one thing.

## Runtime mode is different

`runtime_mode` is not a profile.

* **profile** = value namespace
* **runtime mode** = command policy

Example:

* `profile = "ci"` means “use the `ci` values”
* `runtime_mode = "ci"` means “apply CI command restrictions”

They are separate on purpose.

## If you remember only one sentence

> The contract defines what exists.
> The vault stores local values.
> The active profile selects one value set.
> Resolution decides what runs.
> Projection makes it usable.
