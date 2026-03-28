# Security

**Important:** `envctl` assumes a single-user trusted environment. If your system is compromised, your secrets are compromised.

## Principles

- Secrets stay outside repositories.
- Repository files are symlinks, not secret copies.
- The CLI refuses dangerous overwrites.
- Secret values are never printed in normal command output.
- The repository may describe the environment contract, but it must not contain secret values.
- Validation must not mutate secret state implicitly.

## Core model

`envctl` separates three concerns on purpose:

- **contract**: what variables the project needs
- **storage**: where secret values live
- **linkage**: how the repository connects to the vault

In practice, that means:

- `.envctl.schema.yaml` describes requirements only
- the vault stores real values
- `.envctl.json` links repository and vault
- validation commands do not invent or provide values

This separation reduces confusion and avoids competing sources of truth.

## v1 protections

- Vault directories are created with `0700` permissions (user-only access).
- Vault files are created with `0600` permissions (user-only read/write).
- The config file is created with `0600` permissions.
- `doctor` warns if the vault directory is world-writable.
- Permissions are applied best-effort; errors are ignored on filesystems without POSIX support.

## Contract workflow security rules

The future schema-based workflow must preserve the same security posture.

### Allowed

- versioning a schema file in the repository
- declaring required and optional variables
- storing descriptions or onboarding notes
- validating current vault contents against the schema

### Not allowed

- storing secret values in the schema
- providing operational default values from the schema
- automatically generating secrets
- mutating the vault during read-only validation commands

`envctl` should act as a judge and a storage tool, not as an invisible provider of configuration values.

## Limitations

- No encryption at rest.
- No OS keyring integration.
- No remote access control model.
- No guarantee against exposure on insecure filesystems or compromised local accounts.

## User responsibilities

- Keep the local account secure.
- Back up the vault carefully.
- Ensure vault directories have appropriate permissions.
- Avoid storing the vault on shared or insecure filesystems.
- Keep project schemas free of secrets.

The `doctor` command can help verify local readiness, but the final responsibility for local system security remains with the user.
