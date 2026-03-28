# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Repositioned `envctl` from a symlink-oriented local env file manager to a local environment control plane.
- Reframed the product model around three explicit concerns: contract, resolution, and projection.
- Moved the project away from repository-to-vault linkage as the primary architectural concept.
- Deprecated symlink-first workflows as the core operating model.
- Shifted the repository contract to `.envctl.schema.yaml` as the shared source of truth for environment requirements.
- Treated generated `.env.local` files as derived artifacts rather than canonical state.

### Added

- Introduced contract-driven workflows centered on `.envctl.schema.yaml`.
- Added `check` to validate resolved environment state against the project contract.
- Added `fill` to interactively satisfy missing required values.
- Added `inspect` to display resolved environment state safely.
- Added `explain KEY` to show how one variable is resolved.
- Added `run -- <command>` to inject resolved environment values directly into subprocesses.
- Added `sync` to materialize `.env.local` as an explicit generated artifact.
- Added `export` to print shell-safe export lines from the resolved environment.
- Added domain concepts for contract models and environment resolution results.
- Added repository support for contract loading and local state handling aligned with the v2 model.

### Removed

- Removed symlinks as the central workflow model for the current branch direction.
- Removed legacy command concepts from the active v2 direction, including repository-link repair and unlink flows.
- Removed the assumption that a repository-local metadata linkage file is the primary source of truth.

### Documentation

- Rewrote the main architecture documentation around contract, resolution, and projection.
- Rewrote the command reference to describe the v2 command model.
- Rewrote configuration documentation to clarify the boundary between user config and project contract.
- Rewrote contributor architecture guidance to reflect the new internal workflow model.
- Rewrote metadata documentation to describe local state and derived project identity instead of mandatory repository linkage.
- Rewrote platform documentation to reflect the removal of symlinks as a core dependency.
- Rewrote security documentation around explicit local storage, read-only validation, and projection safety.
- Updated the roadmap to reflect the v2 branch target and follow-on phases.

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