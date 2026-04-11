# Configuration

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    This page describes the user-level config file used by <code>envctl</code>.
    Config controls machine-local tool behavior. It does not define the project contract and it does not replace local stored values.
  </p>
</div>

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
  "contract_filename": ".envctl.yaml",
  "runtime_mode": "local",
  "default_profile": "local",
  "encryption": { "enabled": false }
}
```

## Keys

### `vault_dir`

The local storage location for the vault.

### `env_filename`

The filename used for generated env files. In most projects this remains `.env.local`.

### `contract_filename`

Legacy default filename for the project contract. Root discovery now prefers `.envctl.yaml` and falls back to `.envctl.schema.yaml`.

### `runtime_mode`

The current execution policy. This controls command policy, not which profile values are selected.

### `default_profile`

The default active profile when no explicit selection is provided.

Resolution order is:

1. `--profile`
2. `ENVCTL_PROFILE`
3. `default_profile`
4. `local`

### `encryption`

Optional block controlling vault encryption at rest.

```json
"encryption": { "enabled": true }
```

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `enabled` | bool | `false` | When `true`, vault files are stored as Fernet-encrypted blobs |

When encryption is enabled:

- `envctl` loads or generates `<vault_dir>/master.key`
- vault reads and writes pass through the encryption layer transparently
- `vault edit` decrypts to a temporary file and re-encrypts it afterwards

## Runtime observability environment variables

`envctl` also supports runtime environment variables for observability and tracing without editing `config.json`.

| Variable | Allowed values | Default | Description |
| --- | --- | --- | --- |
| `ENVCTL_OBSERVABILITY_TRACE` | boolean (`1/0`, `true/false`, `yes/no`, `on/off`) | `false` | Enables structured observability events. |
| `ENVCTL_OBSERVABILITY_PROFILE` | boolean (`1/0`, `true/false`, `yes/no`, `on/off`) | `false` | Enables profile and phase summaries at the end of the command. |
| `ENVCTL_OBSERVABILITY_TRACE_FORMAT` | `human` \| `jsonl` | `jsonl` | Selects trace rendering format. |
| `ENVCTL_OBSERVABILITY_TRACE_OUTPUT` | `stderr` \| `file` \| `both` | `stderr` | Selects trace destination. |
| `ENVCTL_OBSERVABILITY_TRACE_FILE` | file path | auto | File path used when output includes `file`. |
| `ENVCTL_OBSERVABILITY_SANITIZATION` | `full` \| `masked` \| `count_only` | `masked` | Sanitization policy for observable payloads. |

Behavior notes:

- `ENVCTL_OBSERVABILITY_TRACE_FILE` only matters when `TRACE_OUTPUT` includes `file`
- when `TRACE_OUTPUT=file|both` and no file path is provided, `envctl` writes to `.envctl/observability/latest.jsonl` or `.txt`
- invalid values fall back to the documented default

### Precedence

When a CLI flag exists, precedence is:

1. CLI flag (`--trace`, `--trace-format`, `--trace-output`, `--trace-file`, `--profile-observability`)
2. `ENVCTL_OBSERVABILITY_*` environment variable
3. internal default

## Rules

Config does **not**:

- store secrets
- define the project contract
- replace local profile values

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Profiles reference

See how config interacts with explicit profile selection.

[Open profiles reference](profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Vault reference

Reconnect config defaults to the local storage layer they affect.

[Open vault reference](vault.md)
</div>

<div class="envctl-doc-card" markdown>
### Encryption reference

See how config enables and governs vault encryption.

[Open encryption reference](encryption.md)
</div>

</div>
