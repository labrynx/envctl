# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

This release makes contracts modular without sacrificing determinism. 
You can now split your contract across files, but envctl still resolves everything into a single, predictable result.
The CLI is now more consistent across commands, making it easier to understand and reason about what envctl is doing.

### Added

- Support for contract composition via `imports`, allowing contracts to be split into multiple files and resolved as a single, deterministic contract
- New root contract format `.envctl.yaml`, with automatic fallback to legacy `.envctl.schema.yaml`
- Global contract graph built at runtime, including:
  - resolved contract files
  - import relationships
  - variable origin tracking (`declared_in`)
  - global indexes for `sets` and `groups`
- Contract graph included in JSON output under `contract_graph`
- Strict validation for contract imports:
  - cycle detection
  - invalid paths
  - forbidden imports of reserved root contracts
- Global uniqueness enforcement for variables across all imported contracts
- Support for contract `sets`, so you can define reusable subsets built from other sets, groups, and explicit variables
- New `--set` and `--var` scope selectors across validation, inspection, projection, and execution commands
- Aggregated deprecation warnings for legacy contract keys

### Changed

- Contract loading is now repo-aware:
  - `.envctl.yaml` is the new standard root contract
  - `.envctl.schema.yaml` is treated as legacy and used only as fallback
- Contracts can now be modular, but are always resolved into a single composed contract with a global namespace
- `sets` and `groups` are now global across all imported contracts and merged deterministically
- Contract validation is stricter:
  - duplicate variables across imports are rejected
  - importing root contracts is not allowed
- `inspect` now exposes both:
  - the resolved runtime environment
  - the underlying contract composition
- `inspect` now supports structural views:
  - `envctl inspect --contracts`
  - `envctl inspect --sets`
  - `envctl inspect --set NAME`
  - `envctl inspect --groups`
  - `envctl inspect --group NAME`
- `ProjectContext.repo_contract_path` now reflects the discovered root contract instead of relying on config
- `check` now behaves like a compact diagnostic command, focused on problems, actions, and a short summary instead of dumping every resolved value
- `inspect` is now the main detailed diagnostic command and can also inspect one variable directly with `envctl inspect KEY`
- Variables now use `groups` as the primary grouping field, with deterministic internal normalization
- Validation and projection now follow one explicit contract scope: full contract, `--group`, `--set`, or `--var`
- `doctor`, `check`, `inspect`, `export`, `run`, and `sync` surface scope-aware behavior more consistently
- CLI commands now handle warnings, JSON payloads, and text-only behavior more consistently

### Deprecated

- `.envctl.schema.yaml` is now considered a legacy root contract format
  It is still supported, but `.envctl.yaml` is the recommended standard going forward
- `envctl doctor` is now a deprecated alias of `envctl inspect` and is scheduled for removal in `v2.6.0`
- `envctl explain KEY` is now a deprecated alias of `envctl inspect KEY` and is scheduled for removal in `v2.6.0`
- Legacy `group` is still accepted, but it is normalized to `groups: [value]` and should be migrated
- Legacy `required` is still accepted for compatibility, but it no longer has functional meaning

---

## [2.4.1] – 2026-04-05

### Fixed

- Upgraded `cryptography` to `46.0.6` to address published security advisories affecting earlier versions.
- Tightened the runtime cryptography dependency used by vault encryption.

---

## [2.4.0] – 2026-04-05

### Added

* Optional encryption for the vault, so you can protect stored values without changing your workflow
* Commands to migrate vault data between plaintext and encrypted formats
* Clearer feedback when environment projection fails (`run`, `sync`, `export`)
* Warnings when running Docker without properly passing environment variables

### Changed

* Resolution is now strictly based on the contract
  If a variable isn’t declared, it won’t be used
* `${VAR}` expansion is now deterministic and part of a clear resolution flow
* Profiles behave more consistently across commands
* CLI behavior is more predictable, especially around unsupported output modes
* Sync and export outputs are easier to control and understand

### Fixed

* Inconsistent behavior in placeholder expansion across commands
* Issues where dotenv output could break with escaped or complex values
* Cases where sync output didn’t reflect the selected profile correctly

### Security

* Vault encryption uses authenticated encryption and a versioned format
* Clear distinction between valid, corrupted, or wrong-key vault data
* Safer handling of encryption keys and temporary files

### Breaking Changes

* envctl no longer reads from the system environment unless explicitly declared

  If you relied on variables like `${HOME}`, you now need to define them in the contract.

---

## [2.3.0] – 2026-03-30

### Added

* Profile support, so you can manage multiple environments explicitly
* Commands to create, copy, list, and remove profiles
* JSON output mode for key commands, making scripting and CI easier
* Runtime modes (like `local` and `ci`) to prevent unsafe operations
* Ability to control where sync output is written

### Changed

* Commands are now more structured, with project-related actions grouped under `envctl project`
* All value operations are profile-aware
* Output is more consistent and easier to parse

### Fixed

* Issues with older state files not working correctly
* Cases where commands mixed JSON and non-JSON output
* Minor inconsistencies in command behavior and messaging

### Security

* Confirmation required for sensitive operations like `vault show --raw`
* Mutating commands are blocked in CI mode

### Breaking Changes

* Some commands were moved under `envctl project`

  If you were using them at the root level, you’ll need to update your workflows.

---

## [2.2.0] – 2026-03-29

### Added

* Contract-aware commands for managing variables (`add`, `remove`, `set`, `unset`)
* Automatic inference of variable metadata (type, patterns, etc.)
* Better integration with dotenv, editors, and git

### Changed

* The contract is now the central source of truth
* Validation is stricter and happens earlier
* `doctor` reflects both contract and vault state

### Fixed

* Issues with dotenv formatting and quoting
* Problems with project identity during initialization
* Reliability issues in file writes and value masking

### Breaking Changes

* Variables must now be defined in the contract before being used

  Workflows relying on implicit variables will need to be updated.

---

## [2.0.0] – 2026-03-29

### Added

* Contract-based model using `.envctl.schema.yaml`
* Clear separation between definition (contract), resolution, and output
* Core commands for validating and managing environments

### Changed

* `.env.local` is now generated instead of being the source of truth
* The CLI begins to move toward a more modular structure

### Breaking Changes

* The previous symlink-based workflow has been removed
* A contract is now required to use envctl

---

## [1.0.2] – 2026-03-28

### Changed

* Internal structure reorganized to make the codebase easier to maintain
* Tests and documentation updated to match the current layout

---

## [1.0.1] – 2026-03-28

### Changed

* Improved explanation of how the environment lifecycle works
* Clearer documentation around validation and structure

---

## [1.0.0] – 2026-03-28

### Added

* Initial release with core commands for managing environments
* Vault-based storage for values
* JSON-based configuration system
* Safe defaults for permissions and destructive operations

### Security

* Secrets are not shown unless explicitly requested
* Files are protected with restrictive permissions
* Risky operations require confirmation

### Known Limitations

* No encryption at rest
* Limited configuration formats
* No machine-readable output

[Unreleased]: https://github.com/labrynx/envctl/compare/v2.4.1...HEAD
[2.4.1]: https://github.com/labrynx/envctl/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/labrynx/envctl/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/labrynx/envctl/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/labrynx/envctl/compare/v2.0.0...v2.2.0
[2.0.0]: https://github.com/labrynx/envctl/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/labrynx/envctl/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/labrynx/envctl/compare/v1.0.0...v1.0.1