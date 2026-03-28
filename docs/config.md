# Configuration

`envctl` uses an XDG config path and a home-based vault path.

## Default config path

```text
~/.config/envctl/config.json
````

## Default vault path

```text
~/.envctl/vault
```

## Supported config file format

v1 supports JSON only.

Planned for a later version:

* YAML support
* config format detection by extension

Example:

```json
{
  "vault_dir": "~/.envctl/vault",
  "env_filename": ".env.local"
}
```

## Supported keys

* `vault_dir`: absolute path or `~`-based path to the vault root
* `env_filename`: repository env filename, default `.env.local`

## What configuration does not do

The application config is intentionally small.

It does **not**:

* store secrets
* define required environment variables
* act as a project schema
* provide default values for project variables

Project-level environment requirements belong in the repository schema file (`.envctl.schema.yaml`), not in the user config.

## Project schema file

`envctl` distinguishes between:

* **user config**: local tool behavior and paths
* **project schema**: shared declaration of expected environment variables

The project schema is expected to live in the repository and be versioned with the project. It is not part of `config.json`.

Expected future filename:

```text
<repo-root>/.envctl.schema.yaml
```

This schema file is intended to describe the environment contract only. It must not contain secrets.

## Permissions

When created by `envctl config init`, the config file is set to `0600` (user-only read/write). The vault root and all its subdirectories are created with `0700` permissions, and vault files with `0600`. On platforms that do not support POSIX permissions, these operations are silently ignored.
