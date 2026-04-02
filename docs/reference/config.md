# Configuration Reference

This page describes the user-level config file used by `envctl`.

The config controls how the tool behaves on your machine. It does not define the project contract, and it does not store secret values.

## Location

Typical location:

```text
~/.config/envctl/config.json
```

## Example

```json
{
  "vault_dir": "~/.envctl/vault",
  "env_filename": ".env.local",
  "schema_filename": ".envctl.schema.yaml",
  "runtime_mode": "local",
  "default_profile": "local"
}
```

## Keys

### `vault_dir`

The local storage location for the vault.

Use this to control where machine-local values are stored.

### `env_filename`

The filename used for generated env files.

In most projects this will remain `.env.local`.

### `schema_filename`

The filename used for the project contract.

In most projects this will remain `.envctl.schema.yaml`.

### `runtime_mode`

The current execution policy.

Examples:

* `local`
* `ci`

This controls command policy, not which profile values are selected.

### `default_profile`

The default active profile.

If no profile is selected explicitly through CLI flags or environment variables, this value is used before falling back to `local`.

Resolution order is always:

1. `--profile`
2. `ENVCTL_PROFILE`
3. `default_profile`
4. `local`

If `default_profile` points to a named profile, that profile must already exist before profile-aware commands can use it.

## Rules

The config does **not**:

* store secrets
* define the project contract
* define local values

Those concerns live elsewhere in the model.
