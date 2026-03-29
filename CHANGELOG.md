## [2.2.0] – 2026-03-29

### Highlights

- envctl evolves into a **local environment control plane**
- Contract-driven workflows become the **core operating model**
- Full CLI modularization and service alignment
- Stronger validation, typing, and file safety guarantees
- Improved developer experience with tooling and testing

### Added

- Contract-driven workflows centered on `.envctl.schema.yaml`.
- `check` command to validate resolved environment state against the contract.
- `fill` command to interactively resolve missing required variables.
- `inspect` command for safe inspection of resolved environment values.
- `explain KEY` command to trace how a variable is resolved.
- `run -- <command>` to inject resolved environment variables into subprocesses.
- `sync` command to explicitly materialize `.env.local`.
- `export` command to output shell-compatible environment exports.
- Contract inference system (types, sensitivity, defaults, patterns, choices).
- Adapters layer (`dotenv`, `editor`, `git`).
- Makefile with quality and testing workflows.

### Changed

- CLI reorganized into modular command packages.
- Services redesigned to align with contract-driven execution.
- Repository layer aligned with contract/resolution model.
- Introduced `pydantic` for stricter validation.
- Improved atomic writes, permissions, and dotenv handling.
- Enhanced `doctor` with contract awareness.

### Removed

- Legacy CLI structure.
- Deprecated templates and unused components.

### Fixed

- Dotenv serialization and quoting.
- Project identity stability.
- Sensitive value masking.
- Atomic file writes.
- Contract validation consistency.
- Version fallback handling.

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

---

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