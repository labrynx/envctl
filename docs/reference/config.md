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
  "default_profile": "local",
  "encryption": { "enabled": false }
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

Legacy default filename for the project contract.

Current root contract discovery prefers `.envctl.yaml` at the repository root and falls back to `.envctl.schema.yaml`. This config field still exists for compatibility and fallback paths, but it is no longer the primary source of truth for locating the root contract.

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

### `encryption`

Optional block controlling vault encryption at rest.

```json
"encryption": { "enabled": true }
```

| Key | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `false` | When `true`, vault files are stored as Fernet-encrypted blobs |

When `enabled` is `true`:

* `envctl` loads or generates `<vault_dir>/master.key` on first use.
* All vault profile reads and writes pass through the encryption layer transparently.
* `vault edit` decrypts to a temporary file before opening the editor and
  re-encrypts afterwards.

See [Encryption Reference](encryption.md) for the full workflow, key backup
guidance, and migration commands.

## Rules

The config does **not**:

* store secrets
* define the project contract
* define local values

Those concerns live elsewhere in the model.
