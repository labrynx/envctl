# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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