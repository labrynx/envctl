# Roadmap

## v1 (current release)

The first stable version focuses on a solid, secure, and deterministic foundation.

### Core architecture

- Layered design (CLI, services, config, utils, models)
- XDG-based configuration with optional JSON config file
- Unique project identification using repository fingerprint (remote URL or local path)
- Per-project vault directories (`<slug>--<id>`)

### Commands

- `envctl config init` — create default config with restrictive permissions
- `envctl init [PROJECT]` — register repository, create vault file and symlink
- `envctl repair` — fix broken or missing symlink; supports `--yes` / `-y`
- `envctl unlink` — remove repository symlink only
- `envctl status` — show human-readable repository state with actionable suggestions
- `envctl set KEY VALUE` — update a variable in the vault file
- `envctl doctor` — diagnostic checks (config, vault permissions, Git detection, symlink support)
- `envctl remove` — unregister repository; supports `--yes` / `-y`

### Security and safety

- Vault directories created with `0700` permissions
- Vault files created with `0600` permissions
- Config file created with `0600` permissions
- Never overwrites regular files without confirmation
- Never prints stored secrets in normal output
- `doctor` warns about world-writable vault directories

### Testing and reliability

- Extensive test suite covering all commands and edge cases
- Isolated test environment (home directory, XDG vars)
- Tests for permissions, confirmation flows, and error conditions

---

## Next major step: environment contract workflow

The next meaningful evolution of `envctl` is not more automation inside `init`, but a clearer lifecycle around project environment contracts.

The intended model is:

- `doctor` validates host readiness
- `status` validates repository-to-vault linkage
- `check` validates vault contents against a project schema
- `fill` interactively collects missing required values
- `set` remains the explicit one-key mutation command

This keeps command identities clear and preserves the deterministic nature of `init`.

### Shared project schema

Planned schema filename:

```text
<repo-root>/.envctl.schema.yaml
````

Design intent:

* versioned in the repository
* contains no secrets
* contains no default values
* declares the environment contract only

Possible schema responsibilities:

* declare required variables
* declare optional variables
* attach short descriptions or notes for onboarding

### `envctl check`

Planned responsibilities:

* read `.envctl.schema.yaml`
* compare declared variables with the managed vault env file
* report missing required variables
* return a non-zero exit code when the contract is not met
* remain fully read-only

### `envctl fill`

Planned responsibilities:

* read `.envctl.schema.yaml`
* detect missing required variables
* prompt the user only for missing required values
* write them to the vault explicitly
* remain separate from `init`

This separation is important. `fill` is the interactive onboarding bridge; `init` remains structural and deterministic.

---

## Additional future improvements

These are useful extensions, but secondary to the contract workflow above.

### Configuration

* YAML support for user config
* config format detection by extension
* optional overwrite mode for `config init`

### Diagnostics and output

* `doctor --json` for scripting
* `status --json` for scripting
* richer `check` output modes
* clearer exit-code semantics across validation commands

### Repository management

* `init --adopt-existing`
* `init --force` for expert recovery scenarios
* configurable repair backup behavior
* `list` command for managed repositories
* vault diagnostics for orphaned or inconsistent entries

### Advanced workflows

* better Git worktree support
* support for multiple managed env files per repository
* import/export helpers for vault data

---

## Out of scope for the core model

These are intentionally excluded to keep the tool simple, explicit, and local-first:

* cloud sync or remote storage
* secret manager integrations as a core feature
* CI/CD integration as a first-class responsibility
* default-value provisioning from schemas
* hidden mutation during validation commands

---

## Guiding principles

* Explicit over implicit
* Local-first, no hidden behavior
* Deterministic and reproducible environments
* Safety by default
* One responsibility per command
* Repository declares the contract, vault stores the secret
