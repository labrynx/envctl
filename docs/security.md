# Security

## Principles

- Secrets stay outside repositories.
- Repository files are symlinks, not secret copies.
- The CLI refuses dangerous overwrites.
- Secret values are never printed in normal command output.

## v1 limitations

- No encryption at rest.
- No OS keyring integration.
- No remote access control model.

## User responsibilities

- Keep the local account secure.
- Back up the vault carefully.
- Ensure vault directories have appropriate permissions.
