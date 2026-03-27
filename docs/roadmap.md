# Roadmap

## v1

- local vault
- symlink-based repository linking
- unique vault project directories based on repository identity
- explicit repository metadata
- per-project `.env.local`
- safe status and doctor commands
- deterministic key updates
- explicit repository link repair command

## v1.1

- YAML config support
- multiple managed env files per repository
- `list` command for repository environments
- `init --adopt-existing`
- `init --force` for explicit recovery flows
- `repair --yes`
- `repair --backup`
- `repair --no-backup`
- optional config bootstrap command
- richer metadata and diagnostics

## Later

- import/export helpers
- better shell completions
- dry-run support

## Out of scope for now

- encryption
- cloud sync
- secret manager integrations
- CI/CD integration
