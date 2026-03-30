# Configuration

`envctl` uses an XDG config path and a home-based vault path.

The application configuration is intentionally small. It controls local tool behavior, not project contracts.

## Default config path

```text
~/.config/envctl/config.json
```

## Default vault path

```text
~/.envctl/vault
```

## Supported config file format

The current implementation supports JSON.

Example:

```json
{
  "vault_dir": "~/.envctl/vault",
  "env_filename": ".env.local",
  "schema_filename": ".envctl.schema.yaml"
}
```

Possible future enhancements may include:

* YAML support
* config format detection by extension
* additional non-secret workflow settings

## Supported keys

* `vault_dir`: absolute path or `~`-based path to the local vault root
* `env_filename`: repository projection filename, default `.env.local`
* `schema_filename`: repository contract filename, default `.envctl.schema.yaml`

## What configuration is for

Application configuration controls local tool defaults such as:

* where the local vault lives
* which filename is used for materialized environment artifacts
* which filename is used for the project contract
* how the tool resolves paths consistently across commands

## What configuration does not do

The application config is intentionally not a catch-all.

It does **not**:

* store secrets
* define required environment variables
* act as a project schema
* define business rules for one repository
* replace the project contract
* store repository bindings
* define canonical project ids
* replace local Git binding metadata

Project-level environment requirements belong in the repository contract file, not in the user config.

## Configuration vs binding

`envctl` distinguishes between:

* **user config**: global local defaults such as vault root and filenames
* **binding**: checkout-local association between a repository and a canonical project id

The binding is not stored in `config.json`.
It is stored in local Git config for the current checkout.

## Project contract file

`envctl` distinguishes between:

* **user config**: local tool behavior and paths
* **project contract**: shared declaration of expected environment variables

The project contract is expected to live in the repository and be versioned with the project.

Default filename:

```text
<repo-root>/.envctl.schema.yaml
```

This file describes the environment contract only. It must not contain secret values.

## Relationship between config and contract

The user config and the project contract solve different problems.

The user config answers:

* where is my local vault
* what is my default projected env filename
* what is my default contract filename

The project contract answers:

* which variables does this project need
* which ones are required
* what basic validation applies
* which values are sensitive
* which defaults are allowed
* which patterns or choices apply

Mixing these two concerns would create confusion and competing sources of truth.

## Contract filename vs artifact filename

It is important to distinguish between these two filenames:

* `schema_filename` → the contract file
* `env_filename` → the generated environment artifact

By default:

* `schema_filename` = `.envctl.schema.yaml`
* `env_filename` = `.env.local`

These files play different roles:

* the contract defines what the project expects
* the generated env file is only a projection of resolved state

## Permissions

When created by `envctl config init`, the config file is set to `0600` when supported.

The vault root and its managed subdirectories are intended to use restrictive permissions such as:

* `0700` for directories
* `0600` for files

On platforms that do not support POSIX permissions, these operations may be ignored or only partially enforced. In such environments, users are responsible for choosing a secure storage location.

## Future direction

Configuration should remain deliberately small.

Future additions, if introduced, should still follow these rules:

* no secrets in config
* no project contract embedded in config
* no hidden behavior encoded in local-only settings
* no required remote dependencies

## Summary

Config defines local tool behavior.

Contract defines project requirements.

Generated env files are artifacts.

Keeping those three concerns separate is one of the main design rules of `envctl`.
