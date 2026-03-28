# Repository metadata format

When a repository is initialized with `envctl init`, a metadata file (default `.envctl.json`) is created inside the repository root. This file stores information needed to connect the repository to its vault entry.

## File location

```
<repo-root>/.envctl.json
```

## Format (version 1)

The file is a JSON object with the following fields:

| Field                 | Type   | Description |
|-----------------------|--------|-------------|
| `version`             | int    | Metadata version (currently `1`). |
| `project_slug`        | string | User‑friendly, filesystem‑safe slug (e.g., `my-app`). |
| `project_id`          | string | Unique identifier derived from repository fingerprint (12 characters). |
| `env_filename`        | string | Name of the environment file (default `.env.local`). |
| `vault_project_dir`   | string | Absolute path to the vault project directory (e.g., `/home/user/.envctl/vault/projects/my-app--abc123def456`). |
| `vault_env_path`      | string | Absolute path to the managed vault env file. |
| `repo_fingerprint`    | string | SHA‑256 hash of the repository identity (origin remote URL or absolute path). |

Example:

```json
{
  "version": 1,
  "project_slug": "my-app",
  "project_id": "abc123def456",
  "env_filename": ".env.local",
  "vault_project_dir": "/home/user/.envctl/vault/projects/my-app--abc123def456",
  "vault_env_path": "/home/user/.envctl/vault/projects/my-app--abc123def456/.env.local",
  "repo_fingerprint": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

## Versioning

The `version` field allows future upgrades. When a new metadata version is introduced, `envctl` will:

- Continue reading older versions (backward compatibility).
- Migrate to the newer version when a command modifies the metadata (e.g., `init --force`).

## Planned changes (v1.1)

- Add `remote_url` field for easier diagnostics.
- Add `created_at` and `updated_at` timestamps (ISO 8601).
- Add `last_validation` timestamp for automated health checks.

## Security note

This file does **not** contain secrets. It only stores paths and identifiers. However, it should still be kept private because it reveals the vault location.
