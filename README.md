# envctl

`envctl` is a local CLI tool that centralizes repository `.env.local` files into a user-owned vault and links them back into repositories using symlinks.

## Goals

- Keep secrets outside repositories.
- Avoid duplicated `.env.local` files.
- Use explicit, deterministic local-only workflows.
- Fail safely when the filesystem is not in the expected state.

## v1 Commands

- `envctl init [PROJECT]`
- `envctl repair`
- `envctl unlink` (removes the managed symlink if present; no-op otherwise)
- `envctl status`
- `envctl set KEY VALUE`
- `envctl doctor`
- `envctl remove`
- `envctl help [COMMAND]`

## Installation

### Local editable install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

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

Project env file:

```text
~/.envctl/vault/projects/<project-slug>--<project-id>/.env.local
```

Repository link:

```text
<repo>/.env.local -> ~/.envctl/vault/projects/<project-slug>--<project-id>/.env.local
```

## Examples

Initialize using the current directory name:

```bash
envctl init
```

Initialize with an explicit project name:

```bash
envctl init my-app
```

Repair the repository link:

```bash
envctl repair
```

Inspect current repository state:

```bash
envctl status
```

Example status output:

```text
On project my-app (abc123def456)

Status: healthy

Repository is correctly linked to the managed vault env file

Repository env: linked
Vault env: present
```

Run environment diagnostics:

```bash
envctl doctor
```

Example doctor output:

```text
[WARN] config: Config file not found; using defaults at /home/user/.config/envctl/config.json
[WARN] vault_path: Vault directory has not been created yet: /home/user/.local/share/envctl/vault
[WARN] vault_permissions: Vault permissions cannot be checked until the vault directory exists
[WARN] repo_detection: No Git repository detected from the current working directory
[OK] symlink_support: Symlink creation works
```

Set a variable:

```bash
envctl set APP_ENV development
```

Restore a real repository env file and remove envctl management:

```bash
envctl remove
```

## Security notes

* `envctl` never prints stored secret values.
* `unlink` does not copy secrets back into the repository.
* `repair` never invents a missing vault file and will advise using `init`.
* `status` reports repository state without modifying files.
* `set` updates only the managed vault env file and requires prior initialization.

## Development

```bash
./scripts/dev.sh
./scripts/test.sh
```
