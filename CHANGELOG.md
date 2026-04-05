# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

[Full Changelog](https://github.com/labrynx/envctl/compare/v1.0.1...v1.0.2)

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

[Unreleased]: https://github.com/labrynx/envctl/compare/v2.4.0...HEAD
[2.4.0]: https://github.com/labrynx/envctl/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/labrynx/envctl/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/labrynx/envctl/compare/v2.0.0...v2.2.0
[2.0.0]: https://github.com/labrynx/envctl/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/labrynx/envctl/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/labrynx/envctl/compare/v1.0.0...v1.0.1


