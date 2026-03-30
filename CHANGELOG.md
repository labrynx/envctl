# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

### Changed

* `remove` command flow:

  * refactored to avoid double loading of project context
  * preflight inspection separated from execution logic
  * improved UX consistency and internal clarity

* `add` command UX:

  * inference warnings are now conditional:

    * only shown when new contract entries are created
    * only shown when inferred fields are actually used
  * avoids noise when updating existing variables or using explicit overrides

* Default coercion logic in `add`:

  * clarified `_coerce_default` behavior
  * improved consistency between CLI input and contract types
  * better handling of `int` and `bool` defaults

* Resolution model:

  * `ResolutionReport` made structurally immutable
  * improved safety and predictability of resolution results
  * reduces risk of accidental mutation across services

* Internal architecture improvements:

  * cleaner separation between:

    * preflight vs execution (remove)
    * inference vs override (add)
  * reduced duplication in context loading
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

### Fixed

* `remove` command inefficiency:

  * removed redundant context loading

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
  
### Security

* Hardened secret exposure safeguards:

  * `vault show --raw` now requires explicit confirmation
  * reduces risk of accidental leakage in terminal sessions

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

### Notes

* This iteration focuses on **UX hardening and semantic clarity**, not new surface area
* Ensures the new identity model works safely with existing vaults
* Key improvements:

  * less noise
  * safer defaults
  * clearer separation of responsibilities

* Prepares the codebase for:

  * richer CLI interactions
  * future policy layers
  * machine-readable outputs

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