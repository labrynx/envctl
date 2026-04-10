# Configuration

This page describes the user-level config file used by `envctl`.

The config controls how the tool behaves on your machine. It does not define the project contract, and it does not store secret values.

!!! note "Config controls tool behavior, not project truth"
    Use config for machine-level defaults such as vault location or default profile. Do not treat it as a place for contract data or secret values.

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

Use this to control where machine-local values are stored.

### `env_filename`

The filename used for generated env files.

In most projects this will remain `.env.local`.

### `contract_filename`

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

* `envctl` loads or generates `<vault_dir>/master.key` on first use
* all vault profile reads and writes pass through the encryption layer transparently
* `vault edit` decrypts to a temporary file before opening the editor and re-encrypts afterwards

See [Encryption Reference](encryption.md) for the full workflow, key backup guidance, and migration commands.

## Rules

The config does **not**:

* store secrets
* define the project contract
* define local values

Those concerns live elsewhere in the model.

## Observability runtime env vars

`envctl` también soporta variables de entorno runtime para controlar observabilidad/tracing en una ejecución puntual, sin editar `config.json`.

| Variable | Valores permitidos | Default | Descripción |
|---|---|---|---|
| `ENVCTL_OBSERVABILITY_TRACE` | booleano (`1/0`, `true/false`, `yes/no`, `on/off`) | `false` | Activa/desactiva emisión de eventos de observabilidad. |
| `ENVCTL_OBSERVABILITY_PROFILE` | booleano (`1/0`, `true/false`, `yes/no`, `on/off`) | `false` | Activa resumen de perfiles/fases al final del comando. |
| `ENVCTL_OBSERVABILITY_TRACE_FORMAT` | `human` \| `jsonl` | `jsonl` | Define el formato de renderizado de eventos. |
| `ENVCTL_OBSERVABILITY_TRACE_OUTPUT` | `stderr` \| `file` \| `both` | `stderr` | Define destino de salida del trace. |
| `ENVCTL_OBSERVABILITY_TRACE_FILE` | ruta de archivo | _auto_ cuando `TRACE_OUTPUT=file|both` | Ruta del archivo de salida para traces en archivo. |
| `ENVCTL_OBSERVABILITY_SANITIZATION` | `full` \| `masked` \| `count_only` | `masked` | Política de sanitización para payloads/eventos observables. |

Notas de comportamiento:

* `ENVCTL_OBSERVABILITY_TRACE_FILE` solo tiene efecto cuando `ENVCTL_OBSERVABILITY_TRACE_OUTPUT` incluye `file`.
* Si `TRACE_OUTPUT=file|both` y no defines `TRACE_FILE`, `envctl` escribe en `.envctl/observability/latest.jsonl` (o `.txt` si el formato es `human`).
* Valores inválidos en `TRACE_FORMAT`, `TRACE_OUTPUT` o `SANITIZATION` hacen fallback silencioso al default indicado en la tabla.

### Precedencia (CLI flag > env var)

Cuando existe flag de CLI equivalente en la implementación actual, la precedencia es:

1. Flag CLI (`--trace`, `--trace-format`, `--trace-output`, `--trace-file`, `--profile-observability`)
2. Variable de entorno (`ENVCTL_OBSERVABILITY_*`)
3. Default interno

`ENVCTL_OBSERVABILITY_SANITIZATION` no tiene flag CLI equivalente hoy; se controla solo vía variable de entorno (o default interno).
