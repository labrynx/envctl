# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

* Prompt/presentation layer for CLI interactions:

  * introduced `cli/prompts` with dedicated prompt builders
  * introduced `cli/presenters` to separate output rendering from command orchestration
  * centralizes construction of human-facing confirmation messages
  * removes string-building logic from command handlers
  * enables future reuse across different UIs (CLI, TUI, etc.)

* Composite confirmation messages:

  * `remove`, `profile remove`, `project rebind`, `vault prune`, and `vault show --raw` now use structured multi-line prompts
  * confirmation messages can reflect execution plans (e.g. affected profiles)
  * improves clarity for destructive operations

* Profile-aware sync target resolution:

  * introduced `build_repo_sync_env_path`
  * `sync` now materializes environment files per profile:

    * `.env.local` for implicit local profile
    * `.env.<profile>` for named profiles

  * enables multi-environment workflows directly in the repository

---

### Changed

* CLI architecture — prompts vs presentation:

  * confirmation message construction moved out of commands into `cli/prompts`
  * commands now orchestrate flow only, without embedding user-facing formatting logic
  * reinforces separation between:

    * prompts → input layer
    * presenters → output layer
    * commands → orchestration layer

* CLI interaction boundaries:

  * interactive flows (`confirm`, `prompt`) now rely on explicit prompt builders
  * destructive and confirmation-based commands use reusable interaction components
  * prepares the CLI for alternative frontends and non-interactive policy handling

* CLI output architecture cleanup:

  * legacy formatter-based output handling was removed
  * output responsibilities are now split more explicitly across presenters, prompts, and shared output utilities
  * reduces leakage of formatting concerns across command handlers

* `sync` command semantics:

  * output file is now derived from the active profile instead of a single fixed path
  * removes implicit coupling to `context.repo_env_path`
  * aligns projection behavior with the profile-aware runtime model

* Internal path responsibilities:

  * repository context no longer dictates sync output location
  * projection paths are now explicitly resolved per operation
  * improves clarity between:

    * context (what exists)
    * projection (what is generated)

* CLI layering consistency:

  * reinforced clean separation between:

    * commands (orchestration)
    * services (business logic)
    * prompts (input construction)
    * presenters (output rendering)

  * makes command implementations smaller and more intention-revealing

* Documentation and repository metadata alignment:

  * refreshed README and documentation for clarity, onboarding, and conceptual consistency
  * aligned repository links, badges, and references with the current project location
  * tightened terminology across concepts, workflows, and reference documentation

---

### Removed

* Legacy repository artifacts:

  * removed outdated local helper scripts from `scripts/`
  * removed obsolete example artifact `examples/vault-layout.txt`
  * removed legacy formatter-based CLI module and related tests
  * cleans up repository surface in favor of the current runtime and interaction model

---

### Fixed

* Inconsistent sync behavior:

  * `sync` previously ignored the active profile when writing repository env files
  * now correctly reflects the selected profile in the generated output file name

* Confirmation message duplication:

  * removed duplicated inline message construction across commands
  * unified confirmation text generation under reusable prompt builders

---

### Build

* Package metadata refinements for the next patch release:

  * `pyproject.toml` metadata was finalized for the upcoming `2.3.1` release
  * packaging information now better matches the current repository and distribution state

---

### Notes

* This iteration strengthens the **interaction architecture of the CLI** and the **profile-aware projection model**.

* Key improvements:

  * clearer separation between input, orchestration, and output
  * safer and more expressive destructive confirmations
  * more predictable multi-profile repository sync behavior
  * cleaner command implementations with less embedded formatting logic
  * better alignment between documentation, packaging metadata, and repository identity

* Prepares the codebase for:

  * richer interactive flows (wizard-style commands)
  * alternative frontends (TUI, GUI, API)
  * localization / i18n of CLI messages
  * policy-aware confirmations (e.g. CI vs local)
  * broader multi-environment workflows directly from repository projections

---

## [2.3.0] – 2026-03-30

### Breaking changes

* Project identity commands have been moved under `envctl project`:
  * `bind`, `unbind`, `rebind`, `repair` are no longer available at root level
  * use `envctl project <command>` instead

### Added

* Confirmation prompt in `vault show --raw`:

  * prevents accidental exposure of unmasked secret values
  * requires explicit user approval before printing raw values

* Remove preflight model:

  * introduced `RemovePlan` domain model
  * enables separation between inspection and execution
  * prepares CLI for richer confirmation logic

* Inference tracking in `add`:

  * added `inferred_fields_used` to `AddResult`
  * allows CLI to show only relevant inferred metadata
  * improves transparency of contract inference

