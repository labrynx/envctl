# Roadmap

## v1 (current release)

The first stable version focuses on a solid, secure, and deterministic foundation.

- **Core architecture**  
  - Layered design (CLI, services, config, utils, models)  
  - XDG‑based configuration with optional JSON config file  
  - Unique project identification using repository fingerprint (remote URL or local path)  
  - Per‑project vault directories (`<slug>--<id>`)

- **Commands**  
  - `envctl config init` – create default config with restrictive permissions  
  - `envctl init [PROJECT]` – register repository, create vault file and symlink  
  - `envctl repair` – fix broken or missing symlink; supports `--yes`/`-y`  
  - `envctl unlink` – remove repository symlink only  
  - `envctl status` – show human‑readable repository state with actionable suggestions  
  - `envctl set KEY VALUE` – update a variable in the vault file  
  - `envctl doctor` – diagnostic checks (config, vault permissions, Git detection, symlink support)  
  - `envctl remove` – unregister repository; supports `--yes`/`-y`  

- **Security & safety**  
  - Vault directories created with `0700` permissions  
  - Vault files created with `0600` permissions  
  - Config file created with `0600` permissions  
  - Never overwrites regular files without confirmation  
  - Never prints stored secrets in normal output  
  - `doctor` warns about world‑writable vault directories  

- **Testing & reliability**  
  - Extensive test suite covering all commands and edge cases  
  - Isolated test environment (home directory, XDG vars)  
  - Tests for permissions, confirmation flows, and error conditions  

## v1.1 (planned)

Enhancements that add functionality without changing the core structure.

- **Configuration**  
  - YAML support (auto‑detected by extension)  
  - Optional `--force` flag for `config init` to overwrite existing config  

- **Repository management**  
  - `init --adopt-existing` – migrate an existing real `.env.local` into the vault  
  - `init --force` – recover from inconsistent states (expert mode)  
  - `repair --backup` / `--no-backup` – control backup behaviour when replacing a regular file  
  - `list` command – show all managed repositories (with status)  

- **Metadata & diagnostics**  
  - Store remote URL, initialization timestamp, last‑validation timestamp  
  - `doctor --json` for machine‑readable output  
  - `status --json` for scripting  

- **Usability**  
  - Shell completions (via Typer’s built‑in support)  
  - Dry‑run mode for destructive operations  

## Later (v1.2+)

- Import/export helpers (e.g., from `.env` to vault)  
- Support for multiple managed environment files per repository  
- Better integration with Git worktrees  
- Optional encryption (OS keyring or GPG)  

## Out of scope (for now)

- Cloud sync or remote storage  
- Secret manager integrations (Hashicorp Vault, AWS Secrets Manager, etc.)  
- CI/CD integration  
- Encryption at rest within the vault  