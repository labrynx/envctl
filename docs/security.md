# Security

**Important:** `envctl` assumes a single‑user trusted environment. If your system is compromised, your secrets are compromised.

## Principles

- Secrets stay outside repositories.
- Repository files are symlinks, not secret copies.
- The CLI refuses dangerous overwrites.
- Secret values are never printed in normal command output.

## v1 protections

- Vault directories are created with `0700` permissions (user‑only access).
- Vault files are created with `0600` permissions (user‑only read/write).
- The config file is created with `0600` permissions.
- `doctor` warns if the vault directory is world‑writable.
- Permissions are applied best‑effort; errors are ignored on filesystems without POSIX support.

## v1 limitations

- No encryption at rest.
- No OS keyring integration.
- No remote access control model.

## User responsibilities

- Keep the local account secure.
- Back up the vault carefully.
- Ensure vault directories have appropriate permissions (the `doctor` command can help verify this).
