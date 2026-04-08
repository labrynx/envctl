# Team

## Problem

Teams need a shared understanding of what the project requires, but they should not share real local values through the repository.

Without a clear split, secrets leak into version control or developers end up guessing what the app actually needs.

## Goal

Collaborate on one shared environment contract while keeping each developer's real values local.

## Steps

When the project itself needs a new variable, add it to the contract:

```bash
envctl add API_KEY
git add .envctl.yaml
git commit
```

After another developer pulls that change, they validate:

```bash
envctl check
```

Then they fill only the values their machine is missing:

```bash
envctl fill
```

## Result

The team shares:

* the contract
* the naming
* the validation rules
* the expected shape of the environment

But each machine keeps its real values local.

## Why this works

`envctl` keeps shared intent and local truth separate.

That means the repository can describe requirements without turning into a secret distribution channel.

* [Contract](../concepts/contract.md)
* [add](../reference/commands/add.md)
* [fill](../reference/commands/fill.md)
* [check](../reference/commands/check.md)