* Identity and repair test coverage:

  * added unit tests for project context resolution
  * covers local bindings, remote recovery, `project_key`, `known_paths`, ambiguity, and derived fallback
  * added unit tests for `repair` service flows
  * covers healthy, repaired, recreated, created, and needs-action outcomes

* Shared project-context test builders:

  * added reusable helpers in `tests/support/contexts.py`
  * centralizes creation of complete `ProjectContext` instances for tests
  * reduces duplication and drift across service and repository test suites

* Rebind command and service test coverage:

  * added unit tests for `rebind` CLI behavior
  * added unit tests for `rebind` service flows, including value-copy scenarios

* Project command group:

  * added `envctl project` to group project identity and binding operations
  * includes `bind`, `unbind`, `rebind`, and `repair`
  * improves CLI discoverability by separating daily workflows from maintenance commands

* Structured JSON output support:

  * added global `--json` output mode
  * introduced structured machine-readable output for:
    * `check`
    * `inspect`
    * `explain`
    * `status`
    * `doctor`
  * establishes a stable scripting-oriented output shape with explicit success and error payloads

* Runtime mode foundations:

  * introduced `RuntimeMode` with `local` and `ci`
  * added runtime mode support to application configuration
  * supports runtime mode overrides through `ENVCTL_RUNTIME_MODE`

* Profile-aware value management:

  * introduced explicit profile model (`local` + named profiles)
  * added profile-specific vault storage:
    * `values.env` for implicit local profile
    * `profiles/<name>.env` for explicit profiles
  * added `DEFAULT_PROFILE` and `ENVCTL_PROFILE` support
  * introduced profile-aware path resolution utilities

* Profile command group:

  * added `envctl profile` commands:
    * `list`, `create`, `copy`, `remove`, `path`
  * enables explicit profile lifecycle management

### Changed

* `remove` command flow:

  * refactored to reuse project context resolved during preflight
  * `run_remove` no longer loads project context independently
  * eliminates redundant Git and filesystem calls
  * improves separation between inspection and execution logic
  * aligns service behavior with plan → execute architecture

* `add` command UX:

  * inference warnings are now conditional:

    * only shown when new contract entries are created
    * only shown when inferred fields are actually used
  * avoids noise when updating existing variables or using explicit overrides

* Default coercion logic in `add`:

  * clarified `_coerce_default` behavior
  * improved consistency between CLI input and contract types
  * better handling of `int` and `bool` defaults

* `ResolutionReport` made structurally immutable:

  * internal state now uses `MappingProxyType` and tuples
  * prevents accidental mutation of resolved values
  * aligns runtime guarantees with domain expectations

* Internal architecture improvements:

  * cleaner separation between:

    * preflight vs execution (remove)
    * inference vs override (add)
  * reduced duplication in context loading within remove flow
  * improved service-level consistency

* Legacy state compatibility:

  * `state.json` version 1 is now accepted and normalized in memory to the current structure
  * recovery and repair flows remain compatible with older vault metadata

* Context binding internals:

  * `load_project_context()` now uses `dataclasses.replace()` when promoting derived identities
  * avoids fragile field-by-field reconstruction of `ProjectContext`

* Test support architecture:

  * test context helpers now build full `ProjectContext` objects instead of lightweight stand-ins
  * aligns test fixtures with the current identity model and binding fields
  * makes future `ProjectContext` changes easier to absorb in one place

* Init service result model:

  * removed duplicate `InitResult` definition from the domain layer
  * unified initialization outcome model under `init_service`
  * eliminates ambiguity between domain and service representations

* CLI surface organization:

  * project identity operations are now grouped under `envctl project`
  * reduces noise at the root command level
  * separates daily workflows from identity and maintenance operations

* `rebind` command UX:

  * removed the artificial `--new-project` guard from `envctl project rebind`
  * relies on explicit confirmation instead of a redundant flag
  * improves discoverability and makes the command behave as users expect

* CLI output architecture:

  * introduced centralized CLI runtime state for output mode selection
  * added serializer-based JSON rendering for supported read-only commands
  * kept human-readable text rendering as the default interface

* Configuration model:

  * extended `AppConfig` with runtime mode support
  * configuration loading now validates and resolves runtime mode consistently across config and environment overrides

* Value mutation commands are now profile-aware:

  * `set`, `unset`, `remove`, `sync`, and `export` now operate on the active profile
  * active profile resolved via CLI (`--profile`) or environment (`ENVCTL_PROFILE`)
  * output now consistently includes `profile` and resolved paths
  * removes implicit coupling to a single vault file

* `remove` command semantics:

  * now removes variables from:
    * contract
    * all persisted profiles
  * introduces global removal behavior instead of local-only mutation
  * improved confirmation messaging with multi-profile awareness

