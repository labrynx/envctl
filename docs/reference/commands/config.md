# config

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
