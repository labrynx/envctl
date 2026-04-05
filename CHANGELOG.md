# Changelog

All notable changes to this project will be documented in this file.

This project follows Keep a Changelog and uses Semantic Versioning.

---

## [Unreleased]

[Full Changelog](https://github.com/labrynx/envctl/compare/v2.3.4...HEAD)

---

## [2.4.0] – 2026-04-05

[Full Changelog](https://github.com/labrynx/envctl/compare/v2.3.4...v2.4.0)

### Added

#### Vault encryption at rest

- Vault files can now be encrypted at rest using a built-in local encryption layer.
- New `envctl vault encrypt` command to migrate existing plaintext vault files to encrypted format.
- New `envctl vault decrypt` command to migrate encrypted vault files back to plaintext.
- `vault edit` now works transparently with encrypted files.
- A dedicated encryption reference was added under `docs/reference/encryption.md`.

### Changed

- `vault check` now reports the physical vault file state more explicitly:
  - `plaintext`
  - `encrypted`
  - `wrong_key`
  - `corrupt`
- Vault operations now fail with clearer messages when a file is encrypted with a different key or the encrypted payload is corrupted.
- Key loading is now safer: `envctl` refuses to silently generate a replacement key if encrypted vault data already exists.
- Config loading and config writing now support the encryption block explicitly.

### Security

- Vault encryption uses authenticated encryption with an explicit versioned file envelope.
- Encrypted vault files can now be distinguished cleanly from plaintext, wrong-key, and corrupted states.
- The vault key is stored as `master.key` with restrictive permissions.
- Temporary files created during encrypted edit flows are cleaned up safely.

### Dependencies

- Added `cryptography` as a runtime dependency for vault encryption support.

### Documentation

- Updated `README.md` to describe the encryption workflow and security model.
- Updated vault, config, and security reference docs to reflect encryption support and migration steps.

---

## [2.3.4] – 2026-04-04

[Full Changelog](https://github.com/labrynx/envctl/compare/v2.3.3...v2.3.4)

### Changed

- Placeholder expansion is now strictly contract-based.
- Unknown placeholders no longer fall back to the host environment.
- References like `${HOME}` now fail unless the variable is declared in the contract.
- `run` and `export` now reject JSON output explicitly.

### Added

- Clearer error messages when projection fails (`run`, `sync`, `export`).
- Optional variable groups in the contract, with `--group` support across commands.
- `sync --output PATH` to write dotenv output to a custom file.
- `export --format dotenv` to print raw dotenv output.
- Warnings when using Docker without properly forwarding environment variables.

### Fixed

- Placeholder expansion now behaves consistently across commands.
- Unknown placeholder references now produce stable errors.

### Security

- Documentation now makes the current security model and its limitations explicit.

---

## [2.3.3] – 2026-04-02

[Full Changelog](https://github.com/labrynx/envctl/compare/v2.3.0...v2.3.3)

### Added

- Canonical active-profile resolution:
  `--profile` → `ENVCTL_PROFILE` → config → `local`.
- `${VAR}` placeholder expansion during resolution.
- Optional string validation with `format: json`, `url`, and `csv`.
- Profile-aware sync output:
  - `.env.local` for local
  - `.env.<profile>` for named profiles

### Changed

- `values.env` is now the canonical storage for the local profile.
- Named profiles must exist before use (fail-fast).
- `add`, `set`, and `unset` now operate only on the active profile.
- `sync`, `run`, and `export` now use fully expanded values.
- Variable names now support both uppercase and lowercase.

### Fixed

- Dotenv rewrites no longer corrupt escaped values (including JSON-like strings).
- `sync` now correctly reflects the selected profile in the output file.
- Confirmation messages are now consistent across commands.

---

## [2.3.0] – 2026-03-30

[Full Changelog](https://github.com/labrynx/envctl/compare/v2.2.0...v2.3.0)

### Breaking changes

- Project identity commands moved under `envctl project`.
- `bind`, `unbind`, `rebind`, and `repair` are no longer available at the root level.

### Added

- Confirmation prompt in `vault show --raw`.
- `envctl project` command group.
- Global `--json` output mode for:
  - `check`, `inspect`, `explain`, `status`, `doctor`
- Runtime modes: `local` and `ci`.
- Profile support:
  - `values.env` (local)
  - `profiles/<name>.env`
- Profile commands:
  - `list`, `create`, `copy`, `remove`, `path`

### Changed

- All value operations are now profile-aware.
- `remove` now deletes variables from the contract and all profiles.
- Profile resolution supports CLI flags and config defaults.
- JSON output is now structured and consistent.

### Fixed

- Compatibility with older `state.json` files.
- `envctl project rebind` no longer requires `--new-project`.
- Commands that don’t support JSON now fail explicitly instead of mixing output.

### Security

- `vault show --raw` requires confirmation.
- Mutating commands are blocked in `ci` mode.

---

## [2.2.0] – 2026-03-29

[Full Changelog](https://github.com/labrynx/envctl/compare/v2.0.0...v2.2.0)

### Breaking changes

- `add`, `remove`, `set`, and `unset` are now contract-aware.
- The contract is now the source of truth for variable definitions.
- Unsupported variable types are rejected.

### Added

- Contract-aware `add` with metadata inference.
- Contract-aware `remove` with confirmation.
- `unset` to remove values without touching the contract.
- Contract inference for:
  - type
  - sensitivity
  - patterns
  - choices
- Adapters for dotenv, editor, and git.

### Changed

- All operations now follow a contract-first model.
- Resolution applies stricter type validation.
- `doctor` reflects the contract + vault state.

### Fixed

- Dotenv serialization and quoting issues.
- Project identity inconsistencies during init.
- Sensitive value masking issues.
- Atomic write reliability.

---

## [2.0.0] – 2026-03-29

[Full Changelog](https://github.com/labrynx/envctl/compare/v1.0.2...v2.0.0)

### Breaking changes

- Removed the symlink-based workflow.
- `.env.local` is no longer the source of truth.
- A contract is now required.

### Added

- New contract format: `.envctl.schema.yaml`.
- Explicit separation between:
  - contract
  - resolution
  - projection
- Core commands:
  - `check`
  - `fill`

### Changed

- `.env.local` is now a generated artifact.
- Repository values are no longer the source of truth.
- CLI begins the transition to a more modular structure.

### Notes

- This release introduces the foundation of the v2 model.

---

## [1.0.2] – 2026-03-28

[Full Changelog](https://github.com/labrynx/envctl/compare/v1.0.1...v1.0.2)

### Changed

- Improved internal structure and separation of responsibilities.
- Updated tests and imports to match the new layout.

### Documentation

- Updated architecture and contributor documentation.

---

## [1.0.1] – 2026-03-28

[Full Changelog](https://github.com/labrynx/envctl/compare/v1.0.0...v1.0.1)

### Changed

- Clarified the environment lifecycle and contract model.
- Improved documentation around structure and validation.

---

## [1.0.0] – 2026-03-28

### Added

- First stable release.
- Core commands:
  - `init`, `repair`, `unlink`, `status`, `set`, `doctor`, `remove`, `config init`
- Vault structure with per-project directories.
- XDG-based JSON configuration.
- Secure default permissions:
  - directories: `0700`
  - files: `0600`
- `doctor` command for environment validation.
- Non-interactive flags (`--yes` / `-y`).
- Full documentation and test suite.
- Global `--version`.

### Security

- Secrets are never printed by default.
- Files are not overwritten without confirmation.
- `doctor` warns about unsafe permissions.

### Known limitations

- No encryption at rest.
- JSON-only configuration.
- No repository listing command.
- No machine-readable output yet.