# Mental Model

If you understand this page, the rest of `envctl` becomes much easier to follow.

Most of the commands, workflows, and design choices make sense once you see the model underneath them.

## The five parts

A useful way to think about `envctl` is as five connected parts:

- **contract**
- **vault**
- **profile**
- **resolution**
- **projection**

Each one has a different job. Keeping them separate is one of the reasons the tool stays easier to reason about.

## Contract

The contract defines what the project needs.

The main contract is discovered at the repo root. It prefers `.envctl.yaml` and still accepts `.envctl.schema.yaml` as a legacy fallback. That root contract may import other contract files, but the result is still one composed project contract. New repositories should treat `.envctl.yaml` as the standard shape, while legacy repositories can continue to work with `.envctl.schema.yaml` during migration.

It lives in the repository:

```text
<repo-root>/.envctl.yaml
<repo-root>/.envctl.schema.yaml  # legacy fallback
```

It may describe things like:

* which variables exist
* whether they are required
* their type
* whether they are sensitive
* optional non-secret defaults
* optional validation rules

The contract must not contain secrets.

A good way to think about it is this: the contract is the shared description of the project’s requirements.

## Vault

The vault stores local machine-owned values outside the repository.

This is where real values live.

The vault is local by design. It is not meant to be shared through version control, and it is not supposed to become part of the project source tree.

## Profile

A profile selects one local value set for the same contract.

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

So profiles give you multiple local setups for one project contract. They do not create multiple versions of the contract itself.

## Resolution

Resolution is how `envctl` decides what value each variable gets at runtime.

The effective order is:

```text
active profile values
-> contract defaults
```

That means the active profile provides explicit values first, and the contract can still provide non-sensitive defaults if no explicit value is set.

There is no hidden profile inheritance. The rules are meant to stay visible and easy to trace.

## Projection

Projection is how resolved state becomes usable.

The main projection modes are:

* `run` → inject values into a subprocess
* `sync` → generate `.env.local`
* `export` → print shell export lines

Projected files are outputs. They are not the source of truth.

That matters because it keeps generated artifacts from silently becoming the real configuration model.

## The most important distinction

The contract defines what exists.

The profile vault defines what is currently set.

The resolved environment defines what actually runs.

That distinction explains most command behavior.

## Why the commands behave the way they do

Once you keep those layers separate, these command semantics make sense:

* `add` → contract + active-profile value
* `set` → active-profile value only
* `unset` → remove active-profile value only
* `remove` → remove contract + all persisted profile values

This is intentional.

It stops shared requirements and machine-local values from getting mixed together.

## Runtime mode is different

`runtime_mode` is not a profile.

* **profile** = which local value set to use
* **runtime mode** = which command policy applies

For example:

* `profile = "ci"` means “use the `ci` profile values”
* `runtime_mode = "ci"` means “apply CI restrictions to command behavior”

They are related only because they may both matter in the same workflow. They are not the same concept.

## If you remember only one thing

> The contract defines what exists.
> The vault stores local values.
> The active profile selects one local value set.
> Resolution decides what runs.
> Projection makes it usable.
