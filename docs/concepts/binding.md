# Binding

Binding connects a repository to its local vault state.

It defines **where values live**, not what they are.

## Why binding exists

Without binding, identity would rely on:

- folder names
- implicit paths
- fragile assumptions

Binding makes identity explicit and recoverable.

## Canonical project id

Each project has an id:

```text
prj_<16-hex>
```

Stored in local Git config:

```text
envctl.projectId
```

## Binding states

A repository can be:

* **local** → explicit binding exists
* **recovered** → restored from vault state
* **derived** → temporary identity

## Operations

* `bind`
* `unbind`
* `rebind`
* `repair`

## What binding does NOT do

Binding does not:

* change contract
* change values
* affect profiles

## Why it matters

Binding allows:

* deterministic lookup
* recovery across checkouts
* safe state management

## See also

* [Profiles](profiles.md)
* [Resolution](resolution.md)
