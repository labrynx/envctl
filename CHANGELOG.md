# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

This unreleased cycle consolidates the CLI around one output-first presenter architecture and
removes legacy compatibility paths that were still mixing formatting concerns across layers.
It also finalizes the hook command reshaping, improves observability initialization ordering,
and raises confidence through broader CLI test coverage and cross-platform output normalization.

### Added

- Added vault audit aggregation primitives:
  - `VaultAuditSummary` domain model
  - summary aggregation logic for audited vault projects
- Added richer vault audit command behavior with consistent summary metadata and exit status signaling.
- Added focused CLI tests for project bind/repair/unbind and vault audit scenarios to increase command coverage.

### Changed

- Completed migration to a unified presenter-driven CLI output flow across core, diagnostic, profile,
  project, vault, hook(s), and guard command families.
- Finalized shared presenter contracts:
  - stable `CommandOutput`/section/item/message model usage
  - centralized warning and diagnostic payload builders
  - normalized renderer behavior for text and JSON output
- Replaced legacy global `--json` behavior with explicit `--output` format selection semantics.
- Standardized command/module layout for hook and guard flows, including nested command organization.
- Renamed internal hook execution flow from `hook-run` to `hook run` and aligned command wiring/tests.
- Centralized runtime initialization responsibilities for config loading and observability context setup.
- Normalized status reporting boundaries:
  - status service now emits structured semantic state
  - presenters derive human-facing summary/issues/action text
  - external command output shape remains stable
- Unified CLI output format typing around one canonical `OutputFormat` source.

### Removed

- Removed legacy CLI output helpers in `utils/output.py`; presenter builders/renderers are now the single path.
- Removed obsolete `command_support` module and stale compatibility helpers no longer used by active command flows.
- Removed deprecated legacy aliases:
  - `envctl doctor`
  - `envctl explain`
- Removed obsolete JSON compatibility serializer paths replaced by the unified presenter payload layer.
- Removed orphan presenter helper/builders that no longer had production consumers.

### Fixed

- Fixed initialization order issues by ensuring observability context is initialized before config loading where required.
- Fixed cross-platform JSON/path payload consistency by normalizing path serialization (notably Windows path assertions).
- Fixed presenter typing and status rendering edge cases discovered during strict typing/linting passes.
- Fixed hook command test wiring to match the final nested module structure and command registration shape.

### Tests

- Expanded and aligned CLI unit/integration coverage for the output-first architecture migration.
- Updated CI-oriented and cross-platform assertions to validate normalized output payloads consistently.

---

## [2.5.1] - 2026-04-14

This release focuses on making `envctl` more predictable for contributors and more maintainable internally.

The development workflow has been standardized around `uv` and a locked environment, removing drift between local setups, hooks, and CI. In parallel, the CLI has been cleaned up to respect architectural boundaries more strictly, reducing hidden coupling across internal layers.

The result is a more reproducible repository, a clearer execution model, and a codebase that is easier to reason about and evolve.

### Changed

#### Dependency and workflow standardization
- Adopted `uv` as the canonical dependency manager for development and CI
- Standardized all workflows around `uv.lock` for deterministic dependency resolution
- Migrated development dependencies from `project.optional-dependencies` to `dependency-groups.dev`
- Refactored all GitHub Actions workflows to use `uv` for dependency management and execution
- Updated pre-commit and pre-push hooks to run via `uv run` with locked environments
- Added `uv-lock` enforcement to pre-commit workflow
- Reworked Makefile targets to delegate execution to `uv` instead of invoking tools directly

#### CLI architecture
- Refactored CLI layer to enforce architectural boundaries
- Reduced direct traversal across internal layers from CLI entry points
- Aligned CLI import paths with defined `import-linter` contracts

#### Release workflow
- Reworked GitHub release generation to derive release notes from `CHANGELOG.md`
- Added automated highlight extraction for GitHub releases
- Established changelog-driven release notes as the canonical release publication workflow

