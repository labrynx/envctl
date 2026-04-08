# Binding

Binding is how `envctl` connects a repository checkout to its local vault state.

In practice, it answers a simple question:

> “If I run `envctl` from this repository, which local project state should it use?”

That question matters because repositories move around more than we like to admit. A project can be cloned into different folders, copied into a second checkout, restored after a machine change, or reopened from a path that `envctl` has never seen before.

If identity depended only on folder names or guessed paths, things would look fine right up until they stopped working.

Binding exists to avoid that.

## What binding is for

Binding is about **project identity**, not project configuration.

It tells `envctl` where the local state for this checkout lives. It does **not** define what variables exist, what values they have, or which profile is active.

That separation is important:

- the **contract** defines what the project expects
- the **vault** stores local values
- the **profile** selects one local value set
- **binding** connects this checkout to the right local project state

So binding is not about values. It is about finding the right place to look for them.

## Why binding exists

Without an explicit binding model, identity would have to be guessed from things like:

- folder names
- filesystem paths
- assumptions about where a repository “should” live

That kind of identity is fragile. Rename a folder, duplicate a repository, or move local state around, and the guess can become wrong.

Binding makes identity explicit, local, and recoverable. That gives `envctl` a stable way to reconnect a repository to the correct local state without relying on accidental conventions.

## Canonical project id

Each bound project has a canonical id:

```text
prj_<16-hex>
```

That id is stored in local Git config:

```text
envctl.projectId
```

This is deliberate. The binding belongs to the local checkout, so it lives in local Git config rather than in the repository itself.

That keeps project identity recoverable without turning it into shared repository data.

## Binding states

A repository can appear in different binding states depending on what `envctl` is able to resolve.

### local

A normal explicit local binding exists for this checkout.

### recovered

`envctl` was able to restore the project identity from existing vault state.

This is useful when the current checkout does not already have a persisted local binding, but enough local information exists to reconnect it safely.

### derived

`envctl` is using a temporary identity for now.

This is a provisional state. It is useful when there is not yet a persisted canonical binding, but `envctl` still needs a working local identity until one is established.

## Operations

Binding-related commands are:

* `bind`
* `unbind`
* `rebind`
* `repair`

These commands are about project identity and local state recovery. You use them when you want to establish a binding, remove one, rebuild one, or fix a broken local connection between a repository and its stored state.

## What binding does NOT do

Binding does not:

* change the contract
* change stored values
* affect profiles

That is intentional. `envctl` keeps identity separate from requirements and values so that each part of the model stays clear.

## Why it matters

Binding helps `envctl` find the right local project state without guessing. It also makes recovery across checkouts possible and keeps local state handling safer when repositories move or paths change.

In day-to-day use, that means fewer surprises and less invisible magic.

## Read next

Continue from project identity into local context and runtime behavior:

<div class="grid cards envctl-read-next" markdown>

-   **Profiles**

    See how the selected local value set stays separate from project identity.

    [Read about profiles](profiles.md)

-   **Resolution**

    See what happens after the right local project state is found.

    [Read about resolution](resolution.md)

</div>
