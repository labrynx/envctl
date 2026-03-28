# Roadmap

## v1 (current release)

The first stable version focuses on a solid, secure, and deterministic foundation.

- **Core architecture**
  - Layered design (CLI, services, config, utils, models)
  - Framework-aware CLI with service-oriented command orchestration
  - XDG-based configuration with optional JSON config file
  - Unique project identification using repository fingerprint (remote URL or local path)
  - Per-project vault directories (`<slug>--<id>`)

- **Commands**
  - `envctl config init` – create default config with restrictive permissions
  - `envctl init [PROJECT]` – register repository, create vault file and symlink
  - `envctl repair` – fix broken or missing symlink; supports `--yes` / `-y`
  - `envctl unlink` – remove repository symlink only
  - `envctl status` – show human-readable repository state with actionable suggestions
  - `envctl set KEY VALUE` – update a variable in the vault file
  - `envctl doctor` – diagnostic checks (config, vault permissions, Git detection, symlink support)
  - `envctl remove` – unregister repository; supports `--yes` / `-y`

- **Security & safety**
  - Vault directories created with `0700` permissions
  - Vault files created with `0600` permissions
  - Config file created with `0600` permissions
  - Never overwrites regular files without confirmation
  - Never prints stored secrets in normal output
  - `doctor` warns about world-writable vault directories

- **Testing & reliability**
  - Extensive test suite covering all implemented commands and key edge cases
  - Isolated test environment (home directory, XDG vars, temporary repositories)
  - Tests for permissions, confirmation flows, and error conditions

## v1.1 (next planned release)

The next iteration should make `envctl` more useful in daily development workflows without changing its core philosophy.

- **Environment contract validation**
  - `envctl check` – validate the managed vault env file against a project contract
  - Initial support for `.env.example` comparison
  - Initial support for `.envctl.schema.yaml` as an explicit validation contract
  - Detection of missing required keys
  - Detection of unexpected or unknown keys
  - Simple type validation for common cases such as `int`, `bool`, `url`, and `string`

- **Interactive completion**
  - `envctl fill` – guide the user through missing required values
  - Prompt only for missing keys
  - Never print existing secret values back to the console
  - Optionally initialize values from `.env.example` defaults when explicitly allowed

- **Repository adoption & recovery**
  - `init --adopt-existing` – migrate an existing real `.env.local` into the vault
  - `init --force` – recover from inconsistent states in explicit expert workflows
  - `repair --backup` / `--no-backup` – control backup behaviour when replacing a regular file
  - `config init --force` – explicitly overwrite an existing config file

- **Automation & machine-readable output**
  - `doctor --json` for scripting and automation
  - `status --json` for scripting and automation
  - Stable output shapes for machine consumers

- **Metadata improvements**
  - Store remote URL for easier diagnostics
  - Store initialization timestamp
  - Store last validation timestamp

## v1.2+

Once validation and adoption flows are stable, the next improvements should reduce friction even more.

- Shell completions
- Dry-run mode for destructive commands
- Better support for multiple managed environment files per repository
- Better Git worktree support
- Smarter doctor flows, including optional guided repair
- Optional shell integration helpers for auto-loading workflows

## Later

These ideas are valuable, but should only be explored once the local-first core is mature.

- Import/export helpers
- Optional encryption helpers
- Optional team-oriented sync workflows
- Optional pluggable storage backends
- Optional integrations with external secret sources

## Out of scope (for now)

These are intentionally excluded from the short-term roadmap.

- Cloud-first sync as a required part of the product
- Mandatory remote storage
- Secret manager integrations as a core dependency
- CI/CD integration
- Full encryption-at-rest inside the vault by default
- A terminal UI as a priority over validation and adoption workflows