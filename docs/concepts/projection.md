# Projection

Projection is how `envctl` exposes an already-resolved environment to other tools.

By the time projection happens, the important decisions are already made:

* the contract has been loaded
* the active profile has been selected
* values have been resolved
* placeholders have been expanded
* validation has happened

Projection does not define state.

It only makes existing resolved state usable.

!!! note "Projection outputs are artifacts, not the source of truth"
    `run`, `sync`, and `export` expose already-resolved state. They do not replace the contract or the vault.

## TL;DR

Projection is how resolved state leaves `envctl` and reaches the thing that needs it.

- `run` projects into a child process
- `sync` projects into a generated file
- `export` projects into stdout
- none of those outputs become the source of truth

## What projection is

Projection is the handoff layer between `envctl`'s model and the outside world.

Its job is to answer:

> how should this resolved environment be exposed for this workflow?

That is why `envctl` has different projection modes instead of pretending every tool wants the same interface.

## What projection is not

Projection is not:

* the source of truth
* a substitute for the contract
* local storage
* resolution itself

A generated `.env.local`, a subprocess environment, or stdout export lines are all outputs of the model, not the model.

## The three projection shapes

Conceptually, `envctl` projects resolved state in three different ways.

### 1. In-memory subprocess injection

This is the `run` shape.

The resolved environment is passed directly into a child process.

What matters conceptually:

* no dotenv file is created
* the handoff is ephemeral
* this is usually the cleanest path when the target process can receive env vars directly

This is the projection mode that stays closest to the runtime model.

### 2. File generation

This is the `sync` shape.

The resolved environment is materialized into a dotenv file on disk.

What matters conceptually:

* the file is generated output
* it exists for compatibility with tools that want a file
* it is safe to delete and regenerate

This mode is useful, but it is easier to misuse if people start treating the generated file as the real source of truth.

### 3. Stdout projection

This is the `export` shape.

The resolved environment is printed to standard output in a shell-oriented or dotenv-oriented format.

What matters conceptually:

* it is designed for chaining into other commands or scripts
* it is still projection output, not storage
* it keeps the handoff explicit

## The core distinction

The main difference between the projection modes is not “which command name do I type?”

It is:

* `run` projects into a process
* `sync` projects into a file
* `export` projects into stdout

That mental split is more important than memorizing syntax.

## Why projection exists at all

Different tools want the same environment in different shapes.

Instead of turning one of those shapes into the hidden canonical form, `envctl` keeps them all downstream of resolution.

That avoids a common failure mode:

* the generated file becomes stale
* the file starts being edited by hand
* the team no longer knows whether the contract, the vault, or the artifact is the truth

Projection exists to prevent that collapse.

## Common mistakes projection avoids

Keeping projection explicit helps avoid:

* treating `.env.local` as the primary state store
* assuming shell inheritance is part of resolution
* writing secrets to disk when direct subprocess injection would be enough
* confusing “what the project needs” with “how one tool expects to receive it”

## Projection and containers

Projection is also where people often make incorrect assumptions about Docker.

If `envctl` injects variables into the Docker client process, that does not automatically mean the container sees the full resolved environment.

That is why container workflows often need explicit forwarding or an env-file handoff. The key idea is not Docker syntax itself, but this:

> projection must match the interface the downstream tool actually consumes

## When to choose each mode

Choose the projection shape by downstream interface:

* choose `run` when the target process can directly receive env vars
* choose `sync` when a tool explicitly expects a file on disk
* choose `export` when another shell command or script wants stdout

The right question is not “which one is most powerful?”

It is:

> what is the narrowest projection that fits this workflow cleanly?

## Why this matters

When projection stays separate from state:

* the model remains easier to trust
* generated artifacts stay disposable
* debugging gets easier
* teams avoid silent divergence between local files and actual runtime truth

In short, projection answers:

> now that the environment is resolved, how should I hand it off?

## Read next

Connect projection back to the model and the exact command behavior:

<div class="grid cards envctl-read-next" markdown>

-   **Resolution**

    Revisit the step that decides the effective environment before any handoff.

    [Read about resolution](resolution.md)

-   **run**

    See the exact subprocess projection behavior.

    [Open the `run` command](../reference/commands/run.md)

-   **sync**

    See when file generation is appropriate and when it is not.

    [Open the `sync` command](../reference/commands/sync.md)

</div>