* Domain operation models:

  * replaced legacy result models with profile-aware structures:
    * `AddVariableResult`
    * `RemoveVariableResult`
    * `VaultEditResult`
  * added explicit profile context to mutation results
  * aligned domain layer with profile-based runtime model

* Configuration model:

  * added `default_profile` to `AppConfig`
  * config writer now persists default profile
  * profile resolution is now part of runtime configuration

### Fixed

* `remove` execution inefficiency:

  * removed redundant context loading between preflight and execution

* `add` command noise:

  * eliminated unnecessary inference warnings

* Lint and type issues:

  * resolved `ruff` complexity and style warnings
  * fixed `mypy` compatibility issues (e.g. `datetime.UTC`)
  * restored compatibility in `state_repository` (`write_state`)

* Backward compatibility in project state:

  * fixed failure when reading vault state created with older `STATE_VERSION = 1`
  * prevents legacy `state.json` files from breaking detection, recovery, and repair flows

* Identity test coverage:

  * restored and expanded test coverage for project context resolution and repair scenarios
  * aligned tests with the current binding and recovery model

* Init service test alignment:

  * updated init-service tests to use the current `ProjectContext` shape
  * aligned `state.json` expectations with the version 2 state model
  * removed outdated assumptions from older identity and state structures

* Domain model inconsistency:

  * removed unused and outdated `InitResult` from `domain/project.py`
  * prevents divergence between declared domain models and actual runtime behavior

* `rebind` command ergonomics:

  * `envctl project rebind` no longer fails with a `BadParameter` when called without `--new-project`

* Unsupported CLI output handling:

  * commands that do not yet support structured JSON now fail explicitly under `--json`
  * avoids mixed human and machine-oriented output on stdout

### Security

* Hardened secret exposure safeguards:

  * `vault show --raw` now requires explicit confirmation
  * reduces risk of accidental leakage in terminal sessions

* CI read-only runtime restrictions:

  * mutating commands are now blocked when running in `ci` runtime mode
  * prevents local vault mutation, rebinding, and other stateful operations during CI execution

* Documentation updates:

  * clarified that `add` mutates the repository contract
  * reinforced distinction between:

    * contract mutation (shared)
    * value mutation (local)

### Documentation

* Updated architecture, commands, and security model:

  * clarified contract mutation semantics
  * documented `add` as a shared, versioned operation
  * improved consistency across docs

* Updated architecture, commands, metadata, security, and README documentation:

  * documented the three-state identity model (`local`, `recovered`, `derived`)
  * documented canonical binding in local Git config
  * clarified recovery by remote, `project_key`, and `known_paths`
  * documented `state.json` v2 semantics and legacy compatibility
  * clarified `vault show --raw` confirmation behavior
  * documented grouped project identity operations under the CLI surface

### Notes

* This iteration focuses on **execution consistency, UX clarity, internal correctness, and scripting readiness**
* Ensures the identity and contract model behaves predictably across legacy and current state
* Introduces the first explicit runtime distinction between local interactive usage and CI-style read-only execution

* Key improvements:

  * less CLI noise
  * safer defaults
  * clearer separation between planning and execution
  * machine-readable output for core read-only workflows
  * explicit runtime restrictions for CI environments

* Prepares the codebase for:

  * richer CLI interactions
  * future policy layers
  * pluggable providers
  * profile-aware resolution
  * broader automation and CI integration

* This iteration introduces the foundation for **multi-environment workflows**:

  * local vs named profiles
  * consistent profile-aware mutation and resolution
  * explicit separation between contract and environment instances

* Key improvements:

  * deterministic profile selection
  * safer multi-environment handling
  * clearer operational semantics for mutation commands

* Prepares the codebase for:

  * environment promotion flows (dev → staging → prod)
  * profile-based automation and CI integration
  * future policy enforcement per profile

---

## [2.2.0] – 2026-03-29

### Highlights

- Contract-driven workflows stabilized and completed
- CRUD operations (`add`, `remove`, `set`, `unset`) redefined under contract semantics
- Contract inference system introduced and integrated
- Strong validation and typing across resolution and contract layers
- Fully modular CLI architecture

---

### Added

- Contract-aware `add` command:
  - infers type, sensitivity, and required status
  - supports interactive metadata editing
  - allows explicit overrides (type, required, sensitive, description, etc.)
- Contract-aware `remove` command:
  - removes variables from both contract and vault
  - explicit confirmation model
- `set` command aligned with contract:
  - updates values without modifying contract definition
- `unset` command:
  - removes value from vault while preserving contract definition
- Contract inference system:
  - type detection (`string`, `int`, `bool`, `url`)
  - sensitivity inference
  - pattern and choices inference
- Adapters layer:
  - `dotenv`
  - `editor`
  - `git`
- Makefile with developer workflows

---

### Changed