### Improved
- Reduced CLI startup surface by avoiding unnecessary imports and deep dependency chains
- Improved consistency between local development, hooks, and CI environments
- Reduced dependency drift through strict lockfile usage
- Improved maintainability of development tooling and release workflows

### Fixed
- Resolved inconsistencies between `pyproject.toml`, `uv.lock`, and CI environments
- Fixed execution inconsistencies in Makefile and pre-commit hooks
- Updated and aligned versions of development tooling (pytest, Ruff, mypy, import-linter, etc.)

### Docs
- Updated README and CONTRIBUTING to reflect the canonical `uv` workflow
- Simplified installation and development setup instructions
- Clarified contributor policy around `uv.lock` as part of the repository contract
- Updated documentation to match actual CI and local validation flows
- Added a release playbook documenting how commits, changelog entries, semver decisions, and release notes should stay aligned

---

## [2.5.0] - 2026-04-12

This release makes contracts modular without sacrificing determinism.
You can now split your contract across files, but envctl still resolves everything into a single, predictable result.
The CLI is now more consistent across commands, making it easier to understand and reason about what envctl is doing.

### Added

- Support for contract composition via `imports`, allowing contracts to be split into multiple files and resolved as a single, deterministic contract
- New CLI observability flags for trace and profile instrumentation controls
- New observability renderers for both human-readable output and `jsonl` streams
- Optional local observability recorder for persisting emitted traces and events
- Stable observability event contract with centralized sanitization before rendering and emission
- New `envctl guard secrets` command to block staged envctl vault payloads and master keys before commit
- New `envctl hooks` command group for inspecting, installing, repairing, and removing envctl-managed Git hooks
- New internal `envctl hook-run <hook>` command used by managed hook wrappers
- New root contract format `.envctl.yaml`, with automatic fallback to legacy `.envctl.schema.yaml`
- `export` now supports structured JSON output for automation-friendly projection
- Release builds now generate a CycloneDX SBOM for the published wheel
- New distribution reference covering release artifacts, checksums, and provenance verification
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

- New master keys now use a canonical, self-identifying master-key format: `ENVCTL-MASTER-KEY-V1:<key-id>:<base64-key>`
- Legacy raw master keys are migrated automatically when loaded from disk and writable
- `envctl init` now attempts to install envctl-managed `pre-commit` and `pre-push` hooks in the effective Git hooks path instead of relying on a repo-owned `.githooks` layout
- Managed hooks now use minimal canonical wrappers that dispatch back to Python through `envctl hook-run`
- Hooks commands now support versioned JSON output for automation-friendly verification and repair flows
- Release builds now publish a `SHA256SUMS` manifest alongside wheel and source artifacts
- Release checksums now cover the published SBOM as part of the release metadata set
- Release builds now generate GitHub attestations for published artifacts
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
- Internal tracing now covers config loading, profile resolution, project-context resolution, contract loading, profile persistence, projection validation, environment resolution, vault crypto, and command execution through one structured observability layer
- Legacy internal logging has been removed in favor of stable, sanitized observability events plus a compact human trace renderer

### Fixed

- Makefile packaging targets now follow the configured Python executable instead of assuming `python` is available on the path
- Vault services are split more explicitly by query, mutation, and project-crypto responsibilities while preserving the public service facade

### Deprecated

- Legacy raw master keys remain supported only as a transition path and are scheduled for removal in `v2.6.0`
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

[Unreleased]: https://github.com/labrynx/envctl/compare/v2.5.1...HEAD
[2.5.1]: https://github.com/labrynx/envctl/compare/v2.5.0...v2.5.1
[2.5.0]: https://github.com/labrynx/envctl/compare/v2.4.1...v2.5.0
[2.4.1]: https://github.com/labrynx/envctl/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/labrynx/envctl/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/labrynx/envctl/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/labrynx/envctl/compare/v2.0.0...v2.2.0
[2.0.0]: https://github.com/labrynx/envctl/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/labrynx/envctl/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/labrynx/envctl/compare/v1.0.0...v1.0.1
