# envctl

`envctl` is a local CLI tool that centralizes repository `.env.local` files into a user-owned vault and links them back into repositories using symlinks.

It is designed around a simple model:

- the repository declares what it needs
- the vault stores the secret values
- the link between both is explicit and local

## Goals

- Keep secrets outside repositories
- Avoid duplicated `.env.local` files
- Use explicit, deterministic local-only workflows
- Fail safely when the filesystem is not in the expected state
- Make environment setup understandable and verifiable

## Non-goals

- No automatic syncing
- No hidden behavior
- No implicit environment creation
- No secret management beyond the local filesystem
- No default-value provisioning from project schemas

Everything is explicit and local.

## Current commands

- `envctl init [PROJECT]`
- `envctl repair` (supports `--yes` / `-y`)
- `envctl unlink`
- `envctl status`
- `envctl set KEY VALUE`
- `envctl doctor`
- `envctl remove` (supports `--yes` / `-y`)
- `envctl config init`

## Command model

Each command has a narrow responsibility:

- `init`: create vault structure, metadata, and repository link
- `doctor`: validate local machine and envctl readiness
- `status`: validate repository-to-vault state
- `set`: update one explicit key in the vault
- `repair`: restore a broken or missing link safely
- `remove`: detach the repository from envctl management

Planned additions complete the model rather than change it:

- `check`: validate vault contents against a project schema
- `fill`: interactively provide missing required values

## Installation

### Local editable install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
````

### Run

```bash
envctl --help
```

## Default paths

Config file:

```text
~/.config/envctl/config.json
```

Vault root:

```text
~/.envctl/vault
```

Managed project env file:

```text
~/.envctl/vault/projects/<project-slug>--<project-id>/.env.local
```

Repository link:

```text
<repo>/.env.local -> ~/.envctl/vault/projects/<project-slug>--<project-id>/.env.local
```

Repository metadata:

```text
<repo>/.envctl.json
```

Planned project schema file:

```text
<repo>/.envctl.schema.yaml
```

## Example workflow

Initialize the repository:

```bash
envctl init
```

Set a variable explicitly:

```bash
envctl set APP_ENV development
```

Inspect repository state:

```bash
envctl status
```

Run local diagnostics:

```bash
envctl doctor
```

Repair the repository link non-interactively:

```bash
envctl repair --yes
```

Remove envctl management and restore a local env file:

```bash
envctl remove --yes
```

## Why the schema matters

A future `.envctl.schema.yaml` file will allow a project to declare its environment contract without storing any secret values.

That makes it possible to separate:

* **contract**: what variables should exist
* **storage**: where the values live
* **validation**: whether the current vault satisfies the project

This leads to a clean workflow:

* `doctor` checks the machine
* `status` checks the bridge
* `check` checks the contract
* `fill` helps complete missing required values

## Important design rule

`init` is intentionally structural only.

It must not:

* prompt for secret values
* populate the vault from a schema
* provide defaults

Interactive onboarding belongs in `fill`, not in `init`. This keeps initialization deterministic and safe for repeated execution.

## Example status output

```text
On project my-app (abc123def456)

Status: healthy

Repository is correctly linked to the managed vault env file

Repository env: linked
Vault env: present
```

## Example doctor output

```text
[OK] config: Using defaults (no config file at /home/user/.config/envctl/config.json)
[WARN] vault_path: Vault directory has not been created yet: /home/user/.envctl/vault
[WARN] vault_permissions: Vault permissions cannot be checked until the vault directory exists
[WARN] repo_detection: No Git repository detected from the current working directory
[OK] symlink_support: Symlink creation works
```

## Security notes

* Vault directories are created with `0700` permissions; vault files with `0600`.
* The config file is created with `0600` permissions.
* `envctl` never prints stored secret values.
* `unlink` does not copy secrets back into the repository.
* `repair` never invents a missing vault file.
* `status` reports repository state without modifying files.
* `set` updates only the managed vault env file and requires prior initialization.
* Future schema files must never contain secrets or defaults.

## Development

```bash
./scripts/dev.sh
./scripts/test.sh
```

For more detail, see the [docs](docs) directory.

For contributor-oriented architectural detail, see [architecture-in-depth.md](docs/dev/architecture-in-depth.md).
