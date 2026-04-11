# config

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>config</code> manages machine-local <code>envctl</code> configuration.
    It is for tool defaults such as vault location and default profile, not for project contract data or secret storage.
  </p>
</div>

```bash
envctl config init
```

## Purpose

`config` manages user-level `envctl` configuration.

This is machine-local tool configuration, not project contract data and not secret value storage.

## Available subcommands

### `envctl config init`

Creates the default envctl config file for the current user.

This is typically the first step before using `envctl` on a machine for the first time.

## What this command group does

* creates and manages user-level config
* controls defaults such as vault location, runtime mode, and default profile
* stays outside the project contract and outside the local vault values

## When to use it

Use `config init` when you are setting up `envctl` on a new machine or user account.

## When not to use it

Do not use `config` to define project requirements or store local secrets. Those belong to the contract and the vault, respectively.

## Related pages

* see [Configuration](../configuration.md) for config keys and behavior
* use [`init`](init.md) after config setup to prepare a repository

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Configuration

See the exact config keys and precedence rules.

[Open configuration reference](../configuration.md)
</div>

<div class="envctl-doc-card" markdown>
### init

Use this next when the machine is configured and the repository still needs bootstrap.

[Open init reference](init.md)
</div>

<div class="envctl-doc-card" markdown>
### Quickstart

See where `config init` fits in the onboarding flow.

[Open quickstart](../../getting-started/quickstart.md)
</div>

</div>
