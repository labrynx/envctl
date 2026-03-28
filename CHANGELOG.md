# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- *(none yet)*

### Changed

- *(none yet)*

### Fixed

- *(none yet)*

## [1.0.0] – 2026-03-28

### Added

- First stable release.
- Core commands: `init`, `repair`, `unlink`, `status`, `set`, `doctor`, `remove`, `config init`.
- Vault structure with unique project directories (`<slug>--<id>`).
- XDG‑based configuration (JSON only) with default path `~/.config/envctl/config.json`.
- Permissions: vault directories created with `0700`, vault files with `0600`, config file with `0600`.
- `doctor` command checks config, vault path, permissions, Git detection, and symlink support.
- `repair` and `remove` support `--yes` / `-y` for non‑interactive use.
- Comprehensive test suite with isolated environment fixtures.
- Full documentation in `docs/` directory.
- Global `--version` option.

### Security

- Secrets are never printed in normal command output.
- No overwriting of regular files without confirmation.
- Doctor warns about world‑writable vault directories.

### Known limitations

- No encryption at rest.
- No YAML config support (planned for v1.1).
- No `list` command (planned for v1.1).
- No `--json` output for scripting (planned for v1.1).