- All variable operations (`add`, `remove`, `set`, `unset`) now follow **contract-first semantics**
- CLI reorganized into modular command packages
- Services refactored to align with contract-driven workflow
- Resolution layer hardened:
  - strict type validation
  - explicit handling of unsupported types
- Repository layer simplified and aligned with contract model
- Improved:
  - dotenv serialization
  - atomic writes
  - permission handling
- `doctor` command updated to reflect contract + vault state

---

### Fixed

- Edge cases in dotenv serialization and quoting
- Project identity inconsistencies during init
- Sensitive value masking issues
- Atomic write reliability
- Contract validation inconsistencies
- Handling of invalid or unsupported variable types

---

### Breaking changes

- `add`, `remove`, `set`, `unset` semantics have changed:
  - operations are now contract-aware
  - contract and values are no longer implicitly coupled
- Strict type validation enforced (unsupported types rejected)
- Contract is now the authoritative source for variable definitions

---

### Notes

- This release finalizes the operational model around:
  - contract → definition
  - resolution → evaluation
  - projection → usage
- CRUD operations are now consistent with this model
- Prepares the system for future resolution strategies and policy layers

---

## [2.0.0] – 2026-03-29

### Highlights

- Major architectural shift from **file manager → environment control system**
- Introduction of **contract / resolution / projection model**
- Removal of symlink-based workflows
- Foundation for future policy-driven environment management

### Added

- New contract format: `.envctl.schema.yaml`
- Explicit separation of:
  - contract (what is needed)
  - resolution (how values are obtained)
  - projection (how values are used)
- Core contract-aware commands:
  - `check`
  - `fill`
- Initial resolution model
- Safer environment handling model (no implicit writes)

### Changed

- `.env.local` redefined as a **generated artifact**, not source of truth
- Repository no longer owns environment values
- Vault usage becomes an implementation detail, not the model
- CLI begins transition toward modular structure
- Internal architecture moves toward domain-driven layering

### Validation model

- Environment variables validated against contract
- Required vs optional variables enforced
- Early detection of missing or invalid values

### Breaking changes

- Removal of symlink-based workflow
- Removal of implicit repo ↔ vault linkage model
- `.env.local` no longer manually managed
- Introduction of mandatory contract for full workflow

### Notes

- This version introduces the **conceptual foundation of v2**
- Some areas are intentionally incomplete and refined in 2.1/2.2
- Represents a transition release rather than final UX

### Design principles

- Explicit configuration over implicit behavior
- Deterministic execution
- Separation of concerns (contract vs runtime)
- Safety-first environment handling

---

## [1.0.2] – 2026-03-28

### Changed

- Refactored the internal codebase into a clearer layered structure with dedicated `cli`, `domain`, `repository`, `services`, `config`, and `utils` packages.
- Replaced the previous flat `cli.py` and `models.py` layout with more focused modules and explicit boundaries.
- Improved separation of concerns between command-line handling, business orchestration, metadata persistence, configuration, and reusable helpers.
- Introduced explicit typed domain models for command results and repository metadata.
- Updated tests and imports to match the new package structure.

### Documentation

- Updated contributor and architecture documentation to reflect the new internal layered structure.
- Added an in-depth architecture guide for contributors in `docs/dev/architecture-in-depth.md`.
- Aligned roadmap and internal architecture references with the refactored package layout.
- Removed outdated references to the previous flat module organization.

## [1.0.1] – 2026-03-28

### Changed

- Refined the documentation to clarify `envctl`'s environment lifecycle model.
- Defined the separation between structure, validation, and secret storage.
- Clarified the future schema-based workflow around `.envctl.schema.yaml`, `check`, and `fill`.
- Documented that `init` remains deterministic and structural only.

### Documentation

- Updated architecture, command model, roadmap, security notes, README, and contribution guidance to reflect the refined product vision.

## [1.0.0] – 2026-03-28

### Added

- First stable release.
- Core commands: `init`, `repair`, `unlink`, `status`, `set`, `doctor`, `remove`, `config init`.
- Vault structure with unique project directories (`<slug>--<id>`).
- XDG-based configuration (JSON only) with default path `~/.config/envctl/config.json`.
- Permissions: vault directories created with `0700`, vault files with `0600`, config file with `0600`.
- `doctor` command checks config, vault path, permissions, Git detection, and symlink support.
- `repair` and `remove` support `--yes` / `-y` for non-interactive use.
- Comprehensive test suite with isolated environment fixtures.
- Full documentation in the `docs/` directory.
- Global `--version` option.

### Security

- Secrets are never printed in normal command output.
- No overwriting of regular files without confirmation.
- `doctor` warns about world-writable vault directories.

### Known limitations

- No encryption at rest.
- JSON configuration only.
- No repository listing command.
- No machine-readable output for scripting.